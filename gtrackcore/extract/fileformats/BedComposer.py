from collections import OrderedDict, namedtuple

from gtrackcore.extract.fileformats.FileFormatComposer import FileFormatComposer, MatchResult
from gtrackcore.track.format.TrackFormat import TrackFormat
from gtrackcore.util.CommonFunctions import getStringFromStrand
from gtrackcore.util.CustomExceptions import ShouldNotOccurError

ColumnInfo = namedtuple('ColumnInfo', ['colIdx', 'defaultVal', 'checkExtra'])

class BedComposer(FileFormatComposer):
    FILE_SUFFIXES = ['bed']
    FILE_FORMAT_NAME = 'BED'

    _BED_COLUMNS_LIST = [('chr', 0, '', ()), \
                         ('start', 1, '', ()), \
                         ('end', 2, '', ()), \
                         (('id','name'), 3, '.', ()), \
                         ('val', 4, '0', ()), \
                         ('strand', 5, '.', ()), \
                         ('thickstart', 6, '0', ('thickend',)), \
                         ('thickend', 7, '0', ('thickstart',)), \
                         ('itemrgb', 8, '0', ()), \
                         ('blockcount', 9, '0', ('blocksizes', 'blockstarts')), \
                         ('blocksizes', 10, '.', ('blockcount', 'blockstarts')), \
                         ('blockstarts', 11, '.', ('blockcount', 'blocksizes'))]

    def __init__(self, geSource):
        FileFormatComposer.__init__(self, geSource)
        self._prefixSet = set(self._geSource.getPrefixList())
        self._bedColumnsDict = OrderedDict([(colName, ColumnInfo(colIdx, defaultVal, checkExtra)) for \
                                            colName, colIdx, defaultVal, checkExtra in self._BED_COLUMNS_LIST])
        self._init()

    def _init(self):
        self._allValsAreBedVals = False
        tf = TrackFormat.createInstanceFromGeSource(self._geSource)
        if tf.getValTypeName() == 'Number (integer)':
            self._allValsAreBedVals = all((0 <= ge.val <= 1000) for ge in self._geSource)

    @staticmethod
    def matchesTrackFormat(trackFormat):
        trackFormatName = ''
        if trackFormat.getValTypeName() == 'Number (integer)':
            trackFormatName += 'valued '

        trackFormatName += 'segments'

        return MatchResult(match=trackFormat.isInterval() and not trackFormat.isDense(), \
                           trackFormatName=trackFormatName)

    # Compose methods

    def _compose(self, out):
        numCols = self._findNumCols()
        bedColumnsList = list(self._bedColumnsDict.iteritems())

        for ge in self._geSource:
            cols = ['']*numCols
            for i in range(numCols):
                colNames, colInfo = bedColumnsList[i]

                for colName in (colNames if type(colNames) == tuple else (colNames,)):
                    try:
                        value = getattr(ge, colName)
                    except AttributeError:
                        value = None

                    if colName == 'end':
                        value = self._handleEnd(ge, value)
                    elif colName == 'val':
                        value = self._handleVal(value)
                    elif colName == 'strand':
                        value = getStringFromStrand(value)

                    if isinstance(value, str) and colName not in ('name', 'id'):
                        if '|' in value or any('|' in getattr(ge, col) \
                                               for col in colInfo.checkExtra if hasattr(ge,col)):
                            cols[i] = colInfo.defaultVal
                        else:
                            cols[i] = value
                    else:
                        cols[i] = value if value is not None else colInfo.defaultVal

                    if colName == 'id' and value is not None:
                        break

            print >>out, '\t'.join([str(x) for x in cols])

    def _handleEnd(self, ge, value):
        return value

    def _handleVal(self, value):
        return value if self._allValsAreBedVals else None

    def _findNumCols(self):
        numCols = None
        for colNames, colInfo in reversed(list(self._bedColumnsDict.iteritems())):
            for colName in (colNames if type(colNames) == tuple else (colNames,)):
                if colName in self._prefixSet:
                    numCols = colInfo.colIdx + 1
                    assert numCols is not None and numCols >= 3
                    return numCols

        raise ShouldNotOccurError

class CategoryBedComposer(BedComposer):
    FILE_SUFFIXES = ['category.bed']
    FILE_FORMAT_NAME = 'Category BED'

    _BED_COLUMNS_LIST = [('chr', 0, '', ()), \
                         ('start', 1, '', ()), \
                         ('end', 2, '', ()), \
                         ('val', 3, '.', ()), \
                         ('score', 4, '0', ()), \
                         ('strand', 5, '.', ()), \
                         ('thickstart', 6, '0', ('thickend',)), \
                         ('thickend', 7, '0', ('thickstart',)), \
                         ('itemrgb', 8, '0', ()), \
                         ('blockcount', 9, '0', ('blocksizes', 'blockstarts')), \
                         ('blocksizes', 10, '.', ('blockcount', 'blockstarts')), \
                         ('blockstarts', 11, '.', ('blockcount', 'blocksizes'))]

    def _init(self):
        pass

    @staticmethod
    def matchesTrackFormat(trackFormat):
        return MatchResult(match=trackFormat.isInterval() and not trackFormat.isDense() \
                                 and trackFormat.getValTypeName() == 'Category', \
                           trackFormatName='valued segments')

    def _handleVal(self, value):
        return value

class ValuedBedComposer(BedComposer):
    FILE_SUFFIXES = ['valued.bed', 'marked.bed']
    FILE_FORMAT_NAME = 'Valued BED'

    def _init(self):
        pass

    @staticmethod
    def matchesTrackFormat(trackFormat):
        return MatchResult(match=trackFormat.isInterval() and not trackFormat.isDense() \
                                 and trackFormat.getValTypeName() == 'Number', \
                           trackFormatName='valued segments')

    def _handleVal(self, value):
        return self._commonFormatNumberVal(value)

class PointBedComposer(BedComposer):
    FILE_SUFFIXES = ['point.bed']
    FILE_FORMAT_NAME = 'Point BED'

    def _init(self):
        BedComposer._init(self)
        self._prefixSet.add('end')

    def _handleEnd(self, ge, value):
        return ge.start + 1

    @staticmethod
    def matchesTrackFormat(trackFormat):
        trackFormatName = ''
        if trackFormat.getValTypeName() == 'Number (integer)':
            trackFormatName += 'valued '

        trackFormatName += 'points'

        return MatchResult(match=not trackFormat.isInterval() and not trackFormat.isDense(), \
                           trackFormatName=trackFormatName)
