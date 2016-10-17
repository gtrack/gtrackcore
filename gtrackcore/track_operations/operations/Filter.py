
import logging

from collections import OrderedDict

from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track.format.TrackFormat import TrackFormat
from gtrackcore.track.core.TrackView import TrackView

from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.operations.Operator import KwArgumentInfo

from gtrackcore.track_operations.utils.TrackHandling import \
    createRawResultTrackView

class Filter(Operator):
    """
    TODO, filters a track.. Remove element.

    Options:
        name: Filter track like track name
        variable: Remove specific column. Strands, values, links ect..

    """
    _trackHelpList = ['Track to filter from']
    _numTracks = 1
    _resultIsTrack = True
    _trackRequirements = [TrackFormatReq()]

    def _calculate(self, region, tv):
        logging.debug("Start call! region:{0}".format(region))

        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()

        if self._removeStrands:
            strands = None
        else:
            strands = tv.strandsAsNumpyArray()

        if self._removeValues:
            vals = None
        else:
            vals = tv.valsAsNumpyArray()

        if self._removeLinks:
            # As edges needs its, we need to remove them,
            # and as weights needs edges, we need to remove them as well.
            ids = None
            edges = None
            weights = None
        else:
            ids = tv.idsAsNumpyArray()
            edges = tv.edgesAsNumpyArray()

            if self._removeWeights:
                weights = None
            else:
                weights = tv.weightsAsNumpyArray()

        if self._removeExtras:
            extras = None
        else:
            extras = tv.allExtrasAsDictOfNumpyArrays()

        tv = createRawResultTrackView(None, region, None,
                                      self._resultAllowOverlap,
                                      newStarts=starts, newEnds=ends,
                                      newValues=vals, newStrands=strands,
                                      newIds=ids, newEdges=edges,
                                      newWeights=weights, newExtras=extras,
                                      trackFormatReq=self._resultTrackFormat)

        return tv

    def _setResultTrackFormat(self):
        """
        Creates the correct TrackFormat according to what kind of data we
        are filtering out.
        :return:
        """

        tr = self._tracks[0].trackFormat
        # Gaps and lengths are not changed
        dense = tr.isDense()
        interval = tr.isInterval()

        valued = tr.isValued()
        linked = tr.isLinked()
        weighted = tr.isWeighted()
        stranded = tr.hasStrand()

        extra = tr.hasExtra()

        if not dense and not interval:
            # Points
            starts = []
            ends = None
        elif not dense and interval:
            # Segments
            starts = []
            ends = []
        elif dense and interval:
            # partition
            starts = None
            ends = []
        else:
            # function
            starts = []
            ends = []

        if stranded:
            if self._removeStrands:
                strands = None
            else:
                strands = []
        else:
            strands = []

        if valued:
            if self._removeValues:
                values = None
            else:
                values = []
        else:
            values = None

        if linked:
            if self._removeLinks:
                ids = None
                edges = None
                weights = None

            else:
                ids = []
                edges = []
                if weighted and self._removeWeights:
                    weights = None
                elif weighted:
                    # Same as with the value name
                    weights = []
                else:
                    weights = None
        else:
            ids = None
            edges = None
            weights = None

        if extra:
            if self._removeExtras:
                extras = None
            else:
                extras = OrderedDict()
        else:
            extras = None

        self._resultTrackFormat = TrackFormat(startList=starts,
                                              endList=ends,
                                              strandList=strands,
                                              valList=values, idList=ids,
                                              edgesList=edges,
                                              weightsList=weights,
                                              extraLists=extras)

    def _getKwArgumentInfoDict(self):
        return OrderedDict([
            ('resultAllowOverlap',
             KwArgumentInfo('resultAllowOverlap','o',
                            'Allow overlap in the result track.', bool,
                            False)),
            ('debug', KwArgumentInfo('debug', 'd', 'Print debug info', bool,
                                     False)),
            ('removeStrands',
             KwArgumentInfo('removeStrands', 's', 'Remove all strands',
                            bool, False)),
            ('removeValues',
             KwArgumentInfo('removeValues', 'v', 'Remove all values',
                            bool, False)),
            ('removeLinks',
             KwArgumentInfo('removeLinks', 'l',
                            'Remove all link info, if present.', bool, False)),
            ('removeWeights',
             KwArgumentInfo('removeWeights', 'w',
                            'Remove all weight info, if present.',
                            bool, False)),
            ('removeExtras',
             KwArgumentInfo('removeExtras', 'e',
                            'Remove all extra information, if present.',
                            bool, False)),
            ])
