import os
import unittest
import shutil

from gtrackcore.input.core.GenomeElementSource import BoundingRegionTuple
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track.memmap.BoundingRegionShelve import BoundingRegionShelve, BoundingRegionInfo
from gtrackcore.util.CommonFunctions import getDirPath
from gtrackcore.util.CustomExceptions import InvalidFormatError, OutsideBoundingRegionError

class TestBoundingRegionShelve(unittest.TestCase):
    def setUp(self):
        self._path = getDirPath(['testBoundingRegionShelve'], 'TestGenome', allowOverlaps=False)
        self._fn = self._path + os.sep + 'boundingRegions.shelve'
        
    def _setUpShelve(self):
        self._brShelve = BoundingRegionShelve('TestGenome',['testBoundingRegionShelve'], allowOverlaps=False)
        
    def tearDown(self):
        if os.path.exists(self._path):
            shutil.rmtree(self._path)
    
    def testNoBoundingRegions(self):
        for sparse in [False, True]:
            self._setUpShelve()
            self._brShelve.storeBoundingRegions([], [], sparse)
            self.assertEquals(BoundingRegionInfo(50000, 52000, 0, 0, 0, 0),
                              self._brShelve.getBoundingRegionInfo(GenomeRegion('TestGenome', 'chr21', 50000, 52000)))
    
    def _commonStoreBoundingRegions(self, sparse):
        brTuples = [BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 0, 1000000), 10 if sparse else 1000000),\
                    BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 2000000, 2500000), 20 if sparse else 500000),\
                    BoundingRegionTuple(GenomeRegion('TestGenome', 'chrM', 1000, 2000), 5 if sparse else 1000)]
        self._brShelve.storeBoundingRegions(brTuples, ['chr21', 'chrM'], sparse)
        
    def testShelveFileExists(self):
        self._setUpShelve()
        
        self.assertFalse(self._brShelve.fileExists())
        self.assertFalse(os.path.exists(self._fn))
        
        self._commonStoreBoundingRegions(sparse=True)
        
        self.assertTrue(self._brShelve.fileExists())
        self.assertTrue(os.path.exists(self._fn))
    
    def testShelveLocking(self):
        self._setUpShelve()
        
        BoundingRegionShelve('TestGenome',['testBoundingRegionShelve'], allowOverlaps=False)
        
        self._commonStoreBoundingRegions(sparse=True)
        
        BoundingRegionShelve('TestGenome',['testBoundingRegionShelve'], allowOverlaps=False)
    
    def testBoundingRegionsOverlapping(self):
        self._setUpShelve()
        
        brTuples = [BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 0, 1000000), 10), \
                    BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 500000, 2500000), 20)]

        self.assertRaises(InvalidFormatError, self._brShelve.storeBoundingRegions, brTuples, ['chr21'], sparse=True)
    
    def testBoundingRegionsNoGaps(self):
        self._setUpShelve()
        
        brTuples = [BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 0, 1000000), 10), \
                    BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 1000000, 2500000), 20)]

        self.assertRaises(InvalidFormatError, self._brShelve.storeBoundingRegions, brTuples, ['chr21'], sparse=True)
        
    def testBoundingRegionsNotPositive(self):
        self._setUpShelve()
        
        brTuples = [BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 0, 0), 1)]

        self.assertRaises(InvalidFormatError, self._brShelve.storeBoundingRegions, brTuples, ['chr21'], sparse=True)
    
    def testBoundingRegionsUnsortedInChr(self):
        self._setUpShelve()
        
        brTuples = [BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 2000000, 2500000), 20),\
                    BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 0, 1000000), 10)]
        
        self.assertRaises(InvalidFormatError, self._brShelve.storeBoundingRegions, brTuples, ['chr21'], sparse=True)
        
    def testBoundingRegionsChrNotGrouped(self):
        self._setUpShelve()
        
        brTuples = [BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 0, 1000000), 10), \
                    BoundingRegionTuple(GenomeRegion('TestGenome', 'chrM', 1000, 2000), 5), \
                    BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 2000000, 2500000), 20)]

        self.assertRaises(InvalidFormatError, self._brShelve.storeBoundingRegions, brTuples, ['chr21', 'chrM'], sparse=True)
        
    def testBoundingRegionsChrInUnsortedOrder(self):
        self._setUpShelve()
        
        brTuples = [BoundingRegionTuple(GenomeRegion('TestGenome', 'chrM', 1000, 2000), 5), \
                    BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 0, 1000000), 10), \
                    BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 2000000, 2500000), 20)]
        
        self._brShelve.storeBoundingRegions(brTuples, ['chr21', 'chrM'], sparse=True)
        
    def testBoundingRegionsNotBoundingAllChrs(self):
        self._setUpShelve()
        
        brTuples = [BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 0, 1000000), 10), \
                    BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 2000000, 2500000), 20)]

        self.assertRaises(InvalidFormatError, self._brShelve.storeBoundingRegions, brTuples, ['chr21', 'chrM'], sparse=True)
        
    def testBoundingRegionsIncorrectCountSparse(self):
        self._setUpShelve()
        
        brTuples = [BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 0, 1000000), 10), \
                    BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 2000000, 2500000), 20), \
                    BoundingRegionTuple(GenomeRegion('TestGenome', 'chrM', 1000, 2000), 5)]

        self.assertRaises(InvalidFormatError, self._brShelve.storeBoundingRegions, brTuples, ['chr21'], sparse=True)
        
    def testBoundingRegionIncorrectCountDense(self):
        self._setUpShelve()
        
        brTuples = [BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 0, 1000000), 1000000), \
                    BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 2000000, 2500000), 500000), \
                    BoundingRegionTuple(GenomeRegion('TestGenome', 'chrM', 1000, 2000), 500)]

        self.assertRaises(InvalidFormatError, self._brShelve.storeBoundingRegions, brTuples, ['chr21', 'chrM'], sparse=False)
    
    def testStdGetBoundingInfoSparse(self):
        self._setUpShelve()
        self._commonStoreBoundingRegions(sparse=True)
        
        self.assertEquals(BoundingRegionInfo(0, 1000000, 0, 30, 0, 470),
                          self._brShelve.getBoundingRegionInfo(GenomeRegion('TestGenome', 'chr21', 50000, 52000)))
        self.assertEquals(BoundingRegionInfo(2000000, 2500000, 0, 30, 0, 470),
                          self._brShelve.getBoundingRegionInfo(GenomeRegion('TestGenome', 'chr21', 2050000, 2052000)))
        self.assertEquals(BoundingRegionInfo(1000, 2000, 30, 35, 470, 471),
                          self._brShelve.getBoundingRegionInfo(GenomeRegion('TestGenome', 'chrM', 1000, 2000)))
        
    def testStdGetBoundingInfoDense(self):
        self._setUpShelve()
        self._commonStoreBoundingRegions(sparse=False)
        
        self.assertEquals(BoundingRegionInfo(0, 1000000, 0, 1000000, 0, 0),
                          self._brShelve.getBoundingRegionInfo(GenomeRegion('TestGenome', 'chr21', 50000, 52000)))
        self.assertEquals(BoundingRegionInfo(2000000, 2500000, 1000000, 1500000, 0, 0),
                          self._brShelve.getBoundingRegionInfo(GenomeRegion('TestGenome', 'chr21', 2050000, 2052000)))
        self.assertEquals(BoundingRegionInfo(1000, 2000, 1500000, 1501000, 0, 0),
                          self._brShelve.getBoundingRegionInfo(GenomeRegion('TestGenome', 'chrM', 1000, 2000)))
    
    def testGetBoundingInfoEmptyBoundingRegionSparse(self):
        self._setUpShelve()
        
        brTuples = [BoundingRegionTuple(GenomeRegion('TestGenome', 'chrM', 1000, 2000), 0), \
                    BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 0, 1000000), 10), \
                    BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 2000000, 2500000), 20)]
        
        self._brShelve.storeBoundingRegions(brTuples, ['chr21'], sparse=True)
        
        self.assertEquals(BoundingRegionInfo(0, 1000000, 0, 30, 0, 470),
                          self._brShelve.getBoundingRegionInfo(GenomeRegion('TestGenome', 'chr21', 50000, 52000)))
        self.assertEquals(BoundingRegionInfo(2000000, 2500000, 0, 30, 0, 470),
                          self._brShelve.getBoundingRegionInfo(GenomeRegion('TestGenome', 'chr21', 2050000, 2052000)))
        self.assertEquals(BoundingRegionInfo(1000, 2000, 0, 0, 0, 0),
                          self._brShelve.getBoundingRegionInfo(GenomeRegion('TestGenome', 'chrM', 1000, 2000)))
    
    def _testGetBoundingInfoOutsideCommon(self, sparse):
        self._setUpShelve()
        self._commonStoreBoundingRegions(sparse=sparse)
        self.assertRaises(OutsideBoundingRegionError, \
                          self._brShelve.getBoundingRegionInfo, \
                          GenomeRegion('TestGenome', 'chr21', 50000, 1052000))
        self.assertRaises(OutsideBoundingRegionError, \
                          self._brShelve.getBoundingRegionInfo, \
                          GenomeRegion('TestGenome', 'chr21', 1000000, 1052000))
        self.assertRaises(OutsideBoundingRegionError, \
                          self._brShelve.getBoundingRegionInfo, \
                          GenomeRegion('TestGenome', 'chrM', 1500, 3000))
        self.assertEquals(BoundingRegionInfo(100000, 110000, 0, 0, 0, 0),
                          self._brShelve.getBoundingRegionInfo(GenomeRegion('TestGenome', 'chr2', 100000, 110000)))
        
    def testGetBoundingInfoOutsideSparse(self):
        self._testGetBoundingInfoOutsideCommon(sparse=True)
        
    def testGetBoundingInfoOutsideDense(self):
        self._testGetBoundingInfoOutsideCommon(sparse=False)
    
    def testStdGetTotalElementCountForChrSparse(self):
        self._setUpShelve()
        self._commonStoreBoundingRegions(sparse=True)
        self.assertEquals(30,
                          self._brShelve.getTotalElementCountForChr('chr21'))
        self.assertEquals(5,
                          self._brShelve.getTotalElementCountForChr('chrM'))
        self.assertEquals(0,
                          self._brShelve.getTotalElementCountForChr('chr1'))
        
    def testStdGetTotalElementCountForChrDense(self):
        self._setUpShelve()
        self._commonStoreBoundingRegions(sparse=False)
        self.assertEquals(1500000,
                          self._brShelve.getTotalElementCountForChr('chr21'))
        self.assertEquals(1000,
                          self._brShelve.getTotalElementCountForChr('chrM'))
        self.assertEquals(0,
                          self._brShelve.getTotalElementCountForChr('chr1'))
        
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestBoundingRegionShelve().debug()
    unittest.main()
    