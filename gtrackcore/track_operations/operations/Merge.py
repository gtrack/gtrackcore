
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


from gtrackcore.track_operations.raw_operations.Merge import merge

class Merge(Operator):
    """
    Merge overlapping segments in a track.

    None dense tracks only
    """

    def __init__(self, *args, **kwargs):
        assert len(args) == 1
        assert args[0] is not None
        self._kwargs = kwargs
        self._options = {'allowOverlap': False,
                         'resultAllowOverlap': False,
                         'trackFormatReqChangeable': False,
                         'resultTrackFormatReqChangeable': False,
                         'mergeValuesFunction': None,
                         'useStrands': True,
                         'treatMissingAsNegative': False
                         }

        # Save the tracks
        self._tracks = args[0]

        # Core properties
        self._numTracks = 1
        self._resultIsTrack = True

        # Merge support all tracks type with the exception if function,
        # linked function and linked base pairs.
        self._trackRequirements = [[TrackFormatReq(dense=False),
                                    TrackFormatReq(dense=True, interval=True)]]

        # The TrackFormat of the result
        self._trackFormat = args[0].trackFormat

        # We set the resultTrackRequirements based on the input track
        tr = self._trackFormat

        # TODO create a createFromTrackFormat method in TrackFormatReq
        self._resultTrackRequirements = TrackFormatReq(dense=tr.isDense(),
                                                       val=tr._val,
                                                       interval=tr.isInterval(),
                                                       linked=tr.isLinked(),
                                                       allowOverlaps=self._resultAllowOverlap)

        super(self.__class__, self).__init__(*args, **kwargs)

    def _calculate(self, region, tv):
        # Remove RawOperationsContent
        logging.debug("Start call! region:{0}".format(region))
        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()
        strands = tv.strandsAsNumpyArray()
        values = tv.valsAsNumpyArray()
        ids = tv.idsAsNumpyArray()
        edges = tv.edgesAsNumpyArray()
        weights = tv.weightsAsNumpyArray()

        print("in merge: edges: {}".format(edges))

        print("")

        if self._useStrands:
            if strands is None:
                self._useStrands = False

        ret = merge(starts, ends, strands=strands, values=values, ids=ids,
                    edges=edges, weights=weights, useStrands=self._useStrands,
                    treatMissingAsNegative=self._treatMissingAsNegative,
                    mergeValuesFunction=self._mergeValuesFunction)


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

            print("edges in result: {}".format(edges))

            tv = createRawResultTrackView(None, region, None,
                                          self.allowOverlaps,
                                          newStarts=starts, newEnds=ends,
                                          newValues=values, newStrands=strands,
                                          newIds=ids, newEdges=edges,
                                          newWeights=weights,
                                          trackFormat=self._trackFormat)

            return tv
        else:
            return None

    def preCalculation(self, tracks):
        return tracks

    def postCalculation(self, track):
        return track

    @classmethod
    def createSubParser(cls, subparsers):
        """
        Creates a subparser. Used by GTool
        :param subparsers:
        :return: None
        """
        parser = subparsers.add_parser('Merge',
                                       help='Merge overlapping segments in a '
                                            'non dense track.' )
        parser.add_argument('track', help='File path of track')
        parser.add_argument('genome', help='File path of Genome definition')
        parser.add_argument('--allowOverlap', action='store_true',
                            help="Allow overlap in the resulting track")
        parser.set_defaults(which='Merge')

    def printResult(self):
        """
        Operation returns track, not in use
        :return:
        """
        pass
