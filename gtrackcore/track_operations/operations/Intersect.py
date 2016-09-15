__author__ = 'skh'

from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.raw_operations.Intersect import intersect
from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.track_operations.RawOperationContent import RawOperationContent
from gtrackcore.track_operations.utils.TrackHandling import \
    createTrackContentFromFile
from gtrackcore.track_operations.Genome import Genome
from gtrackcore.track_operations.utils.TrackHandling import \
    createRawResultTrackView

class Intersect(Operator):

    def __init__(self, *args, **kwargs):
        self._kwargs = kwargs
        self._options = {'debug': False,
                         'allowOverlap': False,
                         'resultAllowOverlap': False
                         }
        # Save the tracks
        self._tracks = args

        self._numTracks = 2
        self._trackRequirements = \
            [TrackFormatReq(dense=False, allowOverlaps=False),
             TrackFormatReq(dense=False, allowOverlaps=False)]

        # Set defaults for changeable properties
        self._resultIsTrack = True
        # For now the result track is always of the same type as track A
        # TODO: Solve this for the case where A and b are not of the same type.
        self._resultTrackRequirements = self._trackRequirements[0]

        super(self.__class__, self).__init__(*args, **kwargs)

    def _calculate(self, region, tv1, tv2):

        # TODO
        # Select with links
        #   - Follow all links in the intersect and add these segments as well.

        print("in intersect!")
        t1Starts = tv1.startsAsNumpyArray()
        t1Ends = tv1.endsAsNumpyArray()

        t2Starts = tv2.startsAsNumpyArray()
        t2Ends = tv2.endsAsNumpyArray()
        ret = intersect(t1Starts, t1Ends, t2Starts, t2Ends)

        print(ret)

        if ret is not None and len(ret[0]) != 0:
            assert len(ret) == 4

            starts = ret[0]
            ends = ret[1]
            index = ret[2]
            encoding = ret[3]

            print("in createTV: starts: {}".format(starts))
            return createRawResultTrackView(index, region, [tv1,tv2],
                                            self.resultAllowOverlaps,
                                            newStarts=starts, newEnds=ends,
                                            encoding=encoding)
        else:
            return None

    def preCalculation(self, tracks):
        return tracks

    def postCalculation(self, result):
        return result

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

        return Intersect(trackA, trackB)

    def printResult(self):
        pass
