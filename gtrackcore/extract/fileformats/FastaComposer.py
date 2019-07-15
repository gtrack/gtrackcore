from gtrackcore.extract.fileformats.FileFormatComposer import FileFormatComposer, MatchResult
from gtrackcore.input.wrappers.GEDependentAttributesHolder import iterateOverBRTuplesWithContainedGEs

class FastaComposer(FileFormatComposer):
    FILE_SUFFIXES = ['fasta', 'fas', 'fa']
    FILE_FORMAT_NAME = 'FASTA'
    _supportsSliceSources = True
    
    @staticmethod
    def matchesTrackFormat(trackFormat):
        return MatchResult(match=trackFormat.reprIsDense() and trackFormat.getValTypeName() == 'Character', \
                           trackFormatName='function')

    # Compose methods
    
    def _compose(self, out):
        fromSliceSource = False
        if self._geSource.isSliceSource():
            fromSliceSource = True
        for brt, geList in iterateOverBRTuplesWithContainedGEs(self._geSource):
            chr, startEnd = str(brt.region).split(':')
            print >> out, '>%s %s' % (chr, startEnd)
             
            line = ''
            for i, ge in enumerate(geList):
                if fromSliceSource:
                    vals = ge.val.tostring()
                    line += vals
                    print >> out, line
                    line = ''
                else:
                    line += ge.val
                    if (i+1) % 60 == 0:
                        print >> out, line
                        line = ''
            
            if not fromSliceSource and i+1 % 60 != 0:
                print >> out, line
