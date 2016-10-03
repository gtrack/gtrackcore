from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.raw_operations.Coverage import coverage
from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.track_operations.utils.TrackHandling import \
    createTrackContentFromFile
from gtrackcore.track_operations.Genome import Genome
from gtrackcore.track_operations.utils.TrackHandling import \
    createRawResultTrackView

class Coverage(Operator):

    def __init__(self, *args, **kwargs):
        assert len(args) == 1

        self._kwargs = kwargs
        self._options = {'debug': False,
                         'allowOverlap': True,
                         'resultAllowOverlap': False,
                         }

        # Save the tracks
        self._tracks = args
        self._trackFormat = args[0].trackFormat

        # None changeable properties
        self._numTracks = 1
        self._resultIsTrack = False

        self._trackRequirements = [TrackFormatReq(dense=False)]
        self._resultTrackRequirements = None

        super(self.__class__, self).__init__(*args, **kwargs)

    def _calculate(self, region, tv):
        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()
        return coverage(starts, ends)


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
        parser = subparsers.add_parser('coverage', help='Find the '
                                                         'coverage of a track')
        parser.add_argument('track', help='File path of track')
        parser.add_argument('genome', help='File path of Genome definition')
        parser.add_argument('-t', '--total', action="store_true",
                            help="Sum the coverage for all of the regions")
        parser.set_defaults(which='Coverage')

    def printResult(self):
        """
        :return:
        """

        if self._resultFound:
            print(self._out)
        else:
            print("ERROR! Calculation not run!")
