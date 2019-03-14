from copy import copy

import bbi
import numpy as np
#from bx.bbi.bigwig_file import BigWigFile
import pyBigWig

from gtrackcore.input.core.GenomeElementSource import GenomeElementSource, BoundingRegionTuple
from input.core.GenomeElement import GenomeElement
from track.core.GenomeRegion import GenomeRegion


class BigBedGenomeElementSource(GenomeElementSource):
    _VERSION = '1.0'
    FILE_SUFFIXES = ['bb', 'bigbed']
    FILE_FORMAT_NAME = 'BigBed'

    MIN_NUM_COLS = 3
    MAX_NUM_COLS = 12

    BED_COLUMNS = ['chrom', 'start', 'end', 'name', 'score', 'strand', 'thickstart', 'thickend',
                   'itemrgb', 'blockcount', 'blocksizes', 'blockstarts']
    BED_EXTRA_COLUMNS = ['name', 'score', 'strand', 'thickstart', 'thickend', 'itemrgb', 'blockcount', 'blocksizes',
                         'blockstarts']

    DTYPES = ['str', 'int', 'str', 'int', 'int', 'str', 'int', 'str', 'str']

    COL_TYPES = zip(BED_EXTRA_COLUMNS, DTYPES)

    _numHeaderLines = 0
    _isSliceSource = True
    _isSorted = True
    _inputIsOneIndexed = True
    _inputIsEndInclusive = True
    _addsStartElementToDenseIntervals = False

    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)

    def __init__(self, *args, **kwArgs):
        GenomeElementSource.__init__(self, *args, **kwArgs)
        self._boundingRegionTuples = []
        self._bigBedFile = pyBigWig.open(self._fn)
        self._chrIter = iter(self._bigBedFile.chroms().items())
        self._currentChrom = None
        self._values = iter([])

    def __iter__(self):
        geIter = copy(self)
        geIter._chrIter = iter(self._bigBedFile.chroms().items())
        geIter._boundingRegionTuples = []
        self._values = iter([])

        return geIter

    def _iter(self):
        return self

    def next(self):
        self._currentChrom = next(self._chrIter, None)
        if not self._currentChrom:
            raise StopIteration

        entries = self._bigBedFile.entries(str(self._currentChrom[0]), 0, self._currentChrom[1])

        print self._bigBedFile.SQL()

        from plastid.readers.autosql import AutoSqlDeclaration
        autoSqlParser = AutoSqlDeclaration(self._bigBedFile.SQL())

        print autoSqlParser.field_formatters


        # there are more values than just start and end
        tupleVals = [(x[0], x[1]) for x in entries]
        intervals = np.array(tupleVals, dtype=np.dtype([('start', 'int'), ('end', 'int')]))
        intervals.dtype.names =['start', 'end']
        numOfCols = len(entries[0])
        if numOfCols >= 2:
            cols = entries[0][2].split('\t')
            dataTypes = self.COL_TYPES[:len(cols)]
            strVals = [x[2] for x in entries]
            #print dataTypes
            values = np.genfromtxt(strVals, dtype=None, names=self.BED_EXTRA_COLUMNS[:len(cols)], delimiter='\t')
            print values
            #print values.dtype

        ge = GenomeElement(genome=self._genome, chr=self._currentChrom[0], start=intervals['start'], end=intervals['end'])




        print ge

        return ge

    def createBoundingRegion(self, header, chr):
        boundingRegion = GenomeRegion(genome=self._genome, chr=chr, start=header.start,
                                      end=header.end)
        br = BoundingRegionTuple(boundingRegion, header.numOfVals)

        return br
