import numpy

from gtrackcore.metadata.GenomeInfo import GenomeInfo
from gtrackcore.track.hierarchy.ExternalTrackManager import ExternalTrackManager
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track.memmap.BoundingRegionShelve import BoundingRegionShelve
from gtrackcore.util.CustomExceptions import BoundingRegionsNotAvailableError
from gtrackcore.util.CommonFunctions import prettyPrintTrackName

class BoundingRegionUserBinSource(object):
    def __init__(self, genome, trackName1, trackName2=None):
        assert trackName1 is not None
        assert genome is not None
        
        self.genome = genome
        self._trackName1 = trackName1
        self._trackName2 = trackName2
        
        self._getBoundingRegionShelve(trackName1)
        self._getBoundingRegionShelve(trackName2)
        
    def _getBoundingRegionShelve(self, trackName):
        if trackName in [None, []] or ExternalTrackManager.isVirtualTrack(trackName):
            brShelve = None
        else:
            brShelve = BoundingRegionShelve(self.genome, trackName, allowOverlaps=False)
            if not brShelve.fileExists():
                raise BoundingRegionsNotAvailableError('Bounding regions not available for track: ' + \
                    prettyPrintTrackName(trackName))
        
        return brShelve
        
    def __iter__(self):
        brShelve1 = self._getBoundingRegionShelve(self._trackName1)
        brShelve2 = self._getBoundingRegionShelve(self._trackName2)
        
        allBrsAreWholeChrs1 = self._commonAllBoundingRegionsAreWholeChr(brShelve1) \
            if brShelve1 is not None else False
        allBrsAreWholeChrs2 = self._commonAllBoundingRegionsAreWholeChr(brShelve2) \
            if brShelve2 is not None else False

        for chr in GenomeInfo.getExtendedChrList(self.genome):
            if brShelve1 is None:
                yield GenomeRegion(self.genome, chr, 0, GenomeInfo.getChrLen(self.genome, chr))
            else:
                brList1 = brShelve1.getAllBoundingRegionsForChr(chr)

                if brShelve2 is None or \
                    (allBrsAreWholeChrs2 and not allBrsAreWholeChrs1):
                    for reg in brList1:
                        yield reg
                else:
                    brList2 = brShelve2.getAllBoundingRegionsForChr(chr)
                    if allBrsAreWholeChrs1 and not allBrsAreWholeChrs2:
                        for reg in brList2:
                            yield reg
                    else:
                        for reg in self.getAllIntersectingRegions(self.genome, chr, brList1, brList2):
                            yield reg
    
    @classmethod
    def getAllIntersectingRegions(cls, genome, chr, regList1, regList2):
        regTuples1 = [(reg.start, reg.end) for reg in regList1]
        regTuples2 = [(reg.start, reg.end) for reg in regList2]
        
        if len(regTuples1) == 0 or len(regTuples2) == 0:
            return []
        
        starts1, ends1 = zip(*regTuples1)
        starts2, ends2 = zip(*regTuples2)
        starts = starts1 + starts2
        ends = ends1 + ends2
        
        borderArray = numpy.array(ends + starts)
        intersectionArray = numpy.array([-1 for e in ends] + [1 for s in starts])
        
        del regTuples1, regTuples2, starts1, starts2, starts, ends1, ends2, ends
        # Use merge sort, as it is stable
        sortedIndex = borderArray.argsort(kind='merge')
        borderArray = borderArray[sortedIndex]
        intersectionArray = intersectionArray[sortedIndex]
        
        intersectStartIndex = numpy.add.accumulate(intersectionArray) == 2
        intersectStarts = borderArray[intersectStartIndex]
        intersectEnds = borderArray[1:][intersectStartIndex[:-1]]
        
        assert len(intersectStarts) == len(intersectEnds)
        return [GenomeRegion(genome, chr, start, end) \
                for start, end in zip(intersectStarts, intersectEnds)]
    
    def  __len__(self):
        return sum(1 for i in self)
    
    def _commonAllBoundingRegionsAreWholeChr(self, brShelve):
        for chr in GenomeInfo.getExtendedChrList(self.genome):
            for reg in brShelve.getAllBoundingRegionsForChr(chr):
                if not reg.isWholeChr():
                    return False
        return True
    
    def allBoundingRegionsAreWholeChr(self):
        return all(self._commonAllBoundingRegionsAreWholeChr(x) for x in 
                   [self._brShelve1] + ([self._brShelve2] if self._brShelve2 is not None else []))
