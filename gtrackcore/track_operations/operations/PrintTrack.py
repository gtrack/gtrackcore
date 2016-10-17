
from collections import OrderedDict

from gtrackcore.track.format.TrackFormat import TrackFormatReq

from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.operations.Operator import KwArgumentInfo

class PrintTrack(Operator):
    """
    Print a track in GTrackCore to terminal
    """

    _trackHelpList = ['Track to print']
    _numTracks = 1
    _resultIsTrack = False
    _trackRequirements = [TrackFormatReq()]

    def _calculate(self, region, tv):

        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()
        values = tv.valsAsNumpyArray()
        strands = tv.strandsAsNumpyArray()
        ids = tv.idsAsNumpyArray()
        edges = tv.edgesAsNumpyArray()
        weights = tv.weightsAsNumpyArray()

        if starts is not None and len(starts) > 0:
            print("Region: {0}".format(region))
            print("*******")
            print("starts: {}".format(starts))
            print("type(starts): {}".format(type(starts)))
            print("ends: {}".format(ends))
            print("type(ends): {}".format(type(ends)))
            print("values: {}".format(values))
            print("type(values): {}".format(type(values)))
            print("strands: {}".format(strands))
            print("type(strands): {}".format(type(strands)))
            print("ids: {}".format(ids))
            print("type(ids): {}".format(type(ids)))
            print("edges: {}".format(edges))
            print("type(edges): {}".format(type(edges)))
            print("weights: {}".format(weights))
            print("type(weights): {}".format(type(weights)))
            print("*******")

    def _getKwArgumentInfoDict(self):
        return OrderedDict([
            ('debug', KwArgumentInfo('debug', 'd', 'Print debug info', bool,
                                     False))])
