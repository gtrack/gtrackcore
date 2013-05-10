import unittest

from track5.input.wrappers.GEBoundingRegionElementCounter import GEBoundingRegionElementCounter
from track5.test.common.Asserts import assertBoundingRegions, TestCaseWithImprovedAsserts
from track5.util.CommonConstants import BINARY_MISSING_VAL

class TestGEBoundingRegionElementCounter(TestCaseWithImprovedAsserts):
    def setUp(self):
        pass
    
    def _assertCounting(self, processedBRList, origBRTuples, origGEList):
        assertBoundingRegions(GEBoundingRegionElementCounter, self.assertEqual, processedBRList, \
                              origBRTuples, origGEList, sendBoundingRegionsToDecorator=True)
        
    def testCountElements(self):
        self._assertCounting([], \
                             [], \
                             [])
        
        self._assertCounting([], \
                             [], \
                             [['A', 'chr1', 10, 100]])
        
        self._assertCounting([['A', 'chr1', 0, 1000, 1]], \
                             [['A', 'chr1', 0, 1000, None]], \
                             [['A', 'chr1', 10, 100]])
        
        self._assertCounting([['A', 'chr1', 0, 1000, 2], ['A', 'chr2', 0, 1000, 1]], \
                             [['A', 'chr1', 0, 1000, None], ['A', 'chr2', 0, 1000, None]], \
                             [['A', 'chr1', 10, 100], ['A', 'chr1', 80, 120], ['A', 'chr2', 10, 100]])
    
        self._assertCounting([['A', 'chr1', 0, 1000, 2], ['A', 'chr2', 0, 1000, 1], ['A', 'chr2', 1000, 2000, 0]], \
                             [['A', 'chr1', 0, 1000, None], ['A', 'chr2', 0, 1000, None], ['A', 'chr2', 1000, 2000, None]], \
                             [['A', 'chr1', 10, 100], ['A', 'chr1', 80, 120], ['A', 'chr2', 10, 100]])
    
        self._assertCounting([['A', 'chr1', 0, 1000, 2], ['A', 'chr2', 0, 1000, 1], ['A', 'chr2', 1000, 2000, 0]], \
                             [['A', 'chr1', 0, 1000, None], ['A', 'chr2', 0, 1000, None], ['A', 'chr2', 1000, 2000, None]], \
                             [['A', 'chr1', 10, None], ['A', 'chr1', 80, None], ['A', 'chr2', 10, None]])
    
        self._assertCounting([['A', 'chr1', 0, 1000, 2], ['A', 'chr1', 1000, 2000, 0], ['A', 'chr2', 0, 1000, 2]], \
                             [['A', 'chr1', 0, 1000, None], ['A', 'chr1', 1000, 2000, None], ['A', 'chr2', 0, 1000, None]], \
                             [['A', 'chr1', None, 0], ['A', 'chr1', None, 1000], ['A', 'chr2', None, 0], ['A', 'chr2', None, 1000]])
        
        self._assertCounting([['A', 'chr1', 0, 2, 2], ['A', 'chr2', 0, 1, 1]], \
                             [['A', 'chr1', 0, 2, None], ['A', 'chr2', 0, 1, None]], \
                             [['A', 'chr1', None, None, {'val':0.0}], ['A', 'chr1', None, None, {'val':1.0}], ['A', 'chr2', None, None, {'val':2.0}]])
    
    def runTest(self):
        pass
        self.testCountElements()
    
if __name__ == "__main__":
    #TestGEBoundingRegionElementCounter().debug()
    unittest.main()