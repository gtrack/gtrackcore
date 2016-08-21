
import logging
import sys
import time

from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.track_operations.RawOperationContent import RawOperationContent
from gtrackcore.track_operations.utils.TrackHandling import \
    createTrackContentFromFile
from gtrackcore.track_operations.Genome import Genome
from gtrackcore.track_operations.utils.TrackHandling import \
    createRawResultTrackView

from gtrackcore.track_operations.raw_operations.Complement import complement

class Complement(Operator):
    """
    Creates a complementing track.
    """

    def _calculate(self, region, tv):
        logging.debug("Start call! region:{0}".format(region))

        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()

        # Get genome size.
        regionSize = len(region)

        ret = complement(starts, ends, regionSize)

        if ret is not None and len(ret[0]) != 0:
            assert len(ret) == 3
            # We do not care about info from the base track..
            # the new track will only contain the starts and ends

            tv = TrackView(region, ret[0], ret[1], None, None, None,
                           None, None, borderHandling='crop',
                           allowOverlaps=self._allowOverlap)
            return tv
        else:
            return None

    def _setConfig(self, track):
        # None changeable properties
        self._numTracks = 1
        self._trackRequirements = \
            [TrackFormatReq(dense=False, allowOverlaps=False)]
        self._resultIsTrack = True

        # Set defaults for changeable properties
        self._allowOverlap = False
        self._resultAllowOverlaps = False

        self._useFraction = False
        self._useMissingStrands = False
        self._treatMissingAsPositive = True
        # For now the result track is always of the same type as track A
        # TODO: Solve this for the case where A and b are not of the same type.
        self._resultTrackRequirements = self._trackRequirements[0]

    def _parseKwargs(self, **kwargs):
        """
        :param kwargs:
        :return: None
        """

        if 'allowOverlap' in kwargs:
            self._allowOverlap = kwargs['allowOverlap']
        else:
            self._allowOverlap = False

        if 'debug' in kwargs:
            self._debug = kwargs['debug']
        else:
            self._debug = False

        if self._debug:
            level = logging.DEBUG
        else:
            level = logging.INFO
        logging.basicConfig(stream=sys.stderr, level=level)

    def _updateTrackFormat(self):
        """
        If we enable or disable overlapping tracks as input, we need to
        update the track requirement as well.
        :return: None
        """
        if self._allowOverlap:
            self._trackRequirements = \
                [TrackFormatReq(dense=False, allowOverlaps=True)]
        else:
            self._trackRequirements = \
                [TrackFormatReq(dense=False, allowOverlaps=False)]

    def _updateResultTrackFormat(self):
        """
        There can not be overlap in the result.
        :return: None
        """
        self._resultTrackRequirements = \
            [TrackFormatReq(dense=False, allowOverlaps=False)]

    def preCalculation(self):
        pass

    def postCalculation(self, result):
        return result

    @classmethod
    def createSubParser(cls, subparsers):
        """
        Creates a subparser. Used by GTool
        :param subparsers:
        :return: None
        """
        parser = subparsers.add_parser('Complement', help='Creates new track '
                                       'that is the complement of the track '
                                       'given')
        parser.add_argument('track', help='File path of track')
        parser.add_argument('genome', help='File path of Genome definition')
        parser.add_argument('--allowOverlap', action='store_true',
                            help="Allow overlap in the input track")
        parser.set_defaults(which='Complement')

    @classmethod
    def createOperation(cls, args):
        """
        Generator classmethod used by GTool

        :param args: args from GTool
        :return: Intersect object
        """
        genome = Genome.createFromJson(args.genome)

        track = createTrackContentFromFile(genome, args.track,
                                           args.allowOverlap)

        allowOverlap = args.allowOverlap
        # TODO: use overlap...

        return Complement(track, allowOverlap=allowOverlap)

    @classmethod
    def createTrackName(cls):
        """
        Track name used by GTools when saving the track i GTrackCore
        :return: Generated track name as a string
        """
        return "complement-{0}".format(int(time.time()))

    def printResult(self):
        """
        Operation returns track, not in use
        :return:
        """
        pass
