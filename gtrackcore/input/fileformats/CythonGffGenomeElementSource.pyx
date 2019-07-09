# cython: infer_types=True
# cython: profile=True


import numpy
import percentcoding

import pyximport;pyximport.install(setup_args={"include_dirs":numpy.get_include()},
                                    reload_support=True, language_level=2)
from input.core.CythonGenomeElement import CythonGenomeElement
from input.core.CythonGenomeElementSource import CythonGenomeElementSource

from gtrackcore.input.core.GenomeElementSource import GenomeElementSource
from gtrackcore.util.CustomExceptions import InvalidFormatError

from util.CommonConstants import BINARY_MISSING_VAL

class CythonGffGenomeElementSource(CythonGenomeElementSource):
    _VERSION = '1.2'
    FILE_SUFFIXES = ['gff', 'gff3']
    FILE_FORMAT_NAME = 'GFF'
    _numHeaderLines = 0

    _inputIsOneIndexed = True
    _inputIsEndInclusive = True

    def _next(self, line):
        if line.startswith('##FASTA'):
            raise StopIteration

        if len(line)>0 and line[0]=='#':
            return None

        origCols = line.split('\t')
        cols = [percentcoding.unquote(x) for x in origCols]

        if len(cols) != 9:
            raise InvalidFormatError("Error: GFF files must contain 9 tab-separated columns")

        ge = CythonGenomeElement(self._genome)
        ge.chr = self._checkValidChr(cols[0])
        ge.source = cols[1]

        self._parseThirdCol(ge, cols[2])

        ge.start = self._checkValidStart(ge.chr, int(cols[3]) - 1)
        ge.end =  self._checkValidEnd(ge.chr, int(cols[4]), start=ge.start)

        self._parseSixthCol(ge, cols[5])

        ge.strand = self._getStrandFromString(cols[6])
        ge.phase = cols[7]
        ge.attributes = cols[8]

        for attr in origCols[8].split(';'):
            attrSplitted = attr.split('=')
            if len(attrSplitted) == 2:
                key, val = attrSplitted
                if key.lower() == 'id':
                    ge.id = percentcoding.unquote(val)
                elif key.lower() == 'name':
                    ge.name = percentcoding.unquote(val)

        return ge

    def _parseThirdCol(self, ge, contents):
        ge.type = contents

    def _parseSixthCol(self, ge, contents):
        ge.val = numpy.float(self._handleNan(contents))

    @classmethod
    def _getStrandFromString(cls, val):
        if val == '?':
            return BINARY_MISSING_VAL
        else:
            return GenomeElementSource._getStrandFromString(val)

class GffCategoryGenomeElementSource(CythonGffGenomeElementSource):
    FILE_SUFFIXES = ['category.gff', 'category.gff3']
    FILE_FORMAT_NAME = 'Category GFF'

    def _parseThirdCol(self, ge, contents):
        ge.val = contents

    def _parseSixthCol(self, ge, contents):
        ge.score = self._handleNan(contents)

    def getValDataType(self):
        return 'S'
