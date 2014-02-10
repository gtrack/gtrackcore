import copy
import datetime
from collections import defaultdict, OrderedDict

from gtrackcore.track.format.TrackFormat import TrackFormat
from gtrackcore.metadata.TrackInfo import constructKey, TrackInfo

class PreProcMetaDataCollector(object):
    _preProcMetaDataStorage = {}

    def __new__(cls, genome, trackName):
        key = constructKey(genome, trackName)
        
        if key in cls._preProcMetaDataStorage:
            return cls._preProcMetaDataStorage[key]
        else:
            obj = object.__new__(cls)
            cls._preProcMetaDataStorage[key] = obj
            return obj
        
    def __init__(self, genome, trackName):
        existingAttrs = copy.copy(self.__dict__)
        
        self._genome = genome
        self._trackName = trackName
        
        self._preProcChrs = defaultdict(OrderedDict)
        self._preProcDirty = False
        self._preProcFilesExist = {}
        self._removedPreProcFiles = {}
        self._overlapRulesFinalized = set()
        
        self._fileSuffix = ''
        self._prefixList = None
        self._valDataType = None
        self._valDim = None
        self._weightDataType = None
        self._weightDim = None
        self._undirectedEdges = None
        self._preProcVersion = ''
        self._id = None
        
        self._numElements = defaultdict(int)
        self._boundingRegionTuples = defaultdict(list)
        self._valCategories = defaultdict(set)
        self._edgeWeightCategories = defaultdict(set)
        
        self.__dict__.update(existingAttrs)
                    
    def _checkAndUpdateAttribute(self, attr, value, mayBeEmptyString=False, isGeSourceAttr=False, extraErrorMsg=''):
        emptyList = [None, ''] if mayBeEmptyString else [None]
        valAllowedList = emptyList + [value]
        assert getattr(self, attr) in valAllowedList, \
            (('Files in the same folder use geSources with different %ss [%s != %s]' % (attr, getattr(self, attr), value)) if isGeSourceAttr else \
             ('Files in the same folder have different %ss [%s != %s]' % (attr, getattr(self, attr), value))) \
            + (' (%s)' % extraErrorMsg if extraErrorMsg else '')
        
        if value not in emptyList:
            setattr(self, attr, value)
        
    @classmethod
    def hasKey(cls, genome, trackName):
        return constructKey(genome, trackName) in cls._preProcMetaDataStorage
        
    def updateMetaDataForFinalization(self, fileSuffix, prefixList, valDataType, valDim, weightDataType, weightDim, undirectedEdges, \
                                      preProcVersion, id, numElements, boundingRegionTuples, valCategories, edgeWeightCategories, allowOverlaps):
        
        self._checkAndUpdateAttribute('_fileSuffix', fileSuffix, mayBeEmptyString=True, isGeSourceAttr=False)
        #TODO: Find out where to remove (or add) seqid from the _prefixList
        self._checkAndUpdateAttribute('_prefixList', set(prefixList) - set(['seqid']), mayBeEmptyString=False, isGeSourceAttr=False, extraErrorMsg='Different formats?')
        self._checkAndUpdateAttribute('_preProcVersion', preProcVersion, mayBeEmptyString=True, isGeSourceAttr=True, extraErrorMsg='strange..')
        self._checkAndUpdateAttribute('_id', id, mayBeEmptyString=True, isGeSourceAttr=True, extraErrorMsg='Have the original files been modified during the run?')

        if 'val' in prefixList:
            self._checkAndUpdateAttribute('_valDim', valDim, mayBeEmptyString=False, isGeSourceAttr=False, extraErrorMsg='Different formats?')
            self._checkAndUpdateAttribute('_valDataType', valDataType, mayBeEmptyString=False, isGeSourceAttr=False, extraErrorMsg='Different formats?')
        
        if 'edges' in prefixList:
            self._checkAndUpdateAttribute('_undirectedEdges', undirectedEdges, mayBeEmptyString=False, isGeSourceAttr=False, extraErrorMsg='Different formats?')   
        
        if 'weights' in prefixList:
            self._checkAndUpdateAttribute('_weightDataType', weightDataType, mayBeEmptyString=False, isGeSourceAttr=False, extraErrorMsg='Different formats?')
            self._checkAndUpdateAttribute('_weightDim', weightDim, mayBeEmptyString=False, isGeSourceAttr=False, extraErrorMsg='Different formats?')
        
        self._numElements[allowOverlaps] += numElements
        self._boundingRegionTuples[allowOverlaps] += boundingRegionTuples
        self._valCategories[allowOverlaps] |= valCategories
        self._edgeWeightCategories[allowOverlaps] |= edgeWeightCategories
        
    def flagChrsAsPreProcessed(self, allowOverlaps, chrList):
        for chr in chrList:
            self._preProcChrs[allowOverlaps][chr] = None
    
    def updatePreProcDirtyStatus(self, dirty):
        if dirty:
            self._preProcDirty = True
                    
    def updatePreProcFilesExistFlag(self, allowOverlaps, val):
        self._preProcFilesExist[allowOverlaps] = val

    def updateRemovedPreProcFilesFlag(self, allowOverlaps, val):
        self._removedPreProcFiles[allowOverlaps] = val
        
    def markOverlapRuleAsFinalized(self, allowOverlaps):
        self._overlapRulesFinalized.add(allowOverlaps)
    
    def getPreProcessedChrs(self, allowOverlaps):
        return self._preProcChrs[allowOverlaps].keys()
    
    def getBoundingRegionTuples(self, allowOverlaps):
        return self._boundingRegionTuples[allowOverlaps]
        
    def getNumElements(self, allowOverlaps):
        return self._numElements[allowOverlaps]
    
    def preProcIsDirty(self):
        return self._preProcDirty
        
    def preProcFilesExist(self, allowOverlaps):
        return self._preProcFilesExist.get(allowOverlaps)
        
    def hasRemovedPreProcFiles(self, allowOverlaps):
        return self._removedPreProcFiles.get(allowOverlaps)
        
    def overlapRuleHasBeenFinalized(self, allowOverlaps):
        return allowOverlaps in self._overlapRulesFinalized
        
    def getTrackFormat(self):
        return TrackFormat.createInstanceFromPrefixList(self._prefixList, \
                                                        self._valDataType, \
                                                        self._valDim, \
                                                        self._weightDataType, \
                                                        self._weightDim)
        
    def getPrefixList(self):
        return self._prefixList
    
    def getValDataType(self):
        return self._valDataType
    
    def getValDim(self):
        return self._valDim
        
    def getEgdeWeightDataType(self):
        return self._weightDataType
    
    def getEgdeWeightDim(self):
        return self._weightDim
        
    def getFileSuffix(self):
        return self._fileSuffix
        
    def hasUndirectedEdges(self):
        return self._undirectedEdges
        
    def getPreProcVersion(self):
        return self._preProcVersion
        
    def getId(self):
        return self._id
                
    def finalize(self, username, printMsg):
        ti = TrackInfo(self._genome, self._trackName)
        
        ti.fileType = self._fileSuffix
        trackFormat = self.getTrackFormat()
        ti.trackFormatName = trackFormat.getFormatName()
        ti.markType = trackFormat.getValTypeName()
        ti.weightType = trackFormat.getWeightTypeName()
        ti.undirectedEdges = self._undirectedEdges
        ti.preProcVersion = self._preProcVersion

        ti.origElCount = self._numElements[True]
        ti.clusteredElCount = self._numElements[False]
        
        if trackFormat.isDense() and trackFormat.isInterval():
            ti.origElCount -= len(self._boundingRegionTuples[True])
            ti.clusteredElCount -= len(self._boundingRegionTuples[False])

        if True in self._valCategories:
            ti.numValCategories = len(self._valCategories[True])
        
        if False in self._valCategories:
            ti.numClusteredValCategories = len(self._valCategories[False])

        if True in self._edgeWeightCategories:
            ti.numEdgeWeightCategories = len(self._edgeWeightCategories[True])
        
        ti.id = self._id
        ti.timeOfPreProcessing = datetime.datetime.now()
    
        ti.lastUpdatedBy = username
        if ti.hbContact == '':
            ti.hbContact = username
        
        ti.store()
        
        if printMsg:
            print "Finished preprocessing track '%s'." % ':'.join(self._trackName)
            print
        
        self.removeEntry()

    def removeEntry(self):
        del self._preProcMetaDataStorage[constructKey(self._genome, self._trackName)]
