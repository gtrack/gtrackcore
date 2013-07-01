import unittest

from gtrackcore.input.userbins.BoundingRegionUserBinSource import BoundingRegionUserBinSource
from gtrackcore.test.common.Asserts import TestCaseWithImprovedAsserts
from gtrackcore.track.core.GenomeRegion import GenomeRegion

class TestBoundingRegionUserBinSource(TestCaseWithImprovedAsserts):
    def setUp(self):
        pass
    
    def _assertIntersect(self, assertRegs, chr, regs1, regs2):
        genomeRegs1 = [GenomeRegion('TestGenome', chr, start, end) for start, end in regs1]
        genomeRegs2 = [GenomeRegion('TestGenome', chr, start, end) for start, end in regs2]
        genomeAssertRegs = [GenomeRegion('TestGenome', chr, start, end) for start, end in assertRegs]
        
        resultRegs = BoundingRegionUserBinSource.getAllIntersectingRegions\
            ('TestGenome', chr, genomeRegs1, genomeRegs2)
        
        #print [str(x) for x in resultRegs]
        self.assertListsOrDicts(genomeAssertRegs, resultRegs)
    
    def testGetAllIntersectingRegions(self):
        self._assertIntersect([], 'chr21', [], [])
        self._assertIntersect([], 'chr21', [], [[3,8]])
        self._assertIntersect([], 'chr21', [[0,6]], [])
        self._assertIntersect([[3,6]], 'chr21', [[0,6]], [[3,8]])
        self._assertIntersect([[3,6],[6,7]], 'chr21', [[2,6],[6,7]], [[3,8]])
        self._assertIntersect([[5,6],[7,8],[9,10]], 'chr21', [[5,10]], [[0,6],[7,8],[9,10]])
        self._assertIntersect([[0,10]], 'chr21', [[0,10]], [[0,10]])
    
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestBoundingRegionUserBinSource().debug()
    unittest.main()