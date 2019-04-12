from functools import partial

from gtrackcore.input.core.GenomeElementSource import BoundingRegionTuple
from gtrackcore.input.adapters.TrackGenomeElementSource import TrackGenomeElementSource
from gtrackcore.input.wrappers.GESourceWrapper import BrTuplesGESourceWrapper
from gtrackcore.input.wrappers.GEOverlapClusterer import GEOverlapClusterer
from gtrackcore.input.wrappers.GEBoundingRegionElementCounter import GEBoundingRegionElementCounter
from gtrackcore.input.wrappers.GEDependentAttributesHolder import GEDependentAttributesHolder
from gtrackcore.track.format.TrackFormat import TrackFormat
from gtrackcore.util.CommonFunctions import flatten
from gtrackcore.util.CommonConstants import RESERVED_PREFIXES
from gtrackcore.util.CommonClasses import OrderedDefaultDict

class GESourceManager(object):
    def __init__(self, geSource):
        self._geSource = self._decorateGESource(geSource)
        self._boundingRegionsAndGEsCorrespond = None

        self._areValsCategorical = TrackFormat.createInstanceFromGeSource(geSource).getValTypeName() == 'Category'
        self._areEdgeWeightsCategorical = TrackFormat.createInstanceFromGeSource(geSource).getWeightTypeName() == 'Category'
        self._valCategories = set()
        self._edgeWeightCategories = set()

        self._numElements = OrderedDefaultDict(int)
        self._maxStrLens = OrderedDefaultDict(partial(self._initMaxStrLens, self._getMaxStrLensKeys()))
        self._maxNumEdges = OrderedDefaultDict(int)

        self._hasCalculatedStats = False
#        self._calcStatisticsInExtraPass()

    def _decorateGESource(self, geSource):
        return GEDependentAttributesHolder(geSource)

    def _getMaxStrLensKeys(self):
        prefixSet = set(self._geSource.getPrefixList())

        return (['val'] if 'val' in prefixSet and self._geSource.getValDataType() == 'S' else []) + \
               (['id'] if 'id' in prefixSet else []) + \
               (['edges'] if 'edges' in prefixSet else []) + \
               (['weights'] if 'weights' in prefixSet and self._geSource.getEdgeWeightDataType() == 'S' else []) + \
               [x for x in prefixSet if x not in RESERVED_PREFIXES]

    @staticmethod
    def _initMaxStrLens(keys):
        return dict([(x,0) for x in keys])

    def _calcStatisticsInExtraPass(self):
        if not self._hasCalculatedStats:
            prevPrintWarnings = self._geSource.getPrintWarnings()
            self._geSource.setPrintWarnings(False)

            prefixList = self.getPrefixList()
            for el in self._geSource:
                if self._geSource.isSliceSource():
                    self._updateStatsFromSliceGenomeElement(el, prefixList)
                else:
                    self._updateStatsFromStdGenomeElement(el)

            self._geSource.setPrintWarnings(prevPrintWarnings)
            self._hasCalculatedStats = True

    def _updateStatsFromStdGenomeElement(self, el):
        chr = el.chr
        self._numElements[chr] += 1

        if el.isBlankElement:
            return

        if self._areValsCategorical:
            self._valCategories.add(el.val)

        if self._areEdgeWeightsCategorical:
            self._edgeWeightCategories |= set(el.weights)

        for prefix in self._maxStrLens[chr]:
            content = getattr(el, prefix, None)

            if content is not None:
                self._maxStrLens[chr][prefix] = \
                    max(self._maxStrLens[chr][prefix],
                        max(1, len(content)) if isinstance(content, basestring) else \
                            max([1] + [len(x) for x in flatten(content)]))

                if prefix == 'edges':
                    self._maxNumEdges[chr] = max(self._maxNumEdges[chr], len(el.edges))

    def _updateStatsFromNumpyArrays(self, chr, arrays):
        if self._areValsCategorical:
            from numpy import unique
            self._valCategories |= set(unique(arrays['val']))

        if self._areEdgeWeightsCategorical:
            from numpy import unique
            self._edgeWeightCategories |= set(unique(arrays['weights']))

        for prefix in self._maxStrLens[chr]:
            array = arrays[prefix]

            dtypeStr = str(array.dtype).replace('|', '')
            assert dtypeStr[0] == 'S', dtypeStr + ', ' + prefix
            strLen = int(dtypeStr[1:])
            self._maxStrLens[chr][prefix] = max(self._maxStrLens[chr][prefix], strLen)

            if prefix == 'edges':
                self._maxNumEdges[chr] = max(self._maxNumEdges[chr], array.shape[1])

    def _updateStatsFromSliceGenomeElement(self, el, prefixList):
        numpyArrays = {}

        self._numElements[el.chr] += len(getattr(el, prefixList[0]))
        for prefix in self._maxStrLens[el.chr]:
            numpyArrays[prefix] = getattr(el, prefix, None)

        self._updateStatsFromNumpyArrays(el.chr, numpyArrays)

    def getGESource(self):
        return self._geSource

    def getBoundingRegionTuples(self):
        boundingRegionTuples = [x for x in self._getBoundingRegionTuples() \
                                if x.region.chr is not None]

        if len(boundingRegionTuples) == 0:
            from gtrackcore.input.core.GenomeElementSource import BoundingRegionTuple
            from gtrackcore.track.core.GenomeRegion import GenomeRegion
            from gtrackcore.metadata.GenomeInfo import GenomeInfo

            geChrList = self.getAllChrs()
            boundingRegionTuples = [BoundingRegionTuple( \
                                     GenomeRegion(chr=chr, start=0, end=GenomeInfo.getChrLen(self._geSource.genome, chr)), \
                                     self.getNumElementsForChr(chr) ) \
                                    for chr in geChrList]
            self._boundingRegionsAndGEsCorrespond = False
        else:
            self._boundingRegionsAndGEsCorrespond = True

        return boundingRegionTuples

    def _getBoundingRegionTuples(self):
        return self._geSource.getBoundingRegionTuples()

    def boundingRegionsAndGEsCorrespond(self):
        assert self._boundingRegionsAndGEsCorrespond is not None
        return self._boundingRegionsAndGEsCorrespond

    def getPrefixList(self):
        return self._geSource.getPrefixList()

    def getValDataType(self):
        return self._geSource.getValDataType()

    def getValDim(self):
        return self._geSource.getValDim()

    def getEdgeWeightDataType(self):
        return self._geSource.getEdgeWeightDataType()

    def getEdgeWeightDim(self):
        return self._geSource.getEdgeWeightDim()

    def isSorted(self):
        return self._geSource.isSorted()

    def getAllChrs(self):
        self._calcStatisticsInExtraPass()
        return self._numElements.keys()

    def getNumElements(self):
        self._calcStatisticsInExtraPass()
        return sum(self._numElements.values())

    def getNumElementsForChr(self, chr):
        self._calcStatisticsInExtraPass()
        return self._numElements[chr]

    def getValCategories(self):
        self._calcStatisticsInExtraPass()
        return self._valCategories

    def getEdgeWeightCategories(self):
        self._calcStatisticsInExtraPass()
        return self._edgeWeightCategories

    def getMaxNumEdges(self):
        self._calcStatisticsInExtraPass()
        return max(self._maxNumEdges.values())

    def getMaxNumEdgesForChr(self, chr):
        self._calcStatisticsInExtraPass()
        return self._maxNumEdges[chr]

    def getMaxStrLens(self):
        self._calcStatisticsInExtraPass()
        return reduce(lambda x,y:dict((key, max(x[key], y[key])) for key in x.keys()), \
               self._maxStrLens.values())

    def getMaxStrLensForChr(self, chr):
        self._calcStatisticsInExtraPass()
        return self._maxStrLens[chr]

    def getMaxChrStrLen(self):
        self._calcStatisticsInExtraPass()
        return max(len(chr) for chr in self._maxStrLens.keys())


class OverlapClusteringGESourceManager(GESourceManager):
    def __init__(self, genome, trackName, origBrTuples):
        self._origBrTuples = origBrTuples
        trackGESource = TrackGenomeElementSource(genome, trackName, \
                                                 [br.region for br in self._origBrTuples],
                                                 allowOverlaps=True)

        GESourceManager.__init__(self, trackGESource)
        self._brTuplesForClusteredElements = None

    def _decorateGESource(self, geSource):
        return GEBoundingRegionElementCounter(GEOverlapClusterer(geSource), \
                                              self._origBrTuples)


class RegionBasedGESourceManager(GESourceManager):
    def __init__(self, geSource, brRegionList, calcStatsInExtraPass, countElsInBoundingRegions):
        assert len(brRegionList) > 0
        self._brRegionList = brRegionList
        self._calcStatsInExtraPass = calcStatsInExtraPass
        self._countElsInBoundingRegions = countElsInBoundingRegions
        GESourceManager.__init__(self, geSource)

    def _decorateGESource(self, geSource):
        brRegionList = geSource.getBoundingRegionTuples()
        
        if self._countElsInBoundingRegions:
            brTuples = [BoundingRegionTuple(region, 0) for region in brRegionList]
            return GEBoundingRegionElementCounter(geSource, brTuples)
        else:
            brTuples = [BoundingRegionTuple(region, len(region)) for region in self._brRegionList]
            return BrTuplesGESourceWrapper(geSource, brTuples)

    def _calcStatisticsInExtraPass(self):
        if not self._hasCalculatedStats:
            if self._calcStatsInExtraPass:
                GESourceManager._calcStatisticsInExtraPass(self)
            else:
                for br in self._brRegionList:
                    self._numElements[br.chr] += len(br)
                self._hasCalculatedStats = True


class TrackGESourceManager(GESourceManager):
    def __init__(self, geSource):
        assert isinstance(geSource, TrackGenomeElementSource)
        GESourceManager.__init__(self, geSource)

    def getBoundingRegionTuples(self):
        return self._geSource.getBoundingRegionTuples()

    def boundingRegionsAndGEsCorrespond(self):
        return True

    def _decorateGESource(self, geSource):
        return geSource
    
    def _calcStatisticsInExtraPass(self):
        if not self._hasCalculatedStats:
            track = self._geSource._getTrack()
            for brTuple in self._geSource.getBoundingRegionTuples():
                chr = brTuple.region.chr
                tv = self._geSource._getTrackView(track, brTuple.region)

                numpyArrays = {}
                for prefix in self._maxStrLens[chr]:
                    if prefix in ['val', 'id']:
                        array = getattr(tv, prefix + 'sAsNumpyArray')()
                    elif prefix in ['edges', 'weights']:
                        array = getattr(tv, prefix + 'AsNumpyArray')()
                    else:
                        array = tv.extrasAsNumpyArray(prefix)
                    numpyArrays[prefix] = array

                self._numElements[chr] += brTuple.elCount
                self._updateStatsFromNumpyArrays(chr, numpyArrays)

            self._hasCalculatedStats = True
