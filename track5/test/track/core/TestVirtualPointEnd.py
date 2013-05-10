import unittest

from numpy import array

from track5.test.common.Asserts import AssertList
from track5.track.core.VirtualPointEnd import VirtualPointEnd

class TestVirtualPointEnd(unittest.TestCase):
    def setUp(self):
        self._array = array(range(100))
        self._vpe = VirtualPointEnd(self._array)
    
    def testIndexing(self):
        AssertList([x+1 for x in self._array], self._vpe, self.assertEqual)

    def _assertSlicing(self, i, j):
        AssertList([x+1 for x in self._array[i:j] ], self._vpe[i:j], self.assertEqual)

    def testSlicing(self):
        self._assertSlicing(10, 20)
        self._assertSlicing(10, 10)
        self._assertSlicing(0, 90)
        self._assertSlicing(10, 100)
        self._assertSlicing(0, 100)
        
    def testNumpyMethods(self):
        self.assertEqual(5050, self._vpe.sum())
    
if __name__ == "__main__":
    unittest.main()