import unittest

from gtrackcore_compressed.test.common.Asserts import AssertList
from gtrackcore_compressed.track.core.GenomeRegion import GenomeRegion
from gtrackcore_compressed.util.CompBinManager import CompBinManager

import gtrackcore_compressed.util.CompBinManager

class TestCompBinManager(unittest.TestCase):
    def setUp(self):
        self.prevCompBinSize = gtrackcore_compressed.util.CompBinManager.COMP_BIN_SIZE
        gtrackcore_compressed.util.CompBinManager.COMP_BIN_SIZE = 100
        
    def tearDown(self):
        gtrackcore_compressed.util.CompBinManager.COMP_BIN_SIZE = self.prevCompBinSize

    def _assertSplitUserBin(self, compBins, start, end):
        region = GenomeRegion('hg18','chr1', start, end)
        compBinRegions = [GenomeRegion('hg18', 'chr1', elStart, elEnd) for elStart, elEnd in compBins]
        AssertList(compBinRegions, CompBinManager.splitUserBin(region), self.assertEqual)
        
    def testSplitUserBin(self):
        self._assertSplitUserBin([[0,100]], 0, 100)
        self._assertSplitUserBin([[100,200], [200,300]], 100, 300)
        self._assertSplitUserBin([[67,100], [100,200], [200,300], [300,314]], 67, 314)
        self._assertSplitUserBin([], 0, 0)
        
    def testGetBinNumber(self):
        self.assertEqual(0, CompBinManager.getBinNumber(0))
        self.assertEqual(2, CompBinManager.getBinNumber(200))
        self.assertEqual(3, CompBinManager.getBinNumber(314))
        
    def testGetPosFromBinNumber(self):
        self.assertEqual(0, CompBinManager.getPosFromBinNumber(0))
        self.assertEqual(200, CompBinManager.getPosFromBinNumber(2))
        self.assertEqual(300, CompBinManager.getPosFromBinNumber(3))

    def testGetNumOfBins(self):
        self.assertEqual(0, CompBinManager.getNumOfBins(GenomeRegion('hg18', 'chr1', 0, 0)))
        self.assertEqual(1, CompBinManager.getNumOfBins(GenomeRegion('hg18', 'chr1', 0, 100)))
        self.assertEqual(2, CompBinManager.getNumOfBins(GenomeRegion('hg18', 'chr1', 200, 400)))
        self.assertEqual(4, CompBinManager.getNumOfBins(GenomeRegion('hg18', 'chr1', 67, 314)))
        
    def testGetOffset(self):
        self.assertEqual(0, CompBinManager.getOffset(0,0))
        self.assertEqual(0,CompBinManager.getOffset(200,2))
        self.assertEqual(14,CompBinManager.getOffset(314,3))
        self.assertEqual(-86,CompBinManager.getOffset(314,4))
        
    def testIsCompBin(self):
        self.assertTrue(CompBinManager.isCompBin( GenomeRegion('TestGenome', 'chr21', 0, 100) ))
        self.assertTrue(CompBinManager.isCompBin( GenomeRegion('TestGenome', 'chr21', 200, 300) ))
        self.assertTrue(CompBinManager.isCompBin( GenomeRegion('TestGenome', 'chr21', 46944300, 46944323) ))
        
        self.assertFalse(CompBinManager.isCompBin( GenomeRegion('TestGenome', 'chr21', 0, 40) ))
        self.assertFalse(CompBinManager.isCompBin( GenomeRegion('TestGenome', 'chr21', 10, 100) ))
        self.assertFalse(CompBinManager.isCompBin( GenomeRegion('TestGenome', 'chr21', 10, 200) ))
        self.assertFalse(CompBinManager.isCompBin( GenomeRegion('TestGenome', 'chr21', 100, 300) ))
        self.assertFalse(CompBinManager.isCompBin( GenomeRegion('TestGenome', 'chr21', 46944300, 46944322) ))
        self.assertFalse(CompBinManager.isCompBin( GenomeRegion('TestGenome', 'chr21', 46944300, 46944324) ))

if __name__ == "__main__":
    unittest.main()
