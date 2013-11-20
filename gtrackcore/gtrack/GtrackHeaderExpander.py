import numpy

from collections import OrderedDict

from gtrackcore.extract.fileformats.GtrackComposer import StdGtrackComposer, ExtendedGtrackComposer
from gtrackcore.gtrack.GtrackSorter import sortedGeSourceHasOverlappingRegions
from gtrackcore.input.fileformats.GtrackGenomeElementSource import GtrackGenomeElementSource
from gtrackcore.input.wrappers.GEDependentAttributesHolder import GEDependentAttributesHolder
from gtrackcore.track.format.TrackFormat import TrackFormat
from gtrackcore.util.CustomExceptions import ShouldNotOccurError, InvalidFormatError

EXPANDABLE_HEADERS = ['track type',\
                      'undirected edges',\
                      'edge weights',\
                      'uninterrupted data lines',\
                      'sorted elements',\
                      'no overlapping elements',\
                      'circular elements']

NOT_GUARANTEED_EXPANDABLE_HEADERS = ['value type',\
                                    'value dimension',\
                                    'edge weight type',\
                                    'edge weight dimension']

VALUE_NOT_KEPT_HEADERS = ['value column', \
                         'edges column', \
                         'fixed-size data lines', \
                         'data line size', \
                         'fixed length', \
                         'fixed gap size']


