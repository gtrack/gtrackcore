from gtrackcore.util.CustomExceptions import InvalidFormatError, ShouldNotOccurError, AbstractClassError
from gtrackcore.input.core.GenomeElementSource import GenomeElementSource
from copy import copy

class GESourceWrapper(object):
    def __init__(self, geSource):
        self._geSource = geSource
        
    def getFileFormatName(self):
        return self._geSource.getFileFormatName()
        
    def getDefaultFileSuffix(self):
        return self._geSource.getDefaultFileSuffix()
    
    def getTrackName(self):
        return self._geSource.getTrackName()
    
    def getGenome(self):
        return self._geSource.getGenome()
        
    def getFileName(self):
        return self._geSource.getFileName()
        
    def getFileSuffix(self):
        return self._geSource.getFileSuffix()
        
    def isExternal(self):
        return self._geSource.isExternal()
        
    def hasOrigFile(self):
        return self._geSource.hasOrigFile()
        
    def isSliceSource(self):
        return self._geSource.isSliceSource()
        
    def addsStartElementToDenseIntervals(self):
        return self._geSource.addsStartElementToDenseIntervals()
        
    def hasCircularElements(self):
        return self._geSource.hasCircularElements()
        
    def getFixedLength(self):
        return self._geSource.getFixedLength()
        
    def getFixedGapSize(self):
        return self._geSource.getFixedGapSize()
        
    def isSorted(self):
        return self._geSource.isSorted()
        
    def hasNoOverlappingElements(self):
        return self._geSource.hasNoOverlappingElements()
        
    def hasUndirectedEdges(self):
        return self._geSource.hasUndirectedEdges()
        
    def inputIsOneIndexed(self):
        return self._geSource.inputIsOneIndexed()
    
    def inputIsEndInclusive(self):
        return self._geSource.inputIsEndInclusive()
        
    def anyWarnings(self):
        return self._geSource.anyWarnings()
        
    def getLastWarning(self):
        return self._geSource.getLastWarning()
    
    def hasBoundingRegionTuples(self):
        return len(self.getBoundingRegionTuples()) > 0
    
    def getBoundingRegionTuples(self):
        return self._geSource.getBoundingRegionTuples()
    
    def parseFirstDataLine(self):
        return self._geSource.parseFirstDataLine()
    
    def getPrefixList(self):
        return self._geSource.getPrefixList()
    
    def getPrintWarnings(self):
        return self._geSource.getPrintWarnings()
        
    def setPrintWarnings(self, printWarnings):
        self._geSource.setPrintWarnings(printWarnings)

    def getValDataType(self):
        return self._geSource.getValDataType()

    def getValDim(self):
        return self._geSource.getValDim()
        
    def getEdgeWeightDataType(self):
        return self._geSource.getEdgeWeightDataType()

    def getEdgeWeightDim(self):
        return self._geSource.getEdgeWeightDim()
        
    def getVersion(self):
        return self._geSource.getVersion()
        
    def getId(self):
        return self._geSource.getId()
        
    def getLastWarning(self):
        return self._geSource.getLastWarning()
    
    genome = property(getGenome)

class BrTuplesGESourceWrapper(GESourceWrapper):
    def __init__(self, geSource, brList=[]):
        GESourceWrapper.__init__(self, geSource)
        self._brList = brList

    def __iter__(self):
        return self._geSource.__iter__()
            
    def getBoundingRegionTuples(self):
        return self._brList
        
class ListGESourceWrapper(GESourceWrapper):
    def __init__(self, geSource, geList, brList=[]):
        GESourceWrapper.__init__(self, geSource)
        self._geList = geList
        self._brList = brList

    def __iter__(self):
        self._geIter = self._geList.__iter__()
        return copy(self)
        
    def next(self):
        return self._geIter.next()
            
    def getBoundingRegionTuples(self):
        return self._brList
        
class SortedListGESourceWrapper(ListGESourceWrapper):
    def isSorted(self):
        return True
        
