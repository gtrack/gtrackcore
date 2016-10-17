
import logging
from collections import OrderedDict

from gtrackcore.track.format.TrackFormat import TrackFormatReq

from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.operations.Operator import KwArgumentInfo
from gtrackcore.track_operations.utils.TrackHandling import \
    createRawResultTrackView


from gtrackcore.track_operations.raw_operations.Merge import merge

class Merge(Operator):
    """
    Merge overlapping segments in a track.

    """
    _trackHelpList = ['Track to create flank track from']
    _numTracks = 1
    _resultIsTrack = True
    _trackRequirements = [TrackFormatReq(dense=False)]

    def _calculate(self, region, tv):
        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()
        strands = tv.strandsAsNumpyArray()
        values = tv.valsAsNumpyArray()
        ids = tv.idsAsNumpyArray()
        edges = tv.edgesAsNumpyArray()
        weights = tv.weightsAsNumpyArray()

        if self._useStrands:
            if strands is None:
                self._useStrands = False

        ret = merge(starts, ends, strands=strands, values=values, ids=ids,
                    edges=edges, weights=weights, useStrands=self._useStrands,
                    treatMissingAsNegative=self._treatMissingAsNegative,
                    mergeValuesFunction=self._mergeValuesFunction,
                    debug=self._debug)

        if ret is not None and len(ret[0]) != 0:
            assert len(ret) == 7
            # We do not care about info from the base track..
            # the new track will only contain starts, ends and (strands if
            # present.

            #starts, ends, values, strands, ids, edges, weights
            starts = ret[0]
            ends = ret[1]
            values = ret[2]
            strands = ret[3]
            ids = ret[4]
            edges = ret[5]
            weights = ret[6]

            tv = createRawResultTrackView(None, region, None,
                                          self._resultAllowOverlap,
                                          newStarts=starts, newEnds=ends,
                                          newValues=values, newStrands=strands,
                                          newIds=ids, newEdges=edges,
                                          newWeights=weights,
                                          trackFormat=self._resultTrackFormat)
            return tv
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
            ('debug', KwArgumentInfo('debug', 'd', 'Print debug info', bool,
                                     False)),
            ('resultAllowOverlap',
             KwArgumentInfo('resultAllowOverlap','o',
                            'Allow overlap in the result track.', bool,
                            False)),
            ('useStrands',
             KwArgumentInfo('useStrands', 's', 'Follow the strand direction',
                            bool, True)),
            ('treatMissingAsNegative',
             KwArgumentInfo('treatMissingAsNegative', 'n',
                            'Treat any missing strand as if they are '
                            'negative. The default is to treat them as '
                            'positive', bool, False)),
            ('mergeValuesFunction',
             KwArgumentInfo('mergeValuesFunction', 'v',
                            'Use a custom function when merging values',
                            None, None))])
