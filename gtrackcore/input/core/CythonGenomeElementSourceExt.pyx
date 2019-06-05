# cython: profile=True
# cython: infer_types=True

import os
from cStringIO import StringIO
from copy import copy

from gtrackcore.core.LogSetup import logException
from gtrackcore.input.core.GenomeElement import GenomeElement
from gtrackcore.metadata.GenomeInfo import GenomeInfo
from gtrackcore.util.CommonConstants import BINARY_MISSING_VAL
from gtrackcore.util.CommonFunctions import getFileSuffix
from gtrackcore.util.CustomExceptions import NotSupportedError, InvalidFormatError, \
    InvalidFormatWarning, Warning


cdef class CythonGenomeElementSourceExt(object):
    cdef str _VERSION
    cdef list FILE_SUFFIXES
    cdef str FILE_FORMAT_NAME

    cdef bint _hasOrigFile
    cdef bint _isSliceSource
    cdef bint _addsStartElementToDenseIntervals
    cdef bint _isSorted
    cdef bint _hasCircularElements
    cdef int _fixedLength
    cdef int _fixedGapSize
    cdef bint _hasNoOverlappingElements
    cdef bint _hasUndirectedEdges
    cdef bint _inputIsOneIndexed
    cdef bint _inputIsEndInclusive

    cdef public str _genome
    cdef object _genomeElement
    cdef str _trackName
    cdef bint external
    cdef list _prefixList
    cdef bint _printWarnings
    cdef str _strToUseInsteadOfFn
    cdef str _lastWarning

#    def __new__(cls, fn, genome=None, trackName=None, suffix=None, forPreProcessor=False, *args, **kwArgs):
#        geSourceCls = getGenomeElementSourceClass(fn, suffix=suffix, forPreProcessor=forPreProcessor)
#        return geSourceCls.__new__(geSourceCls, fn, genome=genome, trackName=trackName, *args, **kwArgs)

    def __init__(self, fn, genome=None, trackName=None, external=False, printWarnings=True, strToUseInsteadOfFn='', *args, **kwArgs): #, depth=0
        self._fn = fn
        self._genome = genome
        self._genomeElement = GenomeElement(genome)
        self._trackName = trackName
        self._external = external
        self._prefixList = None
        self._printWarnings = printWarnings
        self._strToUseInsteadOfFn = strToUseInsteadOfFn
        self._lastWarning = None

    def initDefaultVals(self):
        self._VERSION = '0.0'
        self.FILE_SUFFIXES = []
        self.FILE_FORMAT_NAME = ''

        self._hasOrigFile = True
        self._isSliceSource = False
        self._addsStartElementToDenseIntervals = True
        self._isSorted = False
        self._hasCircularElements = False
        self._fixedLength = 1
        self._fixedGapSize = 0
        self._hasNoOverlappingElements = False
        self._hasUndirectedEdges = False
        self._inputIsOneIndexed = False
        self. _inputIsEndInclusive = False

    def getFileFormatName(self):
        return self.FILE_FORMAT_NAME

    def getDefaultFileSuffix(self):
        return self.FILE_SUFFIXES[0]

    def getTrackName(self):
        return self._trackName

    def getGenome(self):
        return self._genome

    def getFileName(self):
        return self._fn

    def getFileSuffix(self):
        return getFileSuffix(self._fn) if self._fn is not None else None

    def isExternal(self):
        return self._external

    def hasOrigFile(self):
        return self._hasOrigFile

    def isSliceSource(self):
        return self._isSliceSource

    def addsStartElementToDenseIntervals(self):
        return self._addsStartElementToDenseIntervals

    def hasCircularElements(self):
        return self._hasCircularElements

    def getFixedLength(self):
        return self._fixedLength

    def getFixedGapSize(self):
        return self._fixedGapSize

    def isSorted(self):
        return self._isSorted

    def hasNoOverlappingElements(self):
        return self._hasNoOverlappingElements

    def hasUndirectedEdges(self):
        return self._hasUndirectedEdges

    def inputIsOneIndexed(self):
        return self._inputIsOneIndexed

    def inputIsEndInclusive(self):
        return self._inputIsEndInclusive

    def anyWarnings(self):
        return self._lastWarning is not None

    def getLastWarning(self):
        return self._lastWarning

    def next(self):
        cdef str line, lineStripped
        cdef object ge
        while True:
            line = self._file.readline()
            lineStripped = line.rstrip('\r\n')

            try:
                if line == '':#End of file
                    if not self._handledEof:
                        self._handleEndOfFile()
                        self._checkBoundingRegionOverlap()
                        self._handledEof = True
                    if not self._anyPendingElements():
                        raise StopIteration
                elif lineStripped == '': #Blank line
                    self._handleBlankLine()
                    continue

                ge = self._next(lineStripped)
                if ge is None:
                    continue

                self._genomeElement = ge
                return self._genomeElement

            except Warning, e:
                if self._printWarnings:
                    if not hasattr(self, '_numWarningLines'):
                        self._numWarningLines = 0
                    self._numWarningLines +=1
                    if self._numWarningLines > 5:
                        if self._numWarningLines == 6:
                            print os.linesep + '5 warnings shown, skipping rest of warnings for file...'
                    else:
                        print os.linesep + "Warning in line\n---------------\n%s\n\nInternal representation: %s\n\n-> %s. Skipping line.\n---" % (lineStripped, repr(line), str(e))

                self._lastWarning = str(e)
                continue

            except StopIteration:
                raise

            except Exception, e:
                print os.linesep + "Error in line\n-------------\n%s\n\nInternal representation: %s\n\n-> %s\n---" % (lineStripped, repr(line), str(e))
                raise

    def _anyPendingElements(self):
        return False

    def _handleEndOfFile(self):
        pass

    def _handleBlankLine(self):
        pass

    def getHeaders(self):
        return None

    def _readHeaders(self, file):
        self.headers = [file.readline() for i in xrange(self._numHeaderLines)]

    def _getFileNoHeaders(self):
        file = self._getFile()
        self._readHeaders(file)
        return file

    def _getFile(self):
        if self._strToUseInsteadOfFn != '':
            memFile = StringIO()
            memFile.write(self._strToUseInsteadOfFn)
            memFile.seek(0)
            return memFile
        return open(self._fn, 'U', -1)

    def __iter__(self):
        geIter = copy(self)
        geIter._file = geIter._getFileNoHeaders()
        geIter._handledEof = False
        self._lastWarning = None
        return geIter._iter()

    def _iter(self):
        return self

    def _checkValidChr(self, chr):
        if self.genome and not GenomeInfo.isValidChr(self.genome, chr):
            raise InvalidFormatWarning('Chromosome incorrectly specified: ' + chr)
        return chr

    def _checkValidStart(self, chr, start):
        if start < 0:
            raise InvalidFormatError('Error: start position is negative: %s' % start)

        if self.genome and \
            GenomeInfo.isValidChr(self.genome, chr) and \
                start > GenomeInfo.getChrLen(self.genome, chr):
                    raise InvalidFormatError('Error: start position is larger than the size of chromosome "%s" (%s > %s)' % \
                                             (chr, start, GenomeInfo.getChrLen(self.genome, chr)))
        return start

    def _checkValidEnd(self, chr, end, start=None):
        if end < 0:
            raise InvalidFormatError('Error: end position is negative: %s' % end)

        if self.genome and \
            GenomeInfo.isValidChr(self.genome, chr) and \
                end-1 > GenomeInfo.getChrLen(self.genome, chr):
                    raise InvalidFormatError('Error: end position is larger than the size of chromosome "%s" (%s > %s)' % \
                                             (chr, end-1, GenomeInfo.getChrLen(self.genome, chr)))
        if start is not None and end <= start:
            if not start == end == 1:
                raise InvalidFormatError('Error: end position (end-exclusive) is smaller than or equal to start position: %d <= %d' % (end, start))

        return end

    def _checkBoundingRegionOverlap(self):
        if self.hasBoundingRegionTuples():
            for i,brTuple in enumerate(sorted(self.getBoundingRegionTuples())):
                br = brTuple.region

                if i > 0:
                    self._checkBoundingRegionSortedPair(lastBoundingRegion, br)
                lastBoundingRegion = br

    def _checkBoundingRegionSortedPair(self, lastBoundingRegion, br):
        if br.start is not None and br.end is not None:
            if lastBoundingRegion.overlaps(br):
                raise InvalidFormatError("Error: bounding regions '%s' and '%s' overlap." % (lastBoundingRegion, br))

    @classmethod
    def _handleNan(cls, str):
        if str.lower() in ['.', 'na', 'nan', 'n/a', 'none']:
            return 'nan'
        return str

    @classmethod
    def _getStrandFromString(cls, val):
        if val == '+':
            return True
        elif val == '-':
            return False
        elif val == '.':
            return BINARY_MISSING_VAL
        #val == ''?
        else:
            raise InvalidFormatError("Error: strand must be either '+', '-' or '.'. Value: %s" % val)

    def hasBoundingRegionTuples(self):
        return len(self.getBoundingRegionTuples()) > 0

    def getBoundingRegionTuples(self):
        return []

    def parseFirstDataLine(self):
        try:
            geIter = self.__iter__()
            geIter._printWarnings = False
            ge = geIter.next()
        except StopIteration, e:
            #logException(e)
            lastWarningMsg = ' Last warning when parsing file: %s' % geIter.getLastWarning() \
                             if geIter.anyWarnings() else ''
            raise Warning('File has no valid data lines.%s' % lastWarningMsg)
        except Exception, e:
            logException(e)
            raise
        return ge, geIter

    def getPrefixList(self):
        if self._prefixList is None:
            ge, geIter = self.parseFirstDataLine()
            self._prefixList = [prefix for prefix in ['start', 'end', 'val', 'strand', 'id', 'edges', 'weights'] if ge.__dict__.get(prefix) is not None]
            if ge.extra is not None:
                self._prefixList += [x for x in ge.orderedExtraKeys]
        return self._prefixList

    def getPrintWarnings(self):
        return self._printWarnings

    def setPrintWarnings(self, printWarnings):
        self._printWarnings = printWarnings

    def getValDataType(self):
        return 'float64'

    def getValDim(self):
        return 1

    def getEdgeWeightDataType(self):
        return 'float64'

    def getEdgeWeightDim(self):
        return 1

    def getVersion(self):
        return self._VERSION

    def getId(self):
        return None

    genome = property(getGenome)

