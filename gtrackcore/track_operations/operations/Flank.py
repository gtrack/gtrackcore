

from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.TrackContents import TrackContents
import gtrackcore.track_operations.raw_operations.flank.Segments as Segments
from gtrackcore.track_operations.exeptions.Operations import \
    OutputTrackTypeNotSupportedError

from gtrackcore.track_operations.Genome import Genome
from gtrackcore.track_operations.utils.TrackHandling import \
    createTrackContentFromFile

# Add strand!
# Config as properties
class Flank(Operator):
    _NUM_TRACKS = 1
    _TRACK_REQUIREMENTS = [TrackFormatReq(dense=False, allowOverlaps=False)]
    _RESULT_ALLOW_OVERLAPS = False
    _RESULT_IS_TRACK = True

    # Minimum output track (Segments)
    _RESULT_TRACK_REQUIREMENTS = TrackFormat([], [], None, None, None, None,
                                             None, None)

    def __init__(self, *args, **kwargs):
        super(Flank, self).__init__(*args)

        assert 'flankSize' in kwargs.keys()

        if 'flankSize' in kwargs['flankSize']:
            self._flankSize = kwargs['flankSize']

        if 'atStart' in kwargs.keys():
            assert 'startSize' in kwargs.keys()
            self._atStart = kwargs['atStart']
            self._startSize = kwargs['startSize']

        if 'atEnd' in kwargs.keys():
            assert 'endSize' in kwargs.keys()
            self._atEnd = kwargs['atEnd']
            self._endSize = kwargs['endSize']

    @property
    def flankSize(self):
        return self._flankSize

    @flankSize.setter
    def flankSize(self, flankSize):
        self._flankSize = flankSize

    @property
    def atStart(self):
        return self._atStart

    @atStart.setter
    def atStart(self, atStart):
        assert isinstance(atStart, bool)
        self._atStart = atStart

    @property
    def atEnd(self):
        return self._atEnd

    @atEnd.setter
    def atEnd(self, atEnd):
        assert isinstance(atEnd, bool)

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

    @classmethod
    def createSubParser(self, subparsers):
        import argparse

        # TODO add more args
        parser = subparsers.add_parser('flank', help='Create a flank track')
        parser.add_argument('track', help='File path of base track')
        parser.add_argument('genome', help='File path of Genome definition')
        parser.add_argument('flankSize', help="Size of flanks")
        parser.add_argument('--allow_overlap', action='store_true',
                            help="Allow overlap in the resulting track")
        parser.add_argument('-s', '--strands', action='store_true',
                            help="Ignore strand")

    @classmethod
    def createOperation(cls, args):
        """
        Generator classmethod used by GTool

        :param args: args from GTool
        :return: Intersect object
        """
        genome = Genome.createFromJson(args.genome)

        track = createTrackContentFromFile(genome, args.trackA,
                                           args.allowOverlap)

        allowOverlap = args.allowOverlap
        # TODO: use overlap...

        return Flank(track)
