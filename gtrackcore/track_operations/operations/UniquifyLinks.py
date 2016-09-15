
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

    def __init__(self, *args, **kwargs):
        self._kwargs = kwargs
        self._options = {'debug': False,
                         'allowOverlap': False,
                         'resultAllowOverlap': False,
                         'trackIdentifier': None
                         }
        # Save the tracks
        self._tracks = args

        # Core properties
        self._numTracks = 1
        self._resultIsTrack = True
        self._trackRequirements = \
            [TrackFormatReq(dense=False, allowOverlaps=False)]
        self._resultTrackRequirements = self._trackRequirements[0]

        super(self.__class__, self).__init__(*args, **kwargs)

    def _calculate(self, region, tv):
        logging.debug("Start call! region:{0}".format(region))

        ids = tv.idsAsNumpyArray()
        edges = tv.edgesAsNumpyArray()

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

    def printResult(self):
        """
        Operation returns track, not in use
        :return:
        """
        pass
