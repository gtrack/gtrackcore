from collections import OrderedDict

from gtrackcore.track.format.TrackFormat import TrackFormatReq

from gtrackcore.track_operations.raw_operations.Coverage import coverage

from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.operations.Operator import KwArgumentInfo


class Coverage(Operator):

    _trackHelpList = ['Track to be calculated coverage for']
    _numTracks = 1
    _resultIsTrack = False
    _trackRequirements = [TrackFormatReq(dense=False)]

    def _calculate(self, region, tv):
        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()
        return coverage(starts, ends)

    def _getKwArgumentInfoDict(self):
        return OrderedDict([
            ('debug',
             KwArgumentInfo('debug', 'd', 'Print debug info', bool, False)),
            ('resultAllowOverlap',
             KwArgumentInfo('resultAllowOverlap','o',
                            'Allow overlap in the result track.', bool,
                            False)),
            ('total',
             KwArgumentInfo('total', 't',
                            'Sum the coverage for all regions',
                            bool, False))])

    def printResult(self):
        """
        :return:
        """
        if self._result is not None:
            print(self._result)
        else:
            print("ERROR! Calculation not run!")
