from collections import OrderedDict
from copy import copy

from gtrackcore.input.core.GenomeElement import GenomeElement
from gtrackcore.input.core.GenomeElementSource import BoundingRegionTuple, GenomeElementSource
from gtrackcore.metadata.GenomeInfo import GenomeInfo
from gtrackcore.metadata.TrackInfo import TrackInfo
from gtrackcore.preprocess.PreProcMetaDataCollector import PreProcMetaDataCollector
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track.core.Track import Track
from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track.pytables.TrackSource import TrackSource

class TrackGenomeElementSource(GenomeElementSource):
    FILE_FORMAT_NAME = 'Track'
    _VERSION = 1.0
    _hasOrigFile = False
    _addsStartElementToDenseIntervals = False

    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)

    def __init__(self, genome, trackName, boundingRegions, globalCoords=True, allowOverlaps=False, printWarnings=True, *args, **kwArgs):
        assert len(boundingRegions) > 0
    
        GenomeElementSource.__init__(self, '', genome=genome, trackName=trackName, printWarnings=printWarnings, *args, **kwArgs)
        self._boundingRegions = boundingRegions
        self._isSorted = all([x == y for x,y in zip(boundingRegions, sorted(boundingRegions))])
        self._boundingRegionTuples = None
        self._allowOverlaps = allowOverlaps
        self._globalCoords = globalCoords
        
        self._prefixList = None
        self._valDataType = 'float64'
        self._valDim = 1
        self._edgeWeightDataType = 'float64'
        self._edgeWeightDim = 1
        self._foundDataTypesAndDims = False
        
        self._fileType = None
        self._preProcVersion = None
        self._id = None
        self._undirectedEdges = None
        self._foundTrackInfoBasedMetaData = False
        
        self._fixedLength = None
        self._fixedGapSize = None
        self._reprIsDense = None
    
    def _calcFixedValues(self):
        if all(x is not None for x in [self._fixedLength, self._fixedGapSize]):
            return
        
        self._reprIsDense = False
        fixedLengths = set([])
        fixedGapSizes = set([])
        
        track = self._getTrack()
        for i, region, tv in ((i, region, self._getTrackView(track, region)) for i, region in enumerate(self._boundingRegions)):
            if tv.trackFormat.reprIsDense():
                self._reprIsDense = True
                break
            
            starts, ends = tv.startsAsNumpyArray(), tv.endsAsNumpyArray()
            lengths = ends - starts
            
            if len(lengths) == 0:
                continue
                
            if (lengths == lengths[0]).all():
                fixedLengths.add(lengths[0])
            else:
                fixedLengths.add(None)
                break
                
            gaps = starts[1:] - starts[:-1] - lengths[0]
            
            if starts[0] != 0:
                fixedGapSizes.add(None)
                continue
            
            if len(gaps) == 0:
                continue
                
            if (gaps == gaps[0]).all():
                fixedGapSizes.add(gaps[0])
            else:
                fixedGapSizes.add(None)
                    
        self._fixedLength = list(fixedLengths)[0] if len(fixedLengths) == 1 and not None in fixedLengths else 1
        self._fixedGapSize = list(fixedGapSizes)[0] if len(fixedGapSizes) == 1 and not None in fixedGapSizes else 0
        
    def getFixedLength(self):
        self._calcFixedValues()
        return self._fixedLength
        
    def getFixedGapSize(self):
        self._calcFixedValues()
        return self._fixedGapSize
    
    def isSorted(self):
        return self._isSorted
    
    def hasNoOverlappingElements(self):
        return False if self._allowOverlaps else True
    
    def _getTrack(self):
        track = Track(self._trackName)
        track.addFormatReq(TrackFormatReq(allowOverlaps=self._allowOverlaps))
        return track
        
    def _getTrackView(self, track, region):
        if region.genome is None:
            region.genome = self._genome
        return track.getTrackView(region)
        
    def _wrappedTrackElsGenerator(self):
        track = self._getTrack()
        for region,tv in ((region, self._getTrackView(track, region)) for region in self._boundingRegions):
            for te in tv:
                yield GenomeElement.createGeFromTrackEl(te, tv.trackFormat, globalCoords=self._globalCoords)
            
    def next(self):
        return self._generator.next()
        
    def __iter__(self):
        geIter = copy(self)
        geIter._generator = geIter._wrappedTrackElsGenerator()
        return geIter

    def getBoundingRegionTuples(self):
        if self._boundingRegionTuples is None:
            track = self._getTrack()
            self._boundingRegionTuples = []

            for region,tv in ((region, self._getTrackView(track, region)) for region in self._boundingRegions):
                self._boundingRegionTuples.append(BoundingRegionTuple(region, tv.getNumElements()))
            
            self._removeBoundingRegionTuplesIfFullChrsAndNotFixedGapSize()

        return self._boundingRegionTuples
        
    def _removeBoundingRegionTuplesIfFullChrsAndNotFixedGapSize(self):
        if self.getFixedGapSize() == 0 and not self._reprIsDense:
            # If only full chromosomes
            if all(brt.region.chr in GenomeInfo.getExtendedChrList(self._genome) and \
                    brt.region.start == 0 and \
                     brt.region.end == GenomeInfo.getChrLen(self._genome, brt.region.chr) \
                      for brt in self._boundingRegionTuples):
                self._boundingRegionTuples = []
        
    def parseFirstDataLine(self):
        pass
        
    def _getTrackData(self):
        for br in self._boundingRegions:
            chr = br.chr
            break
        
        return TrackSource().getTrackData(self._trackName, self._genome, chr, allowOverlaps=self._allowOverlaps)
    
    def _findPrefixList(self, trackData):
        unorderedPrefixList = [p for p in trackData if p not in ['leftIndex', 'rightIndex']]
        corePrefixes = ['start', 'end', 'val', 'strand', 'id', 'edges', 'weights']
        setFilePrefixList = set(unorderedPrefixList)
        setCore = set(corePrefixes)
        prefixList = [p for p in corePrefixes if p in setFilePrefixList] + \
            sorted([q for q in unorderedPrefixList if q not in setCore])
        return prefixList
        
    def _findDataTypeAndDim(self, numpyArray, edgeWeights):
        dataType = str(numpyArray.dtype).replace('|', '')
        shape = numpyArray.shape
        dim = shape[-1] if edgeWeights and len(shape) == 3 or \
                           not edgeWeights and len(shape) == 2 else 1
        return dataType, dim
        
    def _findDataTypesAndDims(self):
        if not self._foundDataTypesAndDims:
            trackData = self._getTrackData()
            self._prefixList = self._findPrefixList(trackData)
            if 'val' in trackData:
                self._valDataType, self._valDim = self._findDataTypeAndDim(trackData['val'], edgeWeights=False)
                if self._valDataType[0] == 'S' and self._valDataType != 'S1':
                    self._valDataType = 'S'
            if 'weights' in trackData:
                self._edgeWeightDataType, self._edgeWeightDim = self._findDataTypeAndDim(trackData['weights'], edgeWeights=True)
                if self._edgeWeightDataType[0] == 'S' and self._edgeWeightDataType != 'S1':
                    self._edgeWeightDataType = 'S'
            self._foundDataTypesAndDims = True
            
    def getPrefixList(self):
        self._findDataTypesAndDims()
        return self._prefixList
        
    def getValDataType(self):
        self._findDataTypesAndDims()
        return self._valDataType

    def getValDim(self):
        self._findDataTypesAndDims()
        return self._valDim
        
    def getEdgeWeightDataType(self):
        self._findDataTypesAndDims()
        return self._edgeWeightDataType

    def getEdgeWeightDim(self):
        self._findDataTypesAndDims()
        return self._edgeWeightDim
    
    def _findTrackInfoBasedMetaData(self):
        if not self._foundTrackInfoBasedMetaData:
            if PreProcMetaDataCollector.hasKey(self._genome, self._trackName):
                collector = PreProcMetaDataCollector(self._genome, self._trackName)
                self._fileSuffix = collector.getFileSuffix()
                self._preProcVersion = collector.getPreProcVersion()
                self._id = collector.getId()
                self._undirectedEdges = True if collector.hasUndirectedEdges() else False
            else:
                ti = TrackInfo(self._genome, self._trackName)
                self._fileSuffix = ti.fileType
                self._preProcVersion = ti.preProcVersion
                self._id = ti.id
                self._undirectedEdges = True if ti.undirectedEdges else False
    
    def getFileSuffix(self):
        self._findTrackInfoBasedMetaData()
        return self._fileSuffix
        
    def getVersion(self):
        self._findTrackInfoBasedMetaData()
        return self._preProcVersion
        
    def getId(self):
        self._findTrackInfoBasedMetaData()
        return self._id
        
    def hasUndirectedEdges(self):
        self._findTrackInfoBasedMetaData()
        return self._undirectedEdges

