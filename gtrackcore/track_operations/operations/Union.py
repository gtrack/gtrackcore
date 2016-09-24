
import time

from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.operations.Merge import Merge
from gtrackcore.track_operations.operations.UniquifyLinks import UniquifyLinks

from gtrackcore.track_operations.raw_operations.Union import union

from gtrackcore.track_operations.utils.TrackHandling import \
    createRawResultTrackView
from gtrackcore.track_operations.utils.TrackHandling import \
    createTrackContentFromFile

from gtrackcore.track_operations.Genome import Genome

class Union(Operator):

    def __init__(self, *args, **kwargs):
        assert len(args) == 2
        assert args[0] is not None
        self._kwargs = kwargs
        self._options = {'allowOverlap': False,
                         'resultAllowOverlap': False,
                         'trackFormatReqChangeable': False,
                         'resultTrackFormatReqChangeable': False,
                         'useStrands': True,
                         'treatMissingAsNegative': False,
                         'mergeValuesFunction': None,
                         'makeLinksUnique': False,
                         'trackALinkTag': None,
                         'trackBLinkTag': None
                         }

        # Save the tracks
        self._tracks = args

        # Core properties
        self._numTracks = 2
        self._resultIsTrack = True

        # Merge support all tracks type with the exception if function,
        # linked function and linked base pairs.
        self._trackRequirements = [[TrackFormatReq(dense=False),
                                    TrackFormatReq(dense=True, interval=True)],
                                   [TrackFormatReq(dense=False),
                                    TrackFormatReq(dense=True, interval=True)]]

        # TODO, fix this when track A and B have a different trackFormat..
        # The TrackFormat of the result

        t1Trackformat = args[0].trackFormat
        t2Trackformat = args[1].trackFormat

        print(t1Trackformat)
        print(t2Trackformat)
        if t1Trackformat == t2Trackformat:
            # Equal trackFormat
            self._trackFormat = t1Trackformat
        else:
            # TODO. Make the correct trackFormat for the result.
            print("No equal!")
            raise NotImplementedError
        # We set the resultTrackRequirements based on the input track
        tr = self._trackFormat

        # TODO create a createFromTrackFormat method in TrackFormatReq
        self._resultTrackRequirements = TrackFormatReq(dense=tr.isDense(),
                                                       val=tr._val,
                                                       interval=tr.isInterval(),
                                                       linked=tr.isLinked(),
                                                       allowOverlaps=self._resultAllowOverlap)

        super(self.__class__, self).__init__(*args, **kwargs)

    def _calculate(self, region, tv1, tv2):

        t1Starts = tv1.startsAsNumpyArray()
        t1Ends = tv1.endsAsNumpyArray()

        t2Starts = tv2.startsAsNumpyArray()
        t2Ends = tv2.endsAsNumpyArray()

        print("edges tv1: {}".format(tv1.edgesAsNumpyArray()))
        print("edges tv2: {}".format(tv2.edgesAsNumpyArray()))

        ret = union(t1Starts, t1Ends, t2Starts, t2Ends,
                    self._resultAllowOverlap)

        if ret is not None and len(ret[0]) != 0:
            assert len(ret) == 4

            print(self._trackFormat)
            tv = createRawResultTrackView(ret[2], region, [tv1,tv2],
                                            self.allowOverlaps,
                                            newStarts=ret[0], newEnds=ret[1],
                                            encoding=ret[3],
                                            trackFormat=self._trackFormat)
            return tv
        else:
            return None

    def preCalculation(self, tracks):
        if self._makeLinksUnique:
            t1 = tracks[0]
            t2 = tracks[1]

            if self._trackALinkTag is not None:
                u = UniquifyLinks(t1, identifier=self._trackALinkTag)
                t1 = u.calculate()
            else:
                u = UniquifyLinks(t1, identifier="track-1")
                t1 = u.calculate()

            if self._trackBLinkTag is not None:
                u = UniquifyLinks(t2, identifier=self._trackALinkTag)
                t2 = u.calculate()
            else:
                u = UniquifyLinks(t2, identifier="track-2")
                t2 = u.calculate()

            return [t1, t2]

        else:
            return tracks

    def postCalculation(self, track):

        if not self._resultAllowOverlap:
            print("Removing overlap in result!!")
            # Overlap not allowed in the result. Using merge to remove it
            m = Merge(track, both=True, useStrands=True, allowOverlap=False)
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
        parser = subparsers.add_parser('union', help='Find the union of '
                                       'two tracks')
        parser.add_argument('trackA', help='File path of track A')
        parser.add_argument('trackB', help='File path of track B')
        parser.add_argument('genome', help='File path of Genome definition')
        parser.add_argument('--allowOverlap', action='store_true',
                            help="Allow overlap in the resulting track")
        parser.set_defaults(which='Union')

    def printResult(self):
        pass
