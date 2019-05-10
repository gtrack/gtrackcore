from extract.fileformats.FileFormatComposer import FileFormatComposer, MatchResult


class VcfComposer(FileFormatComposer):
    FILE_SUFFIXES = ['vcf']
    FILE_FORMAT_NAME = 'VCF'

    VCF_STANDARD_COLUMNS = ['CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO']

    def __init__(self, geSource):
        FileFormatComposer.__init__(self, geSource)
        self._colNames = self._getColNames()

    @staticmethod
    def matchesTrackFormat(trackFormat):
        return MatchResult(match=True, trackFormatName=trackFormat.getFormatName())

    def _compose(self, out):
        headersDict = self._geSource.getHeaders()
        for headerId, headerVals in headersDict.iteritems():
            for headerVal in headerVals:
                print >> out, '##' + headerId + '=' + headerVal

        print >> out, '#' + '\t'.join(self._colNames)

        for ge in self._geSource:
            composedLine = []

            for colName in self._colNames:
                if colName == 'CHROM':
                    val = ge.chr
                elif colName == 'POS':
                    val = ge.start
                elif colName == 'ALT':
                    val = ','.join(filter(None, ge.val))
                else:
                    val = getattr(ge, colName)

                composedLine.append(val)

            print >> out, '\t'.join([str(col) for col in composedLine])

    def _getColNames(self):
        colNames = self._geSource.getPrefixList()
        for stdCol in self.VCF_STANDARD_COLUMNS:
            if stdCol in colNames:
                colNames.remove(stdCol)

        colNames.remove('start')
        colNames.remove('val')
        if 'end' in colNames:
            colNames.remove('end')
        if colNames:
            colNames = sorted(colNames)
            colNames.insert(0, colNames.pop(colNames.index('FORMAT')))

        return self.VCF_STANDARD_COLUMNS + colNames
