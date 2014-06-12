#!/usr/bin/env python

import os
import sys
import traceback
#import pyximport; pyximport.install()

import gtrackcore
from gtrackcore.input.core.ToolGenomeElementSource import ToolGenomeElementSource

from gtrackcore.input.core.GenomeElementSource import GenomeElementSource
from gtrackcore.metadata.TrackInfo import DynamicTrackInfo, TrackInfo
from gtrackcore.preprocess.GESourceManager import GESourceManager, OverlapClusteringGESourceManager, RegionBasedGESourceManager
from gtrackcore.preprocess.PreProcessGeSourceJob import PreProcessGeSourceJob
from gtrackcore.preprocess.PreProcMetaDataCollector import PreProcMetaDataCollector
from gtrackcore.preprocess.PreProcessUtils import PreProcessUtils
from gtrackcore.track.format.TrackFormat import TrackFormat
from gtrackcore.track.hierarchy.ExternalTrackManager import ExternalTrackManager
from gtrackcore.track.hierarchy.ProcTrackOptions import ProcTrackOptions
from gtrackcore.track.hierarchy.RenameTrack import renameTrack
from gtrackcore.track.hierarchy.OrigTrackFnSource import OrigTrackNameSource
from gtrackcore.track.pytables.database.MetadataHandler import MetadataHandler
from gtrackcore.preprocess.pytables.CommonTableFunctions import merge_and_rename_overlap_tables, sort_preprocessed_table
from gtrackcore.util.CommonFunctions import createOrigPath, get_dir_path, prettyPrintTrackName, \
                                        reorderTrackNameListFromTopDownToBottomUp, \
                                        replaceIllegalElementsInTrackNames
from gtrackcore.util.CustomExceptions import NotSupportedError, AbstractClassError, Warning
from gtrackcore.track.core.GenomeRegion import  GenomeRegion


