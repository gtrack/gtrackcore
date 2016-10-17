
from collections import OrderedDict

from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.raw_operations.Intersect import intersect

from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.operations.Operator import KwArgumentInfo

from gtrackcore.track_operations.utils.TrackHandling import \
    createRawResultTrackView

class Intersect(Operator):
    """
    Find the intersect between two track.

    Possible extension:
    Select with links
        - Follow all links in the intersect and add these segments as well.
    Follow strand
    """

    _trackHelpList = ['Track 1 in the intersect', 'Track 2 intersect']
    _numTracks = 2
    _resultIsTrack = True
    _trackRequirements = [TrackFormatReq(dense=False),
                          TrackFormatReq(dense=False)]

    def _calculate(self, region, tv1, tv2):
        t1Starts = tv1.startsAsNumpyArray()
        t1Ends = tv1.endsAsNumpyArray()

        t2Starts = tv2.startsAsNumpyArray()
        t2Ends = tv2.endsAsNumpyArray()
        ret = intersect(t1Starts, t1Ends, t2Starts, t2Ends, debug=self._debug)

        if ret is not None and len(ret[0]) != 0:
            assert len(ret) == 4

            starts = ret[0]
            ends = ret[1]
            index = ret[2]
            encoding = ret[3]

            return createRawResultTrackView(index, region, [tv1,tv2],
                                            self._resultAllowOverlap,
                                            newStarts=starts, newEnds=ends,
                                            encoding=encoding,
                                            trackFormat=self._resultTrackFormat)
        else:
            return None

    def _setResultTrackFormat(self):
        """
        Create the correct TrackFormat for the output track.
        TODO, do this dynamic
        :return:
        """

        # if one is a point then result is point.
        # else segments.

        trs = [track.trackFormat for track in self._tracks]

        isSegments = all(tr.isInterval() for tr in trs)

        if isSegments:
            starts = []
            ends = []
        else:
            # points
            starts = []
            ends = None

        # TODO add the rest

        self._resultTrackFormat = TrackFormat(startList=starts, endList=ends)

    def _getKwArgumentInfoDict(self):
        print("In flank getKwArgument")
        return OrderedDict([
            ('debug',
             KwArgumentInfo('debug', 'd', 'Print debug info', bool, False)),
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
                            'negative. The default is to treat them as positive',
                            bool, False))])
