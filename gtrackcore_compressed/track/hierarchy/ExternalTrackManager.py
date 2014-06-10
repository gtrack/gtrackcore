
import os
import re

from gtrackcore_compressed.core.Config import Config
from gtrackcore_compressed.core.DataTypes import getSupportedFileSuffixes
from gtrackcore_compressed.metadata.TrackInfo import TrackInfo
from gtrackcore_compressed.track.format.TrackFormat import TrackFormat
from gtrackcore_compressed.util.CommonFunctions import get_dir_path, getClassName, \
                                        extractIdFromGalaxyFn as commonExtractIdFromGalaxyFn
from gtrackcore_compressed.util.CustomExceptions import ShouldNotOccurError

class ExternalTrackManager:
    '''
    Handles external track names. These are of three types:
    
    ['external','...']: ExternalTN. Handled basically just as a standard
        trackname. Only particularity is that the top category 'external' is not
        shown explicitly to users for track selection in HyperBrowser (is
        hidden).. Is of structure ['external'] + [URL_PREFIX] + id + [name],
        where id can be a list of length>1 (typically 2, due to codings from
        galaxy id..)
    
    ['galaxy','...']: GalaxyTN. An especially coded TN, used mainly to process
        files from galaxy history, but can also be used otherwise. Structure is:
        ['galaxy', fileEnding, origformatTrackFn, name] First element used for
        assertion, second element to determine origformat (as galaxy force
        ending .dat) origformatTrackFn is the file name to the data source for
        track data to be preprocessed. Typically ends with
        'XXX/dataset_YYYY.dat'. XXX and YYYY are numbers which are extracted and
        used as id in the form [XXX, YYYY] The last element is the name of the
        track, only used for presentation purposes.
    
    ['virtual','...'] VirtualMinimalTN. An especially coded TN, used for
        minimal runs of all statistics in order to display the analyses fitting
        for the selection of tracks in the user interface. The virtual track
        reads one data line of the original track file, and creates a virtual
        trackview based on the contents (VirtualMinimalTrack). Has the same
        syntax as GalaxyTN, apart from the first element, which is 'virtual'
        instead of 'galaxy'.
        
    ['redirect','...'] RedirectTN. An especially coded TN, used for redirecting
        minimal runs toward one of the preprocessed tracks under the genome
        'ModelsForExternalTracks'. The structure is [ 'redirect', genome, chr,
        description ] + trackName of the track to redirect to. This is used
        instead of the external track, which then does not need to have an
        associated original data file. Is handled by the createDirPath function
        in CommonFunctions.
    '''
    
    #@staticmethod
    #def isHistoryTrack(tn):
    #    return ExternalTrackManager.isExternalTrack(tn) or ExternalTrackManager.isGalaxyTrack(tn) \
    #        or ExternalTrackManager.isVirtualTrack(tn) or ExternalTrackManager.isRedirectTrack(tn)
    #
    #@staticmethod
    #def isExternalTrack(tn):
    #    return (tn is not None and len(tn)>0 and tn[0].lower() == 'external')
    #
    #@staticmethod
    ##@takes(list)
    #def isGalaxyTrack(tn):
    #    return (tn is not None and len(tn)>0 and tn[0].lower() == 'galaxy')
    
    @staticmethod
    def isVirtualTrack(tn):
        return (tn is not None and len(tn)>0 and tn[0].lower() == 'virtual')
    
    #@staticmethod
    #def isRedirectTrack(tn):
    #    return (tn is not None and len(tn)>0 and tn[0]=='redirect')

    #@staticmethod
    #def constructVirtualTrackNameFromGalaxyTN(galaxyTN):
    #    return ['virtual'] + galaxyTN[1:]
        
    #@staticmethod
    #def constructRedirectTrackName(trackName, genome, chr, description):
    #    return [ 'redirect', genome, chr, description ] + trackName
    
    #@staticmethod
    #def extractIdFromGalaxyFn(fn):
    #    return commonExtractIdFromGalaxyFn(fn)
    
    #@staticmethod
    #def extractFnFromGalaxyTN(galaxyTN):
    #    return galaxyTN[2] if type(galaxyTN) == list else galaxyTN.split(':')[2]
    
    #@staticmethod
    #def extractNameFromHistoryTN(galaxyTN):
    #    assert ExternalTrackManager.isHistoryTrack(galaxyTN)
    #    from urllib import unquote
    #    if ExternalTrackManager.isExternalTrack(galaxyTN):
    #        return unquote(galaxyTN[-1])
    #    else:
    #        return unquote(galaxyTN[3])

    #@staticmethod
    #def extractFileSuffixFromGalaxyTN(galaxyTN):
    #    if type(galaxyTN) == str:
    #        galaxyTN.split(':')
    #    suffix = galaxyTN[1]
    #    if not suffix in getSupportedFileSuffixes():
    #        raise ShouldNotOccurError('Filetype ' + suffix + ' not supported.')
    #    return suffix
    
    #@staticmethod
    #def createSelectValueFromGalaxyTN(galaxyTN):
    #    assert(galaxyTN[0].lower() == 'galaxy')
    #    return ','.join(['galaxy',\
    #                    ExternalTrackManager.extractIdFromGalaxyFn\
    #                     (ExternalTrackManager.extractFnFromGalaxyTN(galaxyTN))[1],\
    #                    ExternalTrackManager.extractFileSuffixFromGalaxyTN(galaxyTN),\
    #                    ExternalTrackManager.extractNameFromHistoryTN(galaxyTN)])
    
    #@classmethod
    #def getStdTrackNameFromGalaxyTN(cls, galaxyTN):
    #    assert(galaxyTN[0].lower() == 'galaxy')
    #    assert(galaxyTN[1].lower() in getSupportedFileSuffixes())
    #    fn = cls.extractFnFromGalaxyTN(galaxyTN)
    #    id = cls.extractIdFromGalaxyFn(fn)
    #    name = galaxyTN[-1]
    #    return ExternalTrackManager.createStdTrackName(id, name)
    
    #@classmethod
    #def createStdTrackName(cls, id, name, subtype = ''):
    #    urlPrefix = Config.URL_PREFIX.replace(os.path.sep, '')
    #    return ['external'] + ([urlPrefix] if urlPrefix != '' else []) + id + [name] + ([subtype] if subtype != '' else [])
    
    #@classmethod
    #def renameExistingStdTrackIfNeeded(cls, genome, stdTrackName):
    #    oldTrackName = None
    #    for allowOverlaps in [False, True]:
    #        parentDir = createDirPath(stdTrackName[:-1], genome, allowOverlaps=allowOverlaps)
    #        if os.path.exists(parentDir):
    #            dirContents = os.listdir(parentDir)
    #            if len(dirContents) == 1 and dirContents[0] != stdTrackName[-1]:
    #                oldDir = parentDir + os.sep + dirContents[0]
    #                oldTrackName = stdTrackName[:-1] + [dirContents[0]]
    #                newDir = parentDir + os.sep + stdTrackName[-1]
    #                os.rename(oldDir, newDir)
    #    
    #    if oldTrackName is not None:
    #        ti = TrackInfo(genome, oldTrackName)
    #        ti.trackName = stdTrackName
    #        ti.store()
        
    @staticmethod
    def getGESourceFromGalaxyOrVirtualTN(trackName, genome):
        fn = ExternalTrackManager.extractFnFromGalaxyTN(trackName)
        suffix = ExternalTrackManager.extractFileSuffixFromGalaxyTN(trackName)
        return ExternalTrackManager.getGESource(fn, suffix, genome=genome)
        
    @staticmethod
    def getGESource(fullFn, fileSuffix, extTrackName=None, genome=None, printWarnings=False):
        from gtrackcore_compressed.input.core.GenomeElementSource import GenomeElementSource
        return GenomeElementSource(fullFn, suffix=fileSuffix, forPreProcessor=True, genome=genome, trackName=extTrackName, external=True, printWarnings=printWarnings)
    
    #@staticmethod
    #def preProcess(fullFn, extTrackName, fileSuffix, genome, raiseIfAnyWarnings=False):
    #    from gold.origdata.PreProcessTracksJob import PreProcessExternalTrackJob
    #    job = PreProcessExternalTrackJob(genome, fullFn, extTrackName, fileSuffix, raiseIfAnyWarnings=raiseIfAnyWarnings)
    #    return job.process()
    
    #@classmethod
    #def getPreProcessedTrackFromGalaxyTN(cls, genome, galaxyTN, printErrors=True, raiseIfAnyWarnings=False):
    #    'Takes a GalaxyTN as input, pre-processes the data that GalaxyTN refers to, and finally returns an ExternalTN that refers to the pre-processed data and can be used as a normal track name.'
    #    stdTrackName = cls.getStdTrackNameFromGalaxyTN(galaxyTN)
    #    cls.renameExistingStdTrackIfNeeded(genome, stdTrackName)
    #    fn = cls.extractFnFromGalaxyTN(galaxyTN)
    #    fileSuffix = cls.extractFileSuffixFromGalaxyTN(galaxyTN)
    #    
    #    print 'Preprocessing external track...<br><pre>'
    #    try:
    #        if cls.preProcess(fn, stdTrackName, fileSuffix, genome, raiseIfAnyWarnings=raiseIfAnyWarnings):
    #            print '</pre>Finished preprocessing.<br>'
    #        else:
    #            print '</pre>Already preprocessed, continuing...<br>'
    #    #except IOError:
    #    #    print '</pre>Already preprocessed, continuing...<br>'
    #    except Exception,e:
    #        if printErrors:
    #            print '</pre>An error occured during preprocessing: ', getClassName(e) + ':', e, '<br>'
    #        raise
    #    #else:
    #    #    print '</pre>Finished preprocessing.<br>'
    #    return stdTrackName

    #@classmethod
    #def constructGalaxyTnFromSuitedFn(cls, fn, fileEnding=None,name=''):
    #    #to check that valid ID can later be constructed
    #    cls.extractIdFromGalaxyFn(fn)
    #    
    #    if fileEnding is None:
    #        fileEnding = fn.split('.')[-1]
    #    return ['galaxy', fileEnding, fn, name]