
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


from gtrackcore.track_operations.raw_operations.Merge import merge

class Merge(Operator):
    """
    Merge overlapping segments in a track.

    None dense tracks only
    """

    def _calculate(self, region, tv):
        # Remove RawOperationsContent
        logging.debug("Start call! region:{0}".format(region))
        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()
        strands = None
        values = None

        if self._useStrands:
            strands = tv.strandsAsNumpyArray()
            if strands is None or strands.size == 0:
                # Track has no strand information, ignoring strands.
                strands = None
                self._useStrands = True
        if self._useValues:
            values = tv.valsAsNumpyArray()
            if values is None or values.size == 0:
                # Track has no values, ignoring..
                values = None
                self._useValues = False

        ret = merge(starts, ends, strands=strands, values=values,
                    useStrands=self._useStrands,
                    useMissingStrands=self._useMissingStrands,
                    treatMissingAsPositive=self._treatMissingAsPositive,
                    useValues=self._useValues,
                    valueFunction=self._valueFunction)

        if ret is not None and len(ret[0]) != 0:
            assert len(ret) == 3
            # We do not care about info from the base track..
            # the new track will only contain starts, ends and (strands if
            # present.

            print("In return:")
            print("starts: {}".format(ret[0]))
            print("ends: {}".format(ret[1]))
            print("values: {}".format(ret[2]))

            tv = TrackView(region, ret[0], ret[1], ret[2], None, None,
                           None, None, borderHandling='crop',
                           allowOverlaps=self._allowOverlap)
            return tv
        else:
            return None

    def _setConfig(self):
        # None changeable properties
        self._numTracks = 1
        self._trackRequirements = \
            [TrackFormatReq(dense=False, allowOverlaps=False)]
        self._resultIsTrack = True

        # Set defaults for changeable properties

        self._useValues = False
        self._valueFunction = None

        self._useStrands = False
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

        if 'useValues' in kwargs:
            self._useValues = kwargs['useValues']

        if 'valueFunction' in kwargs:
            self._valueFunction = kwargs['valueFunction']

        if 'useStrands' in kwargs:
            self._useStrands = kwargs['useStrands']

        if 'useMissingStrands' in kwargs:
            self._useMissingStrands = kwargs['useMissingStrands']
        else:
            self._useMissingStrands = False

        if 'treatMissingAsPositive' in kwargs:
            self._treatMissingAsPositive = kwargs['treatMissingAsPositive']

        if 'debug' in kwargs:
            self._debug = kwargs['debug']
        else:
            self._debug = False

        if self._debug:
            level = logging.DEBUG
        else:
            level = logging.INFO
        logging.basicConfig(stream=sys.stderr, level=level)

    def preCalculation(self):
        pass

    def postCalculation(self):
        pass

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
        parser = subparsers.add_parser('Merge',
                                       help='Merge overlapping segments in a '
                                            'non dense track.' )
        parser.add_argument('track', help='File path of track')
        parser.add_argument('genome', help='File path of Genome definition')
        parser.add_argument('-b', type=int, dest='both')
        parser.add_argument('-s', type=int, dest='start')
        parser.add_argument('-e', type=int, dest='end')
        parser.add_argument('--allowOverlap', action='store_true',
                            help="Allow overlap in the resulting track")
        parser.set_defaults(which='Merge')

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

        return Merge(track, both=both, start=start, end=end,
                     allowOverlap=allowOverlap)

    @classmethod
    def createTrackName(cls):
        """
        Track name used by GTools when saving the track i GTrackCore
        :return: Generated track name as a string
        """
        return "merge-{0}".format(int(time.time()))

    def printResult(self):
        """
        Operation returns track, not in use
        :return:
        """
        pass
