
import time

from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.raw_operations.Shift import shift
from gtrackcore.track_operations.utils.TrackHandling import \
    createRawResultTrackView
from gtrackcore.track_operations.operations.Merge import Merge

class Shift(Operator):

    def __init__(self, *args, **kwargs):
        self._kwargs = kwargs
        self._options = {'debug': False,
                         'allowOverlaps': False,
                         'resultAllowOverlaps': False,
                         'shiftLength': None,
                         'useFraction': False,
                         'useStrands': True,
                         'treatMissingAsNegative': False
                         }
        # Save the tracks
        self._tracks = args

        self._trackFormat = args[0].trackFormat

        # Core properties
        self._numTracks = 1
        self._resultIsTrack = True
        self._trackRequirements = \
            [TrackFormatReq(dense=False)]
        self._resultTrackRequirements = TrackFormatReq(
            name=self._trackFormat.getFormatName())

        super(self.__class__, self).__init__(*args, **kwargs)

    def _calculate(self, region, tv):

        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()

        # TODO: only load if we need it?
        strands = tv.strandsAsNumpyArray()

        regionSize = len(region)

        ret = shift(starts, ends, regionSize, strands=strands,
                    shiftLength=self._shiftLength,
                    useFraction=self._useFraction,
                    useStrands=self._useStrands,
                    treatMissingAsNegative=self._treatMissingAsNegative)

        if ret is not None and len(ret[0]) != 0:
            assert len(ret) == 4

            starts = ret[0]
            ends = ret[1]
            index = ret[2]
            strands = ret[3]

            if starts is None:
                print()
                return None

            tv = createRawResultTrackView(index, region, tv,
                                          self._resultAllowOverlaps,
                                          newStarts=starts, newEnds=ends,
                                          newStrands=strands,
                                          trackFormatReq=self._resultTrackRequirements)
            return tv
        else:
            return None

    def preCalculation(self, track):
        return track

    def postCalculation(self, result):

        if not self._resultAllowOverlaps and not result.isEmpty():
            m = Merge(result, useStrands=self._useStrands,
                      treatMissingAsNegative=self._treatMissingAsNegative)
            track = m.calculate()
            return track

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
        parser.set_defaults(which='Shift')

    def printResult(self):
        pass
