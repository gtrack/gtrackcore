from gtrackcore_compressed.extract.fileformats.FileFormatComposer import FileFormatComposer, MatchResult
from gtrackcore_compressed.input.wrappers.GEDependentAttributesHolder import iterateOverBRTuplesWithContainedGEs
from gtrackcore_compressed.track.format.TrackFormat import TrackFormat

class FastaComposer(FileFormatComposer):
    FILE_SUFFIXES = ['fasta', 'fas', 'fa']
    FILE_FORMAT_NAME = 'FASTA'
    
    @staticmethod
    def matchesTrackFormat(trackFormat):
        return MatchResult(match=trackFormat.reprIsDense() and trackFormat.getValTypeName() == 'Character', \
                           trackFormatName='function')

    # Compose methods
    
    def _compose(self, out):
        
        for brt, geList in iterateOverBRTuplesWithContainedGEs(self._geSource):
            chr, startEnd = str(brt.region).split(':')
            print >> out, '>%s %s' % (chr, startEnd)
             
            line = ''
            for i, ge in enumerate(geList):
                line += ge.val
                if (i+1) % 60 == 0:
                    print >> out, line
                    line = ''
            
            if i+1 % 60 != 0:
                print >> out, line