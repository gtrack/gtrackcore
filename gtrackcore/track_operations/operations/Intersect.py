__author__ = 'skh'

from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track.format.TrackFormat import TrackFormat
from gtrackcore.track_operations.raw_operations.Intersect import intersect

class Intersect(Operator):
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

        t1Vals = tv1.valsAsNumpyArray()
        t2Vals = tv2.valsAsNumpyArray()


        (starts, ends) = intersect(t1Starts, t2Starts, t1Ends=t1Ends, t2Ends=t2Ends)

        returnTv = self._createTrackView(region, starts, ends)
        return returnTv