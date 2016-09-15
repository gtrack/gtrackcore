
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
        self._kwargs = kwargs
        self._options = {'debug': False,
                         'customAverageFunction': None}

        # Save the tracks
        self._tracks = args

        # None changeable properties
        self._numTracks = 1
        self._updateTrackFormat()
        self._resultIsTrack = False

        # Set defaults for changeable properties
        self._allowOverlap = True
        self._resultAllowOverlaps = False

        # For now the result track is always of the same type as track A
        # TODO: Solve this for the case where A and b are not of the same type.
        self._resultTrackRequirements = None

        super(self.__class__, self).__init__(*args, **kwargs)

    def _calculate(self, region, tv):
        logging.debug("Start call! region:{0}".format(region))
        weights = tv.weightsAsNumpyArray()

        ret = averageLinkWeight(weights, self._customAverageFunction)

        return ret

    def _setConfig(self, trackViews):
        pass

    def _updateTrackFormat(self):
        """
        For now we do not care about overlapping inputs..
        :return: None
        """

        assert self._tracks is not None
        tv = self._tracks[0]
        assert tv is not None

        dense = tv.firstTrackView().trackFormat.isDense()

        self._trackRequirements = \
            [TrackFormatReq(dense=dense, allowOverlaps=self._allowOverlap)]

    def _updateResultTrackFormat(self):
        """
        Result is not a track
        :return: None
        """
        pass

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

    @classmethod
    def createOperation(cls, args):
        """
        Generator classmethod used by GTool

        Create one factory at the operator level

        :param args: args from GTool
        :return: Intersect object
        """
        genome = Genome.createFromJson(args.genome)

        track = createTrackContentFromFile(genome, args.track,
                                           args.allowOverlap)

        return AverageLinkWeight(track)

    @classmethod
    def createTrackName(cls):
        """
        Track name used by GTools when saving the track i GTrackCore
        :return: Generated track name as a string
        """
        return None

    def printResult(self):
        """
        Operation returns track, not in use
        :return:
        """
        pass
