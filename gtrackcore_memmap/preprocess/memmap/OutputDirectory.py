import os
import numpy as np

from collections import OrderedDict

from gtrackcore_memmap.preprocess.memmap.OutputFile import OutputFile
from gtrackcore_memmap.preprocess.memmap.OutputIndexFilePair import OutputIndexFilePair

class OutputDirectory(object):
    def __init__(self, path, prefixList, fileArraySize, chrSize, valDataType='float64', valDim=1, \
                 weightDataType='float64', weightDim=1, maxNumEdges=0, maxStrLens={}, elementsAreSorted=False):
        self._files = OrderedDict()
        if not os.path.exists(path):
            os.makedirs(path)
            
        for prefix in prefixList:
            self._files[prefix] = OutputFile(path, prefix, fileArraySize, valDataType, valDim, weightDataType, weightDim, maxNumEdges, maxStrLens)
        
        if 'start' in self._files or 'end' in self._files:
            self._indexFiles = OutputIndexFilePair(path, chrSize, self._files.get('start'), self._files.get('end'))
        else:
            self._indexFiles = None
            
        self._elementsAreSorted = elementsAreSorted
        
    def writeElement(self, genomeElement):
        for f in self._files.values():
            f.writeElement(genomeElement)
        
    def writeRawSlice(self, genomeElement):
        for f in self._files.values():
            f.writeRawSlice(genomeElement)
    
    def _sortFiles(self):
        startFile = self._files.get('start')
        endFile = self._files.get('end')
        
        if startFile and endFile:
            sortOrder = np.lexsort((endFile.getContents(), startFile.getContents()))
            startFile.sort(sortOrder)
            endFile.sort(sortOrder)
        elif startFile:
            sortOrder = startFile.sort()
        elif endFile:
            sortOrder = endFile.sort()
        else:
            sortOrder = None
            
        if sortOrder is not None:
            for prefix in self._files.keys():
                if prefix not in ['start', 'end']:
                    self._files[prefix].sort(sortOrder)
        
    def close(self):
        if not self._elementsAreSorted:
            self._sortFiles()
        
        if self._indexFiles:
            self._indexFiles.writeIndexes()
            self._indexFiles.close()

        for f in self._files.values():
            f.close()
