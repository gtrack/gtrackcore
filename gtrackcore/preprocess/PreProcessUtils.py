import os
import shutil
import sys
import numpy

from gtrackcore.core.Config import Config
from gtrackcore.metadata.GenomeInfo import GenomeInfo
from gtrackcore.metadata.TrackInfo import TrackInfo
from gtrackcore.preprocess.PreProcMetaDataCollector import PreProcMetaDataCollector
from gtrackcore.input.core.GenomeElement import GenomeElement
from gtrackcore.track.format.TrackFormat import TrackFormat
from gtrackcore.track.memmap.BoundingRegionShelve import BoundingRegionShelve
from gtrackcore.track.pytables.BoundingRegionHandler import BoundingRegionHandler
from gtrackcore.track.memmap.CommonMemmapFunctions import findEmptyVal
from gtrackcore.track.pytables.TrackSource import TrackSource
from gtrackcore.util.CommonConstants import RESERVED_PREFIXES
from gtrackcore.util.CommonFunctions import getDirPath
from gtrackcore.util.CustomExceptions import InvalidFormatError, ShouldNotOccurError
from gtrackcore.util.CommonFunctions import getDirPath, getDatabaseFilename
from gtrackcore.track.pytables.DatabaseHandler import DatabaseSortHandler

class PreProcessUtils(object):
    @staticmethod
    def shouldPreProcessGESource(trackName, geSource, allowOverlaps):
        genome = geSource.getGenome()
        storedInfo = TrackInfo(genome, trackName)
        
        validFilesExist = PreProcessUtils.preProcFilesExist(genome, trackName, allowOverlaps) and \
            storedInfo.isValid()
        
        if not geSource.hasOrigFile():
            return False if validFilesExist or geSource.isExternal() else True
        
        storedAsAccordingToGeSource = \
            (PreProcessUtils.constructId(geSource) == storedInfo.id and \
             geSource.getVersion() == storedInfo.preProcVersion)
        
        #from gtrackcore.application.LogSetup import logMessage
        #logMessage(geSource.getGenome())
        #logMessage(':'.join(trackName))
        #logMessage('%s %s %s %s %s' % (PreProcessUtils.preProcFilesExist(genome, trackName, allowOverlaps), \
        #                               storedInfo.isValid(), \
        #                               geSource.hasOrigFile(), \
        #                               PreProcessUtils.constructId(geSource) == storedInfo.id, \
        #                               geSource.getVersion() == storedInfo.preProcVersion))
        
        return not (validFilesExist and storedAsAccordingToGeSource)
    
    @staticmethod
    def preProcFilesExist(genome, trackName, allowOverlaps):
        collector = PreProcMetaDataCollector(genome, trackName)
        preProcFilesExist = collector.preProcFilesExist(allowOverlaps)
        if preProcFilesExist is None:
            dirPath = getDirPath(trackName, genome, allowOverlaps=allowOverlaps)
            if BoundingRegionShelve(genome, trackName, allowOverlaps).fileExists():
                preProcFilesExist = True
                #    any( fn.split('.')[0] in ['start', 'end', 'val', 'edges'] \
                #         for fn in os.listdir(dirPath) if os.path.isfile(os.path.join(dirPath, fn)) )
            else:
                if os.path.exists(dirPath):
                    preProcFilesExist = PreProcessUtils._hasOldTypeChromSubDirs(dirPath, genome)
                else:
                    preProcFilesExist = False
            collector.updatePreProcFilesExistFlag(allowOverlaps, preProcFilesExist)
        return preProcFilesExist
    
    @staticmethod
    def _hasOldTypeChromSubDirs(dirPath, genome):
        for subDir in os.listdir(dirPath):
            fullSubDirPath = os.path.join(dirPath, subDir)
            if os.path.isdir(fullSubDirPath) and \
                PreProcessUtils._isOldTypeChromDirectory(fullSubDirPath, genome):
                    return True
        return False
    
    @staticmethod
    def _isOldTypeChromDirectory(dirPath, genome):
        if dirPath[-1] == os.sep:
            dirPath = os.path.dirname(dirPath)
        dirName = os.path.basename(dirPath)
        return dirName in set(GenomeInfo.getExtendedChrList(genome)) and \
            not any(os.path.isdir(os.path.join(dirPath, subFn)) for subFn in os.listdir(dirPath))
    
    @staticmethod
    def constructId(geSource):
        from gtrackcore.preprocess.PreProcessTracksJob import PreProcessTracksJob
        if geSource.hasOrigFile():
            origPath = os.path.dirname(geSource.getFileName()) if not geSource.isExternal() else geSource.getFileName()
            return TrackInfo.constructIdFromPath(geSource.getGenome(), origPath, \
                                                 geSource.getVersion(), PreProcessTracksJob.VERSION)
        else:
            return geSource.getId()
        
    @staticmethod
    def removeOutdatedPreProcessedFiles(genome, trackName, allowOverlaps, mode):
        collector = PreProcMetaDataCollector(genome, trackName)
        if PreProcessUtils.preProcFilesExist(genome, trackName, allowOverlaps) and not \
            collector.hasRemovedPreProcFiles(allowOverlaps):
                dirPath = getDirPath(trackName, genome, allowOverlaps=allowOverlaps)
                
                assert dirPath.startswith(Config.PROCESSED_DATA_PATH), \
                    "Processed data path '%s' does not start with '%s'" % \
                    (dirPath, Config.PROCESSED_DATA_PATH)
                if mode == 'Real':
                    print 'Removing outdated preprocessed data: ', dirPath
                    for fn in os.listdir(dirPath):
                        fullFn = os.path.join(dirPath, fn)
                        if os.path.isfile(fullFn):
                            os.unlink(fullFn)
                        if os.path.isdir(fullFn):
                            if PreProcessUtils._isOldTypeChromDirectory(fullFn, genome):
                                shutil.rmtree(fullFn)
                else:
                    print 'Would now have removed outdated preprocessed data if real run: ', dirPath
                
                collector.updateRemovedPreProcFilesFlag(allowOverlaps, True)
        
        if mode == 'Real':
            ti = TrackInfo(genome, trackName)
            ti.resetTimeOfPreProcessing()

    @staticmethod
    def sort_preprocessed_table(genome, track_name, allow_overlaps):
        dir_path = getDirPath(track_name, genome, allowOverlaps=allow_overlaps)
        assert os.path.exists(dir_path)  # throw error

        db_handler = DatabaseSortHandler(track_name, genome, allow_overlaps)
        db_handler.open()
        column_dict = db_handler.get_columns()

        seqid_column = column_dict['seqid'][:]

        if 'start' in column_dict and 'end' in column_dict:
            start_column = column_dict['start'][:]
            end_column = column_dict['end'][:]
            sort_order = numpy.lexsort((end_column, start_column, seqid_column))
            column_dict['start'][:] = start_column[sort_order]
            column_dict['end'][:] = end_column[sort_order]
        elif 'start' in column_dict:
            start_column = column_dict['start'][:]
            sort_order = numpy.lexsort((start_column, seqid_column))
            column_dict['start'][:] = start_column[sort_order]
        elif 'end' in column_dict:
            end_column = column_dict['end'][:]
            sort_order = numpy.lexsort((end_column, seqid_column))
            column_dict['end'][:] = end_column[sort_order]
        else:
            sort_order = numpy.lexsort(seqid_column)

        column_dict['seqid'][:] = seqid_column[sort_order]

        for column_name, column_val in column_dict.iteritems():
            if column_name not in ['seqid', 'start', 'end']:
                column_val[:] = column_val[:][sort_order]

        db_handler.close()

    @staticmethod
    def create_bounding_region_table(genome, track_name, allow_overlaps):
        collector = PreProcMetaDataCollector(genome, track_name)
        bounding_region_tuples = collector.getBoundingRegionTuples(allow_overlaps)
        if not collector.getTrackFormat().reprIsDense():
            bounding_region_tuples = sorted(bounding_region_tuples)
        ge_chr_list = collector.getPreProcessedChrs(allow_overlaps)

        br_handler = BoundingRegionHandler(genome, track_name, allow_overlaps)
        br_handler.store_bounding_regions(bounding_region_tuples, ge_chr_list, not collector.getTrackFormat().reprIsDense())

        #Sanity check
        if br_handler.getTotalElementCount() != collector.getNumElements(allow_overlaps):
            raise ShouldNotOccurError("Error: The total element count for all bounding regions is not equal to the total number of genome elements. %s != %s" % \
                                      (br_handler.getTotalElementCount(), collector.getNumElements(allow_overlaps)) )

    @staticmethod
    def createBoundingRegionShelve(genome, trackName, allowOverlaps):
        collector = PreProcMetaDataCollector(genome, trackName)
        boundingRegionTuples = collector.getBoundingRegionTuples(allowOverlaps)
        if not collector.getTrackFormat().reprIsDense():
            boundingRegionTuples = sorted(boundingRegionTuples)
        
        geChrList = collector.getPreProcessedChrs(allowOverlaps)
        brShelve = BoundingRegionShelve(genome, trackName, allowOverlaps)
        brShelve.storeBoundingRegions(boundingRegionTuples, geChrList, not collector.getTrackFormat().reprIsDense())
        
        #Sanity check
        if brShelve.getTotalElementCount() != collector.getNumElements(allowOverlaps):
            raise ShouldNotOccurError("Error: The total element count for all bounding regions is not equal to the total number of genome elements. %s != %s" % \
                                      (brShelve.getTotalElementCount(), collector.getNumElements(allowOverlaps)) )
    
    @staticmethod
    def removeChrMemmapFolders(genome, trackName, allowOverlaps):
        chrList = PreProcMetaDataCollector(genome, trackName).getPreProcessedChrs(allowOverlaps)
        for chr in chrList:
            path = getDirPath(trackName, genome, chr, allowOverlaps)
            assert os.path.exists(path), 'Path does not exist: ' + path
            assert os.path.isdir(path), 'Path is not a directory: ' + path
            shutil.rmtree(path)

    @staticmethod
    def checkIfEdgeIdsExist(genome, trackName, allowOverlaps):
        collector = PreProcMetaDataCollector(genome, trackName)
        if not collector.getTrackFormat().isLinked():
            return
        
        uniqueIds = numpy.array([], dtype='S')
        uniqueEdgeIds = numpy.array([], dtype='S')
        
        for chr in collector.getPreProcessedChrs(allowOverlaps):
            trackSource = TrackSource()
            trackData = trackSource.getTrackData(trackName, genome, chr, allowOverlaps)
            uniqueIds = numpy.unique(numpy.concatenate((uniqueIds, trackData['id'][:])))
            uniqueEdgeIds = numpy.unique(numpy.concatenate((uniqueEdgeIds, trackData['edges'][:].flatten())))
        
        uniqueIds = uniqueIds[uniqueIds != '']
        uniqueEdgeIds = uniqueEdgeIds[uniqueEdgeIds != '']
        
        unmatchedIds = set(uniqueEdgeIds) - set(uniqueIds)
        if len(unmatchedIds) > 0:
            raise InvalidFormatError("Error: the following ids specified in the 'edges' column do not exist in the dataset: " + ', '.join(sorted(unmatchedIds)))
    
    @staticmethod
    def checkUndirectedEdges(genome, trackName, allowOverlaps):
        collector = PreProcMetaDataCollector(genome, trackName)
        if not (collector.getTrackFormat().isLinked() and collector.hasUndirectedEdges()):
            return
        
        complementEdgeWeightDict = {}
        
        for chr in collector.getPreProcessedChrs(allowOverlaps):
            trackSource = TrackSource()
            trackData = trackSource.getTrackData(trackName, genome, chr, allowOverlaps)
            
            ids = trackData['id']
            edges = trackData['edges']
            weights = trackData.get('weights')
            
            for i, id in enumerate(ids):
                edgesAttr = edges[i][edges[i] != '']
                weightsAttr = weights[i][edges[i] != ''] if weights is not None else None
                PreProcessUtils._adjustComplementaryEdgeWeightDict(complementEdgeWeightDict, id, edgesAttr, weightsAttr)
        
        if len(complementEdgeWeightDict) != 0:
                unmatchedPairs = []
                for toId in complementEdgeWeightDict:
                    for fromId in complementEdgeWeightDict[toId]:
                        unmatchedPairs.append((fromId, toId, complementEdgeWeightDict[toId][fromId]))
                raise InvalidFormatError("Error: All edges are not undirected. The following edges specifications " +\
                                         "are not matched by an opposite edge with equal weight:" + os.linesep +\
                                         os.linesep.join(["from '%s' to '%s'" % (fromId, toId) + \
                                                          (" with weight '%s'" % weight  if weight != '' else '') \
                                                          for fromId, toId, weight in unmatchedPairs]))
        
    @staticmethod
    def _adjustComplementaryEdgeWeightDict(complementEdgeWeightDict, id, edges, weights):
        for index, edgeId in enumerate(edges):
            weight = weights[index] if weights is not None else ''
                
            if id in complementEdgeWeightDict and edgeId in complementEdgeWeightDict[id]:
                complWeight = complementEdgeWeightDict[id][edgeId]
                try:
                    equal = numpy.all(complWeight == weight | numpy.isnan(complWeight) & numpy.isnan(weight))
                except TypeError:
                    try:
                        equal = (complWeight == weight) or (numpy.isnan(complWeight) and numpy.isnan(weight))
                    except (TypeError, ValueError):
                        equal = numpy.all(complWeight == weight)
                if not equal:
                    raise InvalidFormatError("Error: edge ('%s' <-> '%s') is not undirected. The weight must be equal in both directions (%s != %s)" % (edgeId, id, complementEdgeWeightDict[id][edgeId], weights[index]))
                
                del complementEdgeWeightDict[id][edgeId]
                if len(complementEdgeWeightDict[id]) == 0:
                    del complementEdgeWeightDict[id]
                        
            elif id == edgeId:
                continue
                
            elif edgeId in complementEdgeWeightDict:
                if id in complementEdgeWeightDict[edgeId]:
                    raise ShouldNotOccurError('Error: the complementary edge(%s) has already been added to complementEdgeWeightDict["%s"] ... ' % (id, edgeId))
                complementEdgeWeightDict[edgeId][id] = weight
            else:
                complementEdgeWeightDict[edgeId] = {id: weight}
    