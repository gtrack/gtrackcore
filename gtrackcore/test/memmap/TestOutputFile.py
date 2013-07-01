import unittest
import os
import sys

from stat import *
from numpy import memmap, ndarray, nan
from copy import copy
from collections import OrderedDict

from gtrackcore.input.core.GenomeElement import GenomeElement
from gtrackcore.preprocess.memmap.OutputFile import OutputFile
from gtrackcore.util.CommonFunctions import isIter

from gtrackcore.test.common.Asserts import TestCaseWithImprovedAsserts
from gtrackcore.test.common.FileUtils import removeFile

class Setup:
    def __init__(self, filePrefix, size, dataType, dataTypeDim, elementDim):
        self.path = os.path.dirname(os.tempnam())
        self.filePrefix = filePrefix
        self.dataType = dataType
        baseFn = filePrefix + ('.' + str(max(1, elementDim)) if elementDim is not None else '') +\
                              ('.' + str(dataTypeDim) if dataTypeDim > 1 or elementDim is not None else '') + '.' + dataType
        self.fn = self.path + os.sep + baseFn
        
        self.shape = tuple([size] + \
                          ([max(1, elementDim)] if elementDim is not None else []) + \
                          ([dataTypeDim] if dataTypeDim > 1 else []))
        #self._removeFiles()
        
    def __del__(self):
        self._removeFiles()

    def _removeFiles(self):
        removeFile(self.fn)
    
class GEList:
    def __init__(self):
        self._startList = []
        self._endList = []
        self._strandList = []
        self._valList = []
        self._idList = []
        self._edgesList = []
        self._weightsList = []
        self._extraList = []

    def __iter__(self):
        self = copy(self)
        self._index = -1
        return self
    
    def next(self):
        self._index += 1
        if self._index >= len(self):
            raise StopIteration
        
        return GenomeElement(start = self._startList[self._index] if self._index<len(self._startList) else None,
                             end = self._endList[self._index] if self._index<len(self._endList) else None,
                             strand = self._strandList[self._index] if self._index<len(self._strandList) else None,
                             val = self._valList[self._index] if self._index<len(self._valList) else None,
                             id = self._idList[self._index] if self._index<len(self._idList) else None,
                             edges = self._edgesList[self._index] if self._index<len(self._edgesList) else None,
                             weights = self._weightsList[self._index] if self._index<len(self._weightsList) else None,
                             extra = self._extraList[self._index] if self._index<len(self._extraList) else None)

    def __len__(self):
        return max(len(self._startList), len(self._endList), len(self._strandList), len(self._valList), \
                   len(self._idList), len(self._edgesList), len(self._weightsList), len(self._extraList))
    

class TestOutputFile(TestCaseWithImprovedAsserts):
    def setUp(self):
        self.stderr = sys.stderr
        sys.stderr = open('/dev/null', 'w')
        
    def tearDown(self):
        sys.stderr = sys.stderr
        
    #def testOpenFileExists(self):
    #    s = Setup('start', 1, 'int32', 1, None)
    #    f = open(s.fn, 'w')
    #    f.close()
    #        
    #    self.assertRaises(IOError, OutputFile, s.path, s.filePrefix, 1)
    #    s._removeFiles()
    
    def _assertWriteElement(self, filePrefix, contents, dataType, dataTypeDim, maxNumEdges, maxStrLens, \
                            assertContents, assertDataType, assertDataTypeDim, assertElementDim):
    
        s = Setup(filePrefix, len(assertContents), assertDataType, assertDataTypeDim, assertElementDim)

        valDataType = dataType if filePrefix == 'val' else 'float64'
        valDim = dataTypeDim if filePrefix == 'val' else 1
        weightDataType = dataType if filePrefix == 'weights' else 'float64'
        weightDim = dataTypeDim if filePrefix == 'weights' else 1

        geList = GEList()
        memberName = '_' + filePrefix + 'List'
        if hasattr(geList, memberName):
            geList.__dict__[memberName] = contents
        else:
            geList._extraList = [{filePrefix: x} for x in contents]
        
        #print s.fn, s.path, s.filePrefix, len(geList), valDataType, valDim, weightDataType, weightDim, maxNumEdges, maxStrLens
        of = OutputFile(s.path, s.filePrefix, len(assertContents), valDataType, valDim, weightDataType, weightDim, maxNumEdges, maxStrLens)
        for ge in geList:
            of.writeElement(ge)
        of.close()
        
        self.assertTrue(os.path.exists(s.fn))
                
        fileContents = [el for el in memmap(s.fn, dtype=s.dataType, shape=s.shape, mode='r')]    
        self.assertListsOrDicts(assertContents, fileContents)
        return s
        
    def testWriteElement(self):
        self._assertWriteElement('start', \
                                 [1, 5, 7, 10], None, None, 0, {}, \
                                 [1, 5, 7, 10], 'int32', 1, None)
        
        self._assertWriteElement('end', \
                                 [2, 7, 8, 12], None, None, 0, {}, \
                                 [2, 7, 8, 12], 'int32', 1, None)
        
        self._assertWriteElement('strand', \
                                 [True, False, False, True], None, None, 0, {}, \
                                 [True, False, False, True], 'int8', 1, None)
        
        self._assertWriteElement('val', \
                                 [1.2, 2.3, -2.3, 3.5], 'float64', 1, 0, {}, \
                                 [1.2, 2.3, -2.3, 3.5], 'float64', 1, None)
        
        self._assertWriteElement('val', \
                                 [1, 2, -1, 3], 'int32', 1, 0, {}, \
                                 [1, 2, -1, 3], 'int32', 1, None)
        
        self._assertWriteElement('val', \
                                 ['aa','ab','c','acd'], 'S', 1, 0, {'val':3}, \
                                 ['aa','ab','c','acd'], 'S3', 1, None)
        
        self._assertWriteElement('val', \
                                 [['a','b'], ['a','c'], ['b','c'], ['c','d']], 'S1', 2, 0, {}, \
                                 [['a','b'], ['a','c'], ['b','c'], ['c','d']], 'S1', 2, None)
        
        self._assertWriteElement('id', \
                                 ['a01','a02','a03'], None, None, 0, {'id':3}, \
                                 ['a01','a02','a03'], 'S3', 1, None)
        
        self._assertWriteElement('edges', \
                                 [['a02'],['a03'],['a01']], None, None, 1, {'edges':3}, \
                                 [['a02'],['a03'],['a01']], 'S3', 1, 1)
        
        self._assertWriteElement('edges', \
                                 [['a02','a03'],['a03'],['a01','a02']], None, None, 2, {'edges':3}, \
                                 [['a02','a03'],['a03',''],['a01','a02']], 'S3', 1, 2)
        
        self._assertWriteElement('edges', \
                                 [[],[],[]], None, None, 0, {'edges':3}, \
                                 [[''],[''],['']], 'S3', 1, 1)
        
        self._assertWriteElement('weights', \
                                 [[1.2,2.1],[0.1],[0.8,-1.2]], 'float64', 1, 2, {}, \
                                 [[1.2,2.1],[0.1, nan],[0.8,-1.2]], 'float64', 1, 2)
        
        self._assertWriteElement('weights', \
                                 [ [['aa','ab'],['ab','ac']], [['aa','ac'],['','']], [['ab','c'],['ac','c']] ], 'S', 2, 2, {'weights':2}, \
                                 [ [['aa','ab'],['ab','ac']], [['aa','ac'],['','']], [['ab','c'],['ac','c']] ], 'S2', 2, 2)
        
        self._assertWriteElement('cat', \
                                 ['abc', 'cde', 'de'], None, None, 0, {'cat':3}, \
                                 ['abc', 'cde', 'de'], 'S3', 1, None)
    
    def testWriteElementPartial(self):
        setup = self._assertWriteElement('start', \
                                     [1, 5], None, None, 0, {}, \
                                     [1, 5], 'int32', 1, None)
        self._assertWriteElement('start', \
                                 [7, 10], None, None, 0, {}, \
                                 [1, 5, 7, 10], 'int32', 1, None)
        del setup
    
        setup = self._assertWriteElement('weights', \
                                 [ [['aa','ab'],['ab','ac']] ], 'S', 2, 2, {'weights':2}, \
                                 [ [['aa','ab'],['ab','ac']] ], 'S2', 2, 2)
        self._assertWriteElement('weights', \
                                 [ [['aa','ac'],['','']], [['ab','c'],['ac','c']] ], 'S', 2, 2, {'weights':2}, \
                                 [ [['aa','ab'],['ab','ac']], [['aa','ac'],['','']], [['ab','c'],['ac','c']] ], 'S2', 2, 2)
        del setup
    
    def _assertWrite(self, filePrefix, dataType, contents):
        s = Setup(filePrefix, len(contents), dataType, 1, None)

        of = OutputFile(s.path, s.filePrefix, len(contents))
        for i in contents:
            of.write(i)
        of.close()
        
        self.assertTrue(os.path.exists(s.fn))
        fileContents = [i for i in memmap(s.fn, dataType, mode='r')]
        self.assertListsOrDicts(contents, fileContents)
    
    def testWrite(self):
        self._assertWrite('leftIndex', 'int32', [0, 2, 5, 10])
        self._assertWrite('rightIndex', 'int32', [2, 5, 7, 12])
        
    def testLen(self):
        size = 123
        s = Setup('start', size, 'int32', 1, None)
        of = OutputFile(s.path, s.filePrefix, size)
        self.assertEqual(size, len(of))
    
    def runTest(self):
        self.testOpenClose()
    
if __name__ == "__main__":
    #TestOutputFile().debug()
    unittest.main()
    