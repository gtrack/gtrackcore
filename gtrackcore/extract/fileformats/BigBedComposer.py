from collections import OrderedDict

from extract.fileformats.BedComposer import BedComposer, ColumnInfo


class BigBedComposer(BedComposer):
    FILE_SUFFIXES = ['bb', 'bigbed']
    FILE_FORMAT_NAME = 'BigBed'

    _BED_COLUMNS_LIST = [('chr', 0, '', ()), \
                         ('start', 1, '', ()), \
                         ('end', 2, '', ()), \
                         (('id', 'name'), 3, '.', ()), \
                         ('val', 4, '0', ()), \
                         ('strand', 5, '.', ()), \
                         ('thickstart', 6, '0', ('thickend',)), \
                         ('thickend', 7, '0', ('thickstart',)), \
                         (('itemrgb', 'reserved'), 8, '0', ()), \
                         ('blockcount', 9, '0', ('blocksizes', 'blockstarts')), \
                         ('blocksizes', 10, '.', ('blockcount', 'blockstarts')), \
                         ('blockstarts', 11, '.', ('blockcount', 'blocksizes'))]

    def __init__(self, geSource):
        BedComposer.__init__(self, geSource)
        self._prefixSet = self._geSource.getPrefixList()
        self._bedColumnsDict = self._createColumnsDict(self._prefixSet[:])
        self._init()

    def _createColumnsDict(self, geCols):
        cols = []
        lowercasePrefixMap = {}
        geCols.append('chr')
        for p in geCols:
            lowercasePrefixMap[p.lower()] = p

        for colDefTuple in self._BED_COLUMNS_LIST:
            if colDefTuple[0] in lowercasePrefixMap:
                cols.append((lowercasePrefixMap[colDefTuple[0]],) + colDefTuple[1:])
                geCols.remove(lowercasePrefixMap[colDefTuple[0]])
            elif isinstance(colDefTuple[0], tuple):
                for item in colDefTuple[0]:
                    if item in lowercasePrefixMap:
                        cols.append((item,) + colDefTuple[1:])
                        geCols.remove(lowercasePrefixMap[item])

        lastIndex = cols[-1][1]
        for extraCol in geCols:
            lastIndex += 1
            cols.append((extraCol, lastIndex, '.', ()))

        columnsDict = OrderedDict([(colName, ColumnInfo(colIdx, defaultVal, checkExtra)) for \
                                            colName, colIdx, defaultVal, checkExtra in cols])

        return columnsDict

    def _findNumCols(self):
        return len(self._bedColumnsDict)

