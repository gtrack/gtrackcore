__author__ = 'skh'

__author__ = 'skh'

import logging
import sys

from gtrackcore.util.CommonFunctions import convertTNstrToTNListFormat
from gtrackcore.track.core.Track import Track
from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.track_operations.RawOperationContent import RawOperationContent
from gtrackcore.track_operations.utils.TrackHandling import \
    createTrackContentFromTrack
from gtrackcore.track_operations.Genome import Genome

class PrintTrack(Operator):
    """
    Print a track in GTrackCore to terminal
    """

    def _calculate(self, region, tv):

        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()
        vals = tv.valsAsNumpyArray()
        ids = tv.idsAsNumpyArray()
        edges = tv.edgesAsNumpyArray()
        weights = tv.weightsAsNumpyArray()

        if starts is not None and len(starts) > 0:
            print("Region: {0}".format(region))
            print("{0: >8} {1: >8}".format("start", "end"))
            for x, y in zip(starts,ends):
                print("{0:8d} {1:8d}".format(x, y))

            print("*******")
            print("ids: {}".format(ids))
            print("type(ids): {}".format(type(ids)))
            print("edges: {}".format(edges))
            print("type(edges): {}".format(type(edges)))
            print("weights: {}".format(weights))
            print("starts: {}".format(starts))
            print("type(starts): {}".format(type(starts)))
            print("ends: {}".format(ends))
            print("type(ends): {}".format(type(ends)))
            print("*******")

    def _setConfig(self, args):
        # None changeable properties
        self._numTracks = 1
        self._trackRequirements = \
            [TrackFormatReq(dense=False, allowOverlaps=False)]
        self._allowOverlap = False
        self._resultAllowOverlaps = False
        self._resultIsTrack = False
        self._resultTrackRequirements = None

    def _parseKwargs(self, **kwargs):
        """
        :param kwargs:
        :return: None
        """

        if 'debug' in kwargs:
            self._debug = kwargs['debug']
        else:
            self._debug = False

        if self._debug:
            level = logging.DEBUG
        else:
            level = logging.INFO
        logging.basicConfig(stream=sys.stderr, level=level)

    def preCalculation(self):
        pass

    def postCalculation(self, result):
        return result

    def _updateTrackFormat(self):
        """
        If we enable or disable overlapping tracks as input, we need to
        update the track requirement as well.
        :return: None
        """
        pass

    def _updateResultTrackFormat(self):
        """
        If we enable or disable overlapping tracks in the result, we need to
        update the track requirement as well.
        :return: None
        """
        pass

    def printResult(self):
        pass

    @classmethod
    def createSubParser(cls, subparsers):
        """
        Creates a subparser. Used by GTool
        :param subparsers:
        :return: None
        """
        parser = subparsers.add_parser('print', help='Print a track from '
                                                     'gtrackcore to '
                                                     'terminal. For DEBUG '
                                                     'usage')
        parser.add_argument('track', help='Track name')
        parser.add_argument('genome', help='File path of Genome definition')
        parser.set_defaults(which='PrintTrack')

    @classmethod
    def createOperation(cls, args):
        """
        Generaor classmethod used by GTool

        :param args: args from GTool
        :return: PrintTrack object
        """
        genome = Genome.createFromJson(args.genome)
        trackName = convertTNstrToTNListFormat(args.track, doUnquoting=True)

        track = Track(trackName)
        track.addFormatReq(TrackFormatReq(allowOverlaps=False))
        trackContent = createTrackContentFromTrack(track, genome)

        return PrintTrack(trackContent)