class FullTrackGenomeElementSource(TrackGenomeElementSource):
    def __init__(self, genome, trackName, allowOverlaps=False, *args, **kwArgs):
        from gtrackcore.track.pytables.BoundingRegionContainer import BoundingRegionContainer
        boundingRegions = list(BoundingRegionContainer(genome, trackName, allowOverlaps).get_all_bounding_regions())
        TrackGenomeElementSource.__init__(self, genome=genome, trackName=trackName, \
                                          boundingRegions=boundingRegions, globalCoords=True, \
                                          allowOverlaps=allowOverlaps, printWarnings=True)
        
class TrackViewListGenomeElementSource(TrackGenomeElementSource):
    def __init__(self, genome, trackViewList, trackName, *args, **kwArgs):
        assert len(trackViewList) > 0
        TrackGenomeElementSource.__init__(self, genome=genome, trackName=trackName, boundingRegions=[tv.genomeAnchor for tv in trackViewList], \
                                          globalCoords=True, printWarnings=True, *args, **kwArgs)
        self._trackViewDict = OrderedDict([(tv.genomeAnchor, tv) for tv in trackViewList])
        
    def _getTrackData(self):
        from gtrackcore.track.core.TrackView import noneFunc
        trackView = self._trackViewDict.values()[0]
        te = trackView._trackElement
        corePrefixes = ['start','end','val','strand','id','edges','weights']
        
        prefixList = []
        for prefix in corePrefixes + te.getAllExtraKeysInOrder():
            if getattr(te, prefix) != noneFunc:
                prefixList.append(prefix)
                
        return dict([(prefix, getattr(trackView, '_%sList' % prefix) if prefix in corePrefixes else \
                              trackView._extraLists[prefix]) for prefix in prefixList])
    
    def _getTrack(self):
        pass
        
    def _getTrackView(self, track, region):
        return self._trackViewDict[region]
        
    def getBoundingRegionTuples(self):
        if self._boundingRegionTuples is None:
            self._boundingRegionTuples = [BoundingRegionTuple(tv.genomeAnchor, tv.getNumElements()) for tv in self._trackViewDict.values()]
            self._removeBoundingRegionTuplesIfFullChrsAndNotFixedGapSize()
        return self._boundingRegionTuples
        
class TrackViewGenomeElementSource(TrackViewListGenomeElementSource):
    def __init__(self, genome, trackView, trackName, *args, **kwArgs):
        TrackViewListGenomeElementSource.__init__(self, genome, [trackView], trackName, *args, **kwArgs)
