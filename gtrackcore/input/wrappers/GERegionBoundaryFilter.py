from gtrackcore.input.wrappers.GEFilter import GEFilter

class GERegionBoundaryFilter(GEFilter):
    def __init__(self, geSource, regionBoundaryIter):
        GEFilter.__init__(self, geSource)
        self._boundaryRegions = {}
        for region in regionBoundaryIter:
            if not region.chr in self._boundaryRegions:
                self._boundaryRegions[region.chr] = []
            self._boundaryRegions[region.chr].append(region)
    
    def next(self):
        nextEl = self._geIter.next() 
        while nextEl.chr not in self._boundaryRegions or \
            not True in [r.contains(nextEl) for r in self._boundaryRegions[nextEl.chr]]:
            nextEl = self._geIter.next()
        return nextEl
