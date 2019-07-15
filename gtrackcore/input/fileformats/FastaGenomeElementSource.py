import numpy as np
import pyximport; pyximport.install(setup_args={"include_dirs":np.get_include()},
                                    reload_support=True, language_level=2)

from gtrackcore.input.core.GenomeElementSource import BoundingRegionTuple
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.util.CustomExceptions import InvalidFormatError
from input.core.CythonGenomeElement import CythonGenomeElement
from input.core.CythonGenomeElementSource import CythonGenomeElementSource


class FastaGenomeElementSource(CythonGenomeElementSource):
    _VERSION = '1.1'
    FILE_SUFFIXES = ['fasta', 'fas', 'fa']
    FILE_FORMAT_NAME = 'FASTA'

    _isSliceSource = True

    def __init__(self, *args, **kwArgs):
        CythonGenomeElementSource.__init__(self, *args, **kwArgs)
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
            ge = CythonGenomeElement(self._genome, self._chr)
            ge.val = np.fromstring(line, dtype='S1')
            return ge

    def _handleEndOfFile(self):
        self._appendBoundingRegionTuple()


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
