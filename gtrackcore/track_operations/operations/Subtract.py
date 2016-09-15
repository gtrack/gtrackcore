
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
                         'allowOverlap': False,
                         'resultAllowOverlap': False,
                        }
        # Save the tracks
        self._tracks = args

        # Core properties
        self._numTracks = 2
        self._resultIsTrack = True
        self._trackRequirements = \
            [TrackFormatReq(dense=False, allowOverlaps=False),
             TrackFormatReq(dense=False, allowOverlaps=False)]
        self._resultTrackRequirements = self._trackRequirements[0]

        super(self.__class__, self).__init__(*args, **kwargs)


    def _calculate(self, region, tv1, tv2):

        t1Starts = tv1.startsAsNumpyArray()
        t1Ends = tv1.endsAsNumpyArray()

        t2Starts = tv2.startsAsNumpyArray()
        t2Ends = tv2.endsAsNumpyArray()

        ret = subtract(t1Starts, t1Ends, t2Starts, t2Ends,
                    self._resultAllowOverlaps)

        if ret is not None and len(ret[0]) != 0:
            assert len(ret) == 3

            starts = ret[0]
            ends = ret[1]
            index = ret[2]
            # Check if elements from track 2 have a correct index.
            return createRawResultTrackView(index, region, tv1,
                                            self.resultAllowOverlaps,
                                            newStarts=starts, newEnds=ends)
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
