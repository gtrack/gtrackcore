
from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track_operations.raw_operations.AverageLength import \
    averageLength
from gtrackcore.track_operations.Genome import Genome
from gtrackcore.track_operations.utils.TrackHandling import \
    createTrackContentFromFile

class AverageLength(Operator):

    def __init__(self, *args, **kwargs):
        self._kwargs = kwargs
        self._options = {'debug': False,
                         'allowOverlap': False,
                         'resultAllowOverlap': False
                         }
        # Save the tracks
        self._tracks = args

        # Operations core requirements
        self._numTracks = 1
        self._trackRequirements = \
            [TrackFormatReq(dense=False, allowOverlaps=True)]
        self._resultIsTrack = False
        self._resultTrackRequirements = None

        super(self.__class__, self).__init__(*args, **kwargs)



    def _calculate(self, region, tv):

        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()

        nr = averageLength(starts, ends)

        return nr

    def _updateResultTrackFormat(self):
        """
        Result is not a track. Just passing
        :return:
        """
        pass

    def _updateTrackFormat(self):
        """
        Ignore this for now. We just analyse the track as it is given.
        If the user wants to merge segments, it can be done before calling
        this operation.
        :return:
        """
        pass

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
        parser = subparsers.add_parser('averageLegnth', help='Find the average'
                                                             'length '
                                                             'of the elements'
                                                             'in a track')
        parser.add_argument('track', help='File path of track')
        parser.add_argument('genome', help='File path of Genome definition')
        parser.set_defaults(which='Count')

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

        return AverageLength(track)

    @classmethod
    def createTrackName(cls):
        """
        Result is not a track so we do not care about a name
        :param cls:
        :return:
        """
        return None

    def printResult(self):
        """
        :return:
        """

        if self._resultFound:
            print(self._out)
        else:
            print("ERROR! Calculation not run!")
