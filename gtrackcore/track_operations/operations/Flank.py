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


from gtrackcore.track_operations.raw_operations.Flank import flank

class Flank(Operator):
    """
    Creates a new track of flanking segments.
    """
    # s = Slop(track, size)
    # res = Subtract(s, track)

    def __init__(self, *args, **kwargs):
        self._kwargs = kwargs
        self._options = {'both': None,
                         'start': None,
                         'end': None,
                         'useFraction': False,
                         'ignoreStrand': False,
                         'useMissingStrands': True,
                         'treatMissingAsNegative': False,
                         'resultAllowOverlaps': False,
                         'debug': False
                         }
        self._name = "Flank"

        # Move this into the track req
        #if 'allowOverlap' in kwargs:
        #    self._allowOverlap = kwargs['allowOverlap']
        #    self._updateTrackFormat()

        self._numTracks = 1
        self._trackRequirements = \
            [TrackFormatReq(dense=False, allowOverlaps=False)]
        self._resultIsTrack = True

        # Set defaults for changeable properties
        self._allowOverlap = False

        self._resultTrackRequirements = self._trackRequirements[0]

        super(self.__class__, self).__init__(*args, **kwargs)

    def _calculate(self, region, tv):
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

        ret = flank(starts, ends, genomeSize, strands=strands,
                    start=self._start, end=self._end, both=self._both,
                    ignoreStrands=self._ignoreStrand,
                    useFraction=self._useFraction,
                    useMissingStrands=self._useMissingStrands,
                    treatMissingAsPositive=self._treatMissingAsPositive,
                    allowOverlap=self._allowOverlap, debug=self._debug)

        if ret is not None and len(ret[0]) != 0:
            assert len(ret) == 3
            # We do not care about info from the base track..
            # the new track will only contain starts, ends and (strands if
            # present.

            tv = TrackView(region, ret[0], ret[1], None, ret[2], None,
                           None, None, borderHandling='crop',
                           allowOverlaps=self._allowOverlap)
            return tv
        else:
            return None

    def _setConfig(self, tracks):
        pass


    def preCalculation(self, track):
        return track

    def postCalculation(self, result):
        return result

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
        parser = subparsers.add_parser('Flank', help='Creates flanking '
                                                     'segments of a given '
                                                     'size')
        parser.add_argument('track', help='File path of track')
        parser.add_argument('genome', help='File path of Genome definition')
        parser.add_argument('-b', type=int, dest='both')
        parser.add_argument('-s', type=int, dest='start')
        parser.add_argument('-e', type=int, dest='end')
        parser.add_argument('--allowOverlap', action='store_true',
                            help="Allow overlap in the resulting track")
        parser.set_defaults(which='Flank')

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

        return Flank(track, both=both, start=start, end=end,
                     allowOverlap=allowOverlap)

    @classmethod
    def createTrackName(cls):
        """
        Track name used by GTools when saving the track i GTrackCore
        :return: Generated track name as a string
        """
        return "flank-{0}".format(int(time.time()))

    def printResult(self):
        """
        Operation returns track, not in use
        :return:
        """
        pass
