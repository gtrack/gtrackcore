__author__ = 'skh'


from gtrackcore.track_operations.operations import Operator
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track.format.TrackFormat import TrackFormatReq


class Union(Operator):
    _NUM_TRACKS = 2
    _TRACK_REQUIREMENTS = [TrackFormatReq(dense=False, allowOverlaps=False),
                           TrackFormatReq(dense=False, allowOverlaps=False)]
    _RESULT_ALLOW_OVERLAPS = False

    def _call(self, region, trackView1, trackView):
        starts1 = trackView1.startsAsNumpyArray()



        returnTv = self._createTrackView(region, starts, ends)
        return returnTv

