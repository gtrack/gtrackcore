import os
import unittest
import shutil

from gtrackcore.core.LogSetup import logMessage
from gtrackcore.track.pytables.BoundingRegionHandler import BoundingRegionHandler

from gtrackcore.input.core.GenomeElementSource import BoundingRegionTuple
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.util.CommonFunctions import get_dir_path
from gtrackcore.util.CustomExceptions import InvalidFormatError, OutsideBoundingRegionError


class TestBoundingRegionHandler(unittest.TestCase):
    def setUp(self):
        self._path = get_dir_path('TestGenome', ['test_bounding_region_handler'], allow_overlaps=False)
        if not os.path.exists(self._path):
            os.makedirs(self._path)
        self._fn = self._path + os.sep + 'test_bounding_region_handler.h5'

    def _set_up_handler(self):
        self._br_handler = BoundingRegionHandler('TestGenome', ['test_bounding_region_handler'], allow_overlaps=False)

    def tearDown(self):
        if os.path.exists(self._path):
            shutil.rmtree(self._path)

    def testNoBoundingRegions(self):
        for sparse in [False, True]:
            self._set_up_handler()
            self._br_handler.store_bounding_regions([], [], sparse)
            self.assertRaises(OutsideBoundingRegionError, self._br_handler.get_enclosing_bounding_region, GenomeRegion('TestGenome', 'chr21', 50000, 52000))

    def _commonStoreBoundingRegions(self, sparse):
        brTuples = [BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 0, 1000000), 10 if sparse else 1000000),\
                    BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 2000000, 2500000), 20 if sparse else 500000),\
                    BoundingRegionTuple(GenomeRegion('TestGenome', 'chrM', 1000, 2000), 5 if sparse else 1000)]
        self._br_handler.store_bounding_regions(brTuples, ['chr21', 'chrM'], sparse)

    def testTableFileExists(self):
        self._set_up_handler()
        
        self.assertFalse(self._br_handler.table_exists())
        self.assertFalse(os.path.exists(self._fn))
        
        self._commonStoreBoundingRegions(sparse=True)
        
        self.assertTrue(self._br_handler.table_exists())
        self.assertTrue(os.path.exists(self._fn))

    def testTableLocking(self):
        self._set_up_handler()

        BoundingRegionHandler('TestGenome', ['test_bounding_region_handler'], allow_overlaps=False)

        self._commonStoreBoundingRegions(sparse=True)
        
        BoundingRegionHandler('TestGenome', ['test_bounding_region_handler'], allow_overlaps=False)
        
    def testBoundingRegionsOverlapping(self):
        self._set_up_handler()
        
        brTuples = [BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 0, 1000000), 10), \
                    BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 500000, 2500000), 20)]

        self.assertRaises(InvalidFormatError, self._br_handler.store_bounding_regions, brTuples, ['chr21'], sparse=True)

    def testBoundingRegionsNoGaps(self):
        self._set_up_handler()
        
        brTuples = [BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 0, 1000000), 10), \
                    BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 1000000, 2500000), 20)]

        self.assertRaises(InvalidFormatError, self._br_handler.store_bounding_regions, brTuples, ['chr21'], sparse=True)

    def testBoundingRegionsNotPositive(self):
        self._set_up_handler()
        
        brTuples = [BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 0, 0), 1)]

        self.assertRaises(InvalidFormatError, self._br_handler.store_bounding_regions, brTuples, ['chr21'], sparse=True)
    
    def testBoundingRegionsUnsortedInChr(self):
        self._set_up_handler()
        
        brTuples = [BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 2000000, 2500000), 20),\
                    BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 0, 1000000), 10)]
        
        self.assertRaises(InvalidFormatError, self._br_handler.store_bounding_regions, brTuples, ['chr21'], sparse=True)
        
    def testBoundingRegionsChrNotGrouped(self):
        self._set_up_handler()
        
        brTuples = [BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 0, 1000000), 10), \
                    BoundingRegionTuple(GenomeRegion('TestGenome', 'chrM', 1000, 2000), 5), \
                    BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 2000000, 2500000), 20)]

        self.assertRaises(InvalidFormatError, self._br_handler.store_bounding_regions, brTuples, ['chr21', 'chrM'], sparse=True)
        
    def testBoundingRegionsChrInUnsortedOrder(self):
        self._set_up_handler()
        
        brTuples = [BoundingRegionTuple(GenomeRegion('TestGenome', 'chrM', 1000, 2000), 5), \
                    BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 0, 1000000), 10), \
                    BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 2000000, 2500000), 20)]
        
        self._br_handler.store_bounding_regions(brTuples, ['chr21', 'chrM'], sparse=True)
        
    def testBoundingRegionsNotBoundingAllChrs(self):
        self._set_up_handler()
        
        brTuples = [BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 0, 1000000), 10), \
                    BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 2000000, 2500000), 20)]

        self.assertRaises(InvalidFormatError, self._br_handler.store_bounding_regions, brTuples, ['chr21', 'chrM'], sparse=True)
        
    def testBoundingRegionsIncorrectCountSparse(self):
        self._set_up_handler()
        
        brTuples = [BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 0, 1000000), 10), \
                    BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 2000000, 2500000), 20), \
                    BoundingRegionTuple(GenomeRegion('TestGenome', 'chrM', 1000, 2000), 5)]

        self.assertRaises(InvalidFormatError, self._br_handler.store_bounding_regions, brTuples, ['chr21'], sparse=True)
        
    def testBoundingRegionIncorrectCountDense(self):
        self._set_up_handler()
        
        brTuples = [BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 0, 1000000), 1000000), \
                    BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 2000000, 2500000), 500000), \
                    BoundingRegionTuple(GenomeRegion('TestGenome', 'chrM', 1000, 2000), 500)]

        self.assertRaises(InvalidFormatError, self._br_handler.store_bounding_regions, brTuples, ['chr21', 'chrM'], sparse=False)
    
    def testStdGetBoundingInfoSparse(self):
        self._set_up_handler()
        self._commonStoreBoundingRegions(sparse=True)
        
        self.assertEquals(GenomeRegion(chr='chr21', start=0, end=1000000),
                          self._br_handler.get_enclosing_bounding_region(GenomeRegion('TestGenome', 'chr21', 50000, 52000)))
        self.assertEquals(GenomeRegion(chr='chr21', start=2000000, end=2500000),
                          self._br_handler.get_enclosing_bounding_region(GenomeRegion('TestGenome', 'chr21', 2050000, 2052000)))
        self.assertEquals(GenomeRegion(chr='chrM', start=1000, end=2000),
                          self._br_handler.get_enclosing_bounding_region(GenomeRegion('TestGenome', 'chrM', 1000, 2000)))
        
    def testStdGetBoundingInfoDense(self):
        self._set_up_handler()
        self._commonStoreBoundingRegions(sparse=False)
        
        self.assertEquals(GenomeRegion(chr='chr21', start=0, end=1000000),
                          self._br_handler.get_enclosing_bounding_region(GenomeRegion('TestGenome', 'chr21', 50000, 52000)))
        self.assertEquals(GenomeRegion(chr='chr21', start=2000000, end=2500000),
                          self._br_handler.get_enclosing_bounding_region(GenomeRegion('TestGenome', 'chr21', 2050000, 2052000)))
        self.assertEquals(GenomeRegion(chr='chrM', start=1000, end=2000),
                          self._br_handler.get_enclosing_bounding_region(GenomeRegion('TestGenome', 'chrM', 1000, 2000)))
    
    def testGetBoundingInfoEmptyBoundingRegionSparse(self):
        self._set_up_handler()
        
        brTuples = [BoundingRegionTuple(GenomeRegion('TestGenome', 'chrM', 1000, 2000), 0), \
                    BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 0, 1000000), 10), \
                    BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 2000000, 2500000), 20)]
        
        self._br_handler.store_bounding_regions(brTuples, ['chr21'], sparse=True)

        self.assertEquals(GenomeRegion(chr='chr21', start=0, end=1000000),
                          self._br_handler.get_enclosing_bounding_region(GenomeRegion('TestGenome', 'chr21', 50000, 52000)))
        self.assertEquals(GenomeRegion(chr='chr21', start=2000000, end=2500000),
                          self._br_handler.get_enclosing_bounding_region(GenomeRegion('TestGenome', 'chr21', 2050000, 2052000)))
        self.assertEquals(GenomeRegion(chr='chrM', start=1000, end=2000),
                          self._br_handler.get_enclosing_bounding_region(GenomeRegion('TestGenome', 'chrM', 1000, 2000)))
    
    def _testGetBoundingInfoOutsideCommon(self, sparse):
        self._set_up_handler()
        self._commonStoreBoundingRegions(sparse=sparse)
        self.assertRaises(OutsideBoundingRegionError, \
                          self._br_handler.get_enclosing_bounding_region, \
                          GenomeRegion('TestGenome', 'chr21', 50000, 1052000))
        self.assertRaises(OutsideBoundingRegionError, \
                          self._br_handler.get_enclosing_bounding_region, \
                          GenomeRegion('TestGenome', 'chr21', 1000000, 1052000))
        self.assertRaises(OutsideBoundingRegionError, \
                          self._br_handler.get_enclosing_bounding_region, \
                          GenomeRegion('TestGenome', 'chrM', 1500, 3000))

    def testGetBoundingInfoOutsideSparse(self):
        self._testGetBoundingInfoOutsideCommon(sparse=True)
        
    def testGetBoundingInfoOutsideDense(self):
        self._testGetBoundingInfoOutsideCommon(sparse=False)
    
    def testStdGetTotalElementCountForChrSparse(self):
        self._set_up_handler()
        self._commonStoreBoundingRegions(sparse=True)
        self.assertEquals(30,
                          self._br_handler.get_total_element_count_for_chr('chr21'))
        self.assertEquals(5,
                          self._br_handler.get_total_element_count_for_chr('chrM'))
        self.assertEquals(0,
                          self._br_handler.get_total_element_count_for_chr('chr1'))
        
    def testStdGetTotalElementCountForChrDense(self):
        self._set_up_handler()
        self._commonStoreBoundingRegions(sparse=False)
        self.assertEquals(1500000,
                          self._br_handler.get_total_element_count_for_chr('chr21'))
        self.assertEquals(1000,
                          self._br_handler.get_total_element_count_for_chr('chrM'))
        self.assertEquals(0,
                          self._br_handler.get_total_element_count_for_chr('chr1'))
        
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestBoundingRegionShelve().debug()
    unittest.main()
