import re
import numpy

from gtrackcore_compressed.input.core.GenomeElement import GenomeElement
from gtrackcore_compressed.input.core.GenomeElementSource import GenomeElementSource, BoundingRegionTuple
from gtrackcore_compressed.track.core.GenomeRegion import GenomeRegion
from gtrackcore_compressed.util.CustomExceptions import InvalidFormatError

class WigGenomeElementSource(GenomeElementSource):
    _VERSION = '2.0'
    FILE_SUFFIXES = ['wig']
    FILE_FORMAT_NAME = 'WIG'

    _inputIsOneIndexed = True
    _inputIsEndInclusive = True
    
    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)
    
    def __init__(self, fn, *args, **kwArgs):
        GenomeElementSource.__init__(self, fn, *args, **kwArgs)
        
        self._initAll()
        self._handleTrackDefinitionLineIfPresent(self._getFile().readline())
        self._parseFirstDeclarationLine()
            
    def _initAll(self):
        self._boundingRegionTuples = []
        self._fixedStep = None
        self._isPoints = None
        self._isFunction = False
        self._isStepFunction = False
        
        self._chr = None
        self._start = None
        self._span = None
        self._step = None

    def _handleTrackDefinitionLineIfPresent(self, firstLine):
        if firstLine.startswith('track'):
            if firstLine.startswith('track type=wiggle_0'):
                self._numHeaderLines = 1
            else:
                raise InvalidFormatError('The wiggle track definition line must (if present) start with: track type=wiggle_0')
        else:
            self._numHeaderLines = 0

    def _parseFirstDeclarationLine(self):
        for line in self._getFileNoHeaders():
            line = line.strip()
            if self._isDeclarationLine(line):
                self._parseDeclarationLine(line)
                break
        
    def _isDeclarationLine(self, line):
        return self._isFixedStepLine(line) or self._isVariableStepLine(line)
        
    def _isFixedStepLine(self, line):
        return line.startswith('fixedStep')
  
    def _isVariableStepLine(self, line):
        return line.startswith('variableStep')
        
    def _parseDeclarationLine(self, line):
        returnGE = None
        
        chr, start, step, span = self._getDeclarationLineAttrValues(line)
        
        self._fixedStep = self._checkFixedStep(line, start, step)
        chr = self._handleChr(chr)
        self._span = self._handleSpan(span)
        
        self._isPoints = self._span == 1
        
        if self._fixedStep:
            start = self._handleStart(chr, start)
            self._step = self._handleStep(step)
            
            self._isStepFunction = (self._step == self._span and self._step > 1)
            self._isFunction = (self._step == self._span and self._step == 1)
            if self._isFunction:
                self._genomeElement.chr = chr
            
            if not self._shouldExpandBoundingRegion(chr, start):
                if self._chr is not None: #self._chr is still the chromosome of the previous decl. line
                    self._appendBoundingRegionTuple()
                
                self._start = start
                self._curElCountInBoundingRegion = 0
                
                if self._isStepFunction:
                    returnGE = GenomeElement(genome=self._genome, chr=chr, end=self._start, \
                                             val=numpy.nan, isBlankElement=True)
        
        self._chr = chr
        
        return returnGE
        
    def _getDeclarationLineAttrValues(self, line):
        headerDict = dict( [ pair.split('=') for pair in re.split('\s+', line.strip())[1:] ] )
        return [headerDict.get(a) for a in ['chrom','start','step','span']]
        
    def _checkFixedStep(self, line, start, step):
        fixedStep = self._isFixedStepLine(line)
        
        if self._fixedStep is not None and self._fixedStep != fixedStep:
            raise InvalidFormatError('WIG fixedStep and variableStep declaration lines are not allowed mix within the same file.')
        
        if fixedStep:
            if start is None:
                raise InvalidFormatError('WIG fixedStep requires start values in the declaration line.')
        else:
            if start is not None or step is not None:
                raise InvalidFormatError('WIG variableStep may not have start and step values in the declaration line.')
        
        return fixedStep
        
    def _handleChr(self, chr):
        if chr == None:
            raise InvalidFormatError('WIG declaration line requires the specification of a chromosome.')
        return chr
            
    def _handleSpan(self, span):
        span = int(span) if span is not None else 1
        if span < 1:
            raise InvalidFormatError('The span value must be positive: %s < 1.' % span)
        if self._fixedStep and self._span is not None and span != self._span:
            raise InvalidFormatError('The span value is not allowed to change within the same WIG fixedStep file: %s != %s.' % (self._span, span))
        return span
        
    def _handleStart(self, chr, start):
        return self._checkValidStart(chr, int(start)-1)
    
    def _handleStep(self, step):
        step = int(step) if step is not None else 1
        if step < 1:
            raise InvalidFormatError('The step value must be positive: %s < 1.' % step)
        if self._step is not None and step != self._step:
            raise InvalidFormatError('The step value is not allowed to change within the same WIG file: %s != %s.' % (self._step, step))
        return step
        
    def _shouldExpandBoundingRegion(self, chr, start):
        return (self._isFunction or self._isStepFunction) and \
                (self._chr == chr and self._getEnd(self._getFixedStepCurElStart()) == start)
        
    def _iter(self):
        self._initAll()
        return self
  
    def _next(self, line):
        if self._isDeclarationLine(line):
            ge = self._parseDeclarationLine(line)
            if ge is not None:
                return ge
        else:
            if line.startswith('#'):
                return None
            
            cols = line.split()
            self._checkDataLineCols(cols)

            if self._fixedStep:
                self._curElCountInBoundingRegion += 1
                val = numpy.float(self._handleNan(cols[0]))
                
                if self._isFunction:
                    self._genomeElement.val = val
                    return self._genomeElement
                else:
                    start = self._checkValidStart(self._chr, self._getFixedStepCurElStart())
            else:
                start = self._checkValidStart(self._chr, int(cols[0])-1)
                val = numpy.float(self._handleNan(cols[1]))

            end = None
            if not self._isPoints:
                end = self._checkValidEnd(self._chr, self._getEnd(start), start)
            if self._isStepFunction:
                start = None
            
            return GenomeElement(genome=self._genome, chr=self._chr, start=start, end=end, val=val)
            
    def _checkDataLineCols(self, cols):
        if self._fixedStep is None:
            raise InvalidFormatError('All WIG data lines must be preceded by a declaration line.')
        elif self._fixedStep:
            if len(cols) != 1:
                raise InvalidFormatError('WIG fixedStep requires data lines with one column.')
        else:
            if len(cols) != 2:
                raise InvalidFormatError('WIG variableStep requires data lines with two columns.')

    def _getFixedStepCurElStart(self):
        return self._start + (self._curElCountInBoundingRegion-1) * self._step
  
    def _getEnd(self, start):
        return start + self._span
  
    def _handleEndOfFile(self):
        if self._fixedStep and self._chr is not None:
            self._appendBoundingRegionTuple()
        
    def _appendBoundingRegionTuple(self):
        boundingRegion = GenomeRegion(genome=self._genome, chr=self._chr, start=self._start, \
                                      end=self._getEnd(self._getFixedStepCurElStart()))
        elCount = self._curElCountInBoundingRegion + (1 if self._isStepFunction else 0)
        self._boundingRegionTuples.append(BoundingRegionTuple(boundingRegion, elCount))

    def getBoundingRegionTuples(self):
        return self._boundingRegionTuples
        
    def getFixedLength(self):
        return self._span if self._fixedStep else 1
        
    def getFixedGapSize(self):
        return self._step - self._span if self._fixedStep else 0
        
    def hasNoOverlappingElements(self):
        return True if self._fixedGapSize else False

class HbWigGenomeElementSource(WigGenomeElementSource):
    def _checkBoundingRegionSortedPair(self, lastBoundingRegion, br):
        GenomeElementSource._checkBoundingRegionSortedPair(self, lastBoundingRegion, br)
        if br.start is not None and br.end is not None:
            if lastBoundingRegion.end == br.start:
                raise InvalidFormatError("Error: bounding regions '%s' and '%s' are adjoining (there is no gap between them)." % (lastBoundingRegion, br))
    