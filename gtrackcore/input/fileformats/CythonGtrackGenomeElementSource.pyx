import numpy
import os
import re
import shutil
import urllib
import urllib2

from collections import OrderedDict, namedtuple
from copy import copy
from operator import itemgetter

from gtrackcore.input.core.GenomeElement import GenomeElement
from gtrackcore.input.core.GenomeElementSource import GenomeElementSource, BoundingRegionTuple
from gtrackcore.metadata.GenomeInfo import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.util.CustomExceptions import InvalidFormatError, ShouldNotOccurError
from gtrackcore.util.CommonFunctions import getStringFromStrand, smartRecursiveEquals
from gtrackcore.util.CommonConstants import BINARY_MISSING_VAL


import pyximport;pyximport.install(setup_args={"include_dirs":numpy.get_include()},
                                    reload_support=True, language_level=2)
from input.core.CythonGenomeElementSource import CythonGenomeElementSource
from input.core.CythonGenomeElement import CythonGenomeElement
import percentcoding

class CythonGtrackGenomeElementSource(CythonGenomeElementSource):
    _VERSION = '1.0'
    FILE_SUFFIXES = ['gtrack']
    FILE_FORMAT_NAME = 'GTrack'

    GTRACK_SPEC_VERSION = '1.0'

    DEFAULT_COLUMN_SPEC = OrderedDict([('points', ['seqid', 'start']), \
                                       ('valued points', ['seqid', 'start', 'value']), \
                                       ('segments', ['seqid', 'start', 'end']), \
                                       ('valued segments', ['seqid', 'start', 'end', 'value']), \
                                       ('genome partition', ['seqid', 'end']), \
                                       ('step function', ['seqid', 'end', 'value']), \
                                       ('function', ['seqid', 'value']), \
                                       ('linked points', ['seqid', 'start', 'id', 'edges']), \
                                       ('linked valued points', ['seqid', 'start', 'value', 'id', 'edges']), \
                                       ('linked segments', ['seqid', 'start', 'end', 'id', 'edges']), \
                                       ('linked valued segments', ['seqid', 'start', 'end', 'value', 'id', 'edges']), \
                                       ('linked genome partition', ['seqid', 'end', 'id', 'edges']), \
                                       ('linked step function', ['seqid', 'end', 'value', 'id', 'edges']), \
                                       ('linked function', ['seqid', 'value', 'id', 'edges']), \
                                       ('linked base pairs', ['seqid', 'id', 'edges'])])

    DEFAULT_HEADER_DICT = OrderedDict([('gtrack version', '1.0'), \
                                       ('track type', 'segments'), \
                                       ('value type', 'number'), \
                                       ('value dimension', 'scalar'), \
                                       ('undirected edges', False), \
                                       ('edge weights', False), \
                                       ('edge weight type', 'number'), \
                                       ('edge weight dimension', 'scalar'), \
                                       ('uninterrupted data lines', False), \
                                       ('sorted elements', False), \
                                       ('no overlapping elements', False), \
                                       ('circular elements', False), \
                                       ('1-indexed', False), \
                                       ('end inclusive', False), \
                                       ('value column', 'value'), \
                                       ('edges column', 'edges'), \
                                       ('fixed length', 1), \
                                       ('fixed gap size', 0), \
                                       ('fixed-size data lines', False), \
                                       ('data line size', 1), \
                                       ('gtrack subtype', ''), \
                                       ('subtype version', '1.0'), \
                                       ('subtype url', ''), \
                                       ('subtype adherence', 'free')])

    EXTENDED_HEADERS = ['value column', 'edges column', 'fixed length', 'fixed gap size', \
                       'fixed-size data lines', 'data line size', 'gtrack subtype', \
                       'subtype version', 'subtype url', 'subtype adherence']

    RESERVED_COLUMN_NAMES = ['genome', 'seqid', 'start', 'end', 'value', 'strand', 'id', 'edges']

    CORE_COLUMN_NAMES = ['start', 'end', 'value', 'edges']


    ValTypeInfo = namedtuple('ValTypeInfo', ('pythonType', 'numpyType', 'delim', 'missingVal', 'fromNumpyTypeFunc'))

    VAL_TYPE_DICT = OrderedDict([('number', ValTypeInfo(pythonType=float, \
                                                         numpyType='float64', \
                                                         delim=',', \
                                                         missingVal=numpy.nan, \
                                                         fromNumpyTypeFunc=lambda t:t in ['int32','int64','float32','float64','float128'])), \
                                  ('binary', ValTypeInfo(pythonType=int, \
                                                         numpyType='int8', \
                                                         delim='', \
                                                         missingVal=BINARY_MISSING_VAL, \
                                                         fromNumpyTypeFunc=lambda t:t in ['int8','bool8','bool'])), \
                                  ('character', ValTypeInfo(pythonType=str, \
                                                            numpyType='S1', \
                                                            delim='', \
                                                            missingVal='', \
                                                            fromNumpyTypeFunc=lambda t:t == 'S1')), \
                                  ('category', ValTypeInfo(pythonType=str, \
                                                           numpyType='S', \
                                                           delim=',', \
                                                           missingVal='', \
                                                           fromNumpyTypeFunc=lambda t:t[0] == 'S'))])

    ALLOWED_CHARS = set([chr(x) for x in xrange(128) if x not in set(range(9)+[11,12]+range(14,32)+[127])])
    _RETURN_NUMPY_TYPES = False

    _addsStartElementToDenseIntervals = False

    searchRegex = re.compile(r'[^\x20-\x7E\x09\x0A\x0D]').search

    # def __new__(cls, *args, **kwArgs):
    #     return object.__new__(cls)

    def __init__(self, fn, *args, **kwArgs):
        CythonGenomeElementSource.__init__(self, fn, *args, **kwArgs)

        self._subtype = False if not 'subtype' in kwArgs else kwArgs['subtype']
        #self._printWarnings = False if not 'printWarnings' in kwArgs else kwArgs['printWarnings']
        self._doDenseSortingCheck = True if not 'doDenseSortingCheck' in kwArgs else kwArgs['doDenseSortingCheck']

        self._numHeaderLines = 0
        self._dataLineCountInBlock = 0

        self._headerDict = OrderedDict()
        self._headerDict.update(self.DEFAULT_HEADER_DICT)
        self._headerVariablesInFile = []
        self._subtypeHeadersNotRedefined = []
        self._origColumnSpec = None
        self._columnSpec = None
        self._defaultColumnSpec = False

        self._nonStandardFixedLength = None
        self._nonStandardFixedGapSize = None

        self._initIter()

        self._parseHeaderAndColSpecLines()
        self._updateHeadersAccordingToSubtype()
        self._checkHeaderLines()
        self._columnSpecKeys = self._columnSpec.keys()

    def _initIter(self):
        self._dataLineCountInBlock = 0

        self._valueVectorLength = None
        self._edgeWeightVectorLength = None
        self._complementEdgeWeightDict = {}

        self._elementList = []
        self._prevElement = None
        self._uniqueIds = set([])
        self._uniqueEdgeIds = set([])

        self._boundingRegionTuples = []
        self._boundingRegionType = None
        self._hasBoundingRegionTuples = None


    #
    # Parsing of header lines and column specification line
    #

    def _parseHeaderAndColSpecLines(self):
        self._mode = 1

        for line in self._getFile():
            line = line.rstrip('\r\n')
            if line.startswith('####'):
                self._setMode(4, line)
                break
            elif line.startswith('###'):
                self._setMode(3, line)
                self._parseColumnSpecLine(line)
            elif line.startswith('##'):
                self._setMode(2, line)
                self._parseHeaderLine(line)
            elif line.startswith('#') or line == '':
                pass
            else:
                break

            self._numHeaderLines+=1

        self._setMode(5, '')

    def _setMode(self, mode, line):
        '''
        Modes:
        - For 2-4 hashes: mode=num hashes
        - For 1 hash: mode is left unchanged
        - No hashes: data lines, mode=5
        '''

        if self._mode > mode:
            if mode == 3:
                raise InvalidFormatError('Error: column specification line (###) must come before any bounding region lines:' + line)
            elif mode == 2:
                raise InvalidFormatError('Error: header line (##) must come before any column specification or bounding region lines:' + line)
            else:
                raise ShouldNotOccurError()

        if mode > 3 and self._mode < 3:
            self._makeDefaultColumnSpec()

        self._mode = mode


    # Parsing of column specification line

    def _makeDefaultColumnSpec(self):
        cols = copy(self.DEFAULT_COLUMN_SPEC['segments'])
        self._createColumnSpec(cols, addAnyExtraFixedCols=False)
        self._defaultColumnSpec = True

    def _createColumnSpec(self, cols, addAnyExtraFixedCols=True):
        self._columnSpec = OrderedDict()
        for index, value in enumerate(cols):
            if value.lower() not in self._columnSpec:
                self._columnSpec[value.lower()] = index
            else:
                raise InvalidFormatError("Error: duplicate columns in column specification line: %s" % value)

        self._origColumnSpec = copy(self._columnSpec)

        if addAnyExtraFixedCols:
            if self.hasNonStandardFixedGapSize():
                self._columnSpec['start'] = len(self._columnSpec)

            if self.hasNonStandardFixedLength():
                self._columnSpec['end'] = len(self._columnSpec)

        self._updateColumnSpecWithNonStandardColumnName(stdName='value')
        self._updateColumnSpecWithNonStandardColumnName(stdName='edges')

        self._checkColumnSpecLine()

    def hasNonStandardFixedLength(self):
        if self._nonStandardFixedLength is None:
            self._nonStandardFixedLength = False
            if self._headerDict['fixed length'] > 1:
                if 'end' in self._origColumnSpec:
                    if self._printWarnings:
                        print "Warning: header variable 'fixed length' value (%s) ignored, as 'end' column is specified." % self._headerDict['fixed length']
                else:
                    self._nonStandardFixedLength = True

        return self._nonStandardFixedLength

    def hasNonStandardFixedGapSize(self):
        if self._nonStandardFixedGapSize is None:
            self._nonStandardFixedGapSize = False
            if self._headerDict['fixed gap size'] != 0:
                if any(x in self._origColumnSpec for x in ['start','end']):
                    if self._printWarnings:
                        print "Warning: header variable 'fixed gap size' value (%s) ignored, as 'start' and/or 'end' column is specified." % self._headerDict['fixed gap size']
                else:
                    self._nonStandardFixedGapSize = True

        return self._nonStandardFixedGapSize

    def getFixedLength(self):
        return self._headerDict['fixed length']

    def getFixedGapSize(self):
        return self._headerDict['fixed gap size']

    def _updateColumnSpecWithNonStandardColumnName(self, stdName):
        assert stdName in ['value', 'edges']
        nonStdColName = self._headerDict['%s column' % stdName].lower()

        if nonStdColName != stdName:
            if nonStdColName not in self._columnSpec:
                raise InvalidFormatError("Error: header variable '%s column' has non-default value, but the corresponding column '%s' is not specified." % (stdName, nonStdColName))

            if stdName in self._columnSpec:
                raise InvalidFormatError("Error: header variable '%s column' has non-default value, but the column '%s' is still in the column specification line." % (stdName, stdName))

            self._columnSpec[stdName] = self._columnSpec[nonStdColName]
            del self._columnSpec[nonStdColName]

    def _checkColumnSpecLine(self):
        for col in self._columnSpec:
            self._checkCharUsageOfPhrase(col)

        if self._headerDict['fixed-size data lines']:
            if self._headerDict['track type'] != 'function':
                raise InvalidFormatError("Error: header variable 'fixed-size data lines' is true, but track type is not 'function'. Track type: '%s'" % self._headerDict['track type'])
            if self._columnSpec.keys() != ['value']:
                raise InvalidFormatError("Error: header variable 'fixed-size data lines' is true, but column specification is incorrect. The column specification must consist of one column, the 'value' column. Columns specified: " + ', '.join(self.getColumns(orig=True)))

    def _parseColumnSpecLine(self, line):
        self._createColumnSpec(line[3:].strip().split('\t'))


    # General character usage methods

    @classmethod
    def _checkCharUsageOfPhrase(cls, phrase):
        if cls.searchRegex(phrase):
            raise InvalidFormatError(
                "Error: Invalid character in GTrack file. Offending phrase: %s" % (repr(phrase)))
        # for char in phrase:
        #     if not char in cls.ALLOWED_CHARS:
        #         raise InvalidFormatError("Error: Character %s is not allowed in GTrack file. Offending phrase: %s" % (repr(char), repr(phrase)))

        if phrase != phrase.strip():
            raise InvalidFormatError("Error: phrase %s is incorrectly specified. Phrase must not start or end with whitespace." % repr(phrase))

    @classmethod
    def urlQuote(cls, phrase):
        return urllib.quote(phrase, safe=' ')

    @classmethod
    def convertPhraseToAllowed(cls, phrase):
        return ''.join([x if x in cls.ALLOWED_CHARS and x not in '#\t' \
                        else '%' + '{:0>2X}'.format(ord(x)) for x in phrase])

    # Parsing of header lines

    def _parseHeaderLine(self, line):
        headerKey, headerVal = self.getHeaderKeyValue(line)
        if self._printWarnings and headerKey not in self.DEFAULT_HEADER_DICT:
            print "Warning: Header variable '%s' is not part of the GTrack specification version %s." % (headerKey, self.GTRACK_SPEC_VERSION)
        self._headerDict[headerKey] = headerVal
        self._headerVariablesInFile.append(headerKey)

    @classmethod
    def getHeaderKeyValue(cls, line):
        headerLine = line[2:].split(':')
        headerKey = headerLine[0].lower()
        headerVal = line[2:][len(headerKey)+1:].lstrip(' ')

        cls._checkCharUsageOfPhrase(headerKey)
        cls._checkCharUsageOfPhrase(headerVal)

        if headerKey in cls.DEFAULT_HEADER_DICT:
            typeOfValue = type(cls.DEFAULT_HEADER_DICT[headerKey])
            if typeOfValue == bool:
                if headerVal.lower() not in ['true','false']:
                    raise InvalidFormatError("Error: header value '%s' is not boolean (false/true)" % headerVal)
                headerVal = (headerVal.lower() == 'true')
            headerVal = typeOfValue(headerVal)
            if typeOfValue == str:
                headerVal = headerVal.lower()
        else:
            #headerVal = urllib.unquote(headerVal)
            headerVal = percentcoding.unquote(headerVal)

        return headerKey, headerVal


    #
    # Handling of GTrack subtypes
    #

    def _updateHeadersAccordingToSubtype(self, overrideDefaults=True):
        if self._subtype or self._headerDict['subtype url'] == '':
            return

        self._headerDict['subtype url'] = self._fixUrl(self._headerDict['subtype url'])
        subtypeGESource = self._getSubtypeGESource(self._headerDict['subtype url'], self._printWarnings)

        subtypeHeaderDict = subtypeGESource.getHeaderDictInFile()
        self._checkSubtypeHeaderDict(subtypeHeaderDict)

        fileHeaderDict = self._getFileHeaderDict(overrideDefaults)

        subtypeAdherence = self._getSubtypeAdherence(subtypeHeaderDict, fileHeaderDict)

        redefinableHeaders = self._getRedefinableHeaders(subtypeAdherence)
        self.checkHeaderCorrespondence(subtypeHeaderDict, fileHeaderDict, \
                                       redefinableHeaders, subtypeAdherence)

        self._subtypeHeadersNotRedefined = [key for key in subtypeHeaderDict.keys() if \
            (key not in redefinableHeaders) or \
            (key in redefinableHeaders and key not in fileHeaderDict)]
        self._headerDict.update( OrderedDict((key, subtypeHeaderDict[key]) for key in self._subtypeHeadersNotRedefined) )
        self._resetCachedHeaderFlags()

        if self._defaultColumnSpec:
            self._createColumnSpec(subtypeGESource.getColumns(orig=False))
        else:
            self.checkColumnSpecCorrespondence(subtypeGESource.getColumns(orig=False), \
                                               self.getColumns(orig=True), subtypeAdherence)

    @classmethod
    def _fixUrl(cls, url):
        if url.find('://') < 0:
            url = 'http://' + url
        return url

    @classmethod
    def _getSubtypeGESource(cls, url, printWarnings):
        subtypeContents = cls._downloadSubtypeFileContents(url)
        return CythonGtrackGenomeElementSource('subtype.gtrack', subtype=True, \
                                         printWarnings=printWarnings, \
                                         strToUseInsteadOfFn=subtypeContents)

    @classmethod
    def _downloadSubtypeFileContents(cls, url):
        try:
            if url.startswith('http://gtrack.no/'):
                import pkg_resources
                path = pkg_resources.resource_filename('gtrackcore', 'data')
                fn = os.sep.join([path, 'gtrack', url[17:]])
                return open(fn).read()
            else:
                return urllib2.urlopen(url).read()
        except Exception, e:
            raise InvalidFormatError('Error: problems downloading GTrack subtype with URL: %s. Please check that the URL is correct. Error message: %s' % (url, e))

    @classmethod
    def _checkSubtypeHeaderDict(cls, subtypeHeaderDict):
        if subtypeHeaderDict.get('subtype url'):
            raise InvalidFormatError("Error: header variable 'subtype url' is not allowed in subtype specification file. The subtype tried to set the value to: %s" % subtypeHeaderDict['subtype url'])

    def _getFileHeaderDict(self, overrideDefaults=True):
        fileHeaderDictInFile = self.getHeaderDictInFile()
        if overrideDefaults:
            fileHeaderDict = fileHeaderDictInFile
        else:
            fileHeaderDict = self.getHeaderDict()
            for header in fileHeaderDict:
                if (header in ['gtrack subtype', 'subtype version', 'subtype adherence'] and \
                    header not in fileHeaderDictInFile) or (header in self._subtypeHeadersNotRedefined):
                    del fileHeaderDict[header]
        return fileHeaderDict

    def _getSubtypeAdherence(self, subtypeHeaderDict, fileHeaderDict):
        subtypeAdherence = subtypeHeaderDict.get('subtype adherence')
        if subtypeAdherence is None:
            subtypeAdherence = 'free'
        if subtypeAdherence == 'free':
            if 'subtype adherence' in fileHeaderDict:
                subtypeAdherence = fileHeaderDict['subtype adherence']
        else:
            if 'subtype adherence' in fileHeaderDict and fileHeaderDict['subtype adherence'] != subtypeAdherence:
                raise InvalidFormatError("Error: the GTrack file is not allowed to override the 'subtype adherence' header variable of the subtype specification if it does not have the value 'free'.")
        return subtypeAdherence

    def _getRedefinableHeaders(self, subtypeAdherence):
        if subtypeAdherence in ['strict', 'reorderable', 'extensible']:
            return set([])
        elif subtypeAdherence == 'redefinable':
            return set(['track type', 'value type', 'value dimensions', 'edge weights', 'undirected edges', 'edge weight type', 'edge weight dimensions', 'value column', 'edges column'])
        elif subtypeAdherence == 'free':
            return set(self._headerDict.keys())

    @classmethod
    def checkHeaderCorrespondence(cls, subtypeHeaderDict, fileHeaderDict, redefinableHeaders, subtypeAdherence):
        for header in fileHeaderDict.keys():
            if not cls.headersCorrespond(subtypeHeaderDict, fileHeaderDict, header) \
                and header not in redefinableHeaders:
                    raise InvalidFormatError("Error: the GTrack file redefines the header variable '%s' compared to the subtype specification " \
                                             "file (%s != %s). The subtype adherence rule does not support this (subtype adherence: %s)." % \
                                            (header, fileHeaderDict[header], subtypeHeaderDict[header], subtypeAdherence))

    @classmethod
    def headersCorrespond(cls, dict1, dict2, header):
        if header in dict1 and header in dict2:
            return dict1[header] == dict2[header]
        return True

    def _resetCachedHeaderFlags(self):
        self._nonStandardFixedLength = None
        self._nonStandardFixedGapSize = None

    @classmethod
    def checkColumnSpecCorrespondence(cls, subtypeColumns, fileColumns, subtypeAdherence):
        if not cls.columnSpecsCorrespond(subtypeColumns, fileColumns, subtypeAdherence):
            raise InvalidFormatError("Error: the GTrack subtype with adherence '%s' does not allow the specified "\
                                     "redefinition of the column specification line: %s -> %s" \
                                     % (subtypeAdherence, ', '.join(subtypeColumns), ', '.join(fileColumns)))

    @classmethod
    def columnSpecsCorrespond(cls, subtypeColumns, fileColumns, subtypeAdherence):
        if subtypeAdherence == 'strict':
            return subtypeColumns == fileColumns
        elif subtypeAdherence == 'extensible':
            return fileColumns[:len(subtypeColumns)] == subtypeColumns and \
                all(x not in cls.CORE_COLUMN_NAMES for x in fileColumns[len(subtypeColumns):])
        elif subtypeAdherence == 'redefinable':
            redef = ('value', 'edges')
            if len(fileColumns) >= len(subtypeColumns):
                ok_redef = all([subtypeColumns[i] == fileColumns[i] for i in range(len(subtypeColumns)) \
                            if not (subtypeColumns[i] in redef or fileColumns[i] in redef) ])
                ok_samecore = set(x in cls.CORE_COLUMN_NAMES for x in subtypeColumns) == \
                            set(x in cls.CORE_COLUMN_NAMES for x in fileColumns)
                return ok_redef and ok_samecore
            return False
        elif subtypeAdherence == 'reorderable':
            fileColsSet = set(fileColumns)
            return all(x in fileColsSet for x in subtypeColumns)
        else:
            return True

    def compliesWithSubtype(self, url):
        try:
            self._headerDict['subtype url'] = url
            self._updateHeadersAccordingToSubtype(overrideDefaults=False)
            self.getPrefixList()
            result = True
        except Exception, e:
            #logException(e)
            result = False

        self.__init__(self._fn, genome=self._genome, trackName=self._trackName, \
                      external=self._external, printWarnings=self._printWarnings, \
                      strToUseInsteadOfFn=self._strToUseInsteadOfFn)
        return result

    @classmethod
    def getSubtypeGESource(cls, subtypeUrl):
        subtypeUrl = cls._fixUrl(subtypeUrl)
        return cls._getSubtypeGESource(subtypeUrl, printWarnings=False)


    #
    # Checking of header lines
    #

    def _checkHeaderLines(self):
        self._assertHeaderValueInList('gtrack version', ['1.0'])
        self._assertHeaderValueInList('track type', self.DEFAULT_COLUMN_SPEC.keys())
        self._assertHeaderValueInList('value type', ['number', 'binary', 'character', 'category'])
        self._assertHeaderValueInList('value dimension', ['scalar', 'pair', 'vector', 'list'])
        self._assertHeaderValueInList('edge weight type', ['number', 'binary', 'character', 'category'])
        self._assertHeaderValueInList('edge weight dimension', ['scalar', 'pair', 'vector', 'list'])
        self._assertHeaderValueLargerThan('fixed length', 0, equal=False)
        self._assertHeaderValueLargerThan('data line size', 1, equal=True)
        self._assertHeaderValueInList('subtype adherence', ['strict', 'extensible', 'redefinable', 'reorderable', 'free'])

        self._assertFixedGapSize()
        self._fixNoOverlappingElements()

        if not self._subtype:
            self._checkTrackType()

    def _assertHeaderValueInList(self, header, allowedList):
        if self._headerDict[header] not in allowedList:
            raise InvalidFormatError("Error: GTrack header variable '%s' is set to an " \
                "invalid value ('%s'). Valid values: %s" % (header, self._headerDict[header], ', '.join([str(x) for x in allowedList])))

    def _assertHeaderValueLargerThan(self, header, minValue, equal):
        if not ( self._headerDict[header] > minValue or (equal and self._headerDict[header] == minValue) ):
            raise InvalidFormatError("Error: GTrack header variable '%s' (%s) must be" % (header, self._headerDict[header]) +\
                                    (" equal to or" if equal else '') + " larger than %d." % minValue)

    def _fixNoOverlappingElements(self):
        trackType = self._headerDict['track type']
        if not any(x in trackType for x in ('points', 'segments')):
            # According to spec, 'no overlapping elements' is only used for point and segment tracks
            # The default value is False. This fix means that whenever 'no overlapping elements' is
            # True, we know we are dealing with point or segment tracks, even though it may be a
            # little counter-intuitive for e.g. genome partitions to have 'no overlapping elements' == False
            self._headerDict['no overlapping elements'] = False

    def _assertFixedGapSize(self):
        if self._headerDict['fixed length'] + self._headerDict['fixed gap size'] <= 0:
            raise InvalidFormatError("Error: GTrack header variable 'fixed length' and 'fixed gap size' must add to a positive number: %s + %s <= 0" % (self._headerDict['fixed length'], self._headerDict['fixed gap size']))

    def _checkTrackType(self):
        columnSpec = copy(self._columnSpec)

        for col in self.DEFAULT_COLUMN_SPEC[self._headerDict['track type']]:
            if col != 'seqid':
                if not col in columnSpec:
                    raise InvalidFormatError("Error: track type is '%s' but core reserved column '%s' is not defined." \
                                             % (self._headerDict['track type'], col))
                del columnSpec[col]

        for restCol in columnSpec:
            if restCol in self.CORE_COLUMN_NAMES:
                raise InvalidFormatError("Error: track type is '%s' but core reserved column '%s' is erroneously defined." \
                                         % (self._headerDict['track type'], restCol))


    #
    # Iteration through bounding region specification lines and data lines
    #

    def _iter(self):
        self._initIter()
        return self

    def _next(self, line):
        if line.startswith('####'): #Bounding region specification
            self._parseBoundingRegionLine(line)
            return None
        elif line.startswith('###'): #Column specification
            self._setMode(3, line) #Should raise exception
            raise ShouldNotOccurError
        elif line.startswith('##'): #Header line
            self._setMode(2, line) #Should raise exception
            raise ShouldNotOccurError
        elif line.startswith('#'): #Comment
            self._checkIfInterruptingDataLines(line)
            return None
        elif line == '': #End of file
            pass

        else: #Data line
            self._parseDataLine(line)

        return self._elementList.pop(0)

    def _anyPendingElements(self):
        return len(self._elementList) != 0


    # Parsing of bounding region lines

    def _parseBoundingRegionLine(self, line):
        boundingDict = self._parseBoundingRegionAttributes(line)

        br = GenomeRegion(genome=boundingDict.get('genome'), chr=boundingDict.get('seqid'),\
                          start=boundingDict.get('start'), end=boundingDict.get('end'))

        self._checkIfDataLinesAboveFirstBoundingRegion(line)
        self._checkAndStoreBoundingRegionType(br, line)

        if self._genome:
            self._checkSameGenomeInBoundingRegion(br)
            br.genome = self._genome

        self._checkIfInterruptingDataLines(line)

        if self._boundingRegionType == 'B':
            br = self._checkOrDeduceMissingStartEndForBoundingRegionTypeB(br, line)
            self._handleBoundingRegionLineTypeB(br)

        self._boundingRegionTuples.append(BoundingRegionTuple(br, 0))
        self._dataLineCountInBlock = 0
        self._prevElement = None

    def _parseBoundingRegionAttributes(self, line):
        line = line[4:]
        if line.count('=') != line.count(';') + 1:
            raise InvalidFormatError("Error: bounding region incorrectly specified. All attributes must have values (separated by '='), and attributes must be separated by semicolons (';').")

        self._checkCharUsageOfPhrase(line)
        # boundingDict = dict((x.lower(), urllib.unquote(y)) for x,y in \
        #                     [tuple(v.lstrip(' ').split('=')) for v in line.split(';')])
        boundingDict = dict((x.lower(), percentcoding.unquote(y)) for x,y in \
                            [tuple(v.lstrip(' ').split('=')) for v in line.split(';')])

        for key,val in boundingDict.iteritems():
            if key not in ['genome', 'seqid', 'start', 'end']:
                raise InvalidFormatError("Error: bounding region specification line contains unknown attribute: %s" % repr(key))

            self._checkCharUsageOfPhrase(val)

        return boundingDict

    def _checkIfDataLinesAboveFirstBoundingRegion(self, line):
        if self._prevElement is not None and self._boundingRegionType is None:
            raise InvalidFormatError("Error: no data lines are allowed above the first bounding region: '%s'" % line)

    def _checkAndStoreBoundingRegionType(self, br, line):
        if not br.chr:
            if not br.genome:
                raise InvalidFormatError('Error: bounding region specification line does not contain either a genome or a seqid attribute: ' + line)
            newBoundingRegionType = 'A'
            if br.start or br.end:
                raise InvalidFormatError('Error: bounding region specification line of type A contains start or end attribute: ' + line)
        else:
            newBoundingRegionType = 'B'

        if self._boundingRegionType and self._boundingRegionType != newBoundingRegionType:
            raise InvalidFormatError('Error: bounding region specification lines of both kinds (A & B) in same file: ' + line)

        self._boundingRegionType = newBoundingRegionType

    def _checkSameGenomeInBoundingRegion(self, br):
        if br.genome and br.genome != self._genome:
            raise InvalidFormatError('Error: the genome in the bounding region specification must equal to the genome specified for the track, if any: %s != %s'\
                                     % (br.genome, self._genome))

    def _checkOrDeduceMissingStartEndForBoundingRegionTypeB(self, br, line):
        br.start = self._checkValidStart(br.chr, self._parseStart(br.start) if br.start else 0)
        if br.end:
            br.end = self._checkValidEnd(br.chr, self._parseEnd(br.end), br.start if not self._headerDict['circular elements'] else None)
        else:
            if self._genome:
                br.end = GenomeInfo.getChrLen(self._genome, br.chr)
            else:
                if 'start' not in self._columnSpec:
                    raise InvalidFormatError("Error: bounding region specification line of type B without end attribute is unparsable without genome information. Parsing the end attribute is needed for track type '%s'. Faulty line: " % self._headerDict['track type'] + line)

        return br

    def _handleBoundingRegionLineTypeB(self, boundingRegion):
        br = boundingRegion

        if self.hasBoundingRegionTuples():
            lastBoundingRegion = self._boundingRegionTuples[-1].region
            self._checkBoundingRegionSorting(br, lastBoundingRegion)

        if not 'start' in self._columnSpec:
            if self._boundingRegionType != 'B':
                raise InvalidFormatError("Error: track type '%s' is dense, but bounding region specification is not of type B, as required." % self._columnSpec['track type'])

        self._checkLastBoundingRegion()

    def _checkBoundingRegionSorting(self, br, lastBoundingRegion):
        if self._headerDict['sorted elements'] and br < lastBoundingRegion:
            raise InvalidFormatError("Error: bounding regions are unsorted (%s > %s) while header variable 'sorted elements' is True." % (lastBoundingRegion, br))

    def _checkIfInterruptingDataLines(self, line):
        if self._prevElement is not None and self._headerDict['uninterrupted data lines']:
            raise InvalidFormatError("Error: header variable 'uninterrupted data lines' is true, but data lines are interrupted by the following line: '%s'" % line)


    # Handling end of file

    def _handleEndOfFile(self):
        self._checkLastBoundingRegion()
        self._checkBoundingRegionOverlap()
        self._checkEdgeIdsExist()
        self._checkUndirectedEdges()

    # Handling blank lines

    def _handleBlankLine(self):
        self._checkIfInterruptingDataLines('')

    # Parsing of data lines

    def _parseDataLine(self, line):
        dataLines = self._extractAllDataLines(line)

        for curLine in dataLines:
            self._updateCounts()

            self._checkCharUsageOfPhrase(curLine)
            cols = [x.rstrip() for x in curLine.split('\t')]
            # for col in cols:
            #     self._checkCharUsageOfPhrase(col)

            self._checkNumberOfCols(cols, curLine)
            cols = self._addFixedCols(cols)

            ge = self._createGenomeElement(cols)

            self._checkElementInsideBoundingRegionTypeB(ge)
            self._checkOverlappingAndSortedElements(ge)
            self._checkDenseSorting(ge)

            self._updateEdgeIdInfo(ge)
            self._updateUndirectedEdgesInfo(ge)

            self._prevElement = ge
            self._elementList.append(ge)

    def _extractAllDataLines(self, line):
        if self._headerDict['fixed-size data lines']:
            dataLineSize = self._headerDict['data line size']
            if len(line) % dataLineSize != 0:
                raise InvalidFormatError("Error: fixed-size data lines (size: %i) must not be broken by newlines. Line length: %i" % (dataLineSize, len(line)))
            return [line[i:i+dataLineSize] for i in range(0, len(line), dataLineSize)]
        else:
            return [line]

    def _updateCounts(self):
        if not 'start' in self.getColumnSpec(orig=True) or self.hasNonStandardFixedGapSize():
            if self._boundingRegionType != 'B':
                reason = ("header variable 'fixed gap size' has a non-default value (%s)" % \
                    self._headerDict['fixed gap size']) if self.hasNonStandardFixedGapSize() else \
                    ("track type is dense (%s)" % self._headerDict['track type'])
                raise InvalidFormatError("Error: %s, but bounding region of type B is not used." % reason)
            self._dataLineCountInBlock += 1

        if self.hasBoundingRegionTuples():
            self._boundingRegionTuples[-1].elCount += 1

    def _checkNumberOfCols(self, cols, curLine):
        if len(cols) != len(self.getColumnSpec(orig=True)):
            raise InvalidFormatError('Error: data lines must contain the same number of columns as specified in the column header. '+\
                                     'Column header (%i cols): %s. Faulty data line (%i cols): %s' % (len(self.getColumnSpec(orig=True)), ','.join(self.getColumns(orig=True)), len(cols), repr(curLine)) )

    def _addFixedCols(self, cols):
        if self.hasBoundingRegionTuples():
            lastBoundingRegion = self._boundingRegionTuples[-1].region

        if self.hasNonStandardFixedGapSize():
            startStep = self._headerDict['fixed gap size'] + self._headerDict['fixed length']
            start = lastBoundingRegion.start + (self._dataLineCountInBlock - 1) * startStep
            if self._headerDict['1-indexed']:
                start += 1
            cols += ['%s' % start]

        if self.hasNonStandardFixedLength():
            if 'start' in self._columnSpec:
                start = self._parseStart(cols[self._columnSpec['start']])
            elif self._dataLineCountInBlock == 1:
                start = lastBoundingRegion.start
            else:
                start = self._prevElement.end

            end = start + self._headerDict['fixed length']

            if self.hasBoundingRegionTuples() and lastBoundingRegion.end is not None and \
                end > lastBoundingRegion.end:
                    end = lastBoundingRegion.end

            cols += ['%s' % self.formatEnd(end)]

        return cols

    def _createGenomeElement(self, cols):
        ge = CythonGenomeElement(genome=self._curGenome())
        ge.chr = self._curSeqId(cols)

        for key in self._columnSpecKeys:
            rawValue = cols[self._columnSpec[key]]
            #value = urllib.unquote(rawValue)
            value = percentcoding.unquote(rawValue)

            if key=='genome':
                if self._curGenome() and value != self._curGenome():
                    raise InvalidFormatError("Error: genome in data line is not equal to genome in previously"
                                             " defined genome. %s != %s" % (value, self._curGenome()))
                ge.genome = value
            elif key=='seqid':
                pass #handled explicitly before..
            elif key == 'start':
                ge.start = self._checkValidStart(ge.chr, self._parseStart(value))
            elif key == 'end':
                ge.end = self._checkValidEnd(ge.chr, self._parseEnd(value), \
                                             self._parseStart(cols[self._columnSpec['start']]) \
                                             if 'start' in self._columnSpec and not self._headerDict['circular elements'] else None)
            elif key == 'strand':
                ge.strand = self._getStrandFromString(value)
            elif key == 'value':
                ge.val = self._getValInCorrectType(rawValue)
            elif key == 'id':
                value = self._checkId(value)
                ge.id = value

            elif key == 'edges':
                ge.edges, ge.weights = self._parseEdges(rawValue)
            else:
                setattr(ge, self._renameExtraKeyIfNeeded(key), self._checkIfNotEmpty(key, value))

        return ge

    def _renameExtraKeyIfNeeded(self, key):
        if key in ['extra', 'val', 'chr', 'subtype'] or key[0] == '_':
            return '__' + key
        return key

    def _curSeqId(self, cols):
        if self.hasBoundingRegionTuples():
            lastBoundingRegion = self._boundingRegionTuples[-1].region

        if 'seqid' in self._columnSpec:
            #chr = urllib.unquote(cols[self._columnSpec['seqid']])
            chr = percentcoding.unquote(cols[self._columnSpec['seqid']])
            if self.hasBoundingRegionTuples() and lastBoundingRegion.chr and chr != lastBoundingRegion.chr:
                raise InvalidFormatError("Error: sequence id in data line is not equal to sequence id"
                                         " in previous bounding region. %s != %s" % (chr, lastBoundingRegion.chr))
        else:
            if not self.hasBoundingRegionTuples() or lastBoundingRegion.chr is None:
                raise InvalidFormatError("Error: no sequence id defined in neither data line nor bounding region.")
            chr = lastBoundingRegion.chr

        return self._checkValidChr(chr) if self._genome else chr

    def _curGenome(self):
        return self._boundingRegionTuples[-1].region.genome if self.hasBoundingRegionTuples() else self._genome

    def _parseStart(self, startStr):
        return int(startStr) - (1 if self._headerDict['1-indexed'] else 0)

    def _parseEnd(self, endStr):
        return int(endStr) - (1 if self._headerDict['1-indexed'] else 0) + (1 if self._headerDict['end inclusive'] else 0)

    def _parseEdges(self, edgeStr):
        edges = []
        weights = None

        hasWeights = self._headerDict['edge weights']
        if hasWeights:
            weights = []

        if edgeStr != '.':
            for edgeSpec in edgeStr.split(';'):
                if hasWeights:
                    if not '=' in edgeSpec:
                        raise InvalidFormatError("Error: edges with weights must include an equals sign '='. Maybe the header variable 'edge weight' has the wrong value? Edge: " + edgeSpec)
                    edgeParts = edgeSpec.split('=')
                    if len(edgeParts) != 2:
                        raise InvalidFormatError("Error: edges with weights must include only one equals sign '='. Edge: " + edgeSpec)
                    edge, weight = edgeParts
                    weights.append(self._getValInCorrectType(weight, 'edge weight'))
                else:
                    if '=' in edgeSpec:
                        raise InvalidFormatError("Error: edges without weights must not include an equals sign '='. Maybe the header variable 'edge weight' has the wrong value? Edge: " + edgeSpec)
                    edge = edgeSpec
                self._checkIfNotEmpty('edge', edge)
                #edges.append(urllib.unquote(edge))
                edges.append(percentcoding.unquote(edge))

        return edges, weights

    def _checkIfNotEmpty(self, col, value):
        if value == '':
            raise InvalidFormatError("Error: value for column '%s' is missing. Missing edges must be specified with a period, '.'" % col)
        return value

    def _getValInCorrectType(self, val, valueOrEdgeWeight='value', isEmptyElement=False):
        assert valueOrEdgeWeight in ['value', 'edge weight']

        valTypeStr = self._headerDict[valueOrEdgeWeight + ' type']
        valDim = self._headerDict[valueOrEdgeWeight + ' dimension']
        vectorLength = self._getVectorLength(valueOrEdgeWeight)
        valTypeInfo = self.VAL_TYPE_DICT[valTypeStr]
        valType = valTypeInfo.pythonType if not self._RETURN_NUMPY_TYPES else numpy.dtype(valTypeInfo.numpyType).type

        valList = [x for x in (val.split(valTypeInfo.delim) if valTypeInfo.delim != '' else val)]
        if valList == []:
            valList = ['']
        elif valList == ['.'] and valDim == 'list':
            valList = []
        valLen = len(valList)

        if not isEmptyElement:
            self._checkVal(val, valueOrEdgeWeight, valDim, vectorLength, valLen, valTypeStr, valList)

        for i,el in enumerate(valList):
            #valList[i] = valTypeInfo.missingVal if el == '.' else valType(urllib.unquote(el))
            valList[i] = valTypeInfo.missingVal if el == '.' else valType(percentcoding.unquote(el))

        if not isEmptyElement:
            self._setVectorLength(valueOrEdgeWeight, valDim, vectorLength, valLen)

        if valLen == 1 and valDim in ['scalar']:
            return valList[0]

        return valList

    def _getVectorLength(self, valueOrEdgeWeight):
        return self._valueVectorLength if valueOrEdgeWeight == 'value' else self._edgeWeightVectorLength

    def _checkVal(self, val, valueOrEdgeWeight, valDim, vectorLength, valLen, valType, valList):
        commaNote = '(Note: comma delimits values in GTrack)'
        if valDim == 'scalar' and valLen > 1:
            raise InvalidFormatError("Error: the value of header line '%s dimension' is 'scalar', but dimension of %s '%s' (type: %s) is %i. %s)" % (valueOrEdgeWeight, valueOrEdgeWeight, val, valType, valLen, commaNote))
        elif valDim == 'pair' and valLen != 2:
            raise InvalidFormatError("Error: the value of header line '%s dimension' is 'pair', but dimension of %s '%s' (type: %s) is %i. %s)" % (valueOrEdgeWeight, valueOrEdgeWeight, val, valType, valLen, commaNote))
        elif valDim == 'vector' and vectorLength is not None and valLen != vectorLength:
            raise InvalidFormatError("Error: the value of header line '%s dimension' is 'vector', but dimension of %s '%s' (type: %s) is %i, different from previous dimension: %i.  %s" \
                                     % (valueOrEdgeWeight, valueOrEdgeWeight, val, valType, valLen, vectorLength, commaNote))
        elif valDim == 'vector' and valLen < 1:
            raise InvalidFormatError("Error: the value of header line '%s dimension' is 'vector', but dimension of %s '%s' (type: %s) is %i. %s" \
                                     % (valueOrEdgeWeight, valueOrEdgeWeight, val, valType, valLen, commaNote))

        for el in valList:
            if el == '':
                raise InvalidFormatError("Error: %s missing in %s phrase: %s. Missing %ss must be specified with '.'." % (valueOrEdgeWeight, valueOrEdgeWeight, repr(val), valueOrEdgeWeight))
            self._checkCharUsageOfPhrase(el)

    def _setVectorLength(self, valueOrEdgeWeight, valDim, vectorLength, valLen):
        if valDim == 'vector' and vectorLength is None:
            self._checkVectorLength(valueOrEdgeWeight, valLen)
            if valueOrEdgeWeight == 'value':
                self._valueVectorLength = valLen
            else:
                self._edgeWeightVectorLength = valLen

    def _checkVectorLength(self, valueOrEdgeWeight, vectorLength):
        pass


    # Div data line checks

    def _checkLastBoundingRegion(self):
        if 'start' in self._columnSpec or self._boundingRegionType != 'B':
            return

        if self._prevElement is None:
            if self.hasBoundingRegionTuples():
                raise InvalidFormatError('Error: bounding regions of type B must be followed by at least one data line for dense track types.')
            else:
                return

        self._checkEndOfLastBoundingRegion()

    def _checkEndOfLastBoundingRegion(self):
        lastBoundingRegion = self._boundingRegionTuples[-1].region

        if self._prevElement.end is None: #F...
            if lastBoundingRegion.end != (self._dataLineCountInBlock + lastBoundingRegion.start):
                raise InvalidFormatError('Error: for track types Function (F), Linked Function (LF) and Linked Base Pairs(LBP),'
                                         ' the "end" attribute must, if defined, be exactly equal to the "start" attribute plus'
                                         ' the number of data lines immediately following the bounding region specification line.'
                                         ' %i != %i' % (lastBoundingRegion.end, self._dataLineCountInBlock + lastBoundingRegion.start))
        else: #GP, SF, ...
            if lastBoundingRegion.end != self._prevElement.end:
                raise InvalidFormatError('Error: for track types Genome Partition (GP), Step Function (SF), Linked Genome Partition'
                                         '(LGP) and Linked Step Function (LSF), the "end" attribute must be equal to the end position'
                                         ' of the last track element immediately following the bounding region specification line.'
                                         ' %i != %i' % (lastBoundingRegion.end, self._prevElement.end))

    def _checkId(self, value):
        if value == '':
            raise InvalidFormatError("Error: empty id is not allowed.")

        value = self._checkUniqueIds(value)
        self._uniqueIds.add(value)
        return value

    def _checkUniqueIds(self, value):
        if value in self._uniqueIds:
            raise InvalidFormatError("Error: id '%s' is not unique" % value)
        return value

    def _checkElementInsideBoundingRegionTypeB(self, ge):
        if self._boundingRegionType == 'B':
            lastBoundingRegion = self._boundingRegionTuples[-1].region
            if (ge.start is not None and ge.start < lastBoundingRegion.start) or \
                (ge.end is not None and lastBoundingRegion.end is not None and ge.end > lastBoundingRegion.end):
                raise InvalidFormatError("Error: track element '%s' is outside previous bounding region: '%s'" % (ge, lastBoundingRegion))

    def _checkOverlappingAndSortedElements(self, ge):
        if self._prevElement is not None:
            if self._headerDict['no overlapping elements']:
                if ge.overlaps(self._prevElement):
                    raise InvalidFormatError("Error: genome element '%s' overlaps previous element '%s' while header variable 'no overlapping elements' is True." % (ge, self._prevElement))

            if self._headerDict['sorted elements'] and 'function' not in self._headerDict['track type']:
                if ge < self._prevElement:
                    raise InvalidFormatError("Error: genome element '%s' is smaller than previous element '%s' while header variable 'sorted elements' is True." % (ge, self._prevElement))

    def _checkDenseSorting(self, ge):
        if not self._doDenseSortingCheck or self._prevElement is None or 'start' in self._columnSpec or not 'end' in self._columnSpec:
            return

        if ge < self._prevElement:
            raise InvalidFormatError("Error: genome element '%s' is smaller than previous element '%s', while the track type is dense." % (ge, self._prevElement))

    def _updateEdgeIdInfo(self, ge):
        if ge.edges is not None:
            uniqueEdgeIds = set([])
            for edge in ge.edges:
                if edge in uniqueEdgeIds:
                    raise InvalidFormatError("Error: duplicate id in edges column: %s" % edge)
                uniqueEdgeIds.add(edge)
            self._uniqueEdgeIds.update(uniqueEdgeIds)

    def _checkEdgeIdsExist(self):
        unmatchedIds = self._uniqueEdgeIds - self._uniqueIds
        if len(unmatchedIds) > 0:
            raise InvalidFormatError("Error: the following ids specified in the 'edges' column do not exist in the dataset: " + ', '.join(sorted(unmatchedIds)))

    def _updateUndirectedEdgesInfo(self, ge):
        if ge.edges is not None and self._headerDict['undirected edges']:
            self._adjustComplementaryEdgeWeightDict(ge.id, ge.edges, ge.weights)

    def _adjustComplementaryEdgeWeightDict(self, id, edges, weights):
        #print id, edges, weights, self._complementEdgeWeightDict
        for index, edgeId in enumerate(edges):
            weight = weights[index] if weights else ''

            if id in self._complementEdgeWeightDict and edgeId in self._complementEdgeWeightDict[id]:
                if not smartRecursiveEquals(self._complementEdgeWeightDict[id][edgeId], weight):
                    raise InvalidFormatError("Error: edge ('%s' <-> '%s') is not undirected. The weight must be equal in both directions (%s != %s)" % (edgeId, id, self._complementEdgeWeightDict[id][edgeId], weights[index]))
                del self._complementEdgeWeightDict[id][edgeId]
                if len(self._complementEdgeWeightDict[id]) == 0:
                    del self._complementEdgeWeightDict[id]

            elif id == edgeId:
                continue

            elif edgeId in self._complementEdgeWeightDict:
                if id in self._complementEdgeWeightDict[edgeId]:
                    raise ShouldNotOccurError('Error: the complementary edge(%s) has already been added to self._complementEdgeWeightDict["%s"] ... ' % (id, edgeId))
                self._complementEdgeWeightDict[edgeId][id] = weight
            else:
                self._complementEdgeWeightDict[edgeId]={id:weight}

    def _checkUndirectedEdges(self):
        if self._headerDict['undirected edges']:
            if len(self._complementEdgeWeightDict) != 0:
                unmatchedPairs = []
                for toId in self._complementEdgeWeightDict:
                    for fromId in self._complementEdgeWeightDict[toId]:
                        unmatchedPairs.append((fromId, toId, self._complementEdgeWeightDict[toId][fromId]))
                raise InvalidFormatError("Error: All edges are not undirected. The following edges specifications " +\
                                         "are not matched by an opposite edge with equal weight:" + os.linesep +\
                                         os.linesep.join(["from '%s' to '%s'" % (fromId, toId) + \
                                                          (" with weight '%s'" % weight  if weight != '' else '') \
                                                          for fromId, toId, weight in unmatchedPairs]))

    def hasBoundingRegionTuples(self):
        if self._hasBoundingRegionTuples is None:
            self._hasBoundingRegionTuples = CythonGenomeElementSource.hasBoundingRegionTuples(self)

        return self._hasBoundingRegionTuples

    #
    # Public get-methods
    #

    # Headers, column specification and bounding regions

    def getFileFormatName(self):
        return ('Extended ' if self.isExtendedGtrackFile() else '') + 'GTrack'

    def getHeaderDict(self):
        return self._headerDict

    def getHeaderDictInFile(self):
        headers = self.getHeaderDict()
        return OrderedDict((x, headers[x]) for x in self._headerVariablesInFile)

    def isExtendedGtrackFile(self):
        nonDefaultHeaders = [key for key,val in self._headerDict.iteritems() \
                             if val != self.DEFAULT_HEADER_DICT.get(key)]
        return any(header in self.EXTENDED_HEADERS for header in nonDefaultHeaders)

    def getColumnSpec(self, orig=True):
        return self._origColumnSpec if orig else self._columnSpec

    def getColumns(self, orig=True):
        columnSpec = self._origColumnSpec if orig else self._columnSpec
        if not columnSpec:
            return None
        return [x[0] for x in sorted(columnSpec.items(), key=itemgetter(1))]

    @classmethod
    def getTrackTypeFromColumnSpec(cls, columnSpec):
        inverseColSpecDict = dict((tuple( sorted(set(v) & set(cls.CORE_COLUMN_NAMES)) ),k) \
                                   for k,v in cls.DEFAULT_COLUMN_SPEC.iteritems())
        coreColumns = tuple( sorted(set(columnSpec) & set(cls.CORE_COLUMN_NAMES)) )
        return inverseColSpecDict.get(coreColumns)

    def getBoundingRegionTuples(self):
        return self._boundingRegionTuples

    def isSorted(self):
        return self._headerDict['sorted elements']

    def hasCircularElements(self):
        return self._headerDict['circular elements']

    def hasNoOverlappingElements(self):
        return self._headerDict['no overlapping elements']

    def hasUndirectedEdges(self):
        return self._headerDict['undirected edges']

    def inputIsOneIndexed(self):
        return self._headerDict['1-indexed']

    def inputIsEndInclusive(self):
        return self._headerDict['end inclusive']

    # String representation of lines

    def getHeaderLines(self):
        #fixme: hide default header lines in some cases (perhaps not all? some should perhaps be obligatory?)
        return ''.join(['##' + ': '.join([k, self.urlQuote(str(v))]) + os.linesep for k, v in self.getHeaderDict().iteritems()])

    def getColSpecLine(self, orig=True):
        return '###' + '\t'.join([x for x in self.getColumns(orig)]) + os.linesep

    def formatStart(self, start):
        if self._headerDict['1-indexed']:
            start += 1
        return str(start)

    def formatEnd(self, end):
        if self._headerDict['1-indexed']:
            end += 1
        if self._headerDict['end inclusive']:
            end -= 1
        return str(end)

    @classmethod
    def convertNameFromGtrack(cls, name):
        if name == 'seqid':
            return 'chr'
        elif name == 'value':
            return 'val'
        else:
            return name

    @classmethod
    def convertNameToGtrack(cls, name):
        if name == 'chr':
            return 'seqid'
        elif name == 'val':
            return 'value'
        else:
            return name


    # Data types

    def getValDataType(self):
        return self._getValTypeCommon('value')

    def getEdgeWeightDataType(self):
        return self._getValTypeCommon('edge weight')

    def _getValTypeCommon(self, valueOrEdgeWeight='value'):
        assert valueOrEdgeWeight in ['value', 'edge weight']
        valType = self._headerDict['%s type' % valueOrEdgeWeight]
        valDim = self._headerDict['%s dimension' % valueOrEdgeWeight]

        if valueOrEdgeWeight == 'value' and self._headerDict['gtrack subtype'] == 'mean/sd'\
            or valueOrEdgeWeight == 'edge weight' and self._headerDict['gtrack subtype'] == 'mean/sd weights':
                assert valType == 'number' and valDim == 'pair'
                return 'float128'
        else:
            return self.VAL_TYPE_DICT[valType].numpyType

    # Data dimensions

    def getValDim(self):
        return self._getValDimCommon('value')

    def getEdgeWeightDim(self):
        return self._getValDimCommon('edge weight')

    def _getValDimCommon(self, valueOrEdgeWeight='value'):
        assert valueOrEdgeWeight in ['value', 'edge weight']
        valDim = self._headerDict['%s dimension' % valueOrEdgeWeight]

        if valDim == 'scalar':
            return 1
        elif valDim == 'pair':
            return 2
        elif valDim == 'vector':
            return self._getVectorLength(valueOrEdgeWeight)
        else:
            return 0

    @staticmethod
    def getGtrackValueDimension(valDim):
        assert valDim >= 0

        if valDim == 0:
            return 'list'
        elif valDim == 1:
            return 'scalar'
        elif valDim == 2:
            return 'pair'
        else:
            return 'vector'


class HbGtrackGenomeElementSource(CythonGtrackGenomeElementSource):
    _RETURN_NUMPY_TYPES = True

    _addsStartElementToDenseIntervals = True

    def __init__(self, fn, *args, **kwArgs):
        CythonGtrackGenomeElementSource.__init__(self, fn, *args, **kwArgs)

        self._storedBlankElement = None
        self._prevChrs = []

    def _iter(self):
        self._prevChrs = []

        return CythonGtrackGenomeElementSource._iter(self)

    def _checkHeaderLines(self):
        CythonGtrackGenomeElementSource._checkHeaderLines(self)
        self._assertHeaderValueInList('circular elements', [False])
        self._assertHeaderValueInList('value dimension', ['scalar', 'pair', 'vector']) # list not supported yet
        self._assertHeaderValueInList('edge weight dimension', ['scalar', 'pair', 'vector']) # list not supported yet

    def _checkVectorLength(self, valueOrEdgeWeight, vectorLength):
        if vectorLength == 1:
            raise InvalidFormatError("Error: %s dimension is 'vector', but length of %s is %i. This is not supported by the Genomic HyperBrowser." \
                                     % (valueOrEdgeWeight, valueOrEdgeWeight, vectorLength))

    def _renameExtraKeyIfNeeded(self, key):
        key = CythonGtrackGenomeElementSource._renameExtraKeyIfNeeded(self, key)
        if key in ['none', 'leftIndex', 'rightIndex']:
            return '__' + key
        return key

    def _checkEdgeIdsExist(self):
        pass

    def _checkUndirectedEdges(self):
        pass

    def _parseBoundingRegionLine(self, line):
        CythonGtrackGenomeElementSource._parseBoundingRegionLine(self, line)

        if self._boundingRegionType == 'B' and \
            ('start' not in self._columnSpec and 'end' in self._columnSpec):
            #For the added genome element at the beginning of GP/SF tracks
            self._boundingRegionTuples[-1].elCount += 1

    def _handleBoundingRegionLineTypeB(self, br):
        CythonGtrackGenomeElementSource._handleBoundingRegionLineTypeB(self, br)

        if 'start' in self._columnSpec or 'end' not in self._columnSpec:
            return

        #type GP/SF/LGP/LSF
        self._appendBlankElement(br.chr, end=br.start)

    def _checkBoundingRegionSortedPair(self, lastBoundingRegion, br):
        GenomeElementSource._checkBoundingRegionSortedPair(self, lastBoundingRegion, br)
        if br.start is not None and br.end is not None:
            if lastBoundingRegion.end == br.start:
                raise InvalidFormatError("Error: bounding regions '%s' and '%s' are adjoining (there is no gap between them)." % (lastBoundingRegion, br))

    def _appendBlankElement(self, chr, end=None):
        if self._storedBlankElement is None:
            ge = GenomeElement(isBlankElement=True)
            for col in self._columnSpec:
                if col not in ['genome','seqid','end']:
                    if col == 'start':
                        raise ShouldNotOccurError
                    elif col == 'value':
                        ge.val = self._getValInCorrectType('.', isEmptyElement=True)
                    elif col == 'strand':
                        ge.strand = True
                    elif col == 'id':
                        ge.id = ''
                    elif col == 'edges':
                        ge.edges = []
                        ge.weights = []
                    else:
                        setattr(ge, col, '')
            self._storedBlankElement = ge

        geCopy = self._storedBlankElement.getCopy()
        geCopy.genome=self._curGenome()
        geCopy.chr=chr
        if end is not None:
            geCopy.end=end

        self._elementList.append(geCopy)


class GzipGtrackGenomeElementSource(CythonGtrackGenomeElementSource):
    FILE_SUFFIXES = ['gtrack.gz']

    def _getFile(self):
        import gzip
        return gzip.open(self._fn, 'r')


class HbGzipGtrackGenomeElementSource(HbGtrackGenomeElementSource):
    FILE_SUFFIXES = ['gtrack.gz']

    def _getFile(self):
        import gzip
        return gzip.open(self._fn, 'r')
