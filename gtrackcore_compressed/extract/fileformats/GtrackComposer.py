import os
import numpy as np
import urllib

from copy import copy, deepcopy
from cStringIO import StringIO
from collections import OrderedDict

from gtrackcore_compressed.extract.fileformats.FileFormatComposer import FileFormatComposer, MatchResult
from gtrackcore_compressed.input.wrappers.GEDependentAttributesHolder import iterateOverBRTuplesWithContainedGEs
from gtrackcore_compressed.input.fileformats.GtrackGenomeElementSource import GtrackGenomeElementSource as Gtrack
from gtrackcore_compressed.track.format.TrackFormat import TrackFormat
from gtrackcore_compressed.util.CommonFunctions import getStringFromStrand, isIter, isNan
from gtrackcore_compressed.util.CustomExceptions import InvalidFormatError, ShouldNotOccurError

class StdGtrackComposer(FileFormatComposer):
    FILE_SUFFIXES = ['gtrack']
    FILE_FORMAT_NAME = 'GTrack'
    
    GTRACK_PRIORITIZED_SUBTYPE_LIST = \
        ['http://gtrack.no/wig_fixedstep.gtrack', \
         'http://gtrack.no/wig_variablestep.gtrack', \
         'http://gtrack.no/gff_direct.gtrack', \
         'http://gtrack.no/bedgraph.gtrack', \
         'http://gtrack.no/bed_direct.gtrack', \
         'http://gtrack.no/bed_linked.gtrack', \
         'http://gtrack.no/bed9.gtrack', \
         'http://gtrack.no/bed6.gtrack', \
         'http://gtrack.no/bed5.gtrack', \
         'http://gtrack.no/bed4.gtrack', \
         'http://gtrack.no/bed3.gtrack', \
         'http://gtrack.no/fasta.gtrack', \
         'http://gtrack.no/mean_sd.gtrack', \
         'http://gtrack.no/mean_sd_weights.gtrack']
         
         # Fixme: Manually, only when there is metadata
         #'http://gtrack.no/hyperbrowser.gtrack'
         
    _USE_EXTENDED_GTRACK = False

    def __init__(self, geSource, forcedHeaderDict={}):
        FileFormatComposer.__init__(self, geSource)
        
        self._headerDict = copy(Gtrack.DEFAULT_HEADER_DICT)
        self._forcedHeaderDict = forcedHeaderDict
        
        #Also stores bounding regions and value dimensions in GEDependentAttributesHolder, if present
        self._anyGeHasGenome = False
        for ge in self._geSource:
            if ge.genome is not None:
                self._anyGeHasGenome = True
    
    @staticmethod
    def matchesTrackFormat(trackFormat):
        return MatchResult(match=True, trackFormatName=trackFormat.getFormatName().lower())

    # Compose methods
    
    def _compose(self, out, onlyNonDefault=True):
        hbColumns = self._findHbColumns()
        columns = self._getGtrackColumnsFromHbColumns(hbColumns)
        hbColumns, columns = self._determineHeaderLines(hbColumns, columns)
        
        self._composeContents(out, hbColumns, columns, self._geSource, onlyNonDefault=onlyNonDefault)
        
    def _composeContents(self, out, hbColumns, columns, geSource, onlyNonDefault=True, singleDataLine=False):
        tf = TrackFormat.createInstanceFromGeSource(self._geSource)
        out.write( self._composeHeaderLines(onlyNonDefault) )
        out.write( self._composeColSpecLine(columns) )
        
        for br, geList in iterateOverBRTuplesWithContainedGEs(geSource, onlyYieldTwoGEs=singleDataLine):
            if br is not None:
                out.write( self._composeBoundingRegionLine(br) )
            
            for i, ge in enumerate(self._removeStartElementIfApplicable(tf, geList)):
                out.write( self._composeDataLine(ge, hbColumns, i+1, i+1 == len(geList)) )
                
                if singleDataLine:
                    break
            if singleDataLine:
                break
    
    def _headerShouldBeWritten(self, header, value, onlyNonDefault):
        if header in ['gtrack version', 'track type']:
            return True
        if not self._USE_EXTENDED_GTRACK and header in Gtrack.EXTENDED_HEADERS:
            return False
        if onlyNonDefault:
            return value != Gtrack.DEFAULT_HEADER_DICT.get(header)
        return True
    
    def _composeHeaderLines(self, onlyNonDefault):
        return os.linesep.join( ('##' + key + ': ' + str(val).lower()) \
                                 for key,val in self._headerDict.iteritems() if \
                                 self._headerShouldBeWritten(key, val, onlyNonDefault) ) \
               + os.linesep
        
    def _composeColSpecLine(self, columns):
        return '###' + '\t'.join(self._formatPhraseWithCorrectChrUsage(str(col), useUrlEncoding=False, \
                                 notAllowedChars='#\t') for col in columns) + os.linesep
        
    def _composeBoundingRegionLine(self, boundingRegionTuple):
        region = copy(boundingRegionTuple.region)
        
        if self._headerDict['1-indexed']:
            region.start = region.start+1 if region.start is not None else None
            region.end = region.end+1 if region.end is not None else None
        if self._headerDict['end inclusive']:
            region.end = region.end-1 if region.end is not None else None
            
        brLinePartList = [(Gtrack.convertNameToGtrack(attr), getattr(region, attr)) for attr in ['genome', 'chr', 'start', 'end']]
        return '####' + '; '.join(k + '=' + self._formatPhraseWithCorrectChrUsage(str(v), useUrlEncoding=True, notAllowedChars='=;#\t') \
                                  for k,v in brLinePartList if v is not None) + os.linesep
    
    def _composeDataLine(self, ge, hbColumns, dataLineCount, lastGE):
        cols = []
        for hbColName in hbColumns:
            if hbColName == 'start':
                cols.append( self._formatStart(ge.start) )
            elif hbColName == 'end':
                cols.append( self._formatEnd(ge.end) )
            elif hbColName == 'strand':
                cols.append( getStringFromStrand(ge.strand) )
            elif hbColName == 'val':
                cols.append( self._formatValue(ge.val) )
            elif hbColName == 'edges':
                cols.append( self._formatEdges(ge.edges, ge.weights) )
            elif hbColName == 'weights':
                pass
            else:
                cols.append(self._formatPhraseWithCorrectChrUsage(str(getattr(ge, hbColName)), \
                                                                  useUrlEncoding=True, notAllowedChars='#\t'))
        
        if self._headerDict['fixed-size data lines']:
            assert len(cols) == 1
            return cols[0] + (os.linesep if (dataLineCount * len(cols[0])) % 60 < len(cols[0]) \
                              or lastGE else '')
        else:
            return '\t'.join(cols) + os.linesep

    
    # Column specification line methods
    
    def _findHbColumns(self):
        return (['genome'] if self._geSource.genome is None and self._anyGeHasGenome and not self._hasAttrInBoundingRegion('genome') else []) + \
               (['chr'] if not self._hasAttrInBoundingRegion('chr') else []) + \
                self._geSource.getPrefixList()
        
    def _getGtrackColumnsFromHbColumns(self, hbColumns):
        return [Gtrack.convertNameToGtrack(col) for col in hbColumns if col != 'weights']
        
    def _getHbColumnsFromGtrackColumns(self, columns):
        return [Gtrack.convertNameFromGtrack(col) for col in columns]
    
    def _adjustColumnsAccordingToHeaderLines(self, hbColumns, columns):
        if self._headerDict['fixed length'] != 1:
            if not 'end' in columns:
                raise InvalidFormatError('Error: header "fixed length" does not have the default value ' \
                                         '(%s != 1), but the end prefix is not defined' % self._headerDict['fixed length'])
        
        if self._headerDict['fixed gap size'] != 0:
            if not 'start' in columns:
                raise InvalidFormatError('Error: header "fixed gap size" does not have the default value ' \
                                         '(%s != 0), but the start prefix is not defined' % self._headerDict['fixed gap size'])
            if not self._hasAttrInBoundingRegion('start'):
                raise InvalidFormatError('Error: header "fixed gap size" does not have the default value ' \
                                         '(%s != 0), but bounding regions of type B are not defined' % self._headerDict['fixed gap size'])
    
        toDelete = []
        if self._headerDict['fixed length'] != 1:
            toDelete.append('end')
        
        if self._headerDict['fixed gap size'] != 0:
            toDelete.append('start')
            
        if len(columns) > len(toDelete):
            for col in toDelete:
                del columns[columns.index(col)]
                del hbColumns[hbColumns.index(col)]
        else:
            self._headerDict['fixed length'] = 1
            self._headerDict['fixed gap size'] = 0
        
        return hbColumns, columns
        
    
    # Header specification line methods
    
    def _determineHeaderLines(self, hbColumns, columns):
        self._setHeaderDict('track type', Gtrack.getTrackTypeFromColumnSpec(columns))
        self._setHeaderDict('value type', self._getGtrackValueType())
        self._setHeaderDict('value dimension', Gtrack.getGtrackValueDimension(self._geSource.getValDim()))
        self._setHeaderDict('undirected edges', self._geSource.hasUndirectedEdges())
        self._setHeaderDict('edge weights', ('weights' in hbColumns))
        self._setHeaderDict('edge weight type', self._getGtrackEdgeWeightType())
        self._setHeaderDict('edge weight dimension', Gtrack.getGtrackValueDimension(self._geSource.getEdgeWeightDim()))
        self._setHeaderDict('uninterrupted data lines', not self._hasMoreThanOneBoundingRegion())
        self._setHeaderDict('sorted elements', self._geSource.isSorted())
        self._setHeaderDict('no overlapping elements', self._geSource.hasNoOverlappingElements())
        self._setHeaderDict('circular elements', self._geSource.hasCircularElements())
        
        compliesToSubtype = False
        if self._USE_EXTENDED_GTRACK:
            self._setHeaderDict('fixed length', self._geSource.getFixedLength())
            self._setHeaderDict('fixed gap size', self._geSource.getFixedGapSize())
            self._setHeaderDict('fixed-size data lines', self._determineIfFixedSizeDataLines(columns))
            if self._headerDict['fixed-size data lines']:
                self._setHeaderDict('data line size', self._geSource.getValDim())
            
            hbColumns, columns = self._adjustColumnsAccordingToHeaderLines(hbColumns, columns)
            hbColumns, columns, compliesToSubtype = self._determineIfFileCompliesToSubtypes(hbColumns, columns)
            
        if not compliesToSubtype:                
            self._setHeaderDict('1-indexed', self._geSource.inputIsOneIndexed())
            self._setHeaderDict('end inclusive', self._geSource.inputIsEndInclusive())
        
        for header, val in self._forcedHeaderDict.iteritems():
            if header not in self._headerDict:
                self._headerDict[header] = val
        
        return hbColumns, columns
        
    def _setHeaderDict(self, header, value):
        self._headerDict[header] = value if not header in self._forcedHeaderDict \
                                    else self._forcedHeaderDict[header]
    
    def _determineIfFixedSizeDataLines(self, columns):
        return self._headerDict['track type'] == 'function' and \
               columns == ['value'] and \
               self._headerDict['value type'] in ['binary', 'character']

    def _determineIfFileCompliesToSubtypes(self, hbColumns, columns):
        if 'subtype url' in self._forcedHeaderDict:
            subtypeUrlList = [self._forcedHeaderDict['subtype url']] \
                if self._forcedHeaderDict['subtype url'] != '' else []
        else:
            subtypeUrlList = self.GTRACK_PRIORITIZED_SUBTYPE_LIST
    
        for subtypeUrl in subtypeUrlList:
            subtypeGESource = Gtrack.getSubtypeGESource(subtypeUrl)
            subtypeColumns = subtypeGESource.getColumns(orig=False)
            subtypeHeaders = subtypeGESource.getHeaderDict()
            
            numRepeats = 2 if subtypeHeaders['subtype adherence'] == 'redefinable' else 1
            
            for repeat in range(numRepeats):
                self._setHeaderDict('1-indexed', subtypeHeaders['1-indexed'])
                self._setHeaderDict('end inclusive', subtypeHeaders['end inclusive'])
                
                if subtypeHeaders['subtype adherence'] in ['reorderable', 'free']:
                    rearrangedColumns = columns
                    rearrangedHbColumns = hbColumns
                else:
                    colSet = set(columns)
                    subtypeColSet = set(subtypeColumns)
                    
                    if subtypeHeaders['subtype adherence'] == 'redefinable':
                        colsRemoved = list(subtypeColSet - colSet)
                        colsAdded = list(colSet - subtypeColSet)
                        if len(colsRemoved) != len(colsAdded) or len(colsRemoved) > 2:
                            continue
                        
                        colsRedefinedTo = ['value', 'edges'] if repeat == 1 else ['edges', 'value']
                        
                        rearrangedColumns = []
                        i,j = (0,0)
                        for col in subtypeColumns:
                            if col in colsRemoved:
                                rearrangedColumns.append(colsRedefinedTo[i])
                                i += 1
                            elif col in colsRedefinedTo:
                                rearrangedColumns.append(colsAdded[j])
                                j += 1
                            else:
                                rearrangedColumns.append(col)
                                
                        for col in columns:
                            if col in colsAdded[j:]:
                                rearrangedColumns.append(col)
                    else:
                        rearrangedColumns = [x for x in subtypeColumns if x in colSet] + \
                                            [x for x in columns if x not in subtypeColSet]
                    rearrangedHbColumns = self._getHbColumnsFromGtrackColumns(rearrangedColumns)
                
                try:
                    tempFile = StringIO()
                    self._composeContents(tempFile, rearrangedHbColumns, rearrangedColumns, \
                                          deepcopy(self._geSource), onlyNonDefault=True, singleDataLine=True)
                        
                    gtrackGESource = Gtrack('subtype.test.' + self.getDefaultFileNameSuffix(), printWarnings=False, \
                                            strToUseInsteadOfFn=tempFile.getvalue())
                    tempFile.close()
                    
                    if gtrackGESource.compliesWithSubtype(subtypeUrl):
                        gtrackGESource._headerDict['subtype url'] = subtypeUrl
                        gtrackGESource._updateHeadersAccordingToSubtype()
                        updatedHeaders = OrderedDict([(key, val) for key,val in gtrackGESource.getHeaderDict().iteritems() \
                                          if val != Gtrack.DEFAULT_HEADER_DICT.get(key)])
                        for header in updatedHeaders:
                            self._setHeaderDict(header, updatedHeaders[header])
                        
                        return rearrangedHbColumns, rearrangedColumns, True
                except Exception, e:
                    continue
        
        return hbColumns, columns, False

    
    # Bounding region specification line methods
        
    def _hasAttrInBoundingRegion(self, attr):
        return self._geSource.hasBoundingRegionTuples() and getattr(self._geSource.getBoundingRegionTuples()[0].region, attr) is not None
        
    def _hasMoreThanOneBoundingRegion(self):
        return self._geSource.hasBoundingRegionTuples() and len(self._geSource.getBoundingRegionTuples()) > 1
    
    
    # Data line methods
        
    def _formatStart(self, start):
        return str(start + 1 if self._geSource.inputIsOneIndexed() else start)
    
    def _formatEnd(self, end):
        if self._geSource.inputIsOneIndexed():
            end += 1
        if self._geSource.inputIsEndInclusive():
            end -= 1
        return str(end)
    
    def _formatValue(self, val):
        return self._commonFormatVal(val, self._headerDict['value type'], self._headerDict['value dimension'])
    
    def _formatEdgeWeight(self, val):
        return self._commonFormatVal(val, self._headerDict['edge weight type'], self._headerDict['edge weight dimension'])
    
    def _formatPhraseWithCorrectChrUsage(self, phrase, useUrlEncoding=True, notAllowedChars=''):
        corrected = ''
        for char in phrase:
            if char not in Gtrack.ALLOWED_CHARS or char in notAllowedChars:
                if useUrlEncoding:
                    corrected += '%' + '{:0>2X}'.format(ord(char))
            else:
                corrected += char
        return corrected
    
    def _commonFormatVal(self, val, valueType, valueDim):
        valTypeInfo = Gtrack.VAL_TYPE_DICT[valueType]
        
        if valueDim == 'scalar':
            if not isinstance(val, str) and hasattr(val, '__len__') and len(val)==1:
                val = val[0]
            
            if (val == valTypeInfo.missingVal) or (isNan(val) and isNan(valTypeInfo.missingVal)):
                return '.'
            elif isinstance(val, str):
                return self._formatPhraseWithCorrectChrUsage(val, useUrlEncoding=True, notAllowedChars='#.,;=\t')
            else:
                if isinstance(val, bool):
                    return '1' if val == True else '0'
                else:
                    return str(val)
        else:
            return valTypeInfo.delim.join([self._commonFormatVal(valPart, valueType, 'scalar') for valPart in val]) \
                   if len(val) != 0 else '.'
        
    def _formatEdges(self, edges, weights):
        if len(edges) == 0:
            return '.'
        else:
            return ';'.join(self._formatPhraseWithCorrectChrUsage(edge, useUrlEncoding=True, notAllowedChars='#,;=\t') + \
                             ('=' + self._formatEdgeWeight(weights[i]) if weights is not None else '') \
                              for i,edge in enumerate(edges) )
        
        
    # Helper methods
    
    def _removeStartElementIfApplicable(self, tf, geList):
        if len(geList) > 0 and tf.isDense() and tf.isInterval() and \
                self._geSource.addsStartElementToDenseIntervals():
            return geList[1:]
        return geList
    
    def _getGtrackValueType(self):
        return self._commonGetGtrackValType(self._geSource.getValDataType(), 'value')
        
    def _getGtrackEdgeWeightType(self):
        return self._commonGetGtrackValType(self._geSource.getEdgeWeightDataType(), 'edge weight')
        
    def _commonGetGtrackValType(self, valDataType, valOrEdgeWeights):
        valDataType = valDataType.replace('|','')
        for gtrackValType, valType in Gtrack.VAL_TYPE_DICT.iteritems():
            if valType.fromNumpyTypeFunc(valDataType):
                return gtrackValType
        raise InvalidFormatError('Error: did not understand %s type: %s' % (valOrEdgeWeights, valDataType))
    
class ExtendedGtrackComposer(StdGtrackComposer):
    FILE_FORMAT_NAME = 'Extended GTrack'
    _USE_EXTENDED_GTRACK = True