class PrefixListGESourceWrapper(ListGESourceWrapper):
    def __init__(self, geSource, geList, brList, prefixList):
        ListGESourceWrapper.__init__(self, geSource, geList, brList)
        self._prefixList = prefixList
        
    def getPrefixList(self):
        return self._prefixList
        
class ElementModifierGESourceWrapper(GESourceWrapper, GenomeElementSource):
    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)
        
    def __init__(self, geSource, genome=None):
        from gtrackcore.input.wrappers.GEDependentAttributesHolder import GEDependentAttributesHolder
        geSource = GEDependentAttributesHolder(geSource)
        GESourceWrapper.__init__(self, geSource)
        GenomeElementSource.__init__(self, '', genome=genome)
        
        #for ge in geSource:
        #    pass
        
    def __iter__(self):
        self._brtAndGeIter = self._brtAndGeIterator()
        self._iter()
        return self
        
    def _brtAndGeIterator(self):
        from gtrackcore.input.wrappers.GEDependentAttributesHolder import iterateOverBRTuplesWithContainedGEs
        brtAndGeIter = iterateOverBRTuplesWithContainedGEs(self._geSource, returnIterator=True)
        
        while True:
            try:
                brt, geIter = brtAndGeIter.next()
            except StopIteration:
                return
            
            for i, ge in enumerate(geIter):
                yield brt, ge, i

    def _iter(self):
        pass
        
    def next(self):
        while True:
            ge = self._next(*self._brtAndGeIter.next())
            if ge is None:
                continue
            return ge
        
    def _next(self, ge):
        raise AbstractClassError

    def parseFirstDataLine(self):
        return GenomeElementSource.parseFirstDataLine(self)
        
    def getPrefixList(self):
        return GenomeElementSource.getPrefixList(self)

    def getBoundingRegionTuples(self):
        return self._geSource.getBoundingRegionTuples()

    def inputIsOneIndexed(self):
        return self._geSource.inputIsOneIndexed()
    
    def inputIsEndInclusive(self):
        return self._geSource.inputIsOneIndexed()

class ChrPausedGESourceWrapper(GESourceWrapper):
    def __init__(self, geSource):
        GESourceWrapper.__init__(self, geSource)
        self._geIter = self._geSource.__iter__()
        #self._curEl = deepcopy(self._geIter.next())
        self._curEl = self._geIter.next().getCopy()
        self._chrList = [self._curEl.chr]
        self._finished = False
    
    def __iter__(self):
        try:
            while not self._finished:
                yield self._curEl
                self._curEl = self._geIter.next()
                if self._curEl.chr != self._chrList[-1]:
                    if self._curEl.chr in self._chrList:
                        raise InvalidFormatError('Error: chromosome %s has been previously encountered. Dense datasets must not skip back and forth between chromosomes.' % self._curEl.chr)
                    self._chrList.append(self._curEl.chr)
                    break
            
        except StopIteration:
            self._finished = True
            raise
    
    def checkCurChr(self, chr):
        if chr != self._chrList[-1]:
            raise ShouldNotOccurError('Error: current chromosome %s is not what is expected (%s). This should not have happened.' % (self._chrList[-1], chr))
            
class PausedAtCountsGESourceWrapper(GESourceWrapper):
    def __init__(self, geSource, countList):
        GESourceWrapper.__init__(self, geSource)
        self._geIter = self._geSource.__iter__()
        self._countList = countList
        self._curCountListIdx = 0
        self._finished = False
    
    def __iter__(self):
        try:
            i = 0
            
            while not self._finished:
                if len(self._countList) > self._curCountListIdx and \
                    i == self._countList[self._curCountListIdx]:
                        self._curCountListIdx += 1
                        if len(self._countList) == self._curCountListIdx:
                            self._finished = True
                        break
                
                yield self._geIter.next()
                i += 1
            
        except StopIteration:
            if self._finished:
                raise
            else:
                raise ShouldNotOccurError('Premature stop. GESource was shorter than sum of countList.')