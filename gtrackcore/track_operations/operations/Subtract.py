
import time

from gtrackcore.track.format.TrackFormat import TrackFormatReq

from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.raw_operations.Subtract import subtract

from gtrackcore.track_operations.utils.TrackHandling import \
    createRawResultTrackView
from gtrackcore.track_operations.utils.TrackHandling import \
    createTrackContentFromFile

from gtrackcore.track_operations.Genome import Genome

class Subtract(Operator):

    def __init__(self, *args, **kwargs):
        self._kwargs = kwargs
        self._options = {'debug': False,
                         'allowOverlaps': False,
                         'resultAllowOverlaps': False,
                         'useStrands': True
                         }

        # Save the tracks
        self._tracks = args

        # As we subtract track 2 from track 1, the track format
        # of the result is equal to track 1
        self._trackFormat = args[0].trackFormat

        # Core properties
        self._numTracks = 2
        self._resultIsTrack = True
        self._trackRequirements = \
            [TrackFormatReq(dense=False, allowOverlaps=False),
             TrackFormatReq(dense=False, allowOverlaps=False)]

        self._resultTrackRequirements = TrackFormatReq(
            name=self._trackFormat.getFormatName())

        super(self.__class__, self).__init__(*args, **kwargs)

    def _calculate(self, region, tv1, tv2):

        t1Starts = tv1.startsAsNumpyArray()
        t1Ends = tv1.endsAsNumpyArray()

        t2Starts = tv2.startsAsNumpyArray()
        t2Ends = tv2.endsAsNumpyArray()

        ret = subtract(t1Starts, t1Ends, t2Starts, t2Ends, debug=self._debug)

        if ret is not None and len(ret[0]) != 0:
            assert len(ret) == 3

            starts = ret[0]
            ends = ret[1]
            index = ret[2]

            if self._debug:
                print("Return from raw!")
                print("starts: {}".format(starts))
                print("ends:   {}".format(ends))
                print("index:  {}".format(index))

            return createRawResultTrackView(index, region, tv1,
                                            self.resultAllowOverlaps,
                                            newStarts=starts, newEnds=ends,
                                            trackFormatReq=self._resultTrackRequirements)
        else:
            return None

    def preCalculation(self, track):
        # Merge inputs
        return track

    def postCalculation(self, result):
        #remove dead links
        return result

    @classmethod
    def createSubParser(cls, subparsers):
        """
        Creates a subparser. Used by GTool
        :param subparsers:
        :return: None
        """
        parser = subparsers.add_parser('subtract', help='Subtract track B '
                                                        'from track A')
        parser.add_argument('trackA', help='File path of track A')
        parser.add_argument('trackB', help='File path of track B')
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

        trackA = createTrackContentFromFile(genome, args.trackA,
                                            args.allowOverlap)
        trackB = createTrackContentFromFile(genome, args.trackB,
                                            args.allowOverlap)

        allowOverlap = args.allowOverlap
        # TODO: use overlap...

        return Subtract(trackA, trackB)

    def printResult(self):
        """
        Result is a track. Do nothing
        :return:
        """
        pass
