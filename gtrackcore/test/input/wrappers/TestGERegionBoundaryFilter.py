import unittest

from functools import partial

from gtrackcore.input.wrappers.GERegionBoundaryFilter import GERegionBoundaryFilter
from gtrackcore.input.userbins.UserBinSource import GlobalBinSource
from gtrackcore.test.common.Asserts import assertDecorator

class TestGERegionBoundaryFilter(unittest.TestCase):
    def setUp(self):
        pass    
    
    def _assertFilter(self, filteredList, unfilteredList):
        assertDecorator(partial(GERegionBoundaryFilter, regionBoundaryIter=GlobalBinSource('TestGenome')), \
                                self.assertEqual, filteredList, unfilteredList)
    
    def testFilter(self):
        self._assertFilter([['TestGenome','chr21',2,5],['TestGenome','chrM',3,8]], \
                           [['TestGenome','chr21',2,5],['TestGenome','chrM',3,8]])
        self._assertFilter([['TestGenome','chrM',3,8]], \
                           [['Test','chr21',2,5],['TestGenome','chrM',3,8]])
        self._assertFilter([['TestGenome','chr21',2,5]], \
                           [['TestGenome','chr21',2,5],['TestGenome','chrTest',3,8]])
        self._assertFilter([['TestGenome','chrM',3,8]], \
                           [['TestGenome','chr21',-2,5],['TestGenome','chrM',3,8]])
        
if __name__ == "__main__":
    unittest.main()