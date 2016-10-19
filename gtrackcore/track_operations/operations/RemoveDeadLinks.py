
import numpy as np
from collections import OrderedDict

from gtrackcore.track.format.TrackFormat import TrackFormatReq

from gtrackcore.track_operations.raw_operations.RemoveDeadLinks import \
    removeDeadLinks

from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.operations.Operator import KwArgumentInfo
from gtrackcore.track_operations.utils.TrackHandling import \
    createRawResultTrackView

class RemoveDeadLinks(Operator):
    """
    After operations on linked tracks we can get dead links.
    Links that points to elements that are removed.

    Possible extensions:
        - Move link to closest feature
    """
    _trackHelpList = ['Track to remove dead links from']
    _operationHelp = "Remove any dead links in a linked track"
    _numTracks = 1
    _resultIsTrack = True
    _trackRequirements = [TrackFormatReq(linked=True)]

    _globalIds = None

    def _calculate(self, region, tv):
        ids = tv.idsAsNumpyArray()
        edges = tv.edgesAsNumpyArray()
        weights = tv.weightsAsNumpyArray()

        ret = removeDeadLinks(ids=ids, edges=edges, weights=weights,
                              globalIds=self._globalIds, newId=self._newId)

        if ret is not None and len(ret) != 0:
            assert len(ret) == 4
            ids = ret[0]
            edges = ret[1]
            weights = ret[2]
            index = ret[3]

            tv = createRawResultTrackView(index, region, tv,
                                          True,
                                          newIds=ids, newEdges=edges,
                                          newWeights=weights,
                                          trackFormat=self._resultTrackFormat)
            return tv
        else:
            return None

    def _setGlobalIds(self, track):
        """
        Improvements: test for uniqueness?
        Takes time.. Better to assume that the user knows this and have
        used ids that are unique.
        :param track: Input track of the operation
        :return:
        """
        trackViews = track.trackViews
        self._globalIds = np.concatenate(([x.idsAsNumpyArray() for x in
                                           trackViews.values()]))

    def _preCalculation(self):
        if self._useGlobal:
            self._setGlobalIds(self._tracks[0])

    def _setResultTrackFormat(self):
        """
        Create the correct TrackFormat for the output track.
        :return:
        """

        # As we do not change the format of the track we simply use the
        # input TrackFormat
        tr = self._tracks[0].trackFormat
        self._resultTrackFormat = tr

    @classmethod
    def _getKwArgumentInfoDict(self):
        return OrderedDict([
            ('debug',
             KwArgumentInfo('debug', 'd', 'Print debug info', bool, False)),
            ('useGlobal',
             KwArgumentInfo('useGlobal','g',
                            'Check the ids globally.', bool,
                            False)),
            ('newId',
             KwArgumentInfo('newId', 'm',
                            'Move the dead links to this id instead of '
                            'removing them', str, None))])