class GtrackHeaderExpanderGenomeElementSource(GtrackGenomeElementSource):
    def __init__(self, *args, **kwArgs):
        GtrackGenomeElementSource.__init__(self, *args, **kwArgs)

        self._noOverlappingElements = None
        
    def _iter(self):
        self._valTypeIndexDict = {}
        self._valLenDict = {}
        self._allMissingDict = {}
        
        #self._headerDict['no overlapping elements'] = True
        self._headerDict['sorted elements'] = True            
        if self._headerDict['track type'].startswith('linked'):
            self._headerDict['undirected edges'] = True
        
        return GtrackGenomeElementSource._iter(self)

    def _createColumnSpec(self, cols, addAnyExtraFixedCols=True):
        GtrackGenomeElementSource._createColumnSpec(self, cols, addAnyExtraFixedCols)
        
        self._headerDict['track type'] = GtrackGenomeElementSource.getTrackTypeFromColumnSpec(self._columnSpec)
    
    def _checkColumnSpecLine(self):
        pass
        
    def _checkBoundingRegionSorting(self, br, lastBoundingRegion):
        if self._headerDict['sorted elements'] and br < lastBoundingRegion:
            self._headerDict['sorted elements'] = False
        
    def _checkIfInterruptingDataLines(self, line):
        pass
        
    def _checkValidEnd(self, chr, end, start=None):
        if start is not None and end <= start:
            if not self._headerDict['circular elements']:
                self._headerDict['circular elements'] = True
                start = None
        
        return GtrackGenomeElementSource._checkValidEnd(self, chr, end, start)
        
    def _parseEdges(self, edgeStr):
        if edgeStr != '.':
            for edgeSpec in edgeStr.split(';'):
                if '=' in edgeSpec:
                    if not self._headerDict['edge weights']:
                        self._headerDict['edge weights'] = True
                    self._getValInCorrectType(edgeSpec.split('=')[1], 'edge weight')
        
        return GtrackGenomeElementSource._parseEdges(self, edgeStr)
        
    def _getValInCorrectType(self, val, valueOrEdgeWeight='value', isEmptyElement=False):
        headerDictInFile = self.getHeaderDictInFile()
        
        valTypeList = ['binary', 'number', 'category', 'character']
        for i,valueType in enumerate(valTypeList):
            if valueOrEdgeWeight in self._valTypeIndexDict and self._valTypeIndexDict[valueOrEdgeWeight] > i:
                continue
            
            valTypeInfo = GtrackGenomeElementSource.VAL_TYPE_DICT[valueType]
            
            if self._isValOfParticularType(val, valTypeInfo):
                self._noteIfAllValuesAreMissing(valueOrEdgeWeight, val, valTypeInfo)
                self._valTypeIndexDict[valueOrEdgeWeight] = i

                valueDim = self._getGtrackValueDim(val, valTypeInfo, valueOrEdgeWeight)

                if not '%s type' % valueOrEdgeWeight in headerDictInFile:
                    self._headerDict['%s type' % valueOrEdgeWeight] = valTypeList[i]
                if not '%s dimension' % valueOrEdgeWeight in headerDictInFile:
                    self._headerDict['%s dimension' % valueOrEdgeWeight] = valueDim
                
                return GtrackGenomeElementSource._getValInCorrectType(self, val, valueOrEdgeWeight, isEmptyElement)
        raise ShouldNotOccurError()
        
    def _noteIfAllValuesAreMissing(self, valueOrEdgeWeight, val, valTypeInfo):
        if valueOrEdgeWeight in self._allMissingDict and self._allMissingDict[valueOrEdgeWeight] == False:
            return
        
        allMissing = all([x == '.' for x in \
                          (val.split(valTypeInfo.delim) if valTypeInfo.delim != '' else val)])
        self._allMissingDict[valueOrEdgeWeight] = allMissing
    
    def _isValOfParticularType(self, val, valTypeInfo):
        try:
            valList = [valTypeInfo.pythonType(x) if x != '.' else valTypeInfo.missingVal for x in \
                       (val.split(valTypeInfo.delim) if valTypeInfo.delim != '' else val)]
            
            dtype = valTypeInfo.numpyType
            autoArray = numpy.array(valList)
            manualArray = numpy.array(valList, dtype=dtype)
            
            answer = (autoArray == manualArray)
            
            if isinstance(answer, numpy.ndarray):
                if dtype.startswith('float'):
                    answer |= numpy.isnan(autoArray)
                elif dtype == 'int8':
                    answer &= (autoArray >= -1) & (autoArray <= 1)
                answer = answer.all()
                
            if dtype == 'S' and str(manualArray.dtype).replace('|', '') == 'S1':
                answer &= (len(valList) != 1)
            
            answer &= valTypeInfo.fromNumpyTypeFunc( str(manualArray.dtype).replace('|', '') )
            
            return answer
        
        except Exception, e:
            return False
        
    def _getGtrackValueDim(self, val, valTypeInfo, valueOrEdgeWeight):
        valLen = len(val.split(valTypeInfo.delim) if valTypeInfo.delim != '' else val)
        
        if valueOrEdgeWeight in self._valLenDict:
            if self._valLenDict[valueOrEdgeWeight] != valLen:
                self._valLenDict[valueOrEdgeWeight] = 0
        else:
            self._valLenDict[valueOrEdgeWeight] = valLen
        
        valDim = GtrackGenomeElementSource.getGtrackValueDimension(self._valLenDict[valueOrEdgeWeight])
            
        return valDim
    
    def _checkOverlappingAndSortedElements(self, ge):
        if self._prevElement is not None:
            if self._headerDict['sorted elements']:
                if ge < self._prevElement:
                    self._headerDict['sorted elements'] = False
        
    def _updateUndirectedEdgesInfo(self, ge):
        if self._headerDict['track type'].startswith('linked'):
            try:
                self._adjustComplementaryEdgeWeightDict(ge.id, ge.edges, ge.weights)
            except InvalidFormatError:
                self._headerDict['undirected edges'] = False
        
    def _checkUndirectedEdges(self):     
        if self._headerDict['track type'].startswith('linked'):
            try:       
                GtrackGenomeElementSource._checkUndirectedEdges(self)
            except InvalidFormatError:
                self._headerDict['undirected edges'] = False

    def hasNoOverlappingElements(self):
        if self._noOverlappingElements is None:
            if not any(x in self._headerDict['track type'] for x in ['function', 'base pairs', 'partition']):
                self._noOverlappingElements = not sortedGeSourceHasOverlappingRegions(self)
            else:
                self._noOverlappingElements = False
        
        return self._noOverlappingElements
        
    def _handleEndOfFile(self):
        GtrackGenomeElementSource._handleEndOfFile(self)
        
        #To fix an issue where value dimension is "list" if the value type was wrongly
        #guessed for early elements.
        
        newIter = self.__iter__()
        newIter._valTypeIndexDict = self._valTypeIndexDict
        newIter._handleEndOfFile = newIter._basicHandleEndOfFile
        
        try:
            while True:
                newIter.next()
        except StopIteration:
            pass
        
        self._valLenDict = newIter._valLenDict
        if len(self._uniqueEdgeIds) == 0:
            self._headerDict['undirected edges'] = False
        
        for valueOrEdgeWeight in ['value', 'edge weight']:
            if valueOrEdgeWeight in newIter._allMissingDict and newIter._allMissingDict[valueOrEdgeWeight] == True:
                self._headerDict['%s type' % valueOrEdgeWeight] = 'number'
        
    def _basicHandleEndOfFile(self):
        GtrackGenomeElementSource._handleEndOfFile(self)


class GtrackHeaderExpanderAttributesHolder(GEDependentAttributesHolder):
    #def _initOtherDependentAttrs(self):
    #    GEDependentAttributesHolder._initOtherDependentAttrs(self)
    #    
        #self._isSorted = self._geSource.isSorted()
        #self._hasCircularElements = self._geSource.hasCircularElements()
        #self._hasNoOverlappingElements = self._geSource.hasNoOverlappingElements()
        #self._hasUndirectedEdges = self._geSource.hasUndirectedEdges()
        #self._valDataType = \
        #    self._geSource.VAL_TYPE_DICT[ self._geSource.getHeaderDict()['value type'] ].numpyType
        #self._edgeWeightDataType = \
        #    self._geSource.VAL_TYPE_DICT[ self._geSource.getHeaderDict()['edge weight type'] ].numpyType

    def _storeOtherDependentAttrs(self):
        GEDependentAttributesHolder._storeOtherDependentAttrs(self)
        
        self._isSorted = self._geIter.isSorted()
        self._hasCircularElements = self._geIter.hasCircularElements()
        self._hasNoOverlappingElements = self._geIter.hasNoOverlappingElements()
        self._hasUndirectedEdges = self._geIter.hasUndirectedEdges()
        self._valDataType = self._geIter.getValDataType()
        self._edgeWeightDataType = self._geIter.getEdgeWeightDataType()
        
        self._geSource.__class__ = GtrackGenomeElementSource

        
    def isSorted(self):
        return self._isSorted
        
    def hasCircularElements(self):
        return self._hasCircularElements
        
    def hasNoOverlappingElements(self):
        return self._hasNoOverlappingElements
        
    def hasUndirectedEdges(self):
        return self._hasUndirectedEdges

    def getValDataType(self):
        return self._valDataType

    def getEdgeWeightDataType(self):
        return self._edgeWeightDataType


def expandHeadersOfGtrackFileAndReturnComposer(fn, genome=None, strToUseInsteadOfFn=''):
    expandedGESource = GtrackHeaderExpanderGenomeElementSource(fn, genome, strToUseInsteadOfFn=strToUseInsteadOfFn, printWarnings=False)
    forcedHeaderDict = OrderedDict([(key, val) for key,val in expandedGESource.getHeaderDict().iteritems() \
                                    if key not in ['track type', 'value column', 'edges column'] and \
                                    val != GtrackGenomeElementSource.DEFAULT_HEADER_DICT.get(key)])
    useExtendedGtrack = any(header in GtrackGenomeElementSource.EXTENDED_HEADERS \
                            for header in forcedHeaderDict.keys())
    composerCls = ExtendedGtrackComposer if useExtendedGtrack else StdGtrackComposer
    
    return composerCls( GtrackHeaderExpanderAttributesHolder(expandedGESource), \
                        forcedHeaderDict=forcedHeaderDict)
        
def expandHeadersOfGtrackFileAndReturnContents(inFn, genome=None, onlyNonDefault=True):
    return expandHeadersOfGtrackFileAndReturnComposer(inFn, genome).returnComposed(onlyNonDefault=onlyNonDefault)
    
def expandHeadersOfGtrackFileAndWriteToFile(inFn, outFn, genome=None, onlyNonDefault=True):
    return expandHeadersOfGtrackFileAndReturnComposer(inFn, genome).composeToFile(outFn, onlyNonDefault=onlyNonDefault)
