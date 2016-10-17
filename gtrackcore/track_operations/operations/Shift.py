
from collections import OrderedDict

from gtrackcore.track.format.TrackFormat import TrackFormatReq

from gtrackcore.track_operations.raw_operations.Shift import shift

from gtrackcore.track_operations.operations.Merge import Merge
from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.operations.Operator import KwArgumentInfo

from gtrackcore.track_operations.utils.TrackHandling import \
    createRawResultTrackView

class Shift(Operator):

    _trackHelpList = ['Track to be shifted']
    _numTracks = 1
    _resultIsTrack = True
    _trackRequirements = [TrackFormatReq(dense=False)]

    def _calculate(self, region, tv):

        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()

        if self._useStrands:
            strands = tv.strandsAsNumpyArray()
        else:
            strands = None

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

            tv = createRawResultTrackView(index, region, tv,
                                          self._resultAllowOverlap,
                                          newStarts=starts, newEnds=ends,
                                          newStrands=strands,
                                          trackFormat=self._resultTrackFormat)
            return tv
        else:
            return None

    def _postCalculation(self):
        if not self._resultAllowOverlap and not self._result.isEmpty():
            m = Merge(self._result, useStrands=self._useStrands,
                      treatMissingAsNegative=self._treatMissingAsNegative)
            self._result = m.calculate()

    def _setResultTrackFormat(self):
        """
        Create the correct TrackFormat for the output track.
        :return:
        """
        # As we do not change the trackFormat we simply use the TrackFormat
        # of the input track.
        self._resultTrackFormat = self._tracks[0].trackFormat

    def _getKwArgumentInfoDict(self):
        return OrderedDict([
            ('debug',
             KwArgumentInfo('debug', 'd', 'Print debug info',
                            bool, False)),
            ('resultAllowOverlap',
             KwArgumentInfo('resultAllowOverlap','o',
                            'Allow overlap in the result track.',
                            bool, False)),
            ('shiftLength',
             KwArgumentInfo('shiftLength', 'l',
                            'Length of shift in number of base pairs or as a '
                            'fraction of the elements length',
                            float, None)),
            ('useFraction',
             KwArgumentInfo('useFraction', 'f',
                            'Shift each element a fraction of its length '
                            'instead of given number of base pairs',
                            bool, True)),
            ('useStrands',
             KwArgumentInfo('useStrands', 's', 'Follow the strand direction',
                            bool, True)),
            ('treatMissingAsNegative',
             KwArgumentInfo('treatMissingAsNegative', 'n',
                            'Treat any missing strand as if they are '
                            'negative. The default is to treat them as '
                            'positive',
                            bool, False)),
            ('mergeValuesFunction',
             KwArgumentInfo('mergeValuesFunction', 'v',
                            'Use a custom function when merging values',
                            None, None))])
