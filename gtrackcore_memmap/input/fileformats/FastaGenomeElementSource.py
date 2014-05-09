import os
import numpy as np

from gtrackcore_memmap.input.core.GenomeElementSource import GenomeElementSource, BoundingRegionTuple
from gtrackcore_memmap.track.core.GenomeRegion import GenomeRegion
from gtrackcore_memmap.input.core.GenomeElement import GenomeElement
from gtrackcore_memmap.util.CustomExceptions import InvalidFormatError


class FastaGenomeElementSource(GenomeElementSource):
    _VERSION = '1.1'
    FILE_SUFFIXES = ['fasta', 'fas', 'fa']
    FILE_FORMAT_NAME = 'FASTA'

    _numHeaderLines = 0
    _isSliceSource = True

    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)

    def __init__(self, *args, **kwArgs):
        GenomeElementSource.__init__(self, *args, **kwArgs)
        self._boundingRegionTuples = []
        self._chr = None

    def _iter(self):
        self._elCount = 0
        self._boundingRegionTuples = []
        self._genomeElement.chr = None
        return self

    def _next(self, line):
        if line.startswith('>'):
            self._appendBoundingRegionTuple()
            self._elCount = 0
            self._chr = self._checkValidChr(line[1:].split()[0])
        else:
            if self._chr is None:
                raise InvalidFormatError('FASTA file does not start with the ">" character.')

            self._elCount += len(line)
            ge = GenomeElement(self._genome, self._chr)
            ge.val = np.fromstring(line, dtype='S1')
            return ge

    def _handleEndOfFile(self):
        self._appendBoundingRegionTuple()

    #def next(self):
    #    while True:
    #        bp = self._file.read(1)
    #
    #        if bp == '>':
    #            self._appendBoundingRegionTuple()
    #            self._elCount = 0
    #            line = self._file.readline().rstrip()
    #            self._genomeElement.chr = self._checkValidChr(line.split()[0])
    #
    #        elif bp == '':
    #            self._appendBoundingRegionTuple()
    #            raise StopIteration
    #
    #        elif bp not in '\r\n':
    #            self._elCount += 1
    #            self._genomeElement.val = bp
    #            return self._genomeElement

    def _appendBoundingRegionTuple(self):
        #if self._genomeElement.chr is not None:
        #    brRegion = GenomeRegion(self._genome, self._genomeElement.chr, 0, self._elCount)
        if self._chr is not None:
            brRegion = GenomeRegion(self._genome, self._chr, 0, self._elCount)
            self._boundingRegionTuples.append(BoundingRegionTuple(brRegion, self._elCount))

    def getValDataType(self):
        return 'S1'

    def getPrefixList(self):
        return ['val']

    def getBoundingRegionTuples(self):
        return self._boundingRegionTuples
