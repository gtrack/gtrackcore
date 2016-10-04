
import logging
import sys
import time

from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.operations.Merge import Merge
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.track_operations.RawOperationContent import RawOperationContent
from gtrackcore.track_operations.utils.TrackHandling import \
    createTrackContentFromFile
from gtrackcore.track_operations.Genome import Genome
from gtrackcore.track_operations.utils.TrackHandling import \
    createRawResultTrackView


from gtrackcore.track_operations.raw_operations.Flank import flank

class Flank(Operator):
    """
    Creates a new track of flanking segments.
    """

    def __init__(self, *args, **kwargs):
        assert args[0] is not None
        self._kwargs = kwargs
        self._options = {'debug': False,
                         'allowOverlaps': False,
                         'resultAllowOverlaps': False,
                         'both': None,
                         'start': None,
                         'end': None,
                         'useFraction': False,
                         'useStrands': True,
                         'treatMissingAsNegative': False
                         }
        # Save the tracks
        self._tracks = args[0]
        self._trackFormat = self._tracks.trackFormat

        # Core properties
        self._numTracks = 1
        self._resultIsTrack = True

        # Input need to be a none dense track
        self._trackRequirements = \
            [TrackFormatReq(dense=False, allowOverlaps=self._allowOverlaps)]

        # TrackResultReq is always a segment type
        self._resultTrackRequirements = \
            TrackFormatReq(dense=False, allowOverlaps=self._resultAllowOverlaps)

        super(self.__class__, self).__init__(*args, **kwargs)

    def _calculate(self, region, tv):
        # Remove RawOperationsContent
        logging.debug("Start call! region:{0}".format(region))
        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()
        strands = tv.strandsAsNumpyArray()

        if self._useStrands:
            if strands is None or strands.size == 0:
                # Track has no strand information, ignoring strands.
                self._useStrands = False

        # Get region size.
        regionSize = len(region)

        ret = flank(starts, ends, regionSize, strands=strands,
                    start=self._start, end=self._end, both=self._both,
                    useStrands=self._useStrands,
                    useFraction=self._useFraction,
                    treatMissingAsNegative=self._treatMissingAsNegative,
                    debug=self._debug)

        if ret is not None and len(ret[0]) != 0:
            assert len(ret) == 3
            # We do not care about info from the base track..
            # the new track will only contain starts, ends and (strands if
            # present.

            starts = ret[0]
            ends = ret[1]
            strands = ret[2]

            tv = TrackView(region, starts, ends, None, strands, None,
                           None, None, borderHandling='crop',
                           allowOverlaps=True)
            return tv
        else:
            return None

    def preCalculation(self, track):
        return track

    def postCalculation(self, track):
        if not self._resultAllowOverlap:
            # Overlap not allowed in the result. Using merge to remove it
            m = Merge(track, both=True, mergeValues=True,
                      useStrands=self._useStrands,
                      mergeLinks=True, allowOverlap=False)
            res = m.calculate()
            return res
        else:
            return track

    @classmethod
    def createSubParser(cls, subparsers):
        """
        Creates a subparser. Used by GTool
        :param subparsers:
        :return: None
        """
        parser = subparsers.add_parser('Flank', help='Creates flanking '
                                                     'segments of a given '
                                                     'size')
        parser.add_argument('track', help='File path of track')
        parser.add_argument('genome', help='File path of Genome definition')
        parser.add_argument('-b', type=int, dest='both')
        parser.add_argument('-s', type=int, dest='start')
        parser.add_argument('-e', type=int, dest='end')
        parser.add_argument('-f', '--fractions', action='store_true',
                            dest='fractions',
                            help="Instead if flanks a given nr of base "
                                 "pairs, create them as a fraction of the "
                                 "features length." )
        parser.add_argument('-u', '--useStrands', action='store_true',
                            dest='useStrands',
                            help="Flow the strand direction when creating "
                                 "the flanking segments")
        parser.add_argument('--missingAsNegative', action='store_true',
                            dest='treatMissingAsNegative',
                            help="Treat any features with missing strand "
                                 "information as if they ware negative. The "
                                 "default is to treat them as positive")
        parser.add_argument('--resultAllowOverlap', action='store_true',
                            dest='resultAllowOverlaps',
                            help="Allow overlap in the resulting track")
        parser.set_defaults(which='Flank')

    def printResult(self):
        """
        Operation returns track, not in use
        :return:
        """
        pass
