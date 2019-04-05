import subprocess
import tempfile
from collections import OrderedDict

from extract.fileformats.BedComposer import BedComposer, ColumnInfo
from input.wrappers.GENumpyArrayConverter import GENumpyArrayConverter
from metadata.GenomeInfo import GenomeInfo


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
        if geSource.isSliceSource():
            newGESource = GENumpyArrayConverter(geSource)
            BedComposer.__init__(self, newGESource)
        else:
            BedComposer.__init__(self, geSource)
        self._prefixSet = list(self._prefixSet)
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

    def _compose(self, out):
        tmpFile = tempfile.NamedTemporaryFile(suffix='.bed')
        BedComposer._compose(self, tmpFile)
        tmpFile.flush()

        genome = self._geSource.getGenome()
        chromSizes = GenomeInfo.getStdChrLengthDict(genome)
        tmpChromSizes = tempfile.NamedTemporaryFile(suffix='.sizes')
        for chr, size in chromSizes.iteritems():
            tmpChromSizes.write(chr + '\t' + str(size) + '\n')

        tmpChromSizes.flush()

        bedtype = 'bed%s' % len(self._bedColumnsDict)
        cmds = [
            'bedToBigBed',
            tmpFile.name,
            tmpChromSizes.name,
            out.name,
            '-type=%s' % bedtype
        ]
        # if _as:
        #     cmds.append('-as=%s' % _as)
        p = subprocess.call(cmds)

        tmpFile.close()
        tmpChromSizes.close()

    def _findNumCols(self):
        return len(self._bedColumnsDict)

