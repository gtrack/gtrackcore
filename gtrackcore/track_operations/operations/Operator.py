
import abc
import glob
import time
from collections import OrderedDict
from collections import namedtuple
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

    _numTracks = 0
    _resultIsTrack = False
    _nestedOperator = False

    _result = None

    def __init__(self, *args, **kwargs):
        self._tracks = args

        # Load the default kwargs and set any given ones.
        self._kwargs = self._parseKwargs(**kwargs)

        # Generate the resultTrackFormat
        self._setResultTrackFormat()

        # Run the preCalculate (if any)
        # preCalc updates the self._tracks
        self._preCalculation()

        self._checkArgs()

    def _checkArgs(self):

        if len(self._tracks) != self._numTracks:
            raise InvalidArgumentError("Operation requires {} tracks, but {} "
                                       "tracks were given"
                                       .format(self.numTracks, len(self._tracks)))

        for i, track in enumerate(self._tracks):
            if isinstance(track, Operator):
                # Track is another operator
                self._nestedOperator = True
                trackReq = self.trackRequirements[i]
                trackFormat = track.resultTrackRequirements

                if not trackReq.isCompatibleWith(trackFormat):
                    raise InvalidArgumentError(
                        ("Operation requires track number {} to follow "
                         "the following requirements: {} "
                         "The format of the supplied track is: {}"
                         .format(i+1, trackReq,trackFormat)))
            else:
                if not isinstance(track, TrackContents):
                    raise InvalidArgumentError(
                        "Operation requires TrackContent objects as arguments")

                trackReq = self.trackRequirements[i]
                trackFormat = track.firstTrackView().trackFormat

                if not trackReq.isCompatibleWith(trackFormat):
                    raise InvalidArgumentError(
                        ("Operation requires track number {} to follow "
                         "the following requirements: {} "
                         "The format of the supplied track is: {}"
                         .format(i+1, trackReq, trackFormat)))

        regionsFirstArg = self.getResultRegion()
        genomeFirstArg = self.getResultGenome()
        self._resultGenome = genomeFirstArg
        for i, track in enumerate(self._tracks[1:]):
            if isinstance(track, Operator):
                if track.getResultRegion() != regionsFirstArg:
                    raise InvalidArgumentError(
                        "Region lists must be the same for all tracks")
                if track.getResultGenome() != genomeFirstArg:
                    raise InvalidArgumentError(
                        "All tracks must have the same genome")
            else:
                if track.regions != regionsFirstArg:
                    raise InvalidArgumentError(
                        "Region lists must be the same for all tracks")
                if track.genome != genomeFirstArg:
                    raise InvalidArgumentError(
                        "All tracks must have the same genome")

    # Kwargs handling methods
    def __getattr__(self, name):
        """
        Dynamically return the given options or default value.
        :param name: Variable name
        :return: The value from the _kwargs dict with name as key
        :raises AttributeError: If name is not a key in _kwargs
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
                raise AttributeError("{} not found in kwarg".format(name))
        else:
            raise AttributeError

    def _parseKwargs(self, **kwargs):
        """
        Get the operations default kwargs. Parse the kwargs combine then into
        one dict that define all off the operations options.

        Kwargs not define are ignored
        :return:
        """
        # Extract the default values

        kw = {k: v.defaultValue for k, v in self.getKwArgumentInfoDict().iteritems()}

        for k, v in kwargs.iteritems():
            if k in kw:
                kw[k] = v
            else:
                # Maybe remove this at some point. But is is rather nice
                # when debuging
                raise TypeError("{} not defined in the "
                                "KwArgumentInfoDict!".format(k))

        return kw

    def getKwArgumentInfoDict(self):
        """
        Return the operations keyword arguments.
        :return:
        """
        return self._getKwArgumentInfoDict()

    def _getKwArgumentInfoDict(self):
        """
        Overload this in each operation
        :return:
        """
        pass

    def _setResultTrackFormat(self):
        """
        Overload this method if one wants to define the TrackFormat of the
        result track.
        :return:
        """
        # Set to None if not overloaded
        self._resultTrackFormat = None

    # Calculation methods
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

        if self._result is not None:
            # If we have a result we return it
            return self._result

        self._result = OrderedDict()

        # Compute any nested operations.
        computedTracks = []
        for track in self._tracks:
            if isinstance(track, Operator):
                computedTracks.append(track.calculate())
            else:
                computedTracks.append(track)

        result = OrderedDict()
        for region in self.getResultRegion():
            trackViewPerArg = [track.getTrackView(region) for track in
                               computedTracks]
            tv = self._calculate(region, *trackViewPerArg)

            if tv is not None:
                result[region] = tv

        if self.resultIsTrack:
            # Result is a track. Create new TrackContent
            self._result = TrackContents(self._resultGenome, result)
        else:
            # The result is not a track.
            self._result = result

        self._postCalculation()
        return self._result

    def _preCalculation(self):
        pass

    def _postCalculation(self):
        pass

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

    def getKwArguments(self):
        """
        TODO: List all KwArguments recursively down the operations
        :return:
        """

        pass

    def setKwArguments(self, **kwargs):
        """
        Set a given keyword argument.

        How do we
        :param kwargs:
        :return:
        """
        pass

    def _updateTrackFormatRequirements(self):
        """
        Remove?

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
        Remove ?
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

    def printResult(self):
        """
        Used by GTools.
        Used if the operation returns something other the a new track.
        GTools uses this method to print the result.
        Overload if one wants more complex printing
        :return:
        """

        if isinstance(self._result, TrackContents):
            pass
        else:
            if self._result is not None:
                print(self._out)
            else:
                print("ERROR! Calculation not run!")

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
    def resultTrackFormat(self):
        """
        The TrackFormatReq of the result track (if any).
        :return: None
        """
        return self._resultTrackFormat

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
        if isinstance(self._tracks[0], Operator):
            return self._tracks[0].getResultRegion()
        else:
            return self._tracks[0].regions

    def getResultGenome(self):
        """
        Returns the genome of the results.
        :return:
        """
        if self.isNestable():
            if isinstance(self._tracks[0], Operator):
                return self._tracks[0].getResultGenome()
            else:
                return self._tracks[0].genome
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


# Named tuple uses to define the keyword arguments of a operation
KwArgumentInfo = namedtuple('KwArgumentInfo', ['key', 'shortkey', 'help',
                                               'contentType', 'defaultValue'])


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
