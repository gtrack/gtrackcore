
from collections import OrderedDict

from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.raw_operations.UniquifyLinks import \
    uniquifyLinks

from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.operations.Operator import KwArgumentInfo

from gtrackcore.track_operations.utils.TrackHandling import \
    createRawResultTrackView

class UniquifyLinks(Operator):
    """
    Makes the links of a track more unique. We use this tool when a track
    have links from multiple tracks. Booth tracks can use the same numbering
    system for the ids. This can create error in the resulting track as we
    can have multiple features, with the same ids, and edges witch now
    points to multiple features.

    Options
        - trackIdentifier
    """
    _trackHelpList = ['Track to uniquify links on']
    _operationHelp = "Make all ids in a track more unique by adding a extra " \
                     "tag to all ids."
    _numTracks = 1
    _resultIsTrack = True
    _trackRequirements = [TrackFormatReq(linked=True)]

    def _calculate(self, region, tv):

        ids = tv.idsAsNumpyArray()
        edges = tv.edgesAsNumpyArray()

        ret = uniquifyLinks(ids, edges, self._identifier, self._debug)

        if ret is not None and len(ret) != 0:
            assert len(ret) == 3
            newIds = ret[0]
            newEdges = ret[1]
            index = ret[2]

            tv = createRawResultTrackView(index, region, tv, True,
                                          newIds=newIds, newEdges=newEdges,
                                          trackFormat=self._resultTrackFormat)
            return tv
        else:
            return None

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
            ('identifier',
             KwArgumentInfo('identifier', 'i',
                            'Identifier to add to the ids',
                            str, None))])
