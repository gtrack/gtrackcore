__author__ = 'skh'


from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.track_operations.raw_operations.Union import union


from gtrackcore.track_operations.RawOperationContent import RawOperationContent
from gtrackcore.track_operations.utils.TrackHandling import \
    createRawResultTrackView
from gtrackcore.track_operations.utils.TrackHandling import \
    createTrackContentFromFile

from gtrackcore.track_operations.Genome import Genome

class Union(Operator):
    _NUM_TRACKS = 2
    _TRACK_REQUIREMENTS = [TrackFormatReq(dense=False, allowOverlaps=False),
                           TrackFormatReq(dense=False, allowOverlaps=False)]
    _RESULT_ALLOW_OVERLAPS = False
    _RESULT_IS_TRACK = True

    # Output track (Points)
    # Change to trackFormatReq
    _RESULT_TRACK_REQUIREMENTS = TrackFormat([], None, None, None, None, None,
                                             None, None)

    _TEST = TrackFormatReq(name="points")

    def _call(self, region, tv1, tv2):
        rawTrack1 = RawOperationContent(self._resultGenome, region, tv=tv1)
        rawTrack2 = RawOperationContent(self._resultGenome, region, tv=tv2)

        ret = union(rawTrack1, rawTrack2, self._RESULT_ALLOW_OVERLAPS)

        if ret is not None:
            assert len(ret) == 3
            return createRawResultTrackView(ret[1], ret[1], ret[2],
                                            rawTrack1,
                                            self._RESULT_ALLOW_OVERLAPS)
        else:
            return None

    @classmethod
    def createSubParser(cls, subparsers):
        """
        Creates a subparser. Used by GTool
        :param subparsers:
        :return: None
        """
        parser = subparsers.add_parser('intersect', help='Find the intersect of two tracks')
        parser.add_argument('trackA', help='File path of track A')
        parser.add_argument('trackB', help='File path of track B')
        parser.add_argument('genome', help='File path of Genome definition')
        parser.add_argument('--allowOverlap', action='store_true',
                            help="Allow overlap in the resulting track")
        parser.set_defaults(which='Intersect')

    @classmethod
    def createOperation(cls, args):
        """
        Generator classmethod used by GTool

        :param args: args from GTool
        :return: Intersect object
        """
        genome = Genome.createFromJson(args.genome)

        trackA = createTrackContentFromFile(genome, args.trackA,
                                            args.allowOverlap)
        trackB = createTrackContentFromFile(genome, args.trackB,
                                            args.allowOverlap)

        allowOverlap = args.allowOverlap
        # TODO: use overlap...

        return Union(trackA, trackB)

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


