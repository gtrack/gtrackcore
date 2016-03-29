__author__ = 'skh'

import abc
import glob
from collections import OrderedDict
from os.path import dirname, basename, isfile

from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track.format.TrackFormat import TrackFormatReq
import inspect

class InvalidArgumentError(Exception):
    pass

class Operator(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, *args):
        self._args = args
        self._nestedOperator = False
        self._checkArgs()

    def _checkArgs(self):

        if len(self._args) != self._NUM_TRACKS:
            raise InvalidArgumentError("Operation requires %s tracks, but %s tracks were given"
                                       % (self._NUM_TRACKS, len(self._args)))

        for i, arg in enumerate(self._args):
            if isinstance(arg, Operator):
                # Track is another operator
                self._nestedOperator = True
                trackReq = self._TRACK_REQUIREMENTS[i]
                trackFormat = arg._RESULT_TRACK_REQUIREMENTS

                if not trackReq.isCompatibleWith(trackFormat):
                    raise InvalidArgumentError("Operation requires track number %s to follow " % i+1 +
                                               "the following requirements: %s. " % trackReq +
                                               "The format of the supplied track is: %s" % trackFormat)
            else:
                if not isinstance(arg, TrackContents):
                    raise InvalidArgumentError("Operation requires TrackContent objects as arguments")

                trackReq = self._TRACK_REQUIREMENTS[i]
                trackFormat = arg.firstTrackView().trackFormat
                if not trackReq.isCompatibleWith(trackFormat):
                    raise InvalidArgumentError("Operation requires track number %s to follow " % i+1 +
                                               "the following requirements: %s. " % trackReq +
                                               "The format of the supplied track is: %s" % trackFormat)

        regionsFirstArg = self.getResultRegion()
        genomeFirstArg = self.getResultGenome()
        self._resultGenome = genomeFirstArg
        for i, arg in enumerate(self._args[1:]):
            if isinstance(arg, Operator):
                if arg.getResultRegion() != regionsFirstArg:
                    raise InvalidArgumentError("Region lists must be the same for all tracks")
                if arg.getResultGenome() != genomeFirstArg:
                    raise InvalidArgumentError("All tracks must have the same genome")
            else:
                if arg.regions != regionsFirstArg:
                    raise InvalidArgumentError("Region lists must be the same for all tracks")
                if arg.genome != genomeFirstArg:
                    raise InvalidArgumentError("All tracks must have the same genome")

    def __call__(self):
        """
        Call method. Iterates through all regions in a track.

        TODO: Implement buffering of the results
        :return: The result of the operation as a track or as a ordered dict of the result per region.
        """

        out = OrderedDict()

        if self._nestedOperator:
            # There are nested operators in that needs to be computed.
            computedArg = []
            for arg in self._args:
                if isinstance(arg, Operator):
                    computedArg.append(arg())
                else:
                    computedArg.append(arg)
        else:
            computedArg = self._args

        for region in self.getResultRegion():
            trackViewPerArg = [arg.getTrackView(region) for arg in computedArg]
            tv = self._call(region, *trackViewPerArg)
            out[region] = tv

        if self._RESULT_IS_TRACK:
            return TrackContents(self._resultGenome, out)
        else:
            # The result is not a track. Int, float, etc.
            return out

    @abc.abstractmethod
    def _call(self, *args):
        pass

    @classmethod
    @abc.abstractmethod
    def createSubParser(cls, subparsers):
        pass

    @classmethod
    @abc.abstractmethod
    def createOperation(cls, args):
        """
        Used by GTools.
        Create a operation object from the arguments given from GTools.

        :param args: Arguments from the parser in GTools
        :return: A operation object.
        """
        pass

    def isNestable(self):
        """
        Check if the operation can be "nested" into another operations.
        Any operation that returns a track can be nested. An operation
        that returns a number can not.

        Made this into a method so it can be expanded later without
        changing the call code.
        :return: True if nestable, false else
        """
        return self._RESULT_IS_TRACK


    def getResultRegion(self):
        """
        Returns the regions
        :return:
        """
        if self.isNestable():
            # TODO: Se paa denne!
            # Use extended genome
            if isinstance(self._args[0], Operator):
                return self._args[0].getResultRegion()
            else:
                return self._args[0].regions
        else:
            return None

    def getResultGenome(self):
        """
        Returns the genome of the results.
        :return:
        """
        if self.isNestable():
            if isinstance(self._args[0], Operator):
                return self._args[0].getResultGenome()
            else:
                return self._args[0].genome
        else:
            return None

    def _createTrackView(self, region, startList=None, endList=None, valList=None, strandList=None, idList=None,
                        edgesList=None, weightsList=None, extraLists=OrderedDict()):
        """
        Help function used to create a track view.
        :param region:
        :param startList:
        :param endList:
        :param valList:
        :param strandList:
        :param idList:
        :param edgesList:
        :param weightsList:
        :param extraLists:
        :return:
        """
        return TrackView(region, startList, endList, valList, strandList, idList, edgesList, weightsList,
                         borderHandling='crop', allowOverlaps=self._RESULT_ALLOW_OVERLAPS, extraLists=extraLists)


def getOperation():
    """
    Returns all defined operations. This method is used to create a dynamic
    cli.

    Works in a normal python way. Will ignore any files starting with a
    underscore.

    TODO: Check that we only add valid operations.

    :return: A list of all operations in the operations folder.
    """

    name = __name__.split('.')[-1]
    files = glob.glob(dirname(__file__)+"/*.py")
    operations = [basename(file)[:-3] for file in files if isfile(file) and
                  not basename(file)[:-3].startswith('_') and basename(
                  file)[:-3] != name]

    module = '.'.join(__name__.split('.')[:-1])

    return module, operations
