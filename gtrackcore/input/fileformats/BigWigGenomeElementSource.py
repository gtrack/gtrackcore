from gtrackcore.input.core.GenomeElementSource import GenomeElementSource

import numpy as np
import bbi
from bx.bbi.bigwig_file import BigWigFile

from input.core.GenomeElement import GenomeElement
from collections import namedtuple


class BigWigGenomeElementSource(GenomeElementSource):
    _VERSION = '1.0'
    FILE_SUFFIXES = ['bw', 'bigwig']
    FILE_FORMAT_NAME = 'BigWig'

    _numHeaderLines = 0
    _isSliceSource = True
    _isSorted = True
    _inputIsOneIndexed = True
    _inputIsEndInclusive = True

    Header = namedtuple('Header', ['start', 'end', 'step', 'span', 'stepType', 'numOfVals'])

    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)

    def __init__(self, *args, **kwArgs):
        GenomeElementSource.__init__(self, *args, **kwArgs)
        self._boundingRegionTuples = []
        self._chrIter = iter(bbi.chromsizes(self._fn).items())
        self._currentChrom = None
        self._valuesArray = None
        self._locations = None
        self._lengths = None
        self._values = None
        bxpythonTmp = open(self._fn, 'rb')
        self._bxpythonFile = BigWigFile(file=bxpythonTmp)
        self._headers = iter([])


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

            if self._isFixedStep(header):
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

        fixedStep = self._isFixedStep(header)
        chr = self._currentChrom[0]
        span = header.span
        step = header.step
        start = np.array([header.start])

        isPoints = span == 1
        isStepFunction = None

        if fixedStep:

            isStepFunction = (step == span and step > 1)
            isFunction = (step == span and step == 1)
            if isFunction:
                self._genomeElement.chr = chr

            # if not self._shouldExpandBoundingRegion(chr, start):
            #     if chr is not None:  # self._chr is still the chromosome of the previous decl. line
            #         self._appendBoundingRegionTuple()

                if isStepFunction:
                    returnGE = GenomeElement(genome=self._genome, chr=chr, end=start, \
                                             val=np.nan, isBlankElement=True)

                    print returnGE

                    return returnGE

            val = self._values[:header.numOfVals]
            self._values = self._values[header.numOfVals:]

            if isFunction:
                ge = GenomeElement(genome=self._genome, chr=chr,  val=val)

                print ge

                return ge
            else:
                start = self.getFixedStepStartPositions(header)

        else:
            val = self._values[:header.numOfVals]
            self._values = self._values[header.numOfVals:]
            start = self._locations[:header.numOfVals]
            self._locations = self._locations[header.numOfVals:]

        end = None
        if not isPoints:
            end = self.getEndPositions(header, start)
        if isStepFunction:
            start = None

        ge = GenomeElement(genome=self._genome, chr=chr, start=start, end=end, val=val)
        print ge

        return ge

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
        return False

    def getFixedGapSize(self):
        return False

    def hasNoOverlappingElements(self):
        return False

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

    def _isDense(self, v):
        if np.inf in v:
            return False

        return True

    def getStepType(self, stepNum):
        if stepNum == 1:
            return 'bedGraph'
        elif stepNum == 2:
            return 'variableStep'
        elif stepNum == 3:
            return 'fixedStep'



class BigWigGenomeElementSourceForPreproc(BigWigGenomeElementSource):
    _addsStartElementToDenseIntervals = False