class PreProcessTracksJob(object):
    VERSION = '1.0'

    PASS_ON_EXCEPTIONS = False

    def __init__(self, genome, username='', mode='Real', raiseIfAnyWarnings=False):
        self._genome = genome
        self._username = username
        self._mode = mode
        self._status = ''
        self._raiseIfAnyWarnings = raiseIfAnyWarnings
        self._warningTrackNames = []

    def process(self):
        assert self._genome is not None, 'Error: genome must be specified when preprocessing tracks.'

        gtrackcore.preprocess.is_preprocessing = True

        atLeastOneFinalized = False
        for trackName in self._allTrackNames():
            assert trackName != ['']
            overlapRulesProcessedForTrackName = []
            collector = PreProcMetaDataCollector(self._genome, trackName)

            try:
                trackName = self._renameTrackNameIfIllegal(trackName)

                for allowOverlaps in [True, False]:

                    anyGeSourceManagers = False
                    for geSourceManager in self._allGESourceManagers(trackName, allowOverlaps):
                        anyGeSourceManagers = True

                        # PreProcess if needed
                        if self._shouldPreProcess():
                            PreProcessUtils.removeOutdatedPreProcessedFiles(self._genome, trackName, allowOverlaps, self._mode)

                            if self._shouldPrintProcessMessages() and allowOverlaps not in overlapRulesProcessedForTrackName:
                                self._printProcessTrackMessage(trackName, allowOverlaps)
                                overlapRulesProcessedForTrackName.append(allowOverlaps)

                            self._status = 'Trying to preprocess geSource...'
                            geSourceJob = PreProcessGeSourceJob(trackName, geSourceManager, allowOverlaps, self._mode)
                            anyWarnings = geSourceJob.process()

                            if self._raiseIfAnyWarnings and anyWarnings and trackName not in self._warningTrackNames:
                                self._warningTrackNames.append(trackName)

                            collector.updatePreProcDirtyStatus(geSourceJob.hasModifiedData())

                    # Finalize overlapRule output if needed
                    if anyGeSourceManagers and self._shouldFinalize() and collector.preProcIsDirty():
                        if self._mode == 'Real' and self._shouldMergeChrFolders():
                            sort_preprocessed_table(self._genome, trackName, allowOverlaps)
                            PreProcessUtils.create_bounding_regions(self._genome, trackName, allowOverlaps)

                        self._status = 'Trying to check whether 3D data is correct'
                        PreProcessUtils.checkIfEdgeIdsExist(self._genome, trackName, allowOverlaps)
                        PreProcessUtils.checkUndirectedEdges(self._genome, trackName, allowOverlaps)
                        PreProcessUtils.checkUndirectedEdges(self._genome, trackName, allowOverlaps)
                        collector.markOverlapRuleAsFinalized(allowOverlaps)

                # Finalize track if needed
                if self._shouldFinalize():
                    if collector.preProcIsDirty():
                        self._status = 'Trying to finalize.'
                        collector.finalize(self._username, self._shouldPrintProcessMessages())
                        if not atLeastOneFinalized:
                            atLeastOneFinalized = True
                        merge_and_rename_overlap_tables(self._genome, trackName)
                        self._persist_metadata(trackName)
                else:
                        collector.removeEntry()

            except NotSupportedError, e:
                collector.removeEntry()
                if self.PASS_ON_EXCEPTIONS:
                    raise
                else:
                    self._printExceptionMsg(e, trackName, Error=False)
            except Exception, e:
                collector.removeEntry()
                if self.PASS_ON_EXCEPTIONS:
                    raise
                else:
                    self._printExceptionMsg(e, trackName, Error=True)

            self._calcAndStoreSubTrackCount(trackName)

        if self._raiseIfAnyWarnings and len(self._warningTrackNames) > 0:
            raise Warning('Warnings occurred in the following tracks: ' + \
                          ', '.join(prettyPrintTrackName(tn) for tn in self._warningTrackNames))

        gtrackcore.preprocess.is_preprocessing = False

        return atLeastOneFinalized

    def _persist_metadata(self, track_name):
        dynamic_trackinfo = DynamicTrackInfo(self._genome, track_name)
        metadata_handler = MetadataHandler(self._genome, track_name)
        metadata_handler.update_persisted_trackinfo(dynamic_trackinfo)

    def _allTrackNames(self):
        raise AbstractClassError

    def _allGESourceManagers(self, trackNameList, allowOverlaps):
        """ ??
        Generator that return all the GESourceManagers.

        Basically returns one SourceManager that handle overlaps, and one where overlaps are merged

        Parameters
        ----------
        trackNameList : list
            Track name/id in list format.
        allowOverlaps : bool
            Whether overlaps are allowed or not.
        """
        collector = PreProcMetaDataCollector(self._genome, trackNameList)

        #If there should be no overlaps
        if allowOverlaps == False and collector.overlapRuleHasBeenFinalized(True):
            self._status = 'Trying to prepare preprocessing for track "%s"' % ':'.join(trackNameList) + \
                (' (allowOverlaps: %s)' % allowOverlaps)
            yield self._getGESourceManagerFromTrack(trackNameList)
        else:
            for geSource in self._allGESources(trackNameList):
                if allowOverlaps == True:
                    tf = TrackFormat.createInstanceFromGeSource(geSource)
                    if tf.isDense() or geSource.hasNoOverlappingElements():
                        return

                self._status = 'Trying to prepare preprocessing for track "%s"' % ':'.join(trackNameList) + \
                                (' (filename: "%s")' % geSource.getFileName() if geSource.hasOrigFile() else '') + \
                                (' (allowOverlaps: %s)' % allowOverlaps)
                if PreProcessUtils.shouldPreProcessGESource(trackNameList, geSource, allowOverlaps):
                    yield self._getGESourceManagerFromGESource(geSource)

    def _allGESources(self, trackName):
        raise AbstractClassError

    def _getGESourceManagerFromGESource(self, geSource):
        return GESourceManager(geSource)

    def _getGESourceManagerFromTrack(self, trackName):
        origBrTuples = PreProcMetaDataCollector(self._genome, trackName).getBoundingRegionTuples(allowOverlaps=True)
        return OverlapClusteringGESourceManager(self._genome, trackName, origBrTuples)

    def _shouldPreProcess(self):
        return True

    def _shouldPrintProcessMessages(self):
        return True

    def _shouldFinalize(self):
        return True

    def _shouldMergeChrFolders(self):
        return True

    def _renameTrackNameIfIllegal(self, trackName):
        legalTrackName = [replaceIllegalElementsInTrackNames(x) for x in trackName]

        if legalTrackName != trackName and os.path.exists(get_dir_path(self._genome, trackName)):
            renameTrack(self._genome, trackName, legalTrackName)

        return legalTrackName

    def _updateAllChrs(self, allChrs, chrList, allowOverlaps):
        if not allowOverlaps in allChrs:
            allChrs[allowOverlaps] = set()
        assert all(chr not in allChrs[allowOverlaps] for chr in chrList), \
            'Error: chromosome %s already preprocessed for previous GenomeElementSource (this may be because of elements of the same chromosome is found in different files).' % chr
        allChrs[allowOverlaps].update(set(chrList))

    def _calcAndStoreSubTrackCount(self, trackName):
        ti = TrackInfo(self._genome, trackName)
        if ti.isValid():
            ti.subTrackCount = 1
            ti.store()

    def _printProcessTrackMessage(self, trackName, allowOverlaps):
        if self._mode == 'Simulated':
            print "Would now have processed track: '%s' with allowOverlaps: %s in a real run." % (':'.join(trackName), allowOverlaps)
        elif self._mode == 'UpdateMeta':
            print "Only updating meta info based on track: '%s' with allowOverlaps: %s" % (':'.join(trackName), allowOverlaps)
        elif self._mode == 'Real':
            print "Processing track: '%s' with allowOverlaps: %s" % (':'.join(trackName), allowOverlaps)

    def _printExceptionMsg(self, e, trackName, Error=False):
        print (os.linesep + '--- BEGIN ERROR ---' + os.linesep *2 if Error else 'Warning! ') + \
            "Could not pre-process track '%s'." % ':'.join(trackName)
        print "Status: %s" % self._status
        #print e.__class__.__name__ + ':', e
        if Error:
            traceback.print_exc(file=sys.stdout)
            print os.linesep + '--- END ERROR ---' + os.linesep

