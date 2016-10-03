
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
                         'allowOverlap': True,
                         'customAverageFunction': None
                         }
        # Save the tracks
        self._tracks = args

        # Operations core requirements
        self._numTracks = 1

        self._trackFormat = args[0].trackFormat

        self._trackRequirements = [TrackFormatReq(dense=False),
                                   TrackFormatReq(dense=True, interval=True)]
        self._resultIsTrack = False
        self._resultTrackRequirements = None

        super(self.__class__, self).__init__(*args, **kwargs)

    def _calculate(self, region, tv):

        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()

        nr = averageLength(starts, ends, self._customAverageFunction)

        return nr

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
        parser = subparsers.add_parser('averageLength',
                                       help='Find the average length of the '
                                            'elements in a track')
        parser.add_argument('track', help='File path of track')
        parser.add_argument('genome', help='File path of Genome definition')
        parser.set_defaults(which='Count')

    def printResult(self):
        """
        :return:
        """

        if self._resultFound:
            print(self._out)
        else:
            print("ERROR! Calculation not run!")
