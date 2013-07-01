from copy import copy

from gtrackcore.input.wrappers.GESourceWrapper import GESourceWrapper

class GESorter(GESourceWrapper):
    def __init__(self, geSource):
        GESourceWrapper.__init__(self, geSource)
        self._geIter = None
        self._sortedElements = None
        
    def __iter__(self):
        if True in [attrs in self._geSource.getPrefixList() for attrs in ['start', 'end']]:
            if self._sortedElements is None:
                #self._sortedElements = [deepcopy(el) for el in self._geSource]
                self._sortedElements = [el.getCopy() for el in self._geSource]
                self._sortedElements.sort(key=lambda el: [el.genome, el.chr, el.start, el.end])
                
            self._geIter = self._sortedElements.__iter__()
            return copy(self)
        else:
            return self._geSource.__iter__()        
    
    def next(self):
        el = self._geIter.next()
        return el
        
    def __len__(self):
        if self._sortedElements is None:
            return sum(1 for el in self)
        else:
            return len(self._sortedElements)