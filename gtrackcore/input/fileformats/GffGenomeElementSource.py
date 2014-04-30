import numpy
from urllib import unquote

from gtrackcore.input.core.GenomeElement import GenomeElement
from gtrackcore.input.core.GenomeElementSource import GenomeElementSource
from gtrackcore.util.CustomExceptions import InvalidFormatError

class GffGenomeElementSource(GenomeElementSource):
    _VERSION = '1.2'
    FILE_SUFFIXES = ['gff', 'gff3']
    FILE_FORMAT_NAME = 'GFF'
    _numHeaderLines = 0

    _inputIsOneIndexed = True
    _inputIsEndInclusive = True

    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)

    def _next(self, line):
        if line.startswith('##FASTA'):
            raise StopIteration

        if len(line)>0 and line[0]=='#':
            return None

        origCols = line.split('\t')
        cols = [unquote(x) for x in origCols]

        if len(cols) != 9:
            raise InvalidFormatError("Error: GFF files must contain 9 tab-separated columns")

        ge = GenomeElement(self._genome)
        ge.chr = self._checkValidChr(cols[0])
        ge.source = cols[1]
        ge.type = cols[2]
        ge.start = self._checkValidStart(ge.chr, int(cols[3]) - 1)
        ge.end =  self._checkValidEnd(ge.chr, int(cols[4]), start=ge.start)
        ge.val = numpy.float(self._handleNan(cols[5]))
        ge.strand = self._getStrandFromString(cols[6])
        ge.phase = cols[7]
        ge.attributes = cols[8]

        for attr in origCols[8].split(';'):
            attrSplitted = attr.split('=')
            if len(attrSplitted) == 2:
                key, val = attrSplitted
                if key.lower() == 'id':
                    ge.id = unquote(val)
                elif key.lower() == 'name':
                    ge.name = unquote(val)

        return ge

    @classmethod
    def _getStrandFromString(cls, val):
        if val == '?':
            return BINARY_MISSING_VAL
        else:
            return GenomeElementSource._getStrandFromString(val)
