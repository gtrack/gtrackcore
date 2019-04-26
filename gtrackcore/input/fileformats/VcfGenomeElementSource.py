from copy import copy

from gtrackcore.input.core.GenomeElementSource import GenomeElementSource
import vcf
import numpy as np

from input.core.GenomeElement import GenomeElement


class VcfGenomeElementSource(GenomeElementSource):
    _VERSION = '1.0'
    FILE_SUFFIXES = ['vcf']
    FILE_FORMAT_NAME = 'VCF'

    vcfStandardColumns = ['ID', 'REF', 'QUAL', 'FILTER', 'FORMAT']

    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)

    def __init__(self, *args, **kwArgs):
        GenomeElementSource.__init__(self, *args, **kwArgs)
        self._boundingRegionTuples = []
        self._vcfFile = open(self._fn, 'r')
        self._vcfReader = vcf.Reader(self._vcfFile)
        self._altMaxLength = 0
        self._isPoints = False
        self._initFileInfo()
        self._samplesCols = self._vcfReader.samples

    def _initFileInfo(self):
        refMaxLength = 0
        initReader = vcf.Reader(open(self._fn, 'r'))
        for record in initReader:
            if len(record.ALT) > self._altMaxLength:
                self._altMaxLength = len(record.ALT)

            if record.REF and len(record.REF) > refMaxLength:
                refMaxLength = len(record.REF)

        if refMaxLength == 1:
            self._isPoints = True

    def __iter__(self):
        self._boundingRegionTuples = []
        self._values = iter([])
        geIter = copy(self)

        return geIter

    def _iter(self):
        return self

    def next(self):
        record = next(self._vcfReader, None)
        if not record:
            self._vcfFile.close()
            raise StopIteration

        print record

        val = np.zeros(self._altMaxLength, dtype=str)

        ge = GenomeElement(genome=self._genome, chr=record.CHROM, start=record.POS)
        if not self._isPoints:
            if record.REF:
                ge.end = ge.start + len(record.REF)
            else:
                ge.end = ge.start + 1

        val[:len(record.ALT)] = record.ALT

        ge.val = val

        for colName in self.vcfStandardColumns:
            attrVal = getattr(record, colName)
            if attrVal:
                setattr(ge, colName, str(attrVal))

        for col in record.INFO:
            if isinstance(record.INFO[col], list):
                val = ';'.join(map(str, record.INFO[col]))
            else:
                val = str(record.INFO[col])
            setattr(ge, col, val)

        for sample in self._samplesCols:
            item = record.genotype(sample)
            for colName in record.FORMAT.split(':'):
                val = getattr(item.data, colName)
                if isinstance(val, list):
                    val = ';'.join(map(str, val))
                else:
                    val = str(val)
                setattr(ge, colName, val)

        return ge


