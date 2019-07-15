import numpy
from copy import copy

from gtrackcore.input.core.GenomeElementSource import GenomeElementSource
from gtrackcore.extract.fileformats.GtrackComposer import StdGtrackComposer
from gtrackcore.gtrack.GtrackHeaderExpander import expandHeadersOfGtrackFileAndReturnComposer
from gtrackcore.input.wrappers.GESourceWrapper import ElementModifierGESourceWrapper
from gtrackcore.util.CustomExceptions import ShouldNotOccurError, InvalidFormatError
from gtrackcore.util.CommonConstants import BINARY_MISSING_VAL
from input.core.GenomeElementSourceResolver import GenomeElementSourceResolver


class GtrackElementStandardizer(ElementModifierGESourceWrapper):
    def _iter(self):
        self._prevElement = None
        self._id = 0
        
    def _next(self, brt, ge, i):
        if ge.genome is not None:
            if self._genome is None:
                self._genome = ge.genome
            elif self._genome != ge.genome:
                raise InvalidFormatError('GtrackStandardizer does not support GTrack files with more than one genome')
            ge.genome = None
        
        if ge.start is None:
            if i == 0:
                if brt is not None:
                    ge.start = brt.region.start
                else:
                    raise ShouldNotOccurError
            else:
                ge.start = self._prevElement.end
                
        if ge.end is None:
            ge.end = ge.start + 1
            
        if ge.val is None:
            ge.val = numpy.nan
            
        if ge.strand is None:
            ge.strand = BINARY_MISSING_VAL
            
        if ge.id is None:
            ge.id = str(self._id)
            self._id += 1
            
        if ge.edges is None:
            ge.edges = []
        
        self._prevElement = ge
        return ge

    def getBoundingRegionTuples(self):
        return []
        
    def inputIsOneIndexed(self):
        return False
    
    def inputIsEndInclusive(self):
        return False
        
def _commonStandardizeGtrackFile(fn, genome, suffix=None):
    geSource = GenomeElementSourceResolver(fn, genome, suffix=suffix)
    composedFile = StdGtrackComposer( GtrackElementStandardizer(geSource)).returnComposed()
    return expandHeadersOfGtrackFileAndReturnComposer('', genome, strToUseInsteadOfFn=composedFile)
       
def standardizeGtrackFileAndReturnContents(fn, genome=None, suffix=None):
    return _commonStandardizeGtrackFile(fn, genome, suffix=suffix).returnComposed()
    
def standardizeGtrackFileAndWriteToFile(inFn, outFn, genome=None, suffix=None):
    return _commonStandardizeGtrackFile(inFn, genome, suffix=suffix).composeToFile(outFn)
