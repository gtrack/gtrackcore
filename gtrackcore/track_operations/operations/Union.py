__author__ = 'skh'


from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track.format.TrackFormat import TrackFormat
from gtrackcore.track_operations.raw_operations.Union import union



class Union(Operator):
    _NUM_TRACKS = 2
    _TRACK_REQUIREMENTS = [TrackFormatReq(dense=False, allowOverlaps=False),
                           TrackFormatReq(dense=False, allowOverlaps=False)]
    _RESULT_ALLOW_OVERLAPS = False
    _RESULT_IS_TRACK = True
    # Find out how the TrackFormat works..
    _RESULT_TRACK_REQUIREMENTS = TrackFormat([], [], None, None, None, None, None, None)

    def _call(self, region, tv1, tv2):

        t1Starts = tv1.startsAsNumpyArray()
        t1Ends = tv1.endsAsNumpyArray()
        t2Starts = tv2.startsAsNumpyArray()
        t2Ends = tv2.endsAsNumpyArray()

        (starts, ends) = union(t1Starts, t1Ends, t2Starts, t2Ends)

        returnTv = self._createTrackView(region, starts, ends)
        return returnTv

