from gtrackcore_memmap.track.format.AllFormatConverters import getFormatConverters
from gtrackcore_memmap.track.format.TrackFormat import TrackFormatReq, NeutralTrackFormatReq
from gtrackcore_memmap.util.CustomExceptions import IncompatibleTracksError

class SampleTrackWithConverters:
    IS_MEMOIZABLE = False
    trackNo = 0
    
    def __init__(self, trackView, ignoreTrackFormat = False):
        self._tv = trackView
        self.trackName = ['dummy' + str(SampleTrackWithConverters.trackNo)]
        self._ignoreTrackFormat = ignoreTrackFormat
        SampleTrackWithConverters.trackNo += 1
        self.formatConverters = None
        self._trackFormatReq = NeutralTrackFormatReq()

    def getTrackView(self, region):
        if self.formatConverters is None:
            self.formatConverters = getFormatConverters(self._tv.trackFormat, self._trackFormatReq)
        
        if self.formatConverters == []:
            raise IncompatibleTracksError('Track with format: '\
                                          + str(self._tv.trackFormat) +
                                          ('(' + self._tv.trackFormat._val + ')' if self._tv.trackFormat._val else '') + \
                                          ' does not satisfy ' + str(self._trackFormatReq))
        
        if not self.formatConverters[0].canHandle(self._tv.trackFormat, self._trackFormatReq):
            raise IncompatibleTracksError(getClassName(self.formatConverters[0]) +\
                                          ' does not support conversion from ' + str(self._tv.trackFormat) + \
                                          ' to ' + str(self._trackFormatReq))
        return self.formatConverters[0].convert(self._tv[region.start - self._tv.genomeAnchor.start : \
                                                         region.end - self._tv.genomeAnchor.start])

    def addFormatReq(self, requestedTrackFormat):
        prevFormatReq = self._trackFormatReq
        self._trackFormatReq = TrackFormatReq.merge(self._trackFormatReq, requestedTrackFormat)
        if self._trackFormatReq is None:
            raise IncompatibleTracksError(str(prevFormatReq ) + \
                                          ' is incompatible with additional ' + str(requestedTrackFormat))
        
    
    #def addFormatReq(self, requestedTrackFormat):
        #if not self._ignoreTrackFormat and requestedTrackFormat != None and not requestedTrackFormat.isCompatibleWith(self._tv.trackFormat):
            #raise IncompatibleTracksError(str(requestedTrackFormat) + ' not compatible with ' + str(self._tv.trackFormat))
