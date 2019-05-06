from extract.fileformats.FileFormatComposer import FileFormatComposer, MatchResult


class VcfComposer(FileFormatComposer):
    FILE_SUFFIXES = ['vcf']
    FILE_FORMAT_NAME = 'VCF'

    VCF_STANDARD_COLUMNS = ['CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO']

    def __init__(self, geSource):
        FileFormatComposer.__init__(self, geSource)
        colNames = self._geSource.getPrefixList()
        lastIndex = colNames.index('INFO')
        self._colNames = self.VCF_STANDARD_COLUMNS + colNames[lastIndex+1:]

    @staticmethod
    def matchesTrackFormat(trackFormat):
        return MatchResult(match=True, trackFormatName=trackFormat.getFormatName())

    def _compose(self, out):
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

            print >> out, '\t'.join([str(x) for x in composedLine])



