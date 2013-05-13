from track5.util.CustomExceptions import IncompatibleTracksError

class SampleTrack:
    IS_MEMOIZABLE = False
    trackNo = 0
    
    def __init__(self, trackView, ignoreTrackFormat = False):
        self._tv = trackView
        self.trackName = ['dummy' + str(SampleTrack.trackNo)]
        self._ignoreTrackFormat = ignoreTrackFormat
        SampleTrack.trackNo += 1

    def getTrackView(self, region):
        return self._tv[region.start - self._tv.genomeAnchor.start : region.end - self._tv.genomeAnchor.start]
    
    def addFormatReq(self, requestedTrackFormat):
        if not self._ignoreTrackFormat and requestedTrackFormat != None and not requestedTrackFormat.isCompatibleWith(self._tv.trackFormat):
            raise IncompatibleTracksError(str(requestedTrackFormat) + ' not compatible with ' + str(self._tv.trackFormat))