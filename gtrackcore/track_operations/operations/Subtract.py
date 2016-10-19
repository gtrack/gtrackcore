
from collections import OrderedDict

from gtrackcore.track.format.TrackFormat import TrackFormatReq

from gtrackcore.track_operations.raw_operations.Subtract import subtract

from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.operations.Operator import KwArgumentInfo

from gtrackcore.track_operations.utils.TrackHandling import \
    createRawResultTrackView

from gtrackcore.track_operations.operations.Merge import Merge
from gtrackcore.track_operations.operations.RemoveDeadLinks import \
    RemoveDeadLinks

class Subtract(Operator):

    _trackHelpList = ['Base track', 'Track to be subtracted from']
    _operationHelp = "Subtract one track from another"
    _numTracks = 2
    _resultIsTrack = True
    _trackRequirements = [TrackFormatReq(dense=False),
                          TrackFormatReq(dense=False)]

    def _calculate(self, region, tv1, tv2):

        t1Starts = tv1.startsAsNumpyArray()
        t1Ends = tv1.endsAsNumpyArray()

        t2Starts = tv2.startsAsNumpyArray()
        t2Ends = tv2.endsAsNumpyArray()

        if self._useStrands:
            t1Strands = tv1.strandsAsNumpyArray()
            t2Strands = tv2.strandsAsNumpyArray()

            if t1Strands is None or t2Strands is None:
                self._useStrands = None
                t1Strands = None
                t2Strands = None

        else:
            t1Strands = None
            t2Strands = None

        ret = subtract(t1Starts, t1Ends, t2Starts, t2Ends,
                       t1Strands=t1Strands, t2Strands=t2Strands,
                       useStrands=self._useStrands,
                       treatMissingAsNegative=self._treatMissingAsNegative,
                       debug=self._debug)

        if ret is not None and len(ret[0]) != 0:
            assert len(ret) == 3

            starts = ret[0]
            ends = ret[1]
            index = ret[2]

            return createRawResultTrackView(index, region, tv1,
                                            self._resultAllowOverlap,
                                            newStarts=starts, newEnds=ends,
                                            trackFormat=self._resultTrackFormat)
        else:
            return None

    def _preCalculation(self):
        # There cant be any overlap in any of the tracks.
        m1 = Merge(self._tracks[0], useStrands=self._useStrands,
                   treatMissingAsNegative=self._treatMissingAsNegative)
        t1 = m1.calculate()

        m2 = Merge(self._tracks[1], useStrands=self._useStrands,
                   treatMissingAsNegative=self._treatMissingAsNegative)
        t2 = m2.calculate()

        self._tracks = [t1, t2]

    def _postCalculation(self):
        # Fix split links

        if self._result.trackFormat.isLinked():
            r = RemoveDeadLinks(self._result)
            self._result = r.calculate()

    def _setResultTrackFormat(self):
        """
        Create the correct TrackFormat for the output track.
        :return:
        """
        # We are not changing the type of base track. Using its TrackFormat.
        self._resultTrackFormat = self._tracks[0].trackFormat

    @classmethod
    def _getKwArgumentInfoDict(self):
        return OrderedDict([
            ('debug',
             KwArgumentInfo('debug', 'd', 'Print debug info', bool, False)),
            ('resultAllowOverlap',
             KwArgumentInfo('resultAllowOverlap', 'o',
                            'Allow overlap in the result track.', bool,
                            False)),
            ('useStrands',
             KwArgumentInfo('useStrands', 's', 'Follow the strand direction',
                            bool, True)),
            ('treatMissingAsNegative',
             KwArgumentInfo('treatMissingAsNegative', 'n',
                            'Treat any missing strand as if they are '
                            'negative. The default is to treat them as positive',
                            bool, False))])