class PreProcessAllTracksJob(PreProcessTracksJob):
    """ ??
    Handles preprocessing of tracks stored in the location specified by the trackNameFilter


    Parameters
    ----------
    genome : string
        Genome id.
    trackNameFilter : list
        ?! Track id in list format.
    username : string
        ??
    mergeChrFolders : bool
        ?! Specifies whether chromosome folders should be merged into one.

    Attributes
    ----------
    _trackNameFilter : list
        Track name in list format.

    _mergeChrFolders : bool
        ??

    """

    def __init__(self, genome, trackNameFilter=[], username='', mergeChrFolders=True, **kwArgs):
        PreProcessTracksJob.__init__(self, genome, username=username, **kwArgs)
        if trackNameFilter == ['']:
            trackNameFilter = []
        self._trackNameFilter = trackNameFilter
        self._mergeChrFolders = mergeChrFolders

    def _allTrackNames(self):
        #avoidLiterature = len(self._trackNameFilter) == 0 or (self._trackNameFilter != GenomeInfo.getLiteratureTrackName(self._genome))
        trackSource = OrigTrackNameSource(self._genome, self._trackNameFilter, avoidLiterature=False)
        return reorderTrackNameListFromTopDownToBottomUp(trackSource)

    def _allGESources(self, trackName):
        baseDir = createOrigPath(self._genome, trackName)

        self._status = 'Trying os.listdir on: ' + baseDir
        for relFn in sorted(os.listdir( baseDir )):
            fn = os.sep.join([baseDir, relFn])

            self._status = 'Checking file: ' + fn
            if os.path.isdir(fn):
                continue

            fnPart = os.path.split(fn)[-1]
            if fnPart[0] in ['.','_','#'] or fnPart[-1] in ['~','#']: #to avoid hidden files..
                continue

            self._status = 'Trying to create geSource from fn: ' + fn
            yield GenomeElementSource(fn, self._genome, forPreProcessor=True)

    def _calcAndStoreSubTrackCount(self, trackName):
        ti = TrackInfo(self._genome, trackName)
        trackCount = 0
        for subTrackName in ProcTrackOptions.getSubtypes(self._genome, trackName, True):
            subTrackCount = TrackInfo(self._genome, trackName + [subTrackName]).subTrackCount
            if subTrackCount:
                trackCount += subTrackCount
        if ti.isValid():
            trackCount += 1
        ti.subTrackCount = trackCount
        ti.store()

    def _shouldMergeChrFolders(self):
        return self._mergeChrFolders


class PreProcessExternalTrackJob(PreProcessTracksJob):
    PASS_ON_EXCEPTIONS = True

    def __init__(self, genome, fullFn, extTrackName, fileSuffix, **kwArgs):
        PreProcessTracksJob.__init__(self, genome, **kwArgs)
        self._fullFn = fullFn
        self._extTrackName = extTrackName
        self._fileSuffix = fileSuffix

    def _allTrackNames(self):
        return [self._extTrackName]

    def _allGESources(self, trackName):
        return [ExternalTrackManager.getGESource(self._fullFn, self._fileSuffix, \
                                                 self._extTrackName, self._genome, printWarnings=True)]

