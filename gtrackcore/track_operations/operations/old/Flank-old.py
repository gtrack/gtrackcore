

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
