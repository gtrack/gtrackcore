
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

    def __init__(self, *args, **kwargs):
        self._kwargs = kwargs
        self._options = {'debug': False,
                         'trackFormatReqChangeable': False,
                         'resultTrackFormatReqChangeable': False
                         }

        self._tracks = args
        self._trackFormat = args[0]

        self._numTracks = 1
        self._resultIsTrack = True

        self._trackRequirements = \
            [TrackFormatReq(dense=False, allowOverlaps=False)]

        self._resultTrackRequirements = TrackFormatReq(dense=False,
                                                       allowOverlaps=False,
                                                       val=False,
                                                       linked=False)

        super(self.__class__, self).__init__(*args, **kwargs)

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
        parser = subparsers.add_parser('Complement', help='Creates new track '
                                       'that is the complement of the track '
                                       'given')
        parser.add_argument('track', help='File path of track')
        parser.add_argument('genome', help='File path of Genome definition')
        parser.add_argument('--allowOverlap', action='store_true',
                            help="Allow overlap in the input track")
        parser.set_defaults(which='Complement')

    def printResult(self):
        """
        Operation returns track, not in use
        :return:
        """
        pass
