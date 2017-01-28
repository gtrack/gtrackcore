from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track.format.TrackFormat import TrackFormat
from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.utils.TrackHandling import \
            createRawResultTrackView

from gtrackcore.track_operations.operations.Operator import KwArgumentInfo
from collections import OrderedDict

# Import the appropriate raw operation
from gtrackcore.track_operations.raw_operations.NewOperation import \
    newOperation

# Import operations used in the pre and post methods
from gtrackcore.track_operations.operations.Merge import Merge
from gtrackcore.track_operations.operations.UniquifyLinks import UniquifyLinks
from gtrackcore.track_operations.operations.RemoveDeadLinks import \
    RemoveDeadLinks

# Create a new class of the Operator super class
class NewOperation(Operator):

    # The configuration of the operation.

    _trackHelpList = ['Track 1 description', 'Track 2 description']
    _operationHelp = "Description of the operation"
    _numTracks = 2
    _resultIsTrack = True
    _trackRequirements = [TrackFormatReq(dense=False),
                          TrackFormatReq(dense=False)]

    def _calculate(self, region, tv1, tv2):
        """
        This method is called for each region in the track. Get the data one
        need, call the raw operation and create a new track view from the
        result and return.

        :param region: Current region
        :param tv1: Track view from track 1
        :param tv2: Track view from track 2
        :return: TrackView with a new track, some other results or None.
        """

        # First we need to extract the numpy arrays we need in our operation.
        # The track requirements for each track need to mach what we require.
        t1Starts = tv1.startsAsNumpyArray()
        t1Ends = tv1.endsAsNumpyArray()
        t1Strands = tv1.strandsAsNumpyArray()
        
        t2Starts = tv2.startsAsNumpyArray()
        t2Ends = tv2.endsAsNumpyArray()
        t2Strands = tv2.strandsAsNumpyArray()

        if self._someOtherOption:
            # One might want to use the options to change the raw operation
            # inputs. It's often easier to do this here.
            t1Strands = None
            t2Strands = None

        # Call the raw operation. A raw operation will only take
        # Numpy arrays and options as input
        result = newOperation(t1Starts, t1Ends, t1Strands, t2Strands,
                t2Ends, t2Strands, self._someOption)
        
        # Raw operations will always return new Numpy arrays or 
        # None if there is no result. 
        if result is not None and len(result[0]) != 0:
            # Split the result up for readability 
            starts = result[0]
            ends = result[1]
            strands = result[2]
            index = result[3]
            encoding = result[4]

            # Depending on what the operations does, and how complex
            # it is, you might just want to use create the result 
            # TrackView directly. 
            tv = TrackView(region, starts, ends, None, strands, None,
                           None, None, borderHandling='crop',
                           allowOverlaps=True)
            
            # If we want to keep other data from the input tracks, we
            # can use a function called createRawResultTrackView to 
            # create the trackView. To use this out rawOperation need
            # to return two extra arrays, index and encoding. Index is
            # where in the original track and encoding is witch of the
            # input track (if more then one). Any new* variables are 
            # used, else they are created from the original track
            tv = createRawResultTrackView(index, region, [tv1,tv2], 
                    self._resultAllowOverlaps, encoding=encoding, 
                    newStarts=starts, newEnds=ends)
            return tv
        else:
            # No result or no data at region
            return None


    def preCalculation(self):
        """
        This method can be implement if one want to run operations on the track
        before the start of the main operation.

        Note that this method will run at the initialization of the object.
        :return: None
        """

        # Retrieve the tracks.
        t1 = self._tracks[0]
        t2 = self._tracks[1]

        # Run the calculation on the track. This is often dependent on there
        # track type. Here we uniquify the links if the tracks have them.
        if t1.trackFormat.isLinked():
            u = UniquifyLinks(t1, identifier="track-1")
            t1 = u.calculate()

        if t2.trackFormat.isLinked():
            u = UniquifyLinks(t2, identifier="track-2")
            t2 = u.calculate()

        # Store the updated track.
        self._tracks = [t1, t2]


    def postCalculation(self):
        """
        This method can be implement if one want to run the results through
        one or more operations after the main calculation

        Run the operations using the track in self._result and replace it
        with the new results.
        :return:
        """

        # Run some operation on the result
        r = RemoveDeadLinks(self._result).calculate()
        self._result = r

        if not self._resultAllowOverlap:
            # It is often useful to run cleanup operations here.
            # One we use often is to merge overlap if we do not allow it.
            m =  Merge(self._result).calculate()
            self._result = m

    def _setResultTrackFormat(self):
        """
        Use this method to create the TrackFormat that will correspond to
        the TrackFormat of the result track.

        It is important that the output requirements matches the actual
        output.
        :return: None
        """

        # Here we give some of the common types.

        # Case 1: Result TrackFormat match the TrackFormat of one of the input
        # tracks.
        self._resultTrackFormat = self._tracks[0].trackFormat

        # Case 2: Some form of combination of the different properties
        t1TrackFormat = self._tracks[0].trackFormat
        t2TrackFormat = self._tracks[1].trackFormat

        # Here the resultTrackFormat is stranded only if track 1 is stranded
        # and track 2 is linked.
        if t1TrackFormat.hasStrand() and t2TrackFormat.isLinked():
            strands = []
        else:
            strands = None
        self._resultTrackFormat = TrackFormat(startList=[], endList=[],
                                              strandList=strands)

        # Case 3: Static type.
        # Here the result is always a segmented track
        self._resultTrackFormat = TrackFormat(startList=[], endList=[])


    @classmethod
    def _getKwArgumentInfoDict(self):
        """
        This class defines the operations options

        The KwArgumentInfo contains the following fields.

        key: option key used by argparser
        shortkey: short version of key, used by argparser
        help: help text that describes the option
        contentType: Content type from argparser
        defaultValue: The default value, will be supplied if the options is
            not defined.

        :return: Ordered dict of KwArgumentInfo that define the options
        """
        return OrderedDict([
            ('debug',
            KwArgumentInfo('debug', 'd', 'Print debug info', bool, False)),
            ('resultAllowOverlap',
            KwArgumentInfo('resultAllowOverlap', 'o',
                           'Allow overlap in the result track.', bool,
                            False)),
            ('useStrands',
            KwArgumentInfo('useStrands', 's', 'Follow the strand direction',
                            bool, True)),
            ('treatMissingAsNegative',
            KwArgumentInfo('someOption', 's',
                           'A description of the option',
                            bool, False))])
