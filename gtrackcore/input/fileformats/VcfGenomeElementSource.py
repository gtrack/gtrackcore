from copy import copy

from gtrackcore.input.core.GenomeElementSource import GenomeElementSource
import vcf

from input.core.GenomeElement import GenomeElement


class VcfGenomeElementSource(GenomeElementSource):
    _VERSION = '1.0'
    FILE_SUFFIXES = ['vcf']
    FILE_FORMAT_NAME = 'VCF'

    _numHeaderLines = 0

    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)

    def __init__(self, *args, **kwArgs):
        GenomeElementSource.__init__(self, *args, **kwArgs)
        self._boundingRegionTuples = []
        self._vcfFile = open(self._fn)
        self._vcfReader = vcf.Reader(self._vcfFile)

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
        print record.INFO

        ge = GenomeElement(genome=self._genome, chr=record.CHROM, start=record.POS)
        if record.INFO.END:
            ge.end = record.INFO.END


        return ge




