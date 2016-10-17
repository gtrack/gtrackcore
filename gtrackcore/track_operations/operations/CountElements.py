from collections import OrderedDict

from gtrackcore.track.format.TrackFormat import TrackFormatReq

from gtrackcore.track_operations.raw_operations.CountElements import \
    countElements

from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.operations.Operator import KwArgumentInfo

class CountElements(Operator):

    _trackHelpList = ['Track to be count elements on']
    _numTracks = 1
    _resultIsTrack = False
    _trackRequirements = [TrackFormatReq(dense=False)]
    _resultTrackFormat = None

    def _calculate(self, region, tv):
        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()

        nr = countElements(starts, ends)
        return nr

    def _getKwArgumentInfoDict(self):
        return OrderedDict([
            ('debug',
             KwArgumentInfo('debug', 'd', 'Print debug info', bool, False)),
            ('resultAllowOverlap',
             KwArgumentInfo('resultAllowOverlap','o',
                            'Allow overlap in the result track.', bool,
                            False)),
            ('total',
             KwArgumentInfo('total', 't',
                            'Sum the coverage for all regions',
                            bool, False))])
