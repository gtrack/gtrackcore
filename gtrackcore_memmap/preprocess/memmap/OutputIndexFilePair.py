import math
import numpy as np

from gtrackcore_memmap.preprocess.memmap.OutputFile import OutputFile
from gtrackcore_memmap.util.CompBinManager import CompBinManager

class OutputIndexFilePair(object):
    def __init__(self, path, chrSize, startFile, endFile):
        self._path = path
        self._chrSize = chrSize
        self._startFile = startFile
        self._endFile = endFile
    
    def writeIndexes(self):
        numIndexElements = int(math.ceil(1.0 * self._chrSize / CompBinManager.getIndexBinSize()))
        self._leftIndexFile = OutputFile(self._path, 'leftIndex', numIndexElements, allowAppend=False)
        self._rightIndexFile = OutputFile(self._path, 'rightIndex', numIndexElements, allowAppend=False)
        
        if self._startFile:
            lefts = self._startFile.getContents()
        else:
            lefts = np.r_[0, self._endFile.getContents()[:-1]]
        
        if self._endFile:
            rights = self._endFile.getContents()
            if not self._startFile:
                rights = rights[1:]
        else:
            rights = self._startFile.getContents() + 1
            
        bin_i = 0
        i = 0
        for i, right in enumerate(rights):
            while right > (bin_i) * CompBinManager.getIndexBinSize():
                self._leftIndexFile.write(i)
                bin_i += 1

        bin_j = 0
        j = 0
        for j, left in enumerate(lefts):
            while left >= (bin_j+1) * CompBinManager.getIndexBinSize():
                self._rightIndexFile.write(j)
                bin_j += 1
                
        self._fillRestOfIndexFile(bin_i, i+1, self._leftIndexFile)
        self._fillRestOfIndexFile(bin_j, j+1, self._rightIndexFile)
        
    def _fillRestOfIndexFile(self, numFilled, fillValue, indexFile):
        for i in xrange( len(indexFile) - numFilled ):
            indexFile.write(fillValue)
    
    def close(self):
        self._leftIndexFile.close()
        self._rightIndexFile.close()
        