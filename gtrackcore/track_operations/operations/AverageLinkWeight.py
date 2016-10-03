
import logging
import sys
import time

from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.track_operations.utils.TrackHandling import \
    createTrackContentFromFile
from gtrackcore.track_operations.Genome import Genome
from gtrackcore.track_operations.utils.TrackHandling import \
    createRawResultTrackView

from gtrackcore.track_operations.raw_operations.AverageLinkWeight import \
    averageLinkWeight

class AverageLinkWeight(Operator):
    """
    Find the average weight of the links in a track.
    """

    def __init__(self, *args, **kwargs):
        assert len(args) == 1

        self._kwargs = kwargs
        self._options = {'debug': False,
                         'allowOverlap': True,
                         'resultAllowOverlap': False,
                         'customAverageFunction': None}

        # Save the tracks
        self._tracks = args
        self._trackFormat = args[0].trackFormat

        # None changeable properties
        self._numTracks = 1
        self._resultIsTrack = False

        self._trackRequirements = [TrackFormatReq(linked=True)]
        self._resultTrackRequirements = None

        super(self.__class__, self).__init__(*args, **kwargs)

    def _calculate(self, region, tv):
        logging.debug("Start call! region:{0}".format(region))
        weights = tv.weightsAsNumpyArray()

        ret = averageLinkWeight(weights, self._customAverageFunction)

        return ret

    def preCalculation(self, track):
        return track

    def postCalculation(self, track):
        return track

    @classmethod
    def createSubParser(cls, subparsers):
        """
        Creates a subparser. Used by GTool
        :param subparsers:
        :return: None
        """
        parser = subparsers.add_parser('averageLinkWeight',
                                       help='Find the average weight of a '
                                            'linked track')
        parser.add_argument('track', help='File path of track')
        parser.add_argument('genome', help='File path of Genome definition')
        parser.set_defaults(which='AverageLinkWeight')

    def printResult(self):
        """
        Operation returns track, not in use
        :return:
        """
        if self._resultFound:
            print(self._out)
        else:
            print("ERROR! Calculation not run!")