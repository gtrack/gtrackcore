
# cython: profile=True
# cython: infer_types=True

from collections import OrderedDict

import numpy

import pyximport; pyximport.install(setup_args={"include_dirs":numpy.get_include()},
                                    reload_support=True, language_level=2)
from input.core.CythonGenomeElement import CythonGenomeElement
from input.core.CythonGenomeElementSource import CythonGenomeElementSource


class CythonVcfGenomeElementSource(CythonGenomeElementSource):
    _VERSION = '1.0'
    FILE_SUFFIXES = ['vcf']
    FILE_FORMAT_NAME = 'VCF'
    _addsStartElementToDenseIntervals = False

    def __init__(self, *args, **kwArgs):
        CythonGenomeElementSource.__init__(self, *args, **kwArgs)
        self._boundingRegionTuples = []
        self._numHeaderLines = 0
        # altMaxLength is used to determine size of the val list, it has to always be at least two
        # otherwise the track format is wrongly determined as 'category' insetad of 'category_vector'
        self._altMaxLength = 2
        self._isPoints = False
        self._headersDict = OrderedDict()
        self._colNames = 0
        self._refMaxLength = 0
        self._initFileInfo()

    def _initFileInfo(self):
        with open(self._fn, 'r') as vcfFile:
            for line in vcfFile:
                line = line.strip()
                if line.startswith('##'):
                    # header line
                    self._numHeaderLines += 1
                    headerId, headerVal = line[2:].split('=', 1)
                    if headerId in self._headersDict:
                        self._headersDict[headerId].append(headerVal)
                    else:
                        self._headersDict[headerId] = [headerVal]
                elif line.startswith('#'):
                    # column specification
                    self._numHeaderLines += 1
                    self._colNames = line[1:].split('\t')
                else:
                    # data lines
                    self._initDataInfo(line)

        if self._refMaxLength == 1:
            self._isPoints = True

    def _iter(self):
        return self

    def _next(self, line):
        CHROM, POS, ID, REF, ALT = range(5)
        cols = line.strip().split('\t')
        if len(cols) == 1:
            cols = line.strip().split()
        ge = CythonGenomeElement(genome=self._genome, chr=cols[CHROM], start=int(cols[POS]))
        if not self._isPoints:
            if cols[REF] != '.':
                ge.end = ge.start + len(cols[REF])
            else:
                ge.end = ge.start + 1

        val = [''] * self._altMaxLength

        if cols[ALT] != '.':
            altVals = cols[ALT].split(',')
            val[:len(altVals)] = altVals

        ge.val = val

        setattr(ge, 'ID', cols[ID])
        setattr(ge, 'REF', cols[REF])

        for i, colName in enumerate(self._colNames[5:], 5):
            setattr(ge, colName, cols[i])

        return ge

    def getValDataType(self):
        return 'S'

    def getValDim(self):
        return self._altMaxLength

    def getHeaders(self):
        return self._headersDict

    def _initDataInfo(self, line):
        CHROM, POS, ID, REF, ALT = range(5)
        cols = line.split('\t')
        if len(cols) == 1:
            cols = line.split()

        altItems = cols[ALT].split(',')
        if len(altItems) > self._altMaxLength:
            self._altMaxLength = len(altItems)

        if len(cols[REF]) > self._refMaxLength:
            self._refMaxLength = len(cols[REF])

