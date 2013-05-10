from track5.extract.fileformats.FileFormatComposer import FileFormatComposer, MatchResult
from track5.track.format.TrackFormat import TrackFormat

class BedGraphComposer(FileFormatComposer):
    FILE_SUFFIXES = ['bedgraph']
    FILE_FORMAT_NAME = 'bedGraph'
    
    @staticmethod
    def matchesTrackFormat(trackFormat):
        return MatchResult(match=trackFormat.isInterval() and not trackFormat.isDense() \
                                 and trackFormat.getValTypeName() in ['Number', 'Number (integer)'], \
                           trackFormatName='valued segments')

    # Compose methods
    
    def _compose(self, out):
        trackName = self._geSource.getTrackName()
        if trackName is not None:
            name = ':'.join(self._geSource.getTrackName()).replace(' ','_')
        else:
            name = None
        
        print >>out, 'track type=bedGraph' + (' name=%s' % name if name is not None else '')

        for ge in self._geSource:
            cols = [''] * 4
            
            cols[0] = ge.chr
            cols[1] = ge.start
            cols[2] = ge.end
            cols[3] = self._formatVal(ge.val)
            
            print >>out, '\t'.join([str(x) for x in cols])
            
    def _formatVal(self, value):
        return self._commonFormatNumberVal(value)

class BedGraphTargetControlComposer(BedGraphComposer):
    FILE_SUFFIXES = ['targetcontrol.bedgraph']
    FILE_FORMAT_NAME = 'target/control bedGraph'
    
    @staticmethod
    def matchesTrackFormat(trackFormat):
        return MatchResult(match=trackFormat.isInterval() and not trackFormat.isDense() \
                                 and trackFormat.getValTypeName() == 'Case-control', \
                           trackFormatName='valued segments')
            
    def _formatVal(self, value):
        return self._commonFormatBinaryVal(value)