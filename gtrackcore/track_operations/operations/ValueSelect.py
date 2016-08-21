
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


from gtrackcore.track_operations.raw_operations.ValueSelect import valueSelect

class ValueSelect(Operator):
    """
    Pics the elements of a track
    """

    def _calculate(self, region, tv):
        # Remove RawOperationsContent
        logging.debug("Start call! region:{0}".format(region))
        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()
        values = tv.valsAsNumpyArray()

        ret = valueSelect(starts, ends, values=values, limit=self._limit,
                          compareFunction=self._compareFunction,
                          allowOverlap=self._allowOverlap, debug=self._debug)

        if ret is not None and len(ret) != 0:
            assert len(ret) == 3
            # We do not care about info from the base track..
            # the new track will only contain starts, ends and (strands if
            # present

            print("****DEBUG*****")
            print(ret)
            print(type(ret))
            print("****DEBUG*****")

            t = createRawResultTrackView(ret[2], region, tv,
                                         self._allowOverlap, newStarts=ret[0],
                                         newEnds=ret[1])
            print("**********123***********")
            print(tv.startsAsNumpyArray())
            print(t.startsAsNumpyArray())
            print("**********123***********")

            #tv = TrackView(region, ret[0], ret[1], ret[2], None, None,
            #               None, None, borderHandling='crop',
            #               allowOverlaps=self._allowOverlap)
            return t
        else:
            return None

    def _setConfig(self, trackViews):
        # Access to the operaions tracks.
        self._tracks = trackViews

        # None changeable properties
        self._numTracks = 1
        self._trackRequirements = \
            [TrackFormatReq(dense=False, allowOverlaps=False)]
        self._resultIsTrack = True

        # Set defaults for changeable properties
        self._allowOverlap = False
        self._resultAllowOverlaps = False

        self._useFraction = False
        self._u = False
        self._treatMissingAsPositive = True
        # For now the result track is always of the same type as track A
        # TODO: Solve this for the case where A and b are not of the same type.
        self._resultTrackRequirements = self._trackRequirements[0]

    def _parseKwargs(self, **kwargs):
        """
        :param kwargs:
        :return: None
        """
        if 'allowOverlap' in kwargs:
            self._allowOverlap = kwargs['allowOverlap']
            self._updateTrackFormat()

        if 'limit' in kwargs:
            self._limit = kwargs['limit']
        else:
            self._limit = 0

        if 'compareFunction' in kwargs:
            self._compareFunction = kwargs['compareFunction']
        else:
            self._compareFunction = None

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

        if self._allowOverlap:
            self._trackRequirements = \
                [TrackFormatReq(dense=dense, allowOverlaps=True)]
        else:
            self._trackRequirements = \
                [TrackFormatReq(dense=dense, allowOverlaps=False)]

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
        parser = subparsers.add_parser('ValueSelect', help='Selects '
                                                           'all parts of a '
                                                           'track that has a '
                                                           'value bigger then '
                                                           'a given limit and '
                                                           'create a new '
                                                           'track.')
        parser.add_argument('track', help='File path of track')
        parser.add_argument('genome', help='File path of Genome definition')
        parser.add_argument('-l', dest='limit')
        parser.add_argument('--allowOverlap', action='store_true',
                            help="Allow overlap in the resulting track")
        parser.set_defaults(which='Flank')

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
        # TODO: use overlap...

        if 'limit' in args:
            limit = args.limit
        else:
            print("No limit given!")
            sys.exit(1)

        return ValueSelect(track, limit=limit, allowOverlap=allowOverlap)

    @classmethod
    def createTrackName(cls):
        """
        Track name used by GTools when saving the track i GTrackCore
        :return: Generated track name as a string
        """
        return "valueSelect-{0}".format(int(time.time()))

    def printResult(self):
        """
        Operation returns track, not in use
        :return:
        """
        pass
