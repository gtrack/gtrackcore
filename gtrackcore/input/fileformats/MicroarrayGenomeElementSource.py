import numpy
import re

from gtrackcore.input.core.GenomeElementSource import GenomeElementSource
from gtrackcore.util.CommonFunctions import splitOnWhitespaceWhileKeepingQuotes
from gtrackcore.util.CustomExceptions import InvalidFormatError

class MicroarrayGenomeElementSource(GenomeElementSource):
    _VERSION = '1.3'
    FILE_SUFFIXES = ['microarray']
    FILE_FORMAT_NAME = 'Microarray'
    _numHeaderLines = 1
    
    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)
    
    def __init__(self, fn, *args, **kwArgs):
        GenomeElementSource.__init__(self, fn, *args, **kwArgs)
    
        f = open(fn)
        trackDef = f.readline().replace('\'','"')
        if not trackDef.startswith('track type="array"'):
            raise InvalidFormatError('Track definition line must start with: track type="array". Line: ' + trackDef)
        
        header = self._parseHeader(trackDef)
        if not all(key in header for key in ['expScale', 'expStep', 'expNames']):
            raise InvalidFormatError('Track definition line must define values for expScale, expStep and expNames: ' + trackDef)
        
        expNames = header['expNames']
        if not all(expNames[i] == '"' for i in [0,-1]):
            raise InvalidFormatError('expNames does not start and end in quote marks: ' + trackDef)
        
        self._globExpCount = len( [x for x in expNames[1:-2].split(',') if x != ''] )
        if self._globExpCount < 3:
            raise InvalidFormatError('Microarray data must have at least 3 experiments. Length of expNames: ' + str(self._globExpCount))
        
    def _parseHeader(self, headerLine):
        return dict( [ pair.split('=') for pair in splitOnWhitespaceWhileKeepingQuotes( headerLine )[2:] ] )
  
    def _next(self, line):
        cols = line.split()
        if len(cols) != 15:
            raise InvalidFormatError('File must contain exactly 15 columns, contains ' + str(len(cols)))

        self._genomeElement.chr = self._checkValidChr(cols[0])
        self._genomeElement.start = self._checkValidStart(self._genomeElement.chr, int(cols[1]))
        self._genomeElement.end = self._checkValidEnd(self._genomeElement.chr, int(cols[2]), start=self._genomeElement.start)
        self._genomeElement.strand = self._getStrandFromString(cols[5])
        
        self._genomeElement.val = [numpy.nan] * self._globExpCount
        expCount = int(cols[12])
        expIds = [int(x) for x in cols[13].split(',') if x != '']
        expScores = [numpy.float(x) for x in cols[14].split(',') if x != '']
        
        if len(expIds) != expCount:
            raise InvalidFormatError('expId length (' + str(len(expIds)) + ') is not equal to expCount (' + str(expCount) + ')') 
        if len(expScores) != expCount:
            raise InvalidFormatError('expScores length (' + str(len(expIds)) + ') is not equal to expCount (' + str(expScores) + ')') 

        for i in range(expCount):
            if expIds[i] >= self._globExpCount:
                raise InvalidFormatError('expId ' + str(expIds[i]) + ' too large. expNames in header line defines ' + str(self._globExpCount) + ' experiments. '+\
                                         'Thsi could be because of counting from 1 instead of from 0.')
            self._genomeElement.val[ expIds[i] ] = expScores[i]
        
        return self._genomeElement
    
    def getValDataType(self):
        return 'float64'

    def getValDim(self):
        return self._globExpCount