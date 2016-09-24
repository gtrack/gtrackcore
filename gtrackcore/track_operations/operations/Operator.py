__author__ = 'skh'

import abc
import glob
import time
from collections import OrderedDict
from os.path import dirname, basename, isfile

from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.track_operations.Genome import Genome
from gtrackcore.track_operations.utils.TrackHandling import \
    createTrackContentFromFile

from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track.format.TrackFormat import TrackFormat
from gtrackcore.track.format.TrackFormat import TrackFormatReq


class InvalidArgumentError(Exception):
    pass

class Operator(object):
    __metaclass__ = abc.ABCMeta

    # Global default options. If a default value is not defined in a
    # operation, we use the global default. __getattr__ will use this as
    # a last resort.
    GLOBAL_DEFAULT_OPTIONS = {
        'debug': False,
        'allowOverlap': False,
        'resAllowOverlap': False,
        'trackFormatReqChangeable': False,
        'resultTrackFormatReqChangeable': False
        }

    def __init__(self, *args, **kwargs):
        self._kwargs = kwargs

        # The result
        self._out = None  # Redundant with _resultTrack
        self._resultTrack = None
        self._resultFound = False  # Redundant with _resultTrack

        self._args = self.preCalculation(args)

        # Default value
        self._nestedOperator = False

        # Update the track format requirements.
        #self._updateTrackFormat()
        #self._updateResultTrackFormat()

        self._checkArgs()

    def _checkArgs(self):

        if len(self._args) != self.numTracks:
            raise InvalidArgumentError("Operation requires %s tracks, but %s tracks were given"
                                       % (self.numTracks, len(self._args)))

        for i, arg in enumerate(self._args):
            if isinstance(arg, Operator):
                # Track is another operator
                self._nestedOperator = True
                trackReq = self._trackRequirements[i]
                trackFormat = self._resultTrackRequirements

                #TODO fix this! broken
                trackFormat = TrackFormat(startList=[], endList=[])
                #trackFormat = self.resultTrackRequirements

                if isinstance(trackReq, list):
                    # Track supports multiple track requirements.
                    if not any([tr.isCompatibleWith(trackFormat)
                                for tr in trackReq]):
                        raise InvalidArgumentError("Operation requires track number %s to follow " % i+1 +
                                                   "the following requirements: %s. " % trackReq +
                                                   "The format of the supplied track is: %s" % trackFormat)
                else:
                    if not trackReq.isCompatibleWith(trackFormat):
                        raise InvalidArgumentError("Operation requires track number %s to follow " % i+1 +
                                                   "the following requirements: %s. " % trackReq +
                                                   "The format of the supplied track is: %s" % trackFormat)
            else:
                if not isinstance(arg, TrackContents):
                    raise InvalidArgumentError("Operation requires TrackContent objects as arguments")

                trackReq = self.trackRequirements[i]
                trackFormat = arg.firstTrackView().trackFormat

                if isinstance(trackReq, list):
                    # Track supports multiple track requirements.
                    if not any([tr.isCompatibleWith(trackFormat)
                                for tr in trackReq]):
                        raise InvalidArgumentError("Operation requires track number %s to follow " % i+1 +
                                                    "the following requirements: %s. " % trackReq +
                                               "The format of the supplied track is: %s" % trackFormat)

                else:
                    #
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

    def __getattr__(self, name):
        """
        Dynamically return the given options or default value.
        :param name: Variable name
        :return:
        """
        if name is '_options' or name is '_kwargs':
            # The operation is missing the _options and _kwargs variables
            # These need to be set in the __init__ method.
            raise AttributeError("The operations is missing {}".format(name))
        elif name.startswith('_'):
            try:
                # If in kwargs, return it
                return self._kwargs[name[1:]]
            except KeyError:
                try:
                    # Try to return the default value if we have it
                    return self._options[name[1:]]
                except KeyError:
                    try:
                        # Last resort. Try to return the global default
                        return self.GLOBAL_DEFAULT_OPTIONS[name[1:]]
                    except KeyError:
                        raise AttributeError
        else:
            raise AttributeError

    def __call__(self, *args, **kwargs):
        """
        Legacy, remove at a later point.
        :param args:
        :param kwargs:
        :return:
        """
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

        #self._args = self.preCalculation(self._args)
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

    @classmethod
    def factory(cls, args):
        """
        We get the args dict from argparse

        From this dict we need to pop the track names and create the
        trackContent objects. The rest we give to the object as the kwargs.

        Any arg starting with track is interpreted as a track.

        Track* is reserved for tracks only.

        :param args:
        :return:
        """

        # args is a namespace. Get it's dict
        args = vars(args)

        # Get the genome
        assert 'genome' in args.keys()
        genome = Genome.createFromJson(args['genome'])
        del args['genome']

        # Any key matching 'track*' is assumed to be a track.
        trackKeys = [key for key in args.keys()
                     if key.startswith('track')]
        assert len(trackKeys) > 0

        # TODO: Add support for different allowOverlap on each track.
        allowOverlap = False
        if 'allowOverlap' in args:
            allowOverlap = args['allowOverlap']
        else:
            # Assume False if not set.
            allowOverlap = False

        # Sort the keys
        # The tracks will be given to the operation in alphabetical order.
        trackKeys = sorted(trackKeys)

        tracks = [createTrackContentFromFile(genome, args[key], allowOverlap)
                  for key in trackKeys]

        # Delete the tracks from args
        for key in trackKeys:
            del args[key]

        return cls(*tracks, **args)

    def _updateTrackFormatRequirements(self):
        """
        Called when we have updated some of the properties that the track
        requirement depend on.

        :return:
        """
        if self._trackFormatReqChangeable:
            # Only update requirements if the operation allows it
            self._trackRequirements = \
                [TrackFormatReq(dense=r.isDense(),
                                allowOverlaps=self._allowOverlap) for r in
                 self._trackRequirements]

    def _updateResultTrackFormatRequirements(self):
        """
        Equal to _updateTrackFormat but now updating the result track
        requirments (if any)
        :return: None
        """
        if self._resultTrackFormatReqChangeable:
            # Only update requirements if the operation allows it
            if self._resultIsTrack is not None:
                # Result is a track.
                dense = self._resultTrackRequirements.isDense()
                self._resultTrackRequirements = \
                    TrackFormatReq(dense=dense, allowOverlaps=self._allowOverlap)

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
    def preCalculation(self, tracks):
        pass

    @abc.abstractmethod
    def postCalculation(self, result):
        super(Operator, self).postCalculation(result)
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

    #@classmethod
    #@abc.abstractmethod
    #def createOperation(cls, args):
    #    """
    #    Used by GTools.
    #    Create a operation object from the arguments given from GTools.
    #    :param args: Arguments from the parser in GTools
    #    :return: A operation object.
    #    """
    #    pass

    def createTrackName(self):
        """
        Used by GTools.
        Creates a track name that GTools uses when saving the track in
        GTrackCore.

        >>> operation.createTrackName()
        union-<date-stamp>

        :return: String. Generated track name for the result of a track
        operation.
        """
        if self.resultIsTrack:
            return "{}-{}".format(self.__class__.__name__, int(time.time()))
        else:
            return None

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