def getGenomeElementSourceClass(fn, suffix=None, forPreProcessor=False):
    for geSourceCls in getAllGenomeElementSourceClasses(forPreProcessor):
        for clsSuffix in geSourceCls.FILE_SUFFIXES:
            if (fn.endswith('.' + clsSuffix) if suffix is None else clsSuffix == suffix):
                return geSourceCls
    else:
        fileSuffix = os.path.splitext(fn)[1] if suffix is None else suffix
        raise NotSupportedError('File type ' + fileSuffix  + ' not supported.')


def getAllGenomeElementSourceClasses(forPreProcessor):
    from gtrackcore.input.fileformats.BedGenomeElementSource import PointBedGenomeElementSource, BedValuedGenomeElementSource, \
                                                                BedCategoryGenomeElementSource, BedGenomeElementSource
    from gtrackcore.input.fileformats.GffGenomeElementSource import GffCategoryGenomeElementSource, GffGenomeElementSource
    from gtrackcore.input.fileformats.FastaGenomeElementSource import FastaGenomeElementSource
    from gtrackcore.input.fileformats.HBFunctionGenomeElementSource import HBFunctionGenomeElementSource
    from gtrackcore.input.fileformats.BedGraphGenomeElementSource import BedGraphTargetControlGenomeElementSource, BedGraphGenomeElementSource
    from gtrackcore.input.fileformats.MicroarrayGenomeElementSource import MicroarrayGenomeElementSource
    from gtrackcore.input.fileformats.BigBedGenomeElementSource import BigBedGenomeElementSource

    from input.fileformats.VcfGenomeElementSource import VcfGenomeElementSource
    allGESourceClasses = [PointBedGenomeElementSource, BedValuedGenomeElementSource, BedCategoryGenomeElementSource, \
                          BedGenomeElementSource, GffCategoryGenomeElementSource, GffGenomeElementSource, \
                          FastaGenomeElementSource, HBFunctionGenomeElementSource, \
                          BedGraphTargetControlGenomeElementSource, BedGraphGenomeElementSource, MicroarrayGenomeElementSource,
                          BigBedGenomeElementSource, VcfGenomeElementSource]

    if forPreProcessor:
        from gtrackcore.input.fileformats.WigGenomeElementSource import HbWigGenomeElementSource
        from gtrackcore.input.fileformats.GtrackGenomeElementSource import HbGzipGtrackGenomeElementSource, HbGtrackGenomeElementSource
        from gtrackcore.input.fileformats.BigWigGenomeElementSource import BigWigGenomeElementSourceForPreproc
        allGESourceClasses += [HbWigGenomeElementSource, HbGzipGtrackGenomeElementSource,
                               HbGtrackGenomeElementSource, BigWigGenomeElementSourceForPreproc]
    else:
        from gtrackcore.input.fileformats.WigGenomeElementSource import WigGenomeElementSource
        from gtrackcore.input.fileformats.GtrackGenomeElementSource import GzipGtrackGenomeElementSource, GtrackGenomeElementSource
        from gtrackcore.input.fileformats.BigWigGenomeElementSource import BigWigGenomeElementSource


        allGESourceClasses += [WigGenomeElementSource, GzipGtrackGenomeElementSource,
                               GtrackGenomeElementSource, BigWigGenomeElementSource]

    return allGESourceClasses
