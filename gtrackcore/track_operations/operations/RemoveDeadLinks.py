
import logging
import sys
import time
import numpy as np

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


from gtrackcore.track_operations.raw_operations.RemoveDeadLinks import \
    removeDeadLinks

class RemoveDeadLinks(Operator):
    """
    After operations on linked tracks we can get dead links.
    Links that points to elements that are removed.

    Links in other regions? Find all ids in preCalc and save them..

    Options:
        - Move link to closest feature
            - Strand?
            - Max length
                - Default value
                - User value
        - globalIds
        - localIds
    """

    def __init__(self, *args, **kwargs):
        self._kwargs = kwargs
        self._options = {'debug': False,
                         'allowOverlap': False,
                         'resultAllowOverlap': False,
                         'newId': None,
                         'useGlobalIds': False
                         }
        # Save the tracks
        self._tracks = args

        # Core properties
        self._numTracks = 1
        self._resultIsTrack = True
        self._trackRequirements = \
            [TrackFormatReq(dense=False, allowOverlaps=False)]
        self._resultTrackRequirements = self._trackRequirements[0]

        if 'useGlobalIds' in kwargs and kwargs['useGlobalIds']:
            self._setGlobalIds(args[0])

        super(self.__class__, self).__init__(*args, **kwargs)

    def _calculate(self, region, tv):
        logging.debug("Start call! region:{0}".format(region))
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
                                          self._allowOverlap, newIds=ids,
                                          newEdges=edges, newWeights=weights)
            return tv
        else:
            return None

    def _setGlobalIds(self, track):
        """
        Improvements: test for uniqueness?
        Takes time.. Better to assume that the user knows this and have
        used ids that are unique.
        :param track: Input track of opreation
        :return:
        """
        trackViews = track.trackViews
        self._globalIds = np.concatenate(([x.idsAsNumpyArray() for x in
                                           trackViews.values()]))

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
        parser = subparsers.add_parser('RemoveDeadLinks',
                                       help='Removes links that are '
                                            'missing there end node')
        parser.add_argument('track', help='File path of track')
        parser.add_argument('genome', help='File path of Genome definition')
        parser.add_argument('--allowOverlap', action='store_true',
                            help="Allow overlap in the resulting track")
        parser.add_argument('-g' '--useGlobal', action='store_true',
                            help="Check the ids globally.")
        parser.add_argument('--newId', dest='newId', help="Update the ids to "
                                                          "the given id")
        parser.set_defaults(which='RemoveDeadLinks')

    @classmethod
    def createOperation(cls, args):
        """
        Generator classmethod used by GTool

        :param args: args from GTool
        :return: Intersect object
        """
        genome = Genome.createFromJson(args.genome)

        track = createTrackContentFromFile(genome, args.track,
                                           args.allowOverlap)

        allowOverlap = args.allowOverlap

        return RemoveDeadLinks(track, allowOverlap=allowOverlap)

    def printResult(self):
        """
        Operation returns track, not in use
        :return:
        """
        pass
