import unittest

from gtrackcore.test.common.Asserts import assertDecorator, TestCaseWithImprovedAsserts
from gtrackcore.input.wrappers.GENumpyArrayConverter import GENumpyArrayConverter
import numpy as np


class TestGENumpyArrayConverter(TestCaseWithImprovedAsserts):
    def setUp(self):
        pass

    def _assertConvert(self, convertedList, originalList):
        assertDecorator(GENumpyArrayConverter, self.assertEquals, convertedList, originalList)

    def testConvertor(self):
        self._assertConvert([['A' ,'chr2' ,3 ,8] ,['B' ,'chr1' ,2 ,5]], [['A' ,'chr2' ,3 ,8], ['B' ,'chr1' ,2 ,5]])
        self._assertConvert([['A', 'chr2', 3, 8], ['A', 'chr2', 10, 11], ['B', 'chr1', 2, 5], ['B', 'chr1', 3, 6]], [['A', 'chr2', np.array([3, 10]), np.array([8, 11])], ['B', 'chr1', np.array([2, 3]), np.array([5, 6])]])
        self._assertConvert([['A', 'chr2', 3, 8, {'val' : 100, 'strand' : '+'}], ['A', 'chr2', 10, 11, {'val' : 200, 'strand' : '.'}],
                             ['B', 'chr1', 2, 5, {'val' : 10, 'strand' : '+'}], ['B', 'chr1', 3, 6, {'val' : 20, 'strand' : '-'}]],
                            [['A', 'chr2', np.array([3, 10]), np.array([8, 11]), {'val' : np.array([100, 200]), 'strand' : np.array(['+', '.'])}],
                            ['B', 'chr1', np.array([2, 3]), np.array([5, 6]), {'val' : np.array([10, 20]), 'strand' : np.array(['+', '-'])}]])


if __name__ == "__main__":
    unittest.main()
