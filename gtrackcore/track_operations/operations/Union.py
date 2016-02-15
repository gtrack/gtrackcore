__author__ = 'skh'


from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.TrackContents import TrackContents
import gtrackcore.track_operations.raw_operations.Union.Segments as Segments
import gtrackcore.track_operations.raw_operations.Union.Points as Points
import gtrackcore.track_operations.raw_operations.Union.ValuedPoints as \
    ValuedPoints

from gtrackcore.track_operations.exeptions.Operations import \
    OutputTrackTypeNotSupportedError



class Union(Operator):
    _NUM_TRACKS = 2
    _TRACK_REQUIREMENTS = [TrackFormatReq(dense=False, allowOverlaps=False),
                           TrackFormatReq(dense=False, allowOverlaps=False)]
    _RESULT_ALLOW_OVERLAPS = False
    _RESULT_IS_TRACK = True

    # Minimum output track (Points)
    _RESULT_TRACK_REQUIREMENTS = TrackFormat([], None, None, None, None, None,
                                             None, None)

    def _call(self, region, tv1, tv2):
        # TODO, test if input track are compatible with output requirements.
        # TODO. support overlapping tracks.
        # TODO, check for "stupid" usage. If input is Segments, and out is
        # Points.
        req = self._RESULT_TRACK_REQUIREMENTS
        if req.isDense():
            # GP, SP, F, LGP, LSF, LF, LBP
            # A dense output track type is not supported.
            # The input tracks is defined to not be dense, and a union of
            # such tracks does not make sense in this context.
            raise OutputTrackTypeNotSupportedError("Dense", "Union")
        else:
            # P, VP, S, VS, LP, LVP, LS, LVS
            if req.isValued():
                # VP, VS LVP LVS
                if req.isInterval():
                    # VS, LVS
                    if req.isLinked():
                        # LVS
                        raise OutputTrackTypeNotSupportedError(
                            "Linked Valued Segments", "Union")
                    else:
                        # VS
                        raise OutputTrackTypeNotSupportedError(
                            "Valued Segments", "Union")
                else:
                    # VP, LVP
                    if req.isLinked():
                        # LVP
                        raise OutputTrackTypeNotSupportedError(
                            "Linked Valued Points", "Union")
                    else:
                        # VP
                        t1Starts = tv1.startsAsNumpyArray()
                        t1Ends = tv1.endsAsNumpyArray()
                        t1Vals = tv1.valsAsNumpyArray()
                        t2Starts = tv2.startsAsNumpyArray()
                        t2Ends = tv2.endsAsNumpyArray()
                        t2Vals = tv2.valsAsNumpyArray()

                        (starts, ends, values) = \
                            ValuedPoints.union(t1Starts, t1Ends, t1Vals,
                                               t2Starts, t2Ends, t2Vals)
                        return self._createTrackView(region, starts, ends,
                                                     values)
            else:
                # P, S, LP, LS
                if req.isInterval():
                    # S, LS
                    if req.isLinked():
                        # LS
                        raise OutputTrackTypeNotSupportedError(
                            "Linked Segments", "Union")
                    else:
                        # Segments
                        t1Starts = tv1.startsAsNumpyArray()
                        t1Ends = tv1.endsAsNumpyArray()
                        t2Starts = tv2.startsAsNumpyArray()
                        t2Ends = tv2.endsAsNumpyArray()
                        (starts, ends) = Segments.union(t1Starts,t1Ends,
                                                        t2Starts, t2Ends)
                        return self._createTrackView(region, starts, ends)

                else:
                    # P, LP
                    if req.isLinked():
                        # Linked Points
                        raise OutputTrackTypeNotSupportedError(
                            "Linked Points", "Union")
                    else:
                        # Points
                        t1Starts = tv1.startsAsNumpyArray()
                        t1Ends = tv1.endsAsNumpyArray()
                        t2Starts = tv2.startsAsNumpyArray()
                        t2Ends = tv2.endsAsNumpyArray()
                        (starts, ends) = Points.union(t1Starts, t1Ends,
                                                      t2Starts, t2Ends)
                        return self._createTrackView(region, starts, ends)

    def setResultTrackRequirements(self, trackFormat):
        """
        Change the track requirements of the output track.
        This is done using a TrackFormat object.

        The operations needs to support the given TrackFormat object.

        :param trackFormat: A TrackFormat object that defines the output track.
        :return: None
        """

        self._RESULT_TRACK_REQUIREMENTS = trackFormat

    def setResultAllowOverlap(self, overlap):
        """
        Change if the operations allows overlaps in the result track
        :param overlap: Boolean. Allow overlaps in restult track i true.
        :return: None
        """
        self._RESULT_ALLOW_OVERLAPS = overlap

    def setAllowOverlap(self, overlap):
        """
        Change if the operation allows overlapping inputs.
        :param overlap: Boolean. Allow overlapping inputs if true
        :return: None
        """

        if overlap:
            self._TRACK_REQUIREMENTS = [TrackFormatReq(dense=False,
                                                       allowOverlaps=True),
                                        TrackFormatReq(dense=False,
                                                       allowOverlaps=True)]
        else:
            self._TRACK_REQUIREMENTS = [TrackFormatReq(dense=False,
                                                       allowOverlaps=False),
                                        TrackFormatReq(dense=False,
                                                       allowOverlaps=False)]