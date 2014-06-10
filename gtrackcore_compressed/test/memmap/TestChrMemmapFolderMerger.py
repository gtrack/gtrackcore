import unittest
import numpy as np

from numpy import nan

from gtrackcore_compressed.preprocess.memmap.ChrMemmapFolderMerger import ChrMemmapFolderMerger
from gtrackcore_compressed.test.common.Asserts import TestCaseWithImprovedAsserts
from gtrackcore_compressed.util.CommonConstants import BINARY_MISSING_VAL

class TestChrMemmapFolderMerger(TestCaseWithImprovedAsserts):
    def setUp(self):
        pass
    
    def _assertDepth(self, target, source, delta, val):
        self.assertListsOrDicts(target, ChrMemmapFolderMerger.appendDepth(source, delta, val))
    
    def testAppendDepth(self):
        self._assertDepth(np.array([[[nan]]]),
                          np.array([[[]]]), 1, nan)
        
        self._assertDepth(np.array([[[0,1,nan], [1,2,nan]]]),
                          np.array([[[0,1], [1,2]]], dtype='float'), 1, nan)
        
        self._assertDepth(np.array([[[0,1,nan,nan], [1,2,nan,nan]]]),
                          np.array([[[0,1], [1,2]]], dtype='float'), 2, nan)
    
        self._assertDepth(np.array([[[0,1,0], [1,2,0]]]),
                          np.array([[[0,1], [1,2]]]), 1, 0)
        
        self._assertDepth(np.array([[[0,1], [1,2]]], dtype='float'),
                          np.array([[[0,1], [1,2]]], dtype='float'), 0, nan)
        
        self._assertDepth(np.array([[[0,1,nan], [1,2,nan]], [[1,2,nan], [2,3,nan]]]),
                          np.array([[[0,1], [1,2]], [[1,2], [2,3]]], dtype='float'), 1, nan)
        
        self.assertRaises(AssertionError, ChrMemmapFolderMerger.appendDepth, np.array([[1,2]]), 1, nan)
        self.assertRaises(ValueError, ChrMemmapFolderMerger.appendDepth, np.array([[[1,2]]]), -1, nan)
        self.assertRaises(ValueError, ChrMemmapFolderMerger.appendDepth, np.array([[[1,2]]]), 1, nan)
    
    def _assertHeight(self, target, source, delta, val):
        self.assertListsOrDicts(target, ChrMemmapFolderMerger.appendHeight(source, delta, val))
    
    def testAppendHeight(self):
        self._assertHeight(np.array([[nan]]),
                           np.array([[]]), 1, nan)
        
        self._assertHeight(np.array([[0,1,nan], [1,2,nan]]),
                           np.array([[0,1], [1,2]], dtype='float'), 1, nan)
        
        self._assertHeight(np.array([[0,1,nan,nan], [1,2,nan,nan]]),
                           np.array([[0,1], [1,2]], dtype='float'), 2, nan)
    
        self._assertHeight(np.array([[0,1,0], [1,2,0]]),
                           np.array([[0,1], [1,2]]), 1, 0)
        
        self._assertHeight(np.array([[0,1], [1,2]], dtype='float'),
                           np.array([[0,1], [1,2]], dtype='float'), 0, nan)
        
        self._assertHeight(np.array([[[0,1], [1,2], [nan,nan]]]),
                           np.array([[[0,1], [1,2]]], dtype='float'), 1, nan)
        
        self._assertHeight(np.array([[[0,1], [1,2], [nan,nan]], [[1,2], [2,3], [nan,nan]]]),
                           np.array([[[0,1], [1,2]], [[1,2], [2,3]]], dtype='float'), 1, nan)
        
        self.assertRaises(AssertionError, ChrMemmapFolderMerger.appendHeight, np.array([1,2]), 1, nan)
        self.assertRaises(ValueError, ChrMemmapFolderMerger.appendHeight, np.array([[[1,2]]]), -1, nan)
        self.assertRaises(ValueError, ChrMemmapFolderMerger.appendHeight, np.array([[[1,2]]]), 1, nan)
    
    def _assertMerge(self, target, source1, source2):
        self.assertListsOrDicts(target, ChrMemmapFolderMerger.mergeArrays(source1, source2))
    
    def testMergeArrays(self):
        self._assertMerge(np.array([]), \
                          np.array([]), np.array([]))
        
        self._assertMerge(np.array([1,2,3,4]), \
                          np.array([1,2]), np.array([3,4]))
        
        self._assertMerge(np.array([['a','b'], ['aa',''], ['bb','']], dtype='S2'), \
                          np.array([['a','b']], dtype='S1'), np.array([['aa'], ['bb']], dtype='S2'))
        
        self._assertMerge(np.array([[[1.0,2.0,nan], [3.0,4.0,nan]], [[5.0,6.0,7.0], [nan,nan,nan]]]), \
                          np.array([[[1.0,2.0], [3.0,4.0]]]), np.array([[[5.0,6.0,7.0]]]))
        
        self._assertMerge(np.array([[[True, False], [False, False]], [[False, False], [False, False]]]), \
                          np.array([[[True], [False]]]), np.array([[[False, False]]]))
        
        self._assertMerge(np.array([[[True, BINARY_MISSING_VAL], [False, BINARY_MISSING_VAL]], \
                                    [[False, BINARY_MISSING_VAL], [BINARY_MISSING_VAL, BINARY_MISSING_VAL]]]), \
                          np.array([[[True], [False]]], dtype='int'), np.array([[[False, BINARY_MISSING_VAL]]]))
        
        self._assertMerge(np.array([1,2]), \
                          np.array([1,2]), np.array([], dtype='int'))
        
        self._assertMerge(np.array([[[1.0,2.0], [3.0,4.0]], [[nan,nan], [nan,nan]]]), \
                          np.array([[[1.0,2.0], [3.0,4.0]]]), np.array([[[]]]))
        
        self.assertRaises(AssertionError, ChrMemmapFolderMerger.mergeArrays, np.array([1,2]), np.array([[3,4]]))
        self.assertRaises(AssertionError, ChrMemmapFolderMerger.mergeArrays, np.array([[[[1,2]]]]), np.array([[[[3,4]]]]))
        self.assertRaises(AssertionError, ChrMemmapFolderMerger.mergeArrays, np.array([1,2], dtype='int'), np.array([3,4], dtype='float'))
    
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestChrMemmapFolderMerger().debug()
    unittest.main()