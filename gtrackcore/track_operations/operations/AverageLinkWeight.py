
from collections import OrderedDict

from gtrackcore.track.format.TrackFormat import TrackFormatReq

from gtrackcore.track_operations.raw_operations.AverageLinkWeight import \
    averageLinkWeight

from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.operations.Operator import KwArgumentInfo

class AverageLinkWeight(Operator):
    """
    Find the average weight of the links in a track.
    """

    _trackHelpList = ['Track to find the average link weight on']
    _numTracks = 1
    _resultIsTrack = False
    # TODO: Add a requirement for weight and support multiple types..
    _trackRequirements = [TrackFormatReq(linked=True)]
    _resultTrackFormat = None

    def _calculate(self, region, tv):
        weights = tv.weightsAsNumpyArray()
        ret = averageLinkWeight(weights, self._customAverageFunction)
        return ret

    def _getKwArgumentInfoDict(self):
        return OrderedDict([
            ('debug',
             KwArgumentInfo('debug', 'd', 'Print debug info', bool, False)),
            ('customAverageFunction',
             KwArgumentInfo('customAverageFunction','c',
                            'Use a custom average function', None, None)) ])
