import numpy

from copy import copy
from bisect import insort

from track5.core.Config import Config
from track5.input.wrappers.GESourceWrapper import GESourceWrapper
from track5.util.CommonConstants import BINARY_MISSING_VAL
from track5.util.CustomExceptions import ShouldNotOccurError
from track5.util.CommonFunctions import isIter
from track5.track.format.TrackFormat import TrackFormat

class GEOverlapClusterer(object):
    def __new__(cls, sortedGeSource):
        hasStart, hasEnd = [attrs in sortedGeSource.getPrefixList() for attrs in ['start', 'end']]
        
        if not hasStart and not hasEnd:
            return GEOverlapClusterer_Function(sortedGeSource)
        elif hasStart and hasEnd:
            return GEOverlapClusterer_Segment(sortedGeSource)
        elif hasStart and not hasEnd:
            return GEOverlapClusterer_Point(sortedGeSource)
        elif not hasStart and hasEnd:
            return GEOverlapClusterer_Partition(sortedGeSource)
        else:
            raise ShouldNotOccurError()

class GEOverlapClustererBase(GESourceWrapper):    
    def __init__(self, sortedGeSource):
        GESourceWrapper.__init__(self, sortedGeSource)
        self._geIter = None
        
    def __iter__(self):
        self = copy(self)
        self._curValsDict = {}
        self._geIter = self._geSource.__iter__()
        
        try:
            self._prevEl = None
            self._prevEl = self._geIter.next()
        except StopIteration:
            pass
        return self
    
    def next(self):
        try:
            while True:
                el = self._geIter.next()
                
                if el.genome == self._prevEl.genome and \
                   el.chr == self._prevEl.chr and \
                   self._overlapsPrev(el):
                        self._extendPrev(el)
                        self._updateContentsOfPrev(el)
                else:
                    self._curValsDict = {}
                    self._prevEl, el = el, self._prevEl
                    el = self._removeEdges(el)
                    return el
        
        except StopIteration:
            if self._prevEl != None:
                self._curValsDict = {}
                self._prevEl, el = None, self._prevEl
                el = self._removeEdges(el)
                return el
                
            raise StopIteration
    
    def _removeEdges(self, el):
        #el = deepcopy(el)
        el = el.getCopy()
        el.edges = []
        el.weights = []
        return el
        
    def _updateContentsOfPrev(self, el):
        for prefix in ['val', 'strand', 'id'] + self._prevEl.orderedExtraKeys:
            newVal = self._getNewContentsOfPrev(getattr(self._prevEl, prefix), getattr(el, prefix), prefix)
            if newVal is not None:
                setattr(self._prevEl, prefix, newVal)
            
    def _getNewContentsOfPrev(self, x, y, prefix):
        if x is not None and y is not None:
            if isinstance(x, numpy.ndarray):
                x = x.tolist()
            if isinstance(y, numpy.ndarray):
                y = y.tolist()
            
            if isIter(x):
                if x != y:
                    if len(x) != len(y):
                        return []
                    else:
                        return [self._getMissingValue(prefix) for i,item in enumerate(x)]
            else:
                valDataType = self._geSource.getValDataType()
                if prefix == 'val' and valDataType[0] == 'S' and valDataType != 'S1':
                    return self._getConcatContent(x, y, prefix, sorted=True)
                elif prefix in ['id'] + self._prevEl.orderedExtraKeys:
                    return self._getConcatContent(x, y, prefix, sorted=False)
                else:
                    if x != y:
                        return self._getMissingValue(prefix)
                
    def _getConcatContent(self, x, y, prefix, sorted):
        curValsList = self._curValsDict.get(prefix)
        if curValsList is None:
            curValsList = [x]
            self._curValsDict[prefix] = curValsList
        if sorted:
            insort(curValsList, y)
        else:
            curValsList.append(y)
        
        if all(x == val for val in curValsList):
            return x
        else:
            if len(curValsList) < Config.MAX_CONCAT_LEN_FOR_OVERLAPPING_ELS:
                return '|'.join(curValsList)
            else:
                return curValsList[0] + '|...'
    
    def _getMissingValue(self, prefix):
        if prefix == 'val':
            valDataType = self._geSource.getValDataType()
            if valDataType in ['float32', 'float64', 'float128']:
                return numpy.nan
            elif valDataType in ['int32', 'int64']:
                return 0
            elif valDataType == 'int8':
                return BINARY_MISSING_VAL
            elif valDataType == 'bool8':
                return True
            elif valDataType == 'S1':
                return ''
            elif valDataType[0] == 'S':
                return ''
        elif prefix == 'strand':
            return BINARY_MISSING_VAL
        else:
            return ''
        
class GEOverlapClusterer_Segment(GEOverlapClustererBase):
    def _overlapsPrev(self, el):
        return el.start < self._prevEl.end

    def _extendPrev(self, el):
        #self._prevEl = deepcopy(self._prevEl)
        self._prevEl = self._prevEl.getCopy()
        self._prevEl.end = max(self._prevEl.end, el.end)

class GEOverlapClusterer_Point(GEOverlapClustererBase):
    def _overlapsPrev(self, el):
        return el.start == self._prevEl.start

    def _extendPrev(self, el):
        #self._prevEl = deepcopy(self._prevEl)
        self._prevEl = self._prevEl.getCopy()

class GEOverlapClusterer_Partition(GEOverlapClustererBase):
    def __iter__(self):
        return self._geSource.__iter__()
    
    #def _overlapsPrev(self, el):
    #    return el.end == self._prevEl.end
    #
    #def _extendPrev(self, el):
    #    pass

class GEOverlapClusterer_Function(GEOverlapClustererBase):
    def __iter__(self):
        return self._geSource.__iter__()