class PreProcessCustomTrackJob(PreProcessTracksJob):
    PASS_ON_EXCEPTIONS = True

    def __init__(self, genome, trackName, regionList, getGeSourceCallBackFunc, username='', \
                 preProcess=True, finalize=True, mergeChrFolders=True, **callBackArgs):
        PreProcessTracksJob.__init__(self, genome, username=username)
        self._trackName = trackName
        assert len(regionList) > 0
        self._regionList = regionList
        self._getGeSourceCallBackFunc = getGeSourceCallBackFunc
        self._callBackArgs = callBackArgs
        self._preProcess = preProcess
        self._finalize = finalize
        self._mergeChrFolders = mergeChrFolders

    def _allTrackNames(self):
        return [self._trackName]

    def _allGESources(self, trackName):
        regionList = self._regionList if self._preProcess else [self._regionList[0]]
        for region in regionList:
            yield self._getGeSourceCallBackFunc(self._genome, self._trackName, region, **self._callBackArgs)

    def _getGESourceManagerFromGESource(self, geSource):
        tf = TrackFormat.createInstanceFromGeSource(geSource)
        if tf.reprIsDense():
            if tf.getValTypeName() in ['Number', 'Number (integer)', 'Case-control']:
                return RegionBasedGESourceManager(geSource, self._regionList, \
                                                  calcStatsInExtraPass=False, countElsInBoundingRegions=False)
            else:
                raise NotSupportedError
        else:
            return RegionBasedGESourceManager(geSource, self._regionList, \
                                              calcStatsInExtraPass=True, countElsInBoundingRegions=True)

    def _getGESourceManagerFromTrack(self, trackName):
        raise NotSupportedError

    def _shouldPreProcess(self):
        return self._preProcess

    def _shouldPrintProcessMessages(self):
        return False

    def _shouldFinalize(self):
        return self._finalize

    def _shouldMergeChrFolders(self):
        return self._mergeChrFolders


class PreProcessToolOutputJob(PreProcessTracksJob):

    def __init__(self, tool_name, tool_input, genome, new_track_name, username='', merge_chr_folders=True, **kwArgs):
        PreProcessTracksJob.__init__(self, genome, username=username, **kwArgs)
        self._new_track_name = new_track_name
        self._tool_name = tool_name
        self._tool_input = tool_input
        self._mergeChrFolders = merge_chr_folders

    def _allTrackNames(self):
        return [self._new_track_name]

    def _allGESources(self, track_name):
        raise NotImplementedError

    def _allGESourceManagers(self, track_name_list, allow_overlaps):
        ge_source = ToolGenomeElementSource(self._tool_name, self._tool_input, self._genome, self._new_track_name)

        collector = PreProcMetaDataCollector(self._genome, track_name_list)
        if not allow_overlaps and collector.overlapRuleHasBeenFinalized(True):
            return [self._getGESourceManagerFromTrack(track_name_list)]

        if allow_overlaps and ge_source.hasNoOverlappingElements():
            return []

        return [self._getGESourceManagerFromGESource(ge_source)]

    def _calcAndStoreSubTrackCount(self, trackName):
        ti = TrackInfo(self._genome, trackName)
        trackCount = 0
        if ti.isValid():
            trackCount += 1
        ti.subTrackCount = trackCount
        ti.store()

    def _shouldMergeChrFolders(self):
        return True


if __name__ == "__main__":
    if not len(sys.argv) in [2,3,4]:
        print 'Syntax: python PreProcessTracksJob.py genome [trackName:subType] [mode=Real/Simulated/UpdateMeta]'
        sys.exit(0)

    if len(sys.argv) == 2:
        tn = []
        mode = 'Real'
    elif len(sys.argv) == 3:
        if sys.argv[2] in ['Real', 'Simulated', 'UpdateMeta']:
            tn = []
            mode = sys.argv[2]
        else:
            tn = sys.argv[2].split(':')
            mode = 'Real'
    else:
        tn = sys.argv[2].split(':')
        mode = sys.argv[3]

    assert mode in ['Real', 'Simulated', 'UpdateMeta']
    PreProcessAllTracksJob(sys.argv[1], tn, username='', mode=mode).process()

    #tool_input = {
    #    'track1': {
    #        'name': 'testcat:opertrack1'.split(':'),
    #        'allow_overlaps': False
    #    },
    #    'track2': {
    #        'name': 'testcat:opertrack2'.split(':'),
    #        'allow_overlaps': False
    #    },
    #    'genome_regions': [GenomeRegion('testgenome', 'chr21', 0, 46944323)]
    #}
    #
    #PreProcessToolOutputJob('union', tool_input, 'testgenome', ['testcat', 'union']).process()

    #tool_input = {
    #    'segment_track': {
    #        'name': 'testcat:operations:mean:segment'.split(':'),
    #        'allow_overlaps': False
    #    },
    #    'function_track': {
    #        'name': 'testcat:operations:mean:function'.split(':'),
    #        'allow_overlaps': False
    #    },
    #    'genome_regions': [GenomeRegion('testgenome', 'chr21', 0, 10)]
    #}
    #
    #PreProcessToolOutputJob('mean', tool_input, 'testgenome', ['testcat', 'mean_result']).process()
