
import time

from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.raw_operations.Shift import shift
from gtrackcore.track_operations.utils.TrackHandling import \
    createRawResultTrackView
from gtrackcore.track_operations.utils.TrackHandling import \
    createTrackContentFromFile
from gtrackcore.track_operations.Genome import Genome

class Shift(Operator):

    def __init__(self, *args, **kwargs):
        self._kwargs = kwargs
        self._options = {'debug': False,
                         'allowOverlap': False,
                         'resultAllowOverlap': False,
                         'shift': None,
                         'positive': None,
                         'negative': None,
                         'fraction': False,
                         'useStrand': True,
                         'useMissingStrand': True,
                         'treatMissingAsNegative': False
                         }
        # Save the tracks
        self._tracks = args

        # Core properties
        self._numTracks = 1
        self._resultIsTrack = True
        self._trackRequirements = \
            [TrackFormatReq(dense=False, allowOverlaps=False)]
        self._resultTrackRequirements = self._trackRequirements[0]

        super(self.__class__, self).__init__(*args, **kwargs)

    def _calculate(self, region, tv):

        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()

        # TODO: only load if we need it?
        strands = tv.strandsAsNumpyArray()

        regionSize = len(region)

        ret = shift(starts, ends, regionSize, strands=strands,
                    shift=self._shift, positive=self._positive,
                    negative=self._negative, fraction=self._fraction,
                    useMissingStrand=self._useMissingStrand,
                    treatMissingAsPositive=self._treatMissingAsPositive,
                    allowOverlap=self._allowOverlap)

        if ret is not None and len(ret[0]) != 0:
            assert len(ret) == 4
            return createRawResultTrackView(ret[0], ret[1], ret[2], region,
                                            tv, self._allowOverlap,
                                            newStrands=ret[3])
        else:
            return None

    def preCalculation(self, track):
        return track

    def postCalculation(self, result):
        return result

    @classmethod
    def createSubParser(cls, subparsers):
        """
        Creates a subparser. Used by GTool
        :param subparsers:
        :return: None
        """
        parser = subparsers.add_parser('shift', help='Shift segments in track')
        parser.add_argument('trackA', help='File path of track')
        parser.add_argument('genome', help='File path of Genome definition')
        parser.add_argument('--allowOverlap', action='store_true',
                            help="Allow overlap in the resulting track")
        parser.set_defaults(which='Subtract')

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

        return Shift(track)

    def printResult(self):
        pass
