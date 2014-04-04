from copy import copy

from gtrackcore.input.core.GenomeElement import GenomeElement
from gtrackcore.util.CustomExceptions import InvalidFormatError, NotSupportedError


class BoundingRegionTuple:
    def __init__(self, region, element_count):
        self.region = region
        self.element_count = element_count

    def getCopy(self):
        return BoundingRegionTuple(copy(self.region), self.element_count)

    def __str__(self):
        return 'BoundingRegionTuple(region = %s, elCount = %s)' % (self.region, self.element_count)

    def __cmp__(self, other):
        return cmp(self.region, other.region)


class ToolGenomeElementSource(object):
    _VERSION = '0.0'
    TOOL_NAME = ''

    _hasOrigFile = True
    _isSliceSource = False
    _addsStartElementToDenseIntervals = True
    _isSorted = False
    _hasCircularElements = False
    _fixedLength = 1
    _fixedGapSize = 0
    _hasNoOverlappingElements = False
    _hasUndirectedEdges = False
    _inputIsOneIndexed = False
    _inputIsEndInclusive = False

    def __new__(cls, tool_name, tool_input, genome=None, track_name=None, *args, **kwArgs):
        ge_source_cls = get_genome_element_source_class(tool_name)
        return ge_source_cls.__new__(ge_source_cls, tool_name, tool_input, genome=genome, track_name=track_name, *args, **kwArgs)

    def __init__(self, tool_name, tool_input, genome=None, track_name=None, *args, **kwArgs):
        self._tool_name = tool_name
        self._tool_input = tool_input
        self._genome = genome
        self._genomeElement = GenomeElement(genome)
        self._trackName = track_name
        self._prefixList = None
        self._printWarnings = False
        self._lastWarning = None

    def getFileFormatName(self):
        raise NotImplementedError

    def getDefaultFileSuffix(self):
        raise NotImplementedError

    def getTrackName(self):
        return self._trackName

    def getGenome(self):
        return self._genome

    def getFileName(self):
        raise NotImplementedError

    def getFileSuffix(self):
        return None

    def isExternal(self):
        return False

    def hasOrigFile(self):
        return False

    def isSliceSource(self):
        return False

    def addsStartElementToDenseIntervals(self):
        return False

    def hasCircularElements(self):
        return False

    def getFixedLength(self):
        raise NotImplementedError

    def getFixedGapSize(self):
        raise NotImplementedError

    def isSorted(self):
        return True

    def hasNoOverlappingElements(self):
        return True

    def hasUndirectedEdges(self):
        return False

    def inputIsOneIndexed(self):
        return False

    def inputIsEndInclusive(self):
        return False

    def anyWarnings(self):
        return self._lastWarning is not None

    def getLastWarning(self):
        return self._lastWarning

    def _checkBoundingRegionOverlap(self):
        if self.hasBoundingRegionTuples():
            for i,brTuple in enumerate(sorted(self.getBoundingRegionTuples())):
                br = brTuple.region

                if i > 0:
                    self._checkBoundingRegionSortedPair(lastBoundingRegion, br)
                lastBoundingRegion = br

    def _checkBoundingRegionSortedPair(self, lastBoundingRegion, br):
        if br.start is not None and br.end is not None:
            if lastBoundingRegion.overlaps(br):
                raise InvalidFormatError("Error: bounding regions '%s' and '%s' overlap." % (lastBoundingRegion, br))

    def hasBoundingRegionTuples(self):
        return len(self.getBoundingRegionTuples()) > 0

    def getBoundingRegionTuples(self):
        return []

    def getPrefixList(self):
        return []

    def getPrintWarnings(self):
        return self._printWarnings

    def setPrintWarnings(self, printWarnings):
        self._printWarnings = printWarnings

    def getValDataType(self):
        return 'float64'

    def getValDim(self):
        return 1

    def getEdgeWeightDataType(self):
        return 'float64'

    def getEdgeWeightDim(self):
        return 1

    def getVersion(self):
        return self._VERSION

    def getId(self):
        return None

    genome = property(getGenome)


def get_genome_element_source_class(tool_name):
    for ge_source_cls in get_all_genome_element_source_classes():
        if tool_name == ge_source_cls.TOOL_NAME:
            return ge_source_cls
    raise NotSupportedError('Tool type ' + tool_name + ' not supported.')


def get_all_genome_element_source_classes():
    from gtrackcore.input.tools.OverlapToolGenomeElementSource import OverlapToolGenomeElementSource
    from gtrackcore.input.tools.MeanToolGenomeElementSource import MeanToolGenomeElementSource
    from gtrackcore.input.tools.UnionToolGenomeElementSource import UnionToolGenomeElementSource

    return [OverlapToolGenomeElementSource, MeanToolGenomeElementSource, UnionToolGenomeElementSource]
