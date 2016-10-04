__author__ = 'skh'

from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.raw_operations.Intersect import intersect
from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.track_operations.RawOperationContent import RawOperationContent
from gtrackcore.track_operations.utils.TrackHandling import \
    createTrackContentFromFile
from gtrackcore.track_operations.Genome import Genome
from gtrackcore.track_operations.utils.TrackHandling import \
    createRawResultTrackView

class Intersect(Operator):

    def __init__(self, *args, **kwargs):
        self._kwargs = kwargs
        self._options = {'debug': False,
                         'allowOverlaps': False,
                         'resultAllowOverlaps': False
                         }
        # Save the tracks
        self._tracks = args
        self._trackFormat = [x.trackFormat for x in self._tracks]

        self._numTracks = 2
        self._trackRequirements = \
            [TrackFormatReq(dense=False, allowOverlaps=self._allowOverlaps),
             TrackFormatReq(dense=False, allowOverlaps=self._allowOverlaps)]

        self._resultIsTrack = True
        self._resultTrackRequirements = self._createTrackFormatReq()

        super(self.__class__, self).__init__(*args, **kwargs)

    def _createTrackFormatReq(self):
        """
        Create the correct resultTrackFormatReq
        :return:
        """

        # if one is a point then result is point.
        # else segments.

        trs = self._trackFormat

        for tr in trs:
            if not tr.isDense() and not tr.isInterval():
                print("Result is points")
                # One of the inputs is a point type.
                return TrackFormatReq(dense=False, interval=False,
                                      allowOverlaps=self.resultAllowOverlaps)

        print("Result is segments")

        return TrackFormatReq(dense=False, interval=True,
                              allowOverlaps=self.resultAllowOverlaps)

    def _calculate(self, region, tv1, tv2):

        # TODO
        # Select with links
        #   - Follow all links in the intersect and add these segments as well.

        t1Starts = tv1.startsAsNumpyArray()
        t1Ends = tv1.endsAsNumpyArray()

        t2Starts = tv2.startsAsNumpyArray()
        t2Ends = tv2.endsAsNumpyArray()
        ret = intersect(t1Starts, t1Ends, t2Starts, t2Ends)

        if ret is not None and len(ret[0]) != 0:
            assert len(ret) == 4

            starts = ret[0]
            ends = ret[1]
            index = ret[2]
            encoding = ret[3]

            if not self.resultTrackRequirements.isInterval():
                # Result is a point track.
                print("Points")
                ends = None
            else:
                print("Not points")

            print(starts)
            print(ends)

            return createRawResultTrackView(index, region, [tv1,tv2],
                                            self._resultAllowOverlaps,
                                            newStarts=starts, newEnds=ends,
                                            encoding=encoding)
        else:
            return None



    def preCalculation(self, tracks):
        return tracks

    def postCalculation(self, result):
        return result

    @classmethod
    def createSubParser(cls, subparsers):
        """
        Creates a subparser. Used by GTool
        :param subparsers:
        :return: None
        """
        parser = subparsers.add_parser('intersect', help='Find the intersect of two tracks')
        parser.add_argument('trackA', help='File path of track A')
        parser.add_argument('trackB', help='File path of track B')
        parser.add_argument('genome', help='File path of Genome definition')
        parser.add_argument('--allowOverlap', action='store_true',
                            help="Allow overlap in the resulting track")
        parser.set_defaults(which='Intersect')

    def printResult(self):
        pass
