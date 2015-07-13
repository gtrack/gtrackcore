__author__ = 'skh'


from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track_operations.raw_operations.Union import union



class Union(Operator):
    _NUM_TRACKS = 2
    _TRACK_REQUIREMENTS = [TrackFormatReq(dense=False, allowOverlaps=False),
                           TrackFormatReq(dense=False, allowOverlaps=False)]
    _RESULT_ALLOW_OVERLAPS = False

    def _call(self, region, trackContent1, trackContent2):

        tv1 = trackContent1.getTrackView(region)
        tv2 = trackContent2.getTrackView(region)

        t1Starts = tv1.startsAsNumpyArray()
        t1Ends = tv1.endsAsNumpyArray()
        t2Starts = tv2.startsAsNumpyArray()
        t2Ends = tv2.endsAsNumpyArray()

        (starts, ends) = union(t1Starts, t1Ends, t2Starts, t2Ends)

        returnTv = self._createTrackView(region, starts, ends)
        return returnTv

