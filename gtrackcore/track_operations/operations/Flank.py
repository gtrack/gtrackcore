

from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.TrackContents import TrackContents
import gtrackcore.track_operations.raw_operations.Flank.Segments as Segments
from gtrackcore.track_operations.exeptions.Operations import \
    OutputTrackTypeNotSupportedError



class Flank(Operator):
    _NUM_TRACKS = 1
    _TRACK_REQUIREMENTS = [TrackFormatReq(dense=False, allowOverlaps=False)]
    _RESULT_ALLOW_OVERLAPS = False
    _RESULT_IS_TRACK = True

    # Minimum output track (Segments)
    _RESULT_TRACK_REQUIREMENTS = TrackFormat([], [], None, None, None, None,
                                             None, None)

    def __init__(self, *args):
        super(Flank, self).__init__(*args)
        self._after = True
        self._before = True
        self._flankSize = 100

    # Who do we give other arguments at create time?..
    def setAfter(self, bool):
        """
        Set the after Boolean. If set, the operation will create a flank at
        the end of each segment.
        :param bool: Boolean. Create flank from ends if True.
        :return: None.
        """
        # This is probably not the ideal way (UX or otherwise) to do this...
        # TODO: Find out how to move this to the __init__ method without
        # TODO: messing up the checkArgs method i Operator...

        self._after = bool

    def setBefore(self, bool):
        """
        Set the before boolean. If set the operation will create a flank at
        the before each segment.
        :param bool: Boolean: Create flank from start if True.
        :return: None.
        """
        self._before = bool

    def setFlankSize(self, size):
        """
        Set the size of the flank
        :param size:
        :return:
        """
        self._flankSize = size

    def _call(self, region, tv):
        # TODO, test if input track are compatible with output requirements.
        # TODO. support overlapping tracks.
        # TODO, check for "stupid" usage. If input is Segments, and out is
        # Points.

        req = self._RESULT_TRACK_REQUIREMENTS
        if req.isDense():
            # GP, SP, F, LGP, LSF, LF, LBS
            # A dense output track type is not supported.
            # For now this operation will only work on the segment type
            # tracks. If does not really make sense to create a flank on a
            # Function ect.

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
                    # Point types not supported.
                    raise OutputTrackTypeNotSupportedError(
                        "Points", "Union")
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
                        starts = tv.startsAsNumpyArray()
                        ends = tv.endsAsNumpyArray()
                        (starts, ends) = Segments.flank(starts,ends,
                                                        self._flankSize,
                                                        len(region),
                                                        before=self._before,
                                                        after=self._after)

                        return self._createTrackView(region, starts, ends)

                else:
                    # P, LP
                    # Not supported. A flank can not be a point
                    raise OutputTrackTypeNotSupportedError(
                        "Points", "Union")

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