from copy import copy

from track5.input.core.GenomeElementSource import GenomeElementSource
from track5.input.core.GenomeElement import GenomeElement

class FunctionSliceGenomeElementSource(GenomeElementSource):
    _hasOrigFile = False
    _isSliceSource = True
    
    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)
        
    def __init__(self, genome, trackName, region, valSlice, valDataType='float64'):
        GenomeElementSource.__init__(self, None, genome=genome, trackName=trackName)
        self._returnedOneElement = False
        self._valSlice = valSlice
        self._region = region
        self._valDataType = valDataType

    def __iter__(self):
        return copy(self)
        
    def next(self):
        if self._returnedOneElement:
            raise StopIteration
            
        self._returnedOneElement = True
        return GenomeElement(genome=self._genome, chr=self._region.chr, val=self._valSlice)
    
    def getNumElements(self):
        return 1
        
    def getPrefixList(self):
        return ['val']
    
    def getValDataType(self):
        return self._valDataType