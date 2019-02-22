from gtrackcore.input.core.GenomeElementSource import GenomeElementSource


class BigWigGenomeElementSource(GenomeElementSource):
    _VERSION = '1.0'
    FILE_SUFFIXES = ['bw', 'bigwig']
    FILE_FORMAT_NAME = 'BigWig'

    _numHeaderLines = 0
    _isSliceSource = True
    _isSorted = True
    _inputIsOneIndexed = True
    _inputIsEndInclusive = True

    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)

    def __init__(self, *args, **kwArgs):
        GenomeElementSource.__init__(self, *args, **kwArgs)

    def _iter(self):
        return self

    def next(self):
        raise StopIteration()

    def _handleEndOfFile(self):
        pass

    def _getFile(self):
        return open(self._fn, 'r')

    def getBoundingRegionTuples(self):
        return []

    # The following are currently not tested, but should still be implemented correctly. Can be
    # manually tested by wrapping this geSource in a GTrackComposer object and look at whether
    # these headers are set correctly.

    def getFixedLength(self):
        return False

    def getFixedGapSize(self):
        return False

    def hasNoOverlappingElements(self):
        return False


class BigWigGenomeElementSourceForPreproc(BigWigGenomeElementSource):
    _addsStartElementToDenseIntervals = False
