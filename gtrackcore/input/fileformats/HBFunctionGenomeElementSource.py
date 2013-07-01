import os
import numpy

from gtrackcore.input.core.GenomeElementSource import GenomeElementSource, BoundingRegionTuple
from gtrackcore.track.core.GenomeRegion import GenomeRegion

class HBFunctionGenomeElementSource(GenomeElementSource):
    _VERSION = '1.2'
    FILE_SUFFIXES = ['hbfunction']
    FILE_FORMAT_NAME = 'HB function'
    _numHeaderLines = 0
    _hasOrigFile = False

    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)
    
    def __init__(self, *args, **kwArgs):
        GenomeElementSource.__init__(self, *args, **kwArgs)
        self._returnedOneElement = False
        
    def next(self):
        if self._returnedOneElement:
            raise StopIteration
        
        self._genomeElement.chr = 'chr21'
        self._genomeElement.val = 0.0
        self._returnedOneElement = True
        return self._genomeElement
        
    def getValDataType(self):
        return 'float64'

    def getPrefixList(self):
        return ['val']
        
    def getBoundingRegionTuples(self):
        return [BoundingRegionTuple(GenomeRegion(genome='TestGenome', chr='chr21', start=0, end=1), 1)]
