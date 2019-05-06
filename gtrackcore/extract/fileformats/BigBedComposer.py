import subprocess
import tempfile
from collections import OrderedDict

from extract.fileformats.BedComposer import BedComposer, ColumnInfo
from metadata.GenomeInfo import GenomeInfo
from util.CustomExceptions import InvalidFormatError


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
                         (('blockstarts', 'chromstarts'), 11, '.', ('blockcount', 'blocksizes'))]

    _BED_COLUMNS_AUTOSQL_STR = 'string chrom;       "Reference sequence chromosome or scaffold"\n \
   uint   chromStart;  "Start position in chromosome"\n \
   uint   chromEnd;    "End position in chromosome"\n \
   string name;        "Name of item."\n \
   uint score;          "Score (0-1000)"\n \
   char[1] strand;     "+ or - for strand"\n \
   uint thickStart;   "Start of where display should be thick (start codon)"\n \
   uint thickEnd;     "End of where display should be thick (stop codon)"\n \
   uint reserved;     "Used as itemRgb as of 2004-11-22"\n \
   int blockCount;    "Number of blocks"\n \
   int[blockCount] blockSizes; "Comma separated list of block sizes"\n \
   int[blockCount] chromStarts; "Start positions relative to chromStart"\n'

    _BED_COLUMNS_AUTOSQL = _BED_COLUMNS_AUTOSQL_STR.splitlines(True)

    def __init__(self, geSource):
        BedComposer.__init__(self, geSource)
        self._prefixSet = self._geSource.getPrefixList()
        self._extraCols = []
        self._bedColumnsDict = self._createColumnsDict(self._prefixSet[:])
        self._init()

    def _createColumnsDict(self, geCols):
        # handle alternative column names and case sensitivity (lowercase/camelCase)
        # returns mapped columns and extra columns that were not mapped
        cols, extraCols = self._mapColsToStandardCols(geCols)

        lastColIndex = cols[-1][1]
        for extraCol in extraCols:
            lastColIndex += 1
            cols.append((extraCol, lastColIndex, '.', ()))

        self._extraCols = extraCols

        columnsDict = OrderedDict([(colName, ColumnInfo(colIdx, defaultVal, checkExtra)) for
                                            colName, colIdx, defaultVal, checkExtra in cols])

        return columnsDict

    def _compose(self, out):
        tmpBedFile = self._getBedFile()
        tmpChromSizes = self._getChromSizesFile()

        cmds = [
            'bedToBigBed',
            tmpBedFile.name,
            tmpChromSizes.name,
            out.name
        ]
        bedtype = 'bed%s' % (self._findNumCols() - len(self._extraCols))
        tmpAutoSql = None
        if self._extraCols:
            bedtype += '+%s' % len(self._extraCols)
            autoSql = self._createAutoSql()
            tmpAutoSql = tempfile.NamedTemporaryFile(suffix='.as')
            tmpAutoSql.write(autoSql)
            tmpAutoSql.flush()
            cmds.append('-as=%s' % tmpAutoSql.name)
        cmds.append('-type=%s' % bedtype)

        try:
            subprocess.check_call(cmds)
        except subprocess.CalledProcessError:
            self._closeFiles(tmpBedFile, tmpChromSizes, tmpAutoSql)
            raise InvalidFormatError('There was an error while composing the BigBed file.')

        self._closeFiles(tmpBedFile, tmpChromSizes, tmpAutoSql)

    def returnComposed(self, ignoreEmpty=False, **kwArgs):
        tmpOut = tempfile.NamedTemporaryFile(suffix='.bb')
        self._composeCommon(tmpOut, ignoreEmpty, **kwArgs)

        composedStr = tmpOut.read()
        tmpOut.close()

        return composedStr

    def _findNumCols(self):
        return len(self._bedColumnsDict)

    def _mapColsToStandardCols(self, geCols):
        geCols.append('chr')
        cols = []
        lowercasePrefixMap = {}

        for p in geCols:
            lowercasePrefixMap[p.lower()] = p

        for colDefTuple in self._BED_COLUMNS_LIST:
            colName = colDefTuple[0]
            if colName in lowercasePrefixMap:
                self._handleStandardCol(cols, geCols, lowercasePrefixMap[colName], colDefTuple)
            elif isinstance(colName, tuple):
                for item in colName:
                    if item in lowercasePrefixMap:
                        self._handleStandardCol(cols, geCols, lowercasePrefixMap[item], colDefTuple)

        return cols, geCols

    def _handleStandardCol(self, cols, geCols, colName, colDefTuple):
        cols.append((colName,) + colDefTuple[1:])
        geCols.remove(colName)

    def _getChromSizesFile(self):
        chromSizes = GenomeInfo.getStdChrLengthDict(self._geSource.getGenome())
        tmpChromSizes = tempfile.NamedTemporaryFile(suffix='.sizes')
        for chrom, size in chromSizes.iteritems():
            tmpChromSizes.write(chrom + '\t' + str(size) + '\n')
        tmpChromSizes.flush()

        return tmpChromSizes

    def _createAutoSql(self):
        autoSqlStr = 'table FromBigBedComposer\n'
        autoSqlStr += '"Automatically genearated"\n(\n'
        autoSqlStr += ''.join(self._BED_COLUMNS_AUTOSQL[:self._findNumCols() - len(self._extraCols)])
        for extraCol in self._extraCols:
            autoSqlStr += 'string ' + extraCol + '; " extra field"\n'

        autoSqlStr += ')'

        return autoSqlStr

    def _getBedFile(self):
        tmpFile = tempfile.NamedTemporaryFile(suffix='.bed')
        BedComposer._compose(self, tmpFile)
        tmpFile.flush()

        return tmpFile

    def _closeFiles(self, tmpBedFile, tmpChromSizes, tmpAutoSql):
        tmpBedFile.close()
        tmpChromSizes.close()
        if tmpAutoSql:
            tmpAutoSql.close()
