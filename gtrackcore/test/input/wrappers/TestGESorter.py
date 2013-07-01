import unittest

from gtrackcore.input.wrappers.GESorter import GESorter
from gtrackcore.test.common.Asserts import assertDecorator

class TestGESorter(unittest.TestCase):
    def setUp(self):
        pass    
    
    def _assertSort(self, sortedList, unsortedList):
        assertDecorator(GESorter, self.assertEqual, sortedList, unsortedList)
    
    def testSort(self):
        self._assertSort([['A','chr2',3,8],['B','chr1',2,5]], [['B','chr1',2,5],['A','chr2',3,8]])
        self._assertSort([['A','chr1',3,8],['A','chr2',2,5]], [['A','chr2',2,5],['A','chr1',3,8]])
        self._assertSort([['A','chr1',2,8],['A','chr1',3,5]], [['A','chr1',3,5],['A','chr1',2,8]])
        self._assertSort([['A','chr1',2,5],['A','chr1',2,8]], [['A','chr1',2,8],['A','chr1',2,5]])
        
        self._assertSort([[None,'chr1',3,8],[None,'chr2',2,5]], [[None,'chr2',2,5],[None,'chr1',3,8]])
        self._assertSort([[None,'chr1',2,8],[None,'chr1',3,5]], [[None,'chr1',3,5],[None,'chr1',2,8]])
        self._assertSort([[None,'chr1',2,5],[None,'chr1',2,8]], [[None,'chr1',2,8],[None,'chr1',2,5]])
        
        self._assertSort([['A','chr2',3,None],['B','chr1',2,None]], [['B','chr1',2,None],['A','chr2',3,None]])
        self._assertSort([['A','chr1',3,None],['A','chr2',2,None]], [['A','chr2',2,None],['A','chr1',3,None]])
        self._assertSort([['A','chr1',2,None],['A','chr1',3,None]], [['A','chr1',3,None],['A','chr1',2,None]])

        self._assertSort([['A','chr2',None,8],['B','chr1',None,5]], [['B','chr1',None,5],['A','chr2',None,8]])
        self._assertSort([['A','chr1',None,8],['A','chr2',None,5]], [['A','chr2',None,5],['A','chr1',None,8]])
        self._assertSort([['A','chr1',None,5],['A','chr1',None,8]], [['A','chr1',None,8],['A','chr1',None,5]])

        self._assertSort([['B','chr2',None,None],['A','chr1',None,None]], [['B','chr2',None,None],['A','chr1',None,None]])
        
if __name__ == "__main__":
    unittest.main()