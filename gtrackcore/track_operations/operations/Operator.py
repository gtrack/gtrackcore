__author__ = 'skh'

import abc
import glob
from collections import OrderedDict
from os.path import dirname, basename, isfile

from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track.format.TrackFormat import TrackFormat

class InvalidArgumentError(Exception):
    pass

class Operator(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, *args, **kwargs):
        self._allowOverlap = False
        self._numTracks = 0

        # The result
        self._out = None
        self._resultTrack = None
        self._resultFound = False

        # subclasse nottrack
        self._resultIsTrack = False
        self._trackRequirements = None
        self._resultAllowOverlaps = False
        self._resultTrackRequirements = None
        self._setConfig(args)
        self._parseKwargs(**kwargs)

        self._args = args
        self._nestedOperator = False
        self._checkArgs()

    def _checkArgs(self):

        if len(self._args) != self.numTracks:
            raise InvalidArgumentError("Operation requires %s tracks, but %s tracks were given"
                                       % (self.numTracks, len(self._args)))

        for i, arg in enumerate(self._args):
            if isinstance(arg, Operator):
                # Track is another operator
                self._nestedOperator = True
                trackReq = self.trackRequirements[i]
                trackFormat = self.resultTrackRequirements

                #TODO fix this! broken
                trackFormat = TrackFormat(startList=[], endList=[])
                #trackFormat = self.resultTrackRequirements

                if not trackReq.isCompatibleWith(trackFormat):
                    raise InvalidArgumentError("Operation requires track number %s to follow " % i+1 +
                                               "the following requirements: %s. " % trackReq +
                                               "The format of the supplied track is: %s" % trackFormat)
            else:
                if not isinstance(arg, TrackContents):
                    raise InvalidArgumentError("Operation requires TrackContent objects as arguments")

                trackReq = self.trackRequirements[i]
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

    def __call__(self, *args, **kwargs):
        """
        Legacy, remove at a later point.
        :param args:
        :param kwargs:
        :return:
        """
        print("Remove use of __call__!")
        return self.calculate()

    def calculate(self):
        """
        Run operation. Iterates through all regions in a track.

        :return: The result of the operation as a track or as a ordered dict
        of the result per region.
        """

        if self._resultFound:
            # Result already calculated
            if self._resultIsTrack:
                return self._resultTrack
            else:
                return self._out

        self._out = OrderedDict()

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

        self.preCalculation()
        for region in self.getResultRegion():
            trackViewPerArg = [arg.getTrackView(region) for arg in computedArg]
            tv = self._calculate(region, *trackViewPerArg)

            if tv is not None:
                self._out[region] = tv

        if self.resultIsTrack:
            self._resultFound = True
            self._resultTrack = TrackContents(self._resultGenome, self._out)
            self._resultTrack = self.postCalculation(self._resultTrack)
            return self._resultTrack
        else:
            # The result is not a track. Int, float, etc.
            self._resultFound = True
            res = self.postCalculation(self._out)
            return res

    # **** Abstract methods ****
    @abc.abstractmethod
    def _calculate(self, *args):
        """
        Main run method. This will be called one time per region.
        :param args: Arguments of operation (track views, region, ect..)
        :return: Result of operation
        """
        pass

    @abc.abstractmethod
    def _parseKwargs(self, **kwargs):
        """
        Parse the kwargs if any. Used to give options to operations. We are
        using kwargs so we can separate the tracks (witch are checked in the
        the superclass method _checkArgs) and options specific to the
        operation at hand
        optional agruments.
        :param kwargs: Kwargs form init
        :return: None
        """
        pass

    @abc.abstractmethod
    def _updateTrackFormat(self):
        """
        Called when we have updated some of the properties that the track
        requirement depend on.

        The implemented method should create a new track requirement using
        the properties.
        :return: None
        """
        pass

    @abc.abstractmethod
    def _updateResultTrackFormat(self):
        """
        Equal to _updateTrackFormat but now updating the result track
        requirments (if any)
        :return: None
        """
        pass

    @abc.abstractmethod
    def _setConfig(self, trackViews):
        """
        This method should sett all of the required properties of a operation.
        :return: None
        """
        pass

    @abc.abstractmethod
    def printResult(self):
        """
        Used by GTools.
        Used if the operation returns something other the a new track.
        GTools uses this method to print the result.
        :return:
        """
        pass

    @abc.abstractmethod
    def preCalculation(self):
        pass

    @abc.abstractmethod
    def postCalculation(self, result):
        pass

    # **** Abstract class methods ****
    @classmethod
    @abc.abstractmethod
    def createSubParser(cls, subparsers):
        """
        Used by GTools.
        This method should create a appropriate subparser for the GTool
        program. Define inputs tracks ect.
        :param subparsers:
        :return: None
        """
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

    @classmethod
    @abc.abstractmethod
    def createTrackName(cls):
        """
        Used by GTools.
        Creates a track name that GTools uses when saving the track in
        GTrackCore.

        >>> operation.createTrackName()
        union-<date-stamp>

        :return: String. Generated track name for the result of a track
        operation.
        """
        pass


    # **** Common properties ***
    # Properties common to all operation
    # Setters are only defined for properties that can be changed without
    # braking the operation.

    @property
    def allowOverlaps(self):
        """
        Define if we allow overlapping segments in the input tracks.
        :return: None
        """
        return self._allowOverlap

    @allowOverlaps.setter
    def allowOverlaps(self, allowOverlap):
        assert isinstance(allowOverlap, bool)
        self._allowOverlap = allowOverlap
        self._updateTrackFormat()

    @property
    def numTracks(self):
        """
        The number of tracks a operation uses as input.
        :return: None
        """
        return self._numTracks

    @property
    def trackRequirements(self):
        """
        The TrackFormatReq of the input tracks
        :return: None
        """
        return self._trackRequirements

    # Properties about the result of the operation
    @property
    def resultAllowOverlaps(self):
        """
        Define if we allow overlapping segments in the result track (if any).
        :return: None
        """
        return self._resultAllowOverlaps

    @resultAllowOverlaps.setter
    def resultAllowOverlaps(self, allowOverlap):
        assert isinstance(allowOverlap, bool)
        # TODO, if result allow overlap and not input
        self._resultAllowOverlaps = allowOverlap
        self._updateResultTrackFormat()

    @property
    def resultIsTrack(self):
        """
        Define if result is a track or not.
        :return: None
        """
        return self._resultIsTrack

    @property
    def resultTrackRequirements(self):
        """
        The TrackFormatReq of the result track (if any).
        :return: None
        """
        return self._resultTrackRequirements

    # **** Misc methods ****
    def isNestable(self):
        """
        Check if the operation can be "nested" into another operations.
        Any operation that returns a track can be nested. An operation
        that returns a number can not.

        Made this into a method so it can be expanded later without
        changing the call code.
        :return: True if nestable, false else
        """
        return self.resultIsTrack

    def getResultRegion(self):
        """
        Returns the regions
        :return:
        """
        # TODO: Se paa denne!
        # Use extended genome
        if isinstance(self._args[0], Operator):
            return self._args[0].getResultRegion()
        else:
            return self._args[0].regions

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

    def _createTrackView(self, region, startList=None, endList=None,
                         valList=None, strandList=None, idList=None,
                         edgesList=None, weightsList=None,
                         extraLists=OrderedDict()):
        """
        TODO move this to a util file?
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
        return TrackView(region, startList, endList, valList, strandList,
                         idList, edgesList, weightsList,
                         borderHandling='crop',
                         allowOverlaps=self.resultAllowOverlaps,
                         extraLists=extraLists)


def getOperation():
    """
    Returns all defined operations. This method is used to create a dynamic
    cli.

    Works in the normal pythonic way. Will ignore any files starting with a
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
