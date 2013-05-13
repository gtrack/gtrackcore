import os

from track5.input.core.GenomeElementSource import GenomeElementSource, BoundingRegionTuple
from track5.track.core.GenomeRegion import GenomeRegion
from track5.util.CustomExceptions import InvalidFormatError

class FastaGenomeElementSource(GenomeElementSource):
    _VERSION = '1.1'
    FILE_SUFFIXES = ['fasta', 'fas', 'fa']
    FILE_FORMAT_NAME = 'FASTA'
    
    _numHeaderLines = 0

    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)
    
    def __init__(self, *args, **kwArgs):
        GenomeElementSource.__init__(self, *args, **kwArgs)
        self._boundingRegionTuples = []
        
        if self._getFile().read(1) != '>':
            raise InvalidFormatError('FASTA file does not start with the ">" character.')
    
    def _iter(self):
        self._elCount = 0
        self._boundingRegionTuples = []
        self._genomeElement.chr = None
        return self
        
    def next(self):
        while True:
            bp = self._file.read(1)

            if bp == '>':
                self._appendBoundingRegionTuple()
                self._elCount = 0
                line = self._file.readline().rstrip()
                self._genomeElement.chr = self._checkValidChr(line.split()[0])

            elif bp == '':
                self._appendBoundingRegionTuple()
                raise StopIteration
                
            elif bp not in '\r\n':
                self._elCount += 1
                self._genomeElement.val = bp
                return self._genomeElement
    
    def _appendBoundingRegionTuple(self):
        if self._genomeElement.chr is not None:
            brRegion = GenomeRegion(self._genome, self._genomeElement.chr, 0, self._elCount)
            self._boundingRegionTuples.append(BoundingRegionTuple(brRegion, self._elCount))

    def getValDataType(self):
        return 'S1'

    def getPrefixList(self):
        return ['val']
        
    def getBoundingRegionTuples(self):
        return self._boundingRegionTuples