
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

    def _calculate(self, region, tv):
        logging.debug("Start call! region:{0}".format(region))
        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()
        values = tv.valsAsNumpyArray()

        ids = tv.idsAsNumpyArray()
        edges = tv.edgesAsNumpyArray()

        print("*******")
        print(edges)
        print("*******")

        ret = uniquifyLinks(ids, edges, self._trackIdentifier,
                            self._allowOverlap, self._debug)

        if ret is not None and len(ret) != 0:
            assert len(ret) == 3

            tv = createRawResultTrackView(ret[2], region, tv,
                                          self._allowOverlap, newIds=ret[0],
                                          newEdges=ret[1])
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

        if 'trackIdentifier' in kwargs:
            self._trackIdentifier = kwargs['trackIdentifier']

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
        This operations does not change the format of the track.
        Result track is equal to the input track.
        :return: None
        """
        self._resultTrackRequirements = self._trackRequirements

    def preCalculation(self):
        pass

    def postCalculation(self, track):
        return track

    @classmethod
    def createSubParser(cls, subparsers):
        """
        Creates a subparser. Used by GTool
        :param subparsers:
        :return: None
        """
        parser = subparsers.add_parser('UniquifyLinks',
                                       help='Add a extra identifier to a '
                                            'tracks ids. Used when combining '
                                            'two track with a similar ids '
                                            'naming schemes')
        parser.add_argument('track', help='File path of track')
        parser.add_argument('genome', help='File path of Genome definition')
        parser.add_argument('--allowOverlap', action='store_true',
                            help="Allow overlap in the resulting track")
        parser.add_argument('--trackIdentifier',
                            help="Identifier to add to the ids.")
        parser.set_defaults(which='UniquifyLinks')

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
        trackIdentifier = args.trackIdentifier

        return UniquifyLinks(track, trackIdentifier=trackIdentifier,
                             allowOverlap=allowOverlap)

    @classmethod
    def createTrackName(cls):
        """
        Track name used by GTools when saving the track i GTrackCore
        :return: Generated track name as a string
        """
        return "uniqueLinks-{0}".format(int(time.time()))

    def printResult(self):
        """
        Operation returns track, not in use
        :return:
        """
        pass
