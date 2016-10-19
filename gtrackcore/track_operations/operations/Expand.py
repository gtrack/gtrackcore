__author__ = 'skh'

from collections import OrderedDict

from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.operations.Operator import KwArgumentInfo
from gtrackcore.track_operations.utils.TrackHandling import \
    createRawResultTrackView

from gtrackcore.track_operations.operations.Merge import Merge

from gtrackcore.track_operations.raw_operations.Expand import expand

class Expand(Operator):
    """
    Extends all of the segments in a track a given number of BP.
    """
    _trackHelpList = ['Track to expand']
    _operationHelp = "Expand the elements in a track."
    _numTracks = 1
    _resultIsTrack = True
    _trackRequirements = [TrackFormatReq(dense=False)]

    def _calculate(self, region, tv):

        # Remove RawOperationsContent
        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()
        strands = None

        if self._useStrands:
            strands = tv.strandsAsNumpyArray()
            if strands is None or strands.size == 0:
                # Track has no strand information, ignoring strands.
                strands = None
                self._useStrand = False

        # Get genome size.
        regionSize = len(region)

        ret = expand(regionSize, starts=starts, ends=ends, strands=strands,
                     downstream=self._downstream, upstream=self._upstream,
                     both=self._both, useFraction=self._useFraction,
                     useStrands=self._useStrands,
                     treatMissingAsNegative=self._treatMissingAsNegative,
                     debug=self._debug)

        # Returns start, ends, strands, index
        if ret is not None and len(ret[0]) != 0:
            assert len(ret) == 3
            starts = ret[0]
            ends = ret[1]
            index = ret[2]
            return createRawResultTrackView(index, region, tv,
                                            self._resultAllowOverlap,
                                            newStarts=starts, newEnds=ends,
                                            trackFormat=self._resultTrackFormat)
        else:
            return None

    def _postCalculation(self):
        if not self._resultAllowOverlap:
            # Overlap not allowed in the result. Using merge to remove it
            m = Merge(self._result, useStrands=self._useStrands,
                      treatMissingAsNegative=self._treatMissingAsNegative)
            self._result = m.calculate()

    @classmethod
    def _getKwArgumentInfoDict(cls):
        return OrderedDict([
            ('debug',
             KwArgumentInfo('debug', 'd', 'Print debug info', bool, False)),
            ('resultAllowOverlap',
             KwArgumentInfo('resultAllowOverlap','o',
                            'Allow overlap in the result track.', bool,
                            False)),
            ('both',
             KwArgumentInfo('both', 'b',
                            'Extract the segments in in both directions.',
                            float, None)),
            ('upstream',
             KwArgumentInfo('upstream', 'u',
                            'Size of the upstream flank. In number of base '
                            'pairs', float, None)),
            ('downstream',
             KwArgumentInfo('downstream', 'w',
                            'Size of the downstream flank. In number of base '
                            'pairs', float, None)),
            ('useFraction',
             KwArgumentInfo('useFraction', 'f',
                            'Interpret flak size as a fraction of the '
                            'element size', bool, False)),
            ('useStrands',
             KwArgumentInfo('useStrands', 's', 'Follow the strand direction',
                            bool, True)),
            ('treatMissingAsNegative',
             KwArgumentInfo('treatMissingAsNegative', 'n',
                            'Treat any missing strand as if they are '
                            'negative. The default is to treat them as '
                            'positive',bool, False))])

    def _setResultTrackFormat(self):
        """
        Creates the correct TrackFormatReq according to the input track
        :return:
        """

        tr = self._tracks[0].trackFormat

        if tr.hasStrand():
            strands = []
        else:
            strands = None

        if tr.isValued():
            values = []
        else:
            values = None

        if tr.isLinked:
            ids = []
            edges = []
        else:
            ids = None
            edges = None

        if tr.isWeighted():
            weights = []
        else:
            weights = None

        self._resultTrackFormat = TrackFormat(startList=[], endList=[],
                                              strandList=strands,
                                              valList=values,idList=ids,
                                              edgesList=edges,
                                              weightsList=weights)
