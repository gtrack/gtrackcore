from collections import namedtuple
from copy import copy

import bbi
import numpy as np
from bx.bbi.bigwig_file import BigWigFile
import pyBigWig

from gtrackcore.input.core.GenomeElementSource import GenomeElementSource, BoundingRegionTuple
from input.core.GenomeElement import GenomeElement
from track.core.GenomeRegion import GenomeRegion


class BigWigGenomeElementSource(GenomeElementSource):
    _VERSION = '1.0'
    FILE_SUFFIXES = ['bw', 'bigwig']
    FILE_FORMAT_NAME = 'BigWig'

    _numHeaderLines = 0
    _isSliceSource = True
    _isSorted = True
    _inputIsOneIndexed = True
    _inputIsEndInclusive = True
    _addsStartElementToDenseIntervals = False

    Header = namedtuple('Header', ['start', 'end', 'step', 'span', 'stepType', 'numOfVals'])

    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)

    def __init__(self, *args, **kwArgs):
        GenomeElementSource.__init__(self, *args, **kwArgs)
        self._boundingRegionTuples = []
        self._chrIter = iter(bbi.chromsizes(self._fn).items())
        self._headers = iter([])
        self._currentChrom = None
        self._valuesArray = None
        self._locations = None
        self._lengths = None
        self._values = None
        self._bxpythonFile = BigWigFile(file=self._getFile())
        self._fixedStep = False
        self._span = 1
        self._step = None
        self._isPoints = None
        self._isFunction = False
        self._isStepFunction = False

    def __iter__(self):
        geIter = copy(self)
        geIter._chrIter = iter(bbi.chromsizes(self._fn).items())
        geIter._headers = iter([])
        geIter._boundingRegionTuples = []

        return geIter

    def _iter(self):
        return self

    def next(self):
        header = next(self._headers, None)
        if not header:
            self._currentChrom = next(self._chrIter, None)
            if not self._currentChrom:
                raise StopIteration
            self._headers = iter(self._getHeaderForChrom(self._currentChrom))
            header = next(self._headers, None)

            self._fixedStep = self._isFixedStep(header)
            if self._fixedStep:
                self._valuesArray = self._getValsForChrom(self._currentChrom)
                self._values, self._locations, self._lengths = self._getIntervals(self._valuesArray)
            else:
                self._valuesArray = self._getRawValsForChrom(self._currentChrom)
                self._values, self._locations, self._lengths = self._getIntervals(self._valuesArray)
                oob = np.where(np.isinf(self._values))[0]
                self._values = np.delete(self._values, oob)
                self._locations = np.delete(self._locations, oob)

                # print 'variable step'
                # print header
                # print 'values'
                # print self._values
                # print 'locations'
                # print self._locations

        self._span = header.span
        self._step = header.step
        self._isPoints = (self._span == 1)
        chrName = str(self._currentChrom[0])

        if self._fixedStep:
            br = self.createBoundingRegion(header, chrName)
            print br
            self._boundingRegionTuples.append(br)

            self._isStepFunction = (self._step == self._span and self._step > 1)
            self._isFunction = (self._step == self._span and self._step == 1)

            val = self._values[:header.numOfVals]
            self._values = self._values[header.numOfVals:]

            if self._isFunction:
                ge = GenomeElement(genome=self._genome, chr=chrName,  val=val)
                print ge

                return ge
            else:
                start = self.getFixedStepStartPositions(header)

        else:
            val = self._values[:header.numOfVals]
            self._values = self._values[header.numOfVals:]
            start = self._locations[:header.numOfVals]
            self._locations = self._locations[header.numOfVals:]
            if self._isBedGraph(header):
                br = self.createBoundingRegion(header, chrName)
                print br
                self._boundingRegionTuples.append(br)

        end = None
        if not self._isPoints:
            end = self.getEndPositions(header, start)
        if self._isStepFunction:
            val, end = self.handleStepFunction(val, start, end)
            start = None

        ge = GenomeElement(genome=self._genome, chr=chrName, start=start, end=end, val=val)
        print ge

        return ge

    def createBoundingRegion(self, header, chr):
        boundingRegion = GenomeRegion(genome=self._genome, chr=chr, start=header.start,
                                      end=header.end)
        br = BoundingRegionTuple(boundingRegion, header.numOfVals)

        return br

    def getFixedStepStartPositions(self, header):
        positions = [header.start]
        for i in range(header.numOfVals-1):
            positions.append(positions[-1] + header.step)

        return np.array(positions)

    def getEndPositions(self, header, startPositions):
        positions = []

        for pos in startPositions:
            positions.append(pos + header.span)

        return np.array(positions)

    def _shouldExpandBoundingRegion(self, chr, start):
        return (self._isFunction or self._isStepFunction) and \
                (self._chr == chr and self._getEnd(self._getFixedStepCurElStart()) == start)

    def _handleEndOfFile(self):
        pass

    def handleStepFunction(self, val, start, end):
        return val, end

    def _getFile(self):
        return open(self._fn, 'r')

    def getBoundingRegionTuples(self):
        return self._boundingRegionTuples

    def _isFixedStep(self, header):
        return header.stepType == 3

    def _isVariableStep(self, header):
        return header.stepType == 2

    def _isBedGraph(self, header):
        return header.stepType == 1

    # The following are currently not tested, but should still be implemented correctly. Can be
    # manually tested by wrapping this geSource in a GTrackComposer object and look at whether
    # these headers are set correctly.

    def getFixedLength(self):
        return self._span if self._fixedStep else 1

    def getFixedGapSize(self):
        return self._step - self._span if self._fixedStep else 0

    def hasNoOverlappingElements(self):
        return True if self._fixedGapSize else False

    def _getValsForChrom(self, chrom):
        vals = self._getRawValsForChrom(chrom)
        vals = vals[~np.isposinf(vals)]

        return vals

    def _getRawValsForChrom(self, chrom):
        vals = bbi.fetch(self._fn, str(chrom[0]), 0, chrom[1], missing=np.inf)
        vals[np.isnan(vals)] = np.NINF

        return vals

    def _getHeaderForChrom(self, chrom):
        headers = self._bxpythonFile.get_headers(chrom[0], 0, chrom[1])
        headersNamed = [self.Header(*h) for h in headers]

        return headersNamed

    def _getIntervals(self, v):
        # usage: value, location, lengths = _getIntervals(v)
        # Get one-off shifted slices and then compare element-wise, to give
        # us a mask of start and start positions for each island.
        # Also, get the corresponding indices.
        mask = np.concatenate(([True], v[1:] != v[:-1], [True]))
        loc0 = np.flatnonzero(mask)

        # Get the start locations
        loc = loc0[:-1]

        # The values would be input array indexe by the start locations.
        # The lengths woul be the differentiation between start and stop indices.
        values = v[loc]
        values[np.isneginf(values)] = np.nan

        return values, loc, np.diff(loc0)


class BigWigGenomeElementSourceForPreproc(BigWigGenomeElementSource):
    _addsStartElementToDenseIntervals = True

    def handleStepFunction(self, val, start, end):
        val = np.insert(val, 0, np.nan)
        end = np.insert(end, 0, start[0])

        return val, end

    def createBoundingRegion(self, header, chrName):
        boundingRegion = GenomeRegion(genome=self._genome, chr=chrName, start=header.start,
                                      end=header.end)
        br = BoundingRegionTuple(boundingRegion, header.numOfVals + 1)

        return br
