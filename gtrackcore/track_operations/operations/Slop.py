__author__ = 'skh'

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


from gtrackcore.track_operations.raw_operations.Slop import slop

class Slop(Operator):
    """
    Extends all of the segments in a track a given number of BP.
    """

    def _call(self, region, tv):

        # Remove RawOperationsContent
        logging.debug("Start call! region:{0}".format(region))
        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()
        strands = None

        if not self._ignoreStrand:
            strands = tv.strandsAsNumpyArray()
            if strands is None or strands.size == 0:
                # Track has no strand information, ignoring strands.
                strands = None
                self._ignoreStrand = True

        # Get genome size.
        genomeSize = len(region)

        ret = slop(starts, ends, genomeSize, strands=strands,
                   start=self._start, end=self._end, both=self._both,
                   ignoreStrands=self._ignoreStrand,
                   resultAllowOverlap=self._resultAllowOverlaps,
                   allowOverlap=self._allowOverlap, debug=self._debug)

        if ret is not None and len(ret[0]) != 0:
            assert len(ret) == 3
            return createRawResultTrackView(ret[0], ret[1], ret[2],
                                            region, tv,
                                            self.resultAllowOverlaps)
        else:
            return None

    def _setConfig(self):
        # None changeable properties
        self._numTracks = 1
        self._trackRequirements = \
            [TrackFormatReq(dense=False, allowOverlaps=False)]

        # Set defaults for changeable properties
        self._allowOverlap = False
        self._resultAllowOverlaps = False
        self._resultIsTrack = True
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
            self._updateTrackFormat()

        if 'resultAllowOverlap' in kwargs:
            self._resultAllowOverlaps = kwargs['resultAllowOverlap']
            self._updateResultTrackFormat()

        if 'ignoreStrand' in kwargs:
            self._ignoreStrand = kwargs['ignoreStrand']
        else:
            self._ignoreStrand = False

        if 'both' in kwargs:
            self._both = kwargs['both']
            if self._both is not None:
                assert self._both > 0
        else:
            self._both = None

        if 'start' in kwargs:
            self._start = kwargs['start']
            if self._start is not None:
                assert self._start > 0

        else:
            self._start = None

        if 'end' in kwargs:
            self._end = kwargs['end']
            if self._end is not None:
                assert self._end > 0
        else:
            self._end = None

        if 'useFraction' in kwargs:
            # Define inputs as a fraction of the size of the segment.
            # To be implemented.
            raise NotImplementedError

        if 'debug' in kwargs:
            self._debug = kwargs['debug']
        else:
            self._debug = False

        if self._debug:
            print("IN DEBUG!!")
            level = logging.DEBUG
        else:
            print("IN INFO")
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
                [TrackFormatReq(dense=False, allowOverlaps=True),
                 TrackFormatReq(dense=False, allowOverlaps=True)]
        else:
            self._trackRequirements = \
                [TrackFormatReq(dense=False, allowOverlaps=False),
                 TrackFormatReq(dense=False, allowOverlaps=False)]

    def _updateResultTrackFormat(self):
        """
        If we enable or disable overlapping tracks in the result, we need to
        update the track requirement as well.
        :return: None
        """
        if self._resultAllowOverlaps:
            self._resultTrackRequirements = \
                [TrackFormatReq(dense=False, allowOverlaps=True),
                 TrackFormatReq(dense=False, allowOverlaps=True)]
        else:
            self._resultTrackRequirements = \
                [TrackFormatReq(dense=False, allowOverlaps=False),
                 TrackFormatReq(dense=False, allowOverlaps=False)]

    @classmethod
    def createSubParser(cls, subparsers):
        """
        Creates a subparser. Used by GTool
        :param subparsers:
        :return: None
        """
        parser = subparsers.add_parser('slop', help='Extends segments in a '
                                                    'track a nr of BP.')
        parser.add_argument('track', help='File path of track')
        parser.add_argument('genome', help='File path of Genome definition')
        parser.add_argument('-b', type=int, dest='both')
        parser.add_argument('-s', type=int, dest='start')
        parser.add_argument('-e', type=int, dest='end')
        parser.add_argument('--allowOverlap', action='store_true',
                            help="Allow overlap in the resulting track")
        parser.set_defaults(which='Slop')

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

        if 'both' in args:
            both = args.both
        else:
            both = None

        if 'start' in args:
            start = args.start
        else:
            start = None

        if 'end' in args:
            end = args.end
        else:
            end = None

        return Slop(track, both=both, start=start, end=end)

    @classmethod
    def createTrackName(cls):
        """
        Track name used by GTools when saving the track i GTrackCore
        :return: Generated track name as a string
        """
        return "slop-{0}".format(int(time.time()))
