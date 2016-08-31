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

from gtrackcore.track_operations.operations.Merge import Merge

from gtrackcore.track_operations.raw_operations.Slop import slop

class Slop(Operator):
    """
    Extends all of the segments in a track a given number of BP.
    """

    def _calculate(self, region, tv):

        # Remove RawOperationsContent
        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()
        strands = None

        if self._useStrands:
            strands = tv.strandsAsNumpyArray()
            if strands is None or strands.size == 0:
                # Track has no strand information, ignoring strands.
                strands = None
                self._useStrand = False

        # Get genome size.
        genomeSize = len(region)

        ret = slop(genomeSize, starts=starts, ends=ends, strands=strands,
                   start=self._start, end=self._end, both=self._both,
                   useFraction=self._useFraction, useStrands=self._useStrands,
                   useMissingStrands=self._useMissingStrands,
                   treatMissingAsNegative=self._treatMissingAsNegative,
                   updateMissingStrand=self._updateMissingStrand,
                   ignorePositive=self._ignorePositive,
                   ignoreNegative=self._ignoreNegative, debug=self._debug)

        # slop returns start, ends, strands, index
        if ret is not None and len(ret[0]) != 0:
            assert len(ret) == 4
            if self._keepValuesAndLinks:
                return createRawResultTrackView(ret[3], region, tv,
                                                self.resultAllowOverlaps,
                                                newStarts=ret[0],
                                                newEnds=ret[1],
                                                newStrands=ret[2])
            else:
                return createRawResultTrackView(None, region, tv,
                                                self.resultAllowOverlaps,
                                                newStarts=ret[0],
                                                newEnds=ret[1],
                                                newStrands=ret[2])
        else:
            return None

    def _setConfig(self, track):
        # None changeable properties
        self._numTracks = 1
        self._trackRequirements = \
            [TrackFormatReq(dense=False, allowOverlaps=False)]
        self._resultIsTrack = True

        # Set defaults for changeable properties
        self._both = None
        self._start = None
        self._end = None
        self._useFraction = False

        # Keep the values and links from the base track.
        self._keepValuesAndLinks = True

        # Strand handling
        self._useStrands = False
        self._useMissingStrands = True
        self._treatMissingAsNegative = False
        self._ignorePositive = False
        self._ignoreNegative = False
        self._updateMissingStrand = False

        self._allowOverlap = False
        self._resultAllowOverlaps = False
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

        if 'both' in kwargs:
            self._both = kwargs['both']

        if 'start' in kwargs:
            self._start = kwargs['start']

        if 'end' in kwargs:
            self._end = kwargs['end']

        if 'useFraction' in kwargs:
            self._useFraction = kwargs['useFraction']

        if 'keepValuesAndLinks' in kwargs:
            self._keepValuesAndLInks = kwargs['keepValuesAndLinks']

        # Strand handling
        if 'useStrands' in kwargs:
            self._useStrands = kwargs['useStrands']

        if 'ignorePositive' in kwargs:
            self._ignorePositive = kwargs['ignorePositive']

        if 'ignoreNegative' in kwargs:
            self._ignoreNegative = kwargs['ignoreNegative']

        if 'useMissingStrands' in kwargs:
            self._useMissingStrands = kwargs['useMissingStrands']

        if 'treatMissingAsNegative' in kwargs:
            self._treatMissingAsNegative = kwargs['treatMissingAsNegative']

        if 'updateMissingStrand' in kwargs:
            # Update the strands array from missing to the strand value used
            self._updateMissingStrand = kwargs['updateMissingStrand']

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
        self._trackRequirements = \
            [TrackFormatReq(dense=False, allowOverlaps=self._allowOverlap)]

    def _updateResultTrackFormat(self):
        """
        If we enable or disable overlapping tracks in the result, we need to
        update the track requirement as well.
        :return: None
        """
        self._resultTrackRequirements = \
            [TrackFormatReq(dense=False, allowOverlaps=self._allowOverlap)]

    def preCalculation(self, track):
        return track

    def postCalculation(self, track):
        # TODO call merge.
        if not self._resultAllowOverlaps:
            print("Removing overlap in result!!")
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

    def printResult(self):
        pass