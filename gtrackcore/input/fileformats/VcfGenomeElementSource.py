from copy import copy

import numpy as np
import vcf

from gtrackcore.input.core.GenomeElementSource import GenomeElementSource
from input.core.GenomeElement import GenomeElement


class VcfGenomeElementSource(GenomeElementSource):
    _VERSION = '1.0'
    FILE_SUFFIXES = ['vcf']
    FILE_FORMAT_NAME = 'VCF'

    vcfStandardColumns = ['ID', 'REF', 'QUAL', 'FILTER']

    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)

    def __init__(self, *args, **kwArgs):
        GenomeElementSource.__init__(self, *args, **kwArgs)
        self._boundingRegionTuples = []
        self._vcfFile = open(self._fn, 'r')
        self._vcfReader = vcf.Reader(self._vcfFile)
        self._altMaxLength = 0
        self._isPoints = False
        self._samplesCols = self._vcfReader.samples
        self._altItemMaxLenght = 0
        self._initFileInfo()

    def _initFileInfo(self):
        refMaxLength = 0
        altItemMaxLength = 0
        initReader = vcf.Reader(open(self._fn, 'r'))
        for record in initReader:
            if len(record.ALT) > self._altMaxLength:
                self._altMaxLength = len(record.ALT)

            for altItem in record.ALT:
                if altItem and len(str(altItem)) > altItemMaxLength:
                    altItemMaxLength = len(str(altItem))

            if record.REF and len(record.REF) > refMaxLength:
                refMaxLength = len(record.REF)

        if refMaxLength == 1:
            self._isPoints = True
        self._altItemMaxLenght = altItemMaxLength

    def __iter__(self):
        self._boundingRegionTuples = []
        self._vcfFile = open(self._fn, 'r')
        self._vcfReader = vcf.Reader(self._vcfFile)
        self._samplesCols = self._vcfReader.samples
        geIter = copy(self)

        return geIter

    def _iter(self):
        return self

    def next(self):
        record = next(self._vcfReader, None)
        if not record:
            self._vcfFile.close()
            raise StopIteration

        ge = GenomeElement(genome=self._genome, chr=record.CHROM, start=record.POS)
        if not self._isPoints:
            if record.REF:
                ge.end = ge.start + len(record.REF)
            else:
                ge.end = ge.start + 1

        val = np.zeros(self._altMaxLength, dtype='S' + str(self._altItemMaxLenght))

        #if ALT is missing, record.ALT will be [None] so check for it here
        if record.ALT and record.ALT[0]:
            val[:len(record.ALT)] = record.ALT

        ge.val = val

        for colName in self.vcfStandardColumns:
            attrVal = getattr(record, colName)
            if attrVal:
                if isinstance(attrVal, list):
                    setattr(ge, colName, ';'.join(attrVal))
                else:
                    setattr(ge, colName, str(attrVal))
            else:
                if colName == 'FILTER' and isinstance(attrVal, list):
                    setattr(ge, colName, 'PASS')
                else:
                    setattr(ge, colName, '')

        infoVals = []
        for colName in self._vcfReader.infos:
            if colName in record.INFO:
                strVal = self._getStrValue(record.INFO[colName])
                if strVal == 'True':
                    infoVals.append(colName)
                else:
                    infoVals.append(colName + '=' + strVal)

        if infoVals:
            setattr(ge, 'INFO', ';'.join(infoVals))
        else:
            setattr(ge, 'INFO', '')

        if self._samplesCols:
            setattr(ge, 'FORMAT', record.FORMAT)

            for sample in self._samplesCols:
                item = record.genotype(sample)
                vals = []
                for colName in record.FORMAT.split(':'):
                    val = getattr(item.data, colName)
                    if val is None:
                        vals.append('.')
                    else:
                        strVal = self._getStrValue(val)
                        vals.append(strVal)

                setattr(ge, item.sample, ':'.join(vals))

        print ge
        return ge

    def _getStrValue(self, val):
        if isinstance(val, list):
            valItems = []
            for item in val:
                if item is None:
                    item = '.'
                else:
                    item = str(item)
                valItems.append(item)
            strVal = ','.join(valItems)
        else:
            strVal = str(val)

        return strVal

    def getValDataType(self):
        return 'S'

    def getValDim(self):
        return self._altMaxLength


