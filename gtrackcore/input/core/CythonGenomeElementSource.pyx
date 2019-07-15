# cython: infer_types=True
# cython: profile=True

from input.core.CythonGenomeElementSourceCore import CythonGenomeElementSourceCore

class CythonGenomeElementSource(CythonGenomeElementSourceCore):
    _VERSION = '0.0'
    FILE_SUFFIXES = []
    FILE_FORMAT_NAME = ''

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



    def __init__(self, fn, *args, **kwArgs):
        CythonGenomeElementSourceCore.__init__(self, fn, *args, **kwArgs)

    def hasOrigFile(self):
        return self._hasOrigFile

    def isSliceSource(self):
        return self._isSliceSource

    def addsStartElementToDenseIntervals(self):
        return self._addsStartElementToDenseIntervals

    def hasCircularElements(self):
        return self._hasCircularElements

    def getFixedLength(self):
        return self._fixedLength

    def getFixedGapSize(self):
        return self._fixedGapSize

    def isSorted(self):
        return self._isSorted

    def hasNoOverlappingElements(self):
        return self._hasNoOverlappingElements

    def hasUndirectedEdges(self):
        return self._hasUndirectedEdges

    def inputIsOneIndexed(self):
        return self._inputIsOneIndexed

    def inputIsEndInclusive(self):
        return self._inputIsEndInclusive

    def isExternal(self):
        return self._external

    def getFileFormatName(self):
        return self.FILE_FORMAT_NAME

    def getDefaultFileSuffix(self):
        return self.FILE_SUFFIXES[0]

    def getVersion(self):
        return self._VERSION