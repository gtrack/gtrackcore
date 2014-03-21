import unittest
import os
import sys

import gtrackcore_memmap.preprocess.memmap.OutputDirectory

from gtrackcore_memmap.input.core.GenomeElement import GenomeElement
from gtrackcore_memmap.preprocess.memmap.OutputFile import OutputFile
from gtrackcore_memmap.preprocess.memmap.OutputIndexFilePair import OutputIndexFilePair

from gtrackcore_memmap.test.common.Asserts import TestCaseWithImprovedAsserts
from gtrackcore_memmap.test.common.FileUtils import removeDirectoryTree

class MyOutputFile:
    def __init__(self, path, prefix, size, valDataType, valDim, weightDataType, weightDim, maxNumEdges, maxStrLens):
        self.path = path
        self.prefix = prefix
        self.size = size
        self.valDataType = valDataType
        self.valDim = valDim
        self.weightDataType = weightDataType
        self.weightDim = weightDim
        self.maxNumEdges = maxNumEdges
        self.maxStrLens = maxStrLens
        
    def writeElement(self, genomeElement):
        self.ge = genomeElement

class MyOutputIndexFilePair(MyOutputFile):
    def __init__(self, path, chrSize, startFile, endFile):
        self.path = path
        self.chrSize = chrSize

class SetupDir:
    def __init__(self, path, prefixList):
        self.valDataType = 'int'
        self.valDim = 1
        self.weightDataType = 'float64'
        self.weightDim = 2
        self.maxNumEdges = 3
        self.maxStrLens = {'a':3}
        self.size = 100
        self.chrSize = 1000000
        from gtrackcore_memmap.preprocess.memmap.OutputDirectory import OutputDirectory
        self.od = OutputDirectory(path, prefixList, self.size, self.chrSize, self.valDataType, self.valDim, \
                                  self.weightDataType, self.weightDim, self.maxNumEdges, self.maxStrLens)
    
class TestOutputDirectory(TestCaseWithImprovedAsserts):
    def _removeDirTree(self):
        removeDirectoryTree(self.first_dir)
    
    def setUp(self):
        self.stderr = sys.stderr
        sys.stderr = open('/dev/null', 'w')

        gtrackcore_memmap.preprocess.memmap.OutputDirectory.OutputFile = MyOutputFile
        gtrackcore_memmap.preprocess.memmap.OutputDirectory.OutputIndexFilePair = MyOutputIndexFilePair
        self.path_base = os.path.dirname(os.tempnam())
        self.first_dir = self.path_base + os.sep +'test'
        self.path = os.sep.join([self.first_dir,'directory','structure'])
        self._removeDirTree()
        
    def tearDown(self):
        sys.stderr = sys.stderr

        gtrackcore_memmap.preprocess.memmap.OutputDirectory.OutputFile = OutputFile
        gtrackcore_memmap.preprocess.memmap.OutputDirectory.OutputIndexFilePair = OutputIndexFilePair
        self._removeDirTree()

    def _assertInit(self, prefixList, hasIndexFiles):
        s = SetupDir(self.path, prefixList)
        self.assertTrue(os.path.exists(self.path))
        #self.assertEqual(S_IRWXU|S_IRWXG|S_IROTH|S_IXOTH, S_IMODE(os.stat(self.path)[ST_MODE]))

        numFiles = len(prefixList)
        self.assertEqual(numFiles, len(s.od._files))
        
        if hasIndexFiles:
            self.assertTrue(s.od._indexFiles is not None)
        else:
            self.assertTrue(s.od._indexFiles is None)
        
        for prefix in prefixList:
            self.assertEqual(self.path, s.od._files[prefix].path)
            self.assertListsOrDicts(prefix, s.od._files[prefix].prefix)
            self.assertEqual(s.size, s.od._files[prefix].size)
            self.assertEqual(s.valDataType, s.od._files[prefix].valDataType)
            self.assertEqual(s.valDim, s.od._files[prefix].valDim)
            self.assertEqual(s.weightDataType, s.od._files[prefix].weightDataType)
            self.assertEqual(s.weightDim, s.od._files[prefix].weightDim)
            self.assertEqual(s.maxNumEdges, s.od._files[prefix].maxNumEdges)
            self.assertListsOrDicts(s.maxStrLens, s.od._files[prefix].maxStrLens)
            
        if hasIndexFiles:
            self.assertEqual(self.path, s.od._indexFiles.path)
            self.assertEqual(s.chrSize, s.od._indexFiles.chrSize)
            
    def testInit(self):
        self._assertInit(['val'], False)
        self._assertInit(['start'], True)
        self._assertInit(['end'], True)
        self._assertInit(['start', 'end', 'val', 'strand', 'id', 'edges', 'weights', 'cat'], True)
            
    def testWriteElement(self):
        s = SetupDir(self.path, ['start', 'end', 'val', 'strand', 'id', 'edges', 'weights', 'cat'])
        ge = GenomeElement()
        s.od.writeElement(ge)
        for f in s.od._files.values():
            self.assertEqual(ge, f.ge)
    
    def runTest(self):
        self.testWriteElement()
    
if __name__ == "__main__":
    #TestOutputDirectory().debug()
    unittest.main()
