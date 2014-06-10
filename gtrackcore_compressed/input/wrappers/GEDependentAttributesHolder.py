from gtrackcore_compressed.input.wrappers.GESourceWrapper import GESourceWrapper, PausedAtCountsGESourceWrapper
from gtrackcore_compressed.util.CustomExceptions import InvalidFormatError, NotIteratedYetError

class GEDependentAttributesHolder(GESourceWrapper):    
    def __init__(self, geSource):
        GESourceWrapper.__init__(self, geSource)
        self._geIter = None
        if geSource.hasBoundingRegionTuples():
            self._boundingRegionTuples = geSource.getBoundingRegionTuples()
        else:
            self._boundingRegionTuples = None
        self._initOtherDependentAttrs()
    
    def __iter__(self):
        self._geIter = self._geSource.__iter__()
        return self
    
    def next(self):
        try:
            return self._geIter.next()
        except StopIteration:
            self._storeOtherDependentAttrs()

            if self._valDim is None:
                raise InvalidFormatError('Error: unable to determine value dimension.')
            if self._edgeWeightDim is None:
                raise InvalidFormatError('Error: unable to determine edge weight dimension.')

            self._boundingRegionTuples = self._geIter.getBoundingRegionTuples()
            raise

    def getBoundingRegionTuples(self):
        if self._boundingRegionTuples is None:
            raise NotIteratedYetError
        return self._boundingRegionTuples
    
    def _initOtherDependentAttrs(self):
        self._valDim = self._geSource.getValDim()
        self._edgeWeightDim = self._geSource.getEdgeWeightDim()
        self._anyWarnings = self._geSource.anyWarnings()
        self._lastWarning = self._geSource.getLastWarning()

    def _storeOtherDependentAttrs(self):
        #In order to determine dimensions when type=vector
        self._valDim = self._geIter.getValDim()
        self._edgeWeightDim = self._geIter.getEdgeWeightDim()
        self._anyWarnings = self._geIter.anyWarnings()
        self._lastWarning = self._geIter.getLastWarning()
    
    def getValDim(self):
        return self._valDim
    
    def getEdgeWeightDim(self):
        return self._edgeWeightDim

    def anyWarnings(self):
        return self._anyWarnings

    def getLastWarning(self):
        return self._lastWarning

def iterateOverBRTuplesWithContainedGEs(geSource, onlyYieldTwoGEs=False, returnIterator=False):
    if returnIterator:
        assert onlyYieldTwoGEs == False
    
    try:
        brTuples = geSource.getBoundingRegionTuples()
    except NotIteratedYetError:
        for ge in geSource:
            pass
        brTuples = geSource.getBoundingRegionTuples()
    
    curBrIndex = 0
    
    if returnIterator:
        if len(brTuples) == 0:
            yield None, geSource
        else:
            pausingIterator = PausedAtCountsGESourceWrapper(geSource, [br.elCount for br in brTuples])
            for br in brTuples:
                yield br, pausingIterator
    else:
        geList = []

        for i, ge in enumerate(geSource):
            if len(brTuples) > curBrIndex + 1 \
                and len(geList) == brTuples[curBrIndex].elCount:
                    yield brTuples[curBrIndex], geList
                    curBrIndex += 1
                    geList = []
            
            geList.append(ge.getCopy())
            
            if onlyYieldTwoGEs and i==1:
                break

        yield (brTuples[curBrIndex] if len(brTuples) > 0 else None), geList