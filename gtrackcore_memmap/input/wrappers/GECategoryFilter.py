from gtrackcore_memmap.input.wrappers.GEFilter import GEFilter

class GECategoryFilter(GEFilter):
    def __init__(self, geSource, filterList, strict=True):
        GEFilter.__init__(self, geSource)
        self._filterSet = set(filterList)
        self._strict = strict
    
    def next(self):
        nextEl = self._geIter.next()
        while (self._strict and not nextEl.val in self._filterSet) or \
            (not self._strict and not any(x in nextEl.val for x in self._filterSet)):
            nextEl = self._geIter.next()
        return nextEl
    