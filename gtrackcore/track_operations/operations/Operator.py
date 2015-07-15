__author__ = 'skh'

import abc
from collections import OrderedDict
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track.format.TrackFormat import TrackFormatReq

class InvalidArgumentError(Exception):
    pass


class Operator(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, *args):
        self._args = args
        self._checkArgs()

    def _checkArgs(self):
        if len(self._args) != self._NUM_TRACKS:
            raise InvalidArgumentError("Operation requires %s tracks, but %s tracks were given"
                                       % (self._NUM_TRACKS, len(self._args)))

        for i, arg in enumerate(self._args):
            if not isinstance(arg, TrackContents):
                raise InvalidArgumentError("Operation requires TrackContent objects as arguments")

            trackReq = self._TRACK_REQUIREMENTS[i]
            trackFormat = arg.firstTrackView().trackFormat
            if not trackReq.isCompatibleWith(trackFormat):
                raise InvalidArgumentError("Operation requires track number %s to follow " % i+1 +
                                           "the following requirements: %s. " % trackReq +
                                           "The format of the supplied track is: %s" % trackFormat)

        regionsFirstArg = self._args[0].regions
        genomeFirstArg = self._args[0].genome

        for i, arg in enumerate(self._args[1:]):
            if arg.regions != regionsFirstArg:
                raise InvalidArgumentError("Region lists must be the same for all tracks")

            if arg.genome != genomeFirstArg:
                raise InvalidArgumentError("All tracks must have the same genome")

    def __call__(self):
        out = OrderedDict()

        for region in self._args[0].regions:
            trackViewPerArg = [arg.getTrackView(region) for arg in self._args]
            tv = self._call(region, *trackViewPerArg)

            out[region] = tv

        #TODO get the genome from the trackview
        return TrackContents('hg19', out)


    @abc.abstractmethod
    def _call(self, *args):
        pass

    def _createTrackView(self, region, startList=None, endList=None, valList=None, strandList=None, idList=None,
                        edgesList=None, weightsList=None, extraLists=OrderedDict()):

        return TrackView(region, startList, endList, valList, strandList, idList, edgesList, weightsList,
                         borderHandling='crop', allowOverlaps=self._RESULT_ALLOW_OVERLAPS, extraLists=extraLists)

