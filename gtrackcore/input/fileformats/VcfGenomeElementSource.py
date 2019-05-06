import numpy as np

from gtrackcore.input.core.GenomeElementSource import GenomeElementSource
from input.core.GenomeElement import GenomeElement


class VcfGenomeElementSource(GenomeElementSource):
    _VERSION = '1.0'
    FILE_SUFFIXES = ['vcf']
    FILE_FORMAT_NAME = 'VCF'
    _addsStartElementToDenseIntervals = False

    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)

    def __init__(self, *args, **kwArgs):
        GenomeElementSource.__init__(self, *args, **kwArgs)
        self._boundingRegionTuples = []
        self._numHeaderLines = 0
        self._altMaxLength = 0
        self._isPoints = False
        self._altItemMaxLenght = 0
        self._headerLines = []
        self._colNames = 0
        self._initFileInfo()

    def _initFileInfo(self):
        CHROM, POS, ID, REF, ALT = range(5)
        refMaxLength = 0
        with open(self._fn, 'r') as vcfFile:
            for line in vcfFile:
                line = line.strip()
                if line.startswith('##'):
                    # header line
                    self._numHeaderLines += 1
                    self._headerLines.append(line)
                elif line.startswith('#'):
                    # column specification
                    self._numHeaderLines += 1
                    self._colNames = line[1:].split('\t')
                else:
                    # data lines
                    cols = line.split('\t')
                    if len(cols) == 1:
                        cols = line.split()

                    altItems = cols[ALT].split(',')
                    if len(altItems) > self._altMaxLength:
                        self._altMaxLength = len(altItems)
                    for altItem in altItems:
                        if len(altItem) > self._altItemMaxLenght:
                            self._altItemMaxLenght = len(altItem)

                    if len(cols[REF]) > refMaxLength:
                        refMaxLength = len(cols[REF])

        if refMaxLength == 1:
            self._isPoints = True

    def _iter(self):
        return self

    def _next(self, line):
        CHROM, POS, ID, REF, ALT = range(5)
        cols = line.strip().split('\t')
        if len(cols) == 1:
            cols = line.strip().split()
        ge = GenomeElement(genome=self._genome, chr=cols[CHROM], start=int(cols[POS]))
        if not self._isPoints:
            if cols[REF] != '.':
                ge.end = ge.start + len(cols[REF])
            else:
                ge.end = ge.start + 1

        val = np.zeros(self._altMaxLength, dtype='S' + str(self._altItemMaxLenght))

        if cols[ALT] != '.':
            val[:len(cols[ALT])] = cols[ALT]

        ge.val = val

        setattr(ge, 'ID', cols[ID])
        setattr(ge, 'REF', cols[REF])

        for i, colName in enumerate(self._colNames[5:], 5):
            setattr(ge, colName, cols[i])

        print ge
        return ge

    def getValDataType(self):
        return 'S'

    def getValDim(self):
        return self._altMaxLength

