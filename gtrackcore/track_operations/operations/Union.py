
import time

from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.operations.Merge import Merge
from gtrackcore.track_operations.raw_operations.Union import union

from gtrackcore.track_operations.utils.TrackHandling import \
    createRawResultTrackView
from gtrackcore.track_operations.utils.TrackHandling import \
    createTrackContentFromFile

from gtrackcore.track_operations.Genome import Genome

class Union(Operator):

    def _calculate(self, region, tv1, tv2):

        t1Starts = tv1.startsAsNumpyArray()
        t1Ends = tv1.endsAsNumpyArray()

        t2Starts = tv2.startsAsNumpyArray()
        t2Ends = tv2.endsAsNumpyArray()

        ret = union(t1Starts, t1Ends, t2Starts, t2Ends,
                    self._resultAllowOverlaps)

        if ret is not None and len(ret[0]) != 0:
            assert len(ret) == 4

            tv = createRawResultTrackView(ret[2], region, [tv1,tv2],
                                            self.allowOverlaps,
                                            newStarts=ret[0], newEnds=ret[1],
                                            encoding=ret[3])

            print("In Union: ids: {}".format(tv.idsAsNumpyArray()))
            return tv
        else:
            return None

    def _setConfig(self, args):
        # None changeable properties
        self._numTracks = 2
        self._trackRequirements = \
            [TrackFormatReq(dense=False, allowOverlaps=False),
             TrackFormatReq(dense=False, allowOverlaps=False)]

        # Set defaults for changeable properties
        self._allowOverlap = False
        self._resultAllowOverlaps = False
        self._resultIsTrack = True
        # For now the result track is always of the same type as track A
        # TODO: Solve this for the case where A and b are not of the same type.
        self._resultTrackRequirement = TrackFormat(startList=[], endList=[])

        # Merge with parseKwargs

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

    def preCalculation(self):
        pass

    def postCalculation(self, track):

        if not self._resultAllowOverlaps:
            print("No overlap in result!!")
            # Overlap not allowed in the result. Using merge to remove it
            m = Merge(track, both=True, useValues=True, useStrands=True,
                      useLinks=True, allowOverlap=False)
            res = m.calculate()
            return res
        else:
            return track

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

        pass

        # TODO, the compatible with test breaks this.
        """
        if self._resultAllowOverlaps:
            self._resultTrackRequirements = \
                [TrackFormatReq(dense=False, allowOverlaps=True),
                 TrackFormatReq(dense=False, allowOverlaps=True)]
        else:
            self._resultTrackRequirements = \
                [TrackFormatReq(dense=False, allowOverlaps=False),
                 TrackFormatReq(dense=False, allowOverlaps=False)]
        """
    @classmethod
    def createSubParser(cls, subparsers):
        """
        Creates a subparser. Used by GTool
        :param subparsers:
        :return: None
        """
        parser = subparsers.add_parser('union', help='Find the union of '
                                       'two tracks')
        parser.add_argument('trackA', help='File path of track A')
        parser.add_argument('trackB', help='File path of track B')
        parser.add_argument('genome', help='File path of Genome definition')
        parser.add_argument('--allowOverlap', action='store_true',
                            help="Allow overlap in the resulting track")
        parser.set_defaults(which='Union')

    @classmethod
    def createOperation(cls, args):
        """
        Generator classmethod used by GTool

        :param args: args from GTool
        :return: Intersect object
        """
        genome = Genome.createFromJson(args.genome)

        trackA = createTrackContentFromFile(genome, args.trackA,
                                            args.allowOverlap)
        trackB = createTrackContentFromFile(genome, args.trackB,
                                            args.allowOverlap)

        allowOverlap = args.allowOverlap
        # TODO: use overlap...

        return Union(trackA, trackB)

    @classmethod
    def createTrackName(cls):
        """
        Track name used by GTools when saving the track i GTrackCore
        :return: Generated track name as a string
        """
        return "union-{0}".format(int(time.time()))

    def printResult(self):
        pass
