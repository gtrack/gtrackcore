
# cython: infer_types=True
# cython: profile=True
import numpy
import pyximport; pyximport.install(setup_args={"include_dirs":numpy.get_include()},
                                    reload_support=True, language_level=2)

from gtrackcore.input.core.GenomeElementSource import GenomeElementSource
from gtrackcore.input.core.CythonGenomeElementSource import CythonGenomeElementSource
from gtrackcore.input.core.CythonGenomeElementSourceExt import CythonGenomeElementSourceExt

from gtrackcore.input.core.CythonGenomeElementExt import CythonGenomeElementExt
from gtrackcore.util.CustomExceptions import InvalidFormatError

class CythonBedGenomeElementSource(CythonGenomeElementSource):
    BED_EXTRA_COLUMNS = ['thickstart', 'thickend', 'itemrgb', 'blockcount', 'blocksizes', 'blockstarts']
    _VERSION = '1.2'
    FILE_SUFFIXES = ['bed']
    FILE_FORMAT_NAME = 'BED'
    _numHeaderLines = 0

    MIN_NUM_COLS = 3
    MAX_NUM_COLS = 12


#    def __new__(cls, *args, **kwArgs):
#        return object.__new__(cls)

    def __init__(self, fn, geClass, *args, **kwArgs):
        CythonGenomeElementSource.__init__(self, fn, *args, **kwArgs)
        f = open(fn)
        possibleHeader = f.readline()
        if possibleHeader.startswith('track'):
            self._numHeaderLines = 1
        self._numCols = None
        self._geClass = geClass

    def _next(self, str line):
        cdef list cols
        if line.startswith('#'):
            return

        ge = self._geClass(self._genome)
        cols = line.split('\t')

        if self._numCols is not None:
            if len(cols) != self._numCols:
                raise InvalidFormatError('Error: BED files must have the same number of columns in each data line.')
        else:
            self._numCols = len(cols)

        if self._numCols < self.MIN_NUM_COLS or self._numCols > self.MAX_NUM_COLS:
            raise InvalidFormatError('Error: BED file must contain between %s and %s columns.' % (self.MIN_NUM_COLS, self.MAX_NUM_COLS))

        ge.chr = self._checkValidChr(cols[0])
        ge.start = self._checkValidStart(ge.chr, int(cols[1]))

        self._parseEnd( ge, self._checkValidEnd(ge.chr, int(cols[2]), start=ge.start))
        self._parseName( ge, cols )
        self._parseVal( ge, cols )

        if self._numCols >= 6:
            ge.strand = self._getStrandFromString(cols[5])

        for i,extraCol in enumerate(self.BED_EXTRA_COLUMNS):
            if self._numCols >= i+7:
                setattr(ge, extraCol, cols[i+6])

        return ge

    def _parseEnd(self, ge, int end):
        ge.end = end

    def _parseName(self, ge, cols):
        if self._numCols >= 4:
            ge.name = cols[3]

    def _parseVal(self, ge, cols):
        if self._numCols >= 5:
            if cols[4] in ['-', '.']:
                val = 0
            else:
                val = int(cols[4])

            if val < 0 or val > 1000:
                raise InvalidFormatError("Error: BED score column must be an integer between 0 and 1000: %s. Perhaps you instead " + \
                                         "should use the file formats 'valued.bed' or 'gtrack'?")
            ge.val = val

    def getValDataType(self):
        return 'int32'

# class PointBedGenomeElementSource(CythonBedGenomeElementSource):
#     FILE_SUFFIXES = ['point.bed']
#     FILE_FORMAT_NAME = 'Point BED'
#
#     def _parseEnd(self, ge, end):
#         if end != ge.start + 1:
#             raise InvalidFormatError('Error: point BED files can only have segments of length 1')
#
# class BedValuedGenomeElementSource(CythonBedGenomeElementSource):
#     _VERSION = '1.1'
#     FILE_SUFFIXES = ['valued.bed', 'marked.bed']
#     FILE_FORMAT_NAME = 'Valued BED'
#
#     MIN_NUM_COLS = 5
#
#     def _parseVal(self, ge, cols):
#         ge.val = numpy.float(self._handleNan(cols[4]))
#
#     def getValDataType(self):
#         return 'float64'
#
# class BedCategoryGenomeElementSource(CythonBedGenomeElementSource):
#     _VERSION = '1.5'
#     FILE_SUFFIXES = ['category.bed']
#     FILE_FORMAT_NAME = 'Category BED'
#
#     MIN_NUM_COLS = 4
#
#     def _parseVal(self, ge, cols):
#         if self._numCols >= 5:
#             ge.score = cols[4]
#
#         ge.val = cols[3]
#
#     def _parseName(self, ge, cols):
#         pass
#
#     def getValDataType(self):
#         return 'S'
