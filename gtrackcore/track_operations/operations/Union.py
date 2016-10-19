
from collections import OrderedDict

from gtrackcore.track.format.TrackFormat import TrackFormatReq

from gtrackcore.track_operations.raw_operations.Union import union

from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.operations.Operator import KwArgumentInfo

from gtrackcore.track_operations.operations.Merge import Merge
from gtrackcore.track_operations.operations.UniquifyLinks import UniquifyLinks

from gtrackcore.track_operations.utils.TrackHandling import \
    createRawResultTrackView

class Union(Operator):

    _trackHelpList = ['Track 1 of Union', 'Track 2 of Union']
    _operationHelp = "Combine two tracks into one"
    _numTracks = 2
    _resultIsTrack = True
    _trackRequirements = [TrackFormatReq(dense=False),
                          TrackFormatReq(dense=False)]

    def _calculate(self, region, tv1, tv2):

        t1Starts = tv1.startsAsNumpyArray()
        t1Ends = tv1.endsAsNumpyArray()

        t2Starts = tv2.startsAsNumpyArray()
        t2Ends = tv2.endsAsNumpyArray()

        ret = union(t1Starts, t1Ends, t2Starts, t2Ends,
                    self._resultAllowOverlap)

        if ret is not None and len(ret[0]) != 0:
            assert len(ret) == 4

            tv = createRawResultTrackView(ret[2], region, [tv1,tv2],
                                            self._resultAllowOverlap,
                                            newStarts=ret[0], newEnds=ret[1],
                                            encoding=ret[3],
                                            trackFormat=self._resultTrackFormat)
            return tv
        else:
            return None

    def _preCalculation(self):
        t1 = self._tracks[0]
        t2 = self._tracks[1]

        print("**************")
        print(t1.trackFormat)
        print(t2.trackFormat)
        print("**************")

        if t1.trackFormat.isLinked():
            u = UniquifyLinks(t1, identifier="track-1")
            t1 = u.calculate()

        if t2.trackFormat.isLinked():
            u = UniquifyLinks(t2, identifier="track-2")
            t2 = u.calculate()

        self._tracks = [t1, t2]

    def _postCalculation(self):
        if not self._resultAllowOverlap:
            # Overlap not allowed in the result. Using merge to remove it
            m = Merge(self._result, useStrands=self._useStrands,
                      treatMissingAsNegative=self._treatMissingAsNegative)
            self._result = m.calculate()

    def _setResultTrackFormat(self):
        """
        Create the correct TrackFormat for the output track.
        :return:
        """
        # We are not changing the type of base track. Using its TrackFormat.
        self._resultTrackFormat = self._tracks[0].trackFormat

        t1TrackFormat = self._tracks[0].trackFormat
        t2TrackFormat = self._tracks[1].trackFormat

        # Create a trackFormatReq from one or more TrackFormats.

        if t1TrackFormat == t2TrackFormat:
            # Equal trackFormat
            self._resultTrackFormat = t1TrackFormat
        else:
            print(t1TrackFormat)
            print(t2TrackFormat)
            # What makes sense?
            # Points and segments?
            # Maybe better to say that the tracks needs to be equal?
            # TODO. Make the correct trackFormat for the result.
            raise NotImplementedError

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
