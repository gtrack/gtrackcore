from gtrackcore_memmap.extract.fileformats.GtrackComposer import StdGtrackComposer, ExtendedGtrackComposer
from gtrackcore_memmap.gtrack.FullInfoDict import IdFullInfoDict, TupleFullInfoDict
from gtrackcore_memmap.gtrack.GtrackHeaderExpander import expandHeadersOfGtrackFileAndReturnComposer
from gtrackcore_memmap.input.fileformats.GtrackGenomeElementSource import GtrackGenomeElementSource
from gtrackcore_memmap.input.wrappers.GESourceWrapper import ElementModifierGESourceWrapper
from gtrackcore_memmap.util.CustomExceptions import ShouldNotOccurError

class ElementComplementer(ElementModifierGESourceWrapper):
    def __init__(self, geSource, fullDbDict, gtrackColsToAdd):
        self._prefixesToAdd = [GtrackGenomeElementSource.convertNameFromGtrack(col) for col in gtrackColsToAdd]
        if 'edges' in self._prefixesToAdd:
            self._prefixesToAdd.append('weights')
            
        ElementModifierGESourceWrapper.__init__(self, geSource)
        
        self._fullDbDict = fullDbDict
        self._prefixList = geSource.getPrefixList() + self._prefixesToAdd
        
    def _next(self, brt, ge, i):
        for prefix in self._prefixesToAdd:
            dbGE = self._fullDbDict.get(ge)
            if prefix == 'weights' and (dbGE is None or dbGE.get('edges') is None):
                continue
            setattr(ge, prefix, dbGE.get(prefix) if dbGE is not None else '.')
        return ge
        
    def getPrefixList(self):
        return self._prefixList

def _commonComplementGtrackFile(origFn, dbFn, intersectingFactor, gtrackColsToAdd, genome):
    origGESource = GtrackGenomeElementSource(origFn, genome)
    dbGESource = GtrackGenomeElementSource(dbFn, genome)
    
    dbPrefixes = dbGESource.getPrefixList()

    if intersectingFactor == 'id':
        fullDbDict = IdFullInfoDict(dbGESource, dbPrefixes)
    elif intersectingFactor == 'position':
        fullDbDict = TupleFullInfoDict(dbGESource, dbPrefixes)
    else:
        ShouldNotOccurError
        
    forcedHeaderDict = {}
    dbHeaderDict = dbGESource.getHeaderDict()
    
    if 'value' in gtrackColsToAdd:
        forcedHeaderDict['value type'] = dbHeaderDict['value type']
        forcedHeaderDict['value dimension'] = dbHeaderDict['value dimension']
    if 'edges' in gtrackColsToAdd:
        forcedHeaderDict['edge weight type'] = dbHeaderDict['edge weight type']
        forcedHeaderDict['edge weight dimension'] = dbHeaderDict['edge weight dimension']
    
    composerCls = ExtendedGtrackComposer if origGESource.isExtendedGtrackFile() else StdGtrackComposer    
    composedFile = composerCls( ElementComplementer(origGESource, fullDbDict, gtrackColsToAdd), \
                                forcedHeaderDict=forcedHeaderDict).returnComposed()
        
    return expandHeadersOfGtrackFileAndReturnComposer('', genome, strToUseInsteadOfFn=composedFile)
        
def complementGtrackFileAndReturnContents(origFn, dbFn, intersectingFactor, gtrackColsToAdd, genome=None):
    return _commonComplementGtrackFile(origFn, dbFn, intersectingFactor, gtrackColsToAdd, genome).returnComposed()
    
def complementGtrackFileAndWriteToFile(origFn, dbFn, outFn, intersectingFactor, gtrackColsToAdd, genome=None):
    return _commonComplementGtrackFile(origFn, dbFn, intersectingFactor, gtrackColsToAdd, genome).composeToFile(outFn)
