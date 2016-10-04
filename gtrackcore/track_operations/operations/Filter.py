
import logging
import sys
import time

from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.track_operations.RawOperationContent import RawOperationContent
from gtrackcore.track_operations.utils.TrackHandling import \
    createTrackContentFromFile
from gtrackcore.track_operations.Genome import Genome
from gtrackcore.track_operations.utils.TrackHandling import \
    createRawResultTrackView


from gtrackcore.track_operations.raw_operations.UniquifyLinks import \
    uniquifyLinks

class Filter(Operator):
    """
    TODO, filters a track.. Remove element.

    Options:
        name: Filter track like track name
        variable: Remove specific column. Strands, values, links ect..

    """

    def __init__(self, *args, **kwargs):

        assert args[0] is not None

        self._kwargs = kwargs
        self._options = {'debug': False,
                         'allowOverlaps': True,
                         'resultAllowOverlaps': True,
                         'removeStrands': False,
                         'removeValues': False,
                         'removeIds': False,
                         'removeEdges': False,
                         'removeWeights': False,
                         'removeExtras': False
                         }
        # Save the tracks
        self._tracks = args[0]

        self._trackFormat = args[0].trackFormat

        # Core properties
        self._numTracks = 1
        self._resultIsTrack = True
        self._trackRequirements = [TrackFormatReq()]

        # S
        tr = self._trackFormat
        # TODO, update his to reflect
        self._resultTrackRequirements = self._createTrackFormatReq()
        super(self.__class__, self).__init__(*args, **kwargs)

    def _createTrackFormatReq(self):
        """
        Creates the correct TrackFormatReq according to what kind of data we
        are filtering out.
        :return:
        """

        tr = self._trackFormat
        # Gaps and lengths are not changed
        dense = tr.isDense()
        intervals = tr.isInterval()

        valued = tr.isValued()
        linked = tr.isLinked()
        weighted = tr.isWeighted()
        stranded = tr.hasStrand()

        if stranded and self._removeStrands:
            stranded = False

        if valued:
            if self._removeValues:
                valued = None
            else:
                # Using the _val variable to get the key. The value
                # name function returns the value from the dict.
                # TrackFormatReq requires the key in its __init__ function..
                valued = tr._val
        else:
            valued = None

        if linked:
            if self._removeIds:
                linked = False

            if weighted:
                if self._removeWeights:
                    weighted = False
                else:
                    # Same as with the value name
                    weighted = tr._weights
            else:
                weighted = None
        else:
            weighted = None

        req = TrackFormatReq(dense=dense, interval=intervals, linked=linked,
                             weights=weighted, val=valued, strand=stranded,
                             allowOverlaps=self._resultAllowOverlaps)

        return req

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

        if self._removeIds:
            # As edges needs its, we need to remove them,
            # and as weights needs edges, we need to remove them as well.
            ids = None
            edges = None
            weights = None
        else:
            ids = tv.idsAsNumpyArray()

            if self._removeEdges:
                edges = None
                weights = None
            else:
                edges = tv.edgesAsNumpyArray()

                if self._removeWeights:
                    weights = None
                else:
                    weights = tv.weightsAsNumpyArray()

        #if self._removeExtras:
            #extras = None
        #else:
            #extras = tv.extrasAsNumpyArray()

        tv = createRawResultTrackView(None, region, [None],
                                      self._resultAllowOverlaps,
                                      newStarts=starts, newEnds=ends,
                                      newStrands=strands, newValues=vals,
                                      newIds=ids, newEdges=edges,
                                      newWeights=weights,
                                      trackFormatReq=self._resultTrackRequirements)
                                      # newExtras=extras)
        return tv

    def preCalculation(self, track):
        return track

    def postCalculation(self, track):
        return track

    @classmethod
    def createSubParser(cls, subparsers):
        """
        Creates a subparser. Used by GTool
        :param subparsers:
        :return: None
        """
        parser = subparsers.add_parser('Filter',
                                       help='Filter out data in track')
        parser.add_argument('track', help='File path of track')
        parser.add_argument('genome', help='File path of Genome definition')
        parser.add_argument('--strands',
                            action='store_true',
                            dest='removeStrands',
                            help="Remove strands, if present")
        parser.add_argument('--values', action='store_true',
                            dest='removeValues',
                            help="Remove values, if present")
        parser.add_argument('--ids', action='store_true',
                             dest='removeIds',
                             help="Remove the ids (and all of the links),"
                                  " if present")
        parser.add_argument('--edges', action='store_true',
                            dest='removeEdges',
                            help="Remove edges (and weights), if present")
        parser.add_argument('--weights', action='store_true',
                            dest='removeWeights',
                            help="Remove weights, if present")
        parser.add_argument('--extras', action='store_true',
                            dest='removeExtras',
                            help="Remove extras, if present")
        parser.set_defaults(which='Filter')

    def printResult(self):
        """
        Operation returns track, not in use
        :return:
        """
        pass
