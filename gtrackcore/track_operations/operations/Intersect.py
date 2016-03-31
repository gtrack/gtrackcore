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

class Intersect(Operator):
    _NUM_TRACKS = 2
    _TRACK_REQUIREMENTS = [TrackFormatReq(dense=False, allowOverlaps=False),
                           TrackFormatReq(dense=False, allowOverlaps=False)]
    _RESULT_ALLOW_OVERLAPS = False
    _RESULT_IS_TRACK = True
    # Find out how the TrackFormat works..
    _RESULT_TRACK_REQUIREMENTS = TrackFormat([], [], None, None, None, None, None, None)

    def _call(self, region, tv1, tv2):

        #t1Starts = tv1.startsAsNumpyArray()
        #t1Ends = tv1.endsAsNumpyArray()
        #t2Starts = tv2.startsAsNumpyArray()
        #t2Ends = tv2.endsAsNumpyArray()

        #t1Vals = tv1.valsAsNumpyArray()
        #t2Vals = tv2.valsAsNumpyArray()

        rawTrack1 = RawOperationContent(self._resultGenome, region, tv=tv1)
        rawTrack2 = RawOperationContent(self._resultGenome, region, tv=tv2)

        print("Starts: {0}".format(rawTrack1.starts))
        print("Starts tv: {0}".format(tv1.startsAsNumpyArray()))

        print("Ends: {0}".format(rawTrack1.ends))
        print("Ends tv: {0}".format(tv1.endsAsNumpyArray()))

        rawRes = intersect(rawTrack1, rawTrack2)

        print("In Intersect call!!")

        #returnTv = self._createTrackView(region, starts, ends)
        #return returnTv

        return rawRes

    @classmethod
    def createSubParser(cls, subparsers):
        import argparse

        parser = subparsers.add_parser('intersect', help='Find the intersect of two tracks')
        parser.add_argument('trackA', help='File path of track A')
        parser.add_argument('trackB', help='File path of track B')
        parser.add_argument('genome', help='File path of Genome definition')
        parser.add_argument('--allowOverlap', action='store_true',
                            help="Allow overlap in the resulting track")
        parser.set_defaults(which='Intersect')

    @classmethod
    def createOperation(cls, args):
        """
        Generator classmethod used by GTool

        :param args:
        :return:
        """
        genome = Genome.createFromJson(args.genome)

        trackA = createTrackContentFromFile(genome, args.trackA,
                                            args.allowOverlap)
        trackB = createTrackContentFromFile(genome, args.trackB,
                                            args.allowOverlap)

        allowOverlap = args.allowOverlap
        # TODO: use overlap...

        return Intersect(trackA, trackB)

    def test(self):
        print("loff")
