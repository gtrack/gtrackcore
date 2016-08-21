
import time

from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.raw_operations.Shift import shift
from gtrackcore.track_operations.utils.TrackHandling import \
    createRawResultTrackView
from gtrackcore.track_operations.utils.TrackHandling import \
    createTrackContentFromFile
from gtrackcore.track_operations.Genome import Genome

class Shift(Operator):

    def _calculate(self, region, tv):

        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()

        # TODO: only load if we need it?
        strands = tv.strandsAsNumpyArray()

        regionSize = len(region)

        ret = shift(starts, ends, regionSize, strands=strands,
                    shift=self._shift, positive=self._positive,
                    negative=self._negative, fraction=self._fraction,
                    useMissingStrand=self._useMissingStrand,
                    treatMissingAsPositive=self._treatMissingAsPositive,
                    allowOverlap=self._allowOverlap)

        if ret is not None and len(ret[0]) != 0:
            assert len(ret) == 4
            return createRawResultTrackView(ret[0], ret[1], ret[2], region,
                                            tv, self._allowOverlap,
                                            newStrands=ret[3])
        else:
            return None

    def _setConfig(self, track):
        # None changeable properties
        self._numTracks = 1
        self._trackRequirements = \
            [TrackFormatReq(dense=False, allowOverlaps=True)]
        self._resultIsTrack = True

        # Set defaults for changeable properties
        self._allowOverlap = True
        self._shift = None
        self._positive = None
        self._negative = None
        self._fraction = False
        self._useMissingStrand = True
        self._treatMissingAsPositive = True

        # For now the result track is always of the same type as track A
        self._resultTrackRequirements = self._trackRequirements[0]

    def _parseKwargs(self, **kwargs):
        """
        :param kwargs:
        :return: None
        """
        if 'allowOverlap' in kwargs:
            self._allowOverlap = kwargs['allowOverlap']
            self._updateTrackFormat()

        if 'shift' in kwargs:
            self._shift = kwargs['shift']

        if 'positive' in kwargs:
            self._positive = kwargs['positive']

        if 'negative' in kwargs:
            self._negative = kwargs['negative']

        if 'fraction' in kwargs:
            self._fraction = kwargs['fraction']

        if 'useMissingStrand' in kwargs:
            self._useMissingStrand = kwargs['useMissingStrand']

        if 'treatMissingAsPositive' in kwargs:
            self._treatMissingAsPositive = kwargs['treatMissingAsPositive']

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
        If we enable or disable overlapping tracks in the result, we need to
        update the track requirement as well.
        :return: None
        """
        if self._resultAllowOverlaps:
            self._resultTrackRequirements = \
                [TrackFormatReq(dense=False, allowOverlaps=True)]
        else:
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
        parser = subparsers.add_parser('shift', help='Shift segments in track')
        parser.add_argument('trackA', help='File path of track')
        parser.add_argument('genome', help='File path of Genome definition')
        parser.add_argument('--allowOverlap', action='store_true',
                            help="Allow overlap in the resulting track")
        parser.set_defaults(which='Subtract')

    @classmethod
    def createOperation(cls, args):
        """
        Generator classmethod used by GTool

        :param args: args from GTool
        :return: Intersect object
        """
        genome = Genome.createFromJson(args.genome)

        track = createTrackContentFromFile(genome, args.trackA,
                                            args.allowOverlap)

        allowOverlap = args.allowOverlap
        # TODO: use overlap...

        return Shift(track)

    @classmethod
    def createTrackName(cls):
        """
        Track name used by GTools when saving the track i GTrackCore
        :return: Generated track name as a string
        """
        return "shifted-{0}".format(int(time.time()))

    def printResult(self):
        pass
