from copy import copy

import numpy as np
import pyBigWig

from gtrackcore.input.core.GenomeElementSource import GenomeElementSource
from input.core.GenomeElement import GenomeElement


class BigBedGenomeElementSource(GenomeElementSource):
    _VERSION = '1.0'
    FILE_SUFFIXES = ['bb', 'bigbed']
    FILE_FORMAT_NAME = 'BigBed'

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
        tupleVals = [(x[0], x[1]) for x in entries]
        intervals = np.array(tupleVals, dtype=np.dtype([('start', 'int'), ('end', 'int')]))
        intervals.dtype.names =['start', 'end']

        ge = GenomeElement(genome=self._genome, chr=self._currentChrom[0],
                           start=intervals['start'], end=intervals['end'])

        numOfCols = len(entries[0])
        if numOfCols >= 2 and entries[0][2]:
            extraCols = entries[0][2].split('\t')
            autoSql = self._bigBedFile.SQL()
            if autoSql:
                from plastid.readers.autosql import AutoSqlDeclaration
                autoSqlParser = AutoSqlDeclaration(self._bigBedFile.SQL())
                colNames = autoSqlParser.field_formatters.keys()
                colNames = colNames[3:]
            else:
                colNames = self.BED_EXTRA_COLUMNS[:len(extraCols)]

            strVals = [x[2] for x in entries]
            values = np.genfromtxt(strVals, dtype=None, names=colNames, delimiter='\t')
            #print values

            if 'score' in colNames:
                ge.val = values['score']
                colNames.remove('score')
            for colName in colNames:
                setattr(ge, colName, values[colName])

        print ge

        return ge
