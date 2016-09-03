
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

    def _calculate(self, region, tv):
        logging.debug("Start call! region:{0}".format(region))
        ids = tv.idsAsNumpyArray()
        edges = tv.edgesAsNumpyArray()
        weights = tv.weightsAsNumpyArray()

        # Remove dead links

        ret = removeDeadLinks(ids=ids, edges=edges, weights=weights,
                              newId=self._newId)

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

    def _setConfig(self, trackViews):
        # Access to the operations tracks.
        self._tracks = trackViews

        # None changeable properties
        self._numTracks = 1
        self._updateTrackFormat()
        self._resultIsTrack = True

        # Set defaults for changeable properties
        self._allowOverlap = False
        self._resultAllowOverlaps = False

        self._newId = None
        self._useGlobalIds = False

        # For now the result track is always of the same type as track A
        self._resultTrackRequirements = self._trackRequirements[0]

    def _parseKwargs(self, **kwargs):
        """
        :param kwargs:
        :return: None
        """
        if 'allowOverlap' in kwargs:
            self._allowOverlap = kwargs['allowOverlap']
            self._updateTrackFormat()

        if 'resultAllowOverlaps' in kwargs:
            self._resultAllowOverlaps = kwargs['resultAllowOverlaps']
            self._updateResultTrackFormat()

        if 'newId' in kwargs:
            self._newId = kwargs['newId']

        if 'useGlobalIds' in kwargs:
            self._useGlobalIds = kwargs['useGlobalIds']

        if 'debug' in kwargs:
            self._debug = kwargs['debug']
        else:
            self._debug = False

        if self._debug:
            level = logging.DEBUG
        else:
            level = logging.INFO
        logging.basicConfig(stream=sys.stderr, level=level)

    def _updateTrackFormat(self):
        """
        If we enable or disable overlapping tracks as input, we need to
        update the track requirement as well.
        :return: None
        """

        assert self._tracks is not None
        tv = self._tracks[0]
        assert tv is not None
        dense = tv.firstTrackView().trackFormat.isDense()

        self._trackRequirements = \
            [TrackFormatReq(dense=dense, allowOverlaps=self._allowOverlap)]

    def _updateResultTrackFormat(self):
        """
        If we enable or disable overlapping tracks in the result, we need to
        update the track requirement as well.
        :return: None
        """
        # Probably OK. Result will i most cases be a non dense track..
        if self._resultAllowOverlaps:
            self._resultTrackRequirements = \
                [TrackFormatReq(dense=False, allowOverlaps=True)]
        else:
            self._resultTrackRequirements = \
                [TrackFormatReq(dense=False, allowOverlaps=False)]

    def preCalculation(self, track):

        if self._useGlobalIds:
            print("Using global ids!")

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

        if 'limit' in args:
            limit = args.limit
        else:
            print("No limit given!")
            sys.exit(1)

        return RemoveDeadLinks(track, allowOverlap=allowOverlap)

    @classmethod
    def createTrackName(cls):
        """
        Track name used by GTools when saving the track i GTrackCore
        :return: Generated track name as a string
        """
        return "deadLinksRemoved-{0}".format(int(time.time()))

    def printResult(self):
        """
        Operation returns track, not in use
        :return:
        """
        pass
