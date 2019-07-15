from collections import namedtuple
from copy import copy

import numpy as np
import pyBigWig
from bx.bbi.bigwig_file import BigWigFile

from gtrackcore.input.core.GenomeElementSource import GenomeElementSource, BoundingRegionTuple
from input.core.GenomeElement import GenomeElement
from track.core.GenomeRegion import GenomeRegion
from util.CustomExceptions import InvalidFormatError


class BigWigGenomeElementSource(GenomeElementSource):
    _VERSION = '1.0'
    FILE_SUFFIXES = ['bw', 'bigwig']
    FILE_FORMAT_NAME = 'BigWig'

    _isSliceSource = True
    _isSorted = True
    _inputIsOneIndexed = True
    _inputIsEndInclusive = True
    _addsStartElementToDenseIntervals = False

    # stepType values: 1(BedGraph), 2(variableStep), 3(fixedStep)
    Header = namedtuple('Header', ['start', 'end', 'step', 'span', 'stepType', 'numOfVals'])

    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)

    def __init__(self, *args, **kwArgs):
        GenomeElementSource.__init__(self, *args, **kwArgs)
        self._file = open(self._fn, 'r')
        self._bxpythonFile = BigWigFile(file=self._file)
        self._bw = pyBigWig.open(self._fn)

        self._fixedStep = False
        self._span = 1
        self._step = None
        self._isPoints = None
        self._isFunction = False
        self._isStepFunction = False

        self._chrs = sorted(self._bw.chroms().items())
        self._headers = iter([])
        self._boundingRegionTuples = []
        self._currentChrom = None
        self._chrName = None
        self._initFileVariables()

    def _initFileVariables(self):
        header = self._getHeaderForChrom(self._chrs[0])[0]
        self._span = header.span
        self._step = header.step
        self._fixedStep = self._isFixedStep(header)
        self._isPoints = (self._span == 1)
        if self._fixedStep:
            self._isStepFunction = (self._step == self._span and self._step > 1)
            self._isFunction = (self._step == self._span and self._step == 1)
        else:
            self._isStepFunction = False
            self._isFunction = False

    def __iter__(self):
        geIter = copy(self)
        geIter._chrIter = iter(self._chrs)
        geIter._headers = iter([])
        geIter._boundingRegionTuples = []
        self._file = open(self._fn, 'r')
        self._bxpythonFile = BigWigFile(file=self._file)
        self._bw = pyBigWig.open(self._fn)

        return geIter

    def _iter(self):
        return self

    def next(self):
        header = next(self._headers, None)
        if not header:
            self._currentChrom = next(self._chrIter, None)
            if not self._currentChrom:
                self._closeFiles()
                raise StopIteration

            self._chrName = str(self._currentChrom[0])
            self._headers = iter(self._getHeaderForChrom(self._currentChrom))
            header = next(self._headers, None)

        self._checkHeader(header)
        if self._fixedStep:
            br = self.createBoundingRegion(header)
            self._boundingRegionTuples.append(br)

            if self._isFunction:
                values = self._bw.values(self._chrName, header.start, header.start + header.numOfVals, numpy=True)
                values = np.float64(values)
                ge = GenomeElement(genome=self._genome, chr=self._chrName, val=values)
                # print ge

                return ge

        start, end, val = self._parseBigWigFile(header)
        ge = GenomeElement(genome=self._genome, chr=self._chrName, start=start, end=end, val=val)
        #print ge

        return ge

    def _checkHeader(self, header):
        if self._fixedStep and (header.span != self._span):
            raise InvalidFormatError(
                'The span value is not allowed to change within the same file: %s != %s.' % (
                self._span, header.span))
        if header.step != self._step:
            raise InvalidFormatError(
                'The step value is not allowed to change within the same file: %s != %s.' % (
                self._step, header.step))

        if self._isFixedStep(header) != self._fixedStep:
            raise InvalidFormatError(
                'fixedStep and variableStep/bedGraph formats are not allowed to mix within the same file.')

    def _parseBigWigFile(self, header):
        intervals = list(self._bw.intervals(self._chrName, header.start, header.end))
        if len(intervals) != header.numOfVals:
            raise InvalidFormatError(
                'Mismatch between number of values in header and number of values got: %s != %s.' % (
                    len(intervals), header.numOfVals))

        intervalsArray = np.array(intervals, dtype=np.dtype(
            [('start', 'int32'), ('end', 'int32'), ('val', 'float64')]))

        val = intervalsArray['val']
        start = intervalsArray['start']
        end = None
        if not self._isPoints:
            end = intervalsArray['end']
        if self._isStepFunction:
            val, end = self._handleStepFunction(val, start, end)
            start = None

        return start, end, val

    def _closeFiles(self):
        self._file.close()
        self._bw.close()

    def createBoundingRegion(self, header):
        boundingRegion = GenomeRegion(genome=self._genome, chr=self._chrName, start=header.start,
                                      end=header.end)
        br = BoundingRegionTuple(boundingRegion, header.numOfVals)

        return br

    def _shouldExpandBoundingRegion(self, chr, start):
        return (self._isFunction or self._isStepFunction) and \
                (self._chr == chr and self._getEnd(self._getFixedStepCurElStart()) == start)

    def _handleEndOfFile(self):
        pass

    def _handleStepFunction(self, val, start, end):
        return val, end

    def getBoundingRegionTuples(self):
        return self._boundingRegionTuples

    def _isFixedStep(self, header):
        return header.stepType == 3

    # The following are currently not tested, but should still be implemented correctly. Can be
    # manually tested by wrapping this geSource in a GTrackComposer object and look at whether
    # these headers are set correctly.

    def getFixedLength(self):
        return self._span if self._fixedStep else 1

    def getFixedGapSize(self):
        return self._step - self._span if self._fixedStep else 0

    def hasNoOverlappingElements(self):
        return True if self._fixedGapSize else False

    def _getHeaderForChrom(self, chrom):
        headers = self._bxpythonFile.get_headers(chrom[0], 0, chrom[1])
        headersNamed = [self.Header(*h) for h in headers]

        return headersNamed


class BigWigGenomeElementSourceForPreproc(BigWigGenomeElementSource):
    _addsStartElementToDenseIntervals = True

    def _handleStepFunction(self, val, start, end):
        val = np.insert(val, 0, np.nan)
        end = np.insert(end, 0, start[0])

        return val, end

    def createBoundingRegion(self, header):
        boundingRegion = GenomeRegion(genome=self._genome, chr=self._chrName, start=header.start,
                                      end=header.end)
        if self._isStepFunction:
            br = BoundingRegionTuple(boundingRegion, header.numOfVals + 1)
        else:
            br = BoundingRegionTuple(boundingRegion, header.numOfVals)

        return br
