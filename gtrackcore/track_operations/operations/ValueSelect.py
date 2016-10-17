
from collections import OrderedDict

from gtrackcore.track.format.TrackFormat import TrackFormatReq

from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.operations.Operator import KwArgumentInfo

from gtrackcore.track_operations.utils.TrackHandling import \
    createRawResultTrackView

from gtrackcore.track_operations.raw_operations.ValueSelect import valueSelect

class ValueSelect(Operator):
    """
    Pics the elements of a track
    """
    _trackHelpList = ['Track to do a value select on']
    _numTracks = 1
    _resultIsTrack = True
    _trackRequirements = [TrackFormatReq(dense=False)]

    def _calculate(self, region, tv):
        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()
        values = tv.valsAsNumpyArray()

        ret = valueSelect(starts, ends, values=values, limit=self._limit,
                          compareFunction=self._compareFunction,
                          allowOverlap=self._allowOverlap, debug=self._debug)

        if ret is not None and len(ret) != 0:
            assert len(ret) == 3
            # We do not care about info from the base track..
            # the new track will only contain starts, ends and (strands if
            # present

            t = createRawResultTrackView(ret[2], region, tv,True,
                                         newStarts=ret[0], newEnds=ret[1])
            return t
        else:
            return None

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
           ('limit',
             KwArgumentInfo('useFraction', 'l',
                            'Value limit to select based on',
                            float, 0)),
            ('compareFunction',
             KwArgumentInfo('useStrands', 's',
                            'Custom compare function',
                            None, None))])
