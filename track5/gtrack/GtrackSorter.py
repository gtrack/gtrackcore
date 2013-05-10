import numpy

from collections import OrderedDict
from itertools import chain

from track5.extract.fileformats.GtrackComposer import StdGtrackComposer, ExtendedGtrackComposer
from track5.input.fileformats.GtrackGenomeElementSource import GtrackGenomeElementSource
from track5.input.wrappers.GEDependentAttributesHolder import GEDependentAttributesHolder, iterateOverBRTuplesWithContainedGEs
from track5.input.wrappers.GESourceWrapper import SortedListGESourceWrapper
from track5.track.format.TrackFormat import TrackFormat
from track5.util.CustomExceptions import ShouldNotOccurError, InvalidFormatError

class UnsortedGtrackGenomeElementSource(GtrackGenomeElementSource):
    def _checkBoundingRegionSorting(self, br, lastBoundingRegion):
        pass
        
    def _checkEndOfLastBoundingRegion(self):
        pass
    
    def _checkOverlappingAndSortedElements(self, ge):
        pass
        
    def _checkDenseSorting(self, ge):
        pass

def _getSortedBoundingRegionsAndGenomeElements(geSource):
    geSource = GEDependentAttributesHolder(geSource)
    
    doubleElList = [[brTuple, geList] for brTuple, geList in iterateOverBRTuplesWithContainedGEs(geSource)]
    
    noBoundingRegions = doubleElList[0][0] is None
    if not noBoundingRegions:
        doubleElList.sort(key=lambda x:x[0].region)
    
    for x in doubleElList:
        if len(x[1]) >= 2:
            if x[1][0].reprIsDense():
                break
            x[1].sort()
            
    return doubleElList, geSource
        
def _commonSortGtrackFile(fn, genome):
    gtrackGESource = UnsortedGtrackGenomeElementSource(fn, genome, printWarnings=False)
    useExtendedGtrack = gtrackGESource.isExtendedGtrackFile()
    
    doubleElList, geSource = _getSortedBoundingRegionsAndGenomeElements(gtrackGESource)
    noBoundingRegions = doubleElList[0][0] is None
    
    sortedGESource = SortedListGESourceWrapper(geSource, list(chain(*(x[1] for x in doubleElList))), \
                                               [x[0] for x in doubleElList] if not noBoundingRegions else [])
    
    
    composerCls = ExtendedGtrackComposer if useExtendedGtrack else StdGtrackComposer
    return composerCls( sortedGESource )

def sortedGeSourceHasOverlappingRegions(geSource):
    doubleElList = _getSortedBoundingRegionsAndGenomeElements(geSource)[0]
    
    hasOverlaps = False
    prevSortedElement = None
    for ge in chain(*(x[1] for x in doubleElList)):
        if prevSortedElement is not None and ge.overlaps(prevSortedElement):
            hasOverlaps = True
            break
        prevSortedElement = ge
    
    return hasOverlaps
    
def sortGtrackFileAndReturnContents(inFn, genome=None):
    return _commonSortGtrackFile(inFn, genome).returnComposed()
    
def sortGtrackFileAndWriteToFile(inFn, outFn, genome=None):
    return _commonSortGtrackFile(inFn, genome).composeToFile(outFn)

    