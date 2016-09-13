import numpy as np
import sys

def subtract(t1Starts, t1Ends, t2Starts, t2Ends, allowOverlapingInputs):
    """
    Subtract a track from another. A-B
    Equal to the set operation relative complement of B in A.

    TODO: support overlapping inputs

    :param t1Starts: Numpy array: Start positions of track A
    :param t1Ends: Numpy array: End positions of track A
    :param t2Starts: Numpy array: Start positions of track B
    :param t2Ends: Numpy array: End positions of track B
    :param allowOverlapingInputs: Boolean: Allow overlap in input tracks.
    :return:
    """

    if len(t1Starts) == 0:
        # TODO: fix for partitions
        # Nothing to subtract from.
        # Returning empty arrays
        return [], [], []

    if t1Ends is None and t2Ends is None:
        # Points - points
        t1Index = np.arange(0, len(t1Starts), 1, dtype='int32')
        select = np.in1d(t1Starts, t2Starts)

        starts = t1Starts[~select]
        index = t1Index[~select]

        return starts, None, index

    elif t1Ends is None:
        # Points - segments
        raise NotImplementedError

    elif t2Ends is None:
        # Segments - points
        raise NotImplementedError
    else:
        # segments - segments

        t1Index = np.arange(0, len(t1Starts), 1, dtype='int32')
        t2Index = np.arange(0, len(t2Starts), 1, dtype='int32')

        if len(t2Starts) == 0:
            # Nothing to subtract, returning track 1
            return t1Starts, t1Ends, t1Index

        t1Encode = np.zeros(len(t1Starts), dtype=np.int) + 1
        t2Encode = np.zeros(len(t2Starts), dtype=np.int) + 2

        t1CodedStarts = t1Starts * 8 + 5
        t1CodedEnds = t1Ends * 8 + 3
        t2CodedStarts = t2Starts * 8 + 6
        t2CodedEnds = t2Ends * 8 + 2

        allCodedEvents = np.concatenate((t1CodedStarts, t1CodedEnds,
                                         t2CodedStarts, t2CodedEnds))

        index = np.concatenate((t1Index,t1Index,t2Index,t2Index))
        encode = np.concatenate((t1Encode,t1Encode,t2Encode,t2Encode))

        combined = np.column_stack((allCodedEvents, index, encode))
        combined = combined[np.lexsort((combined[:, -1], combined[:, 0]))]

        combinedIndex = np.arange(0,len(combined))
        combined = np.column_stack((combined, combinedIndex))

        allSortedEvents = combined[:, 0]
        allEventCodes = (allSortedEvents % 8) - 4
        allSortedDecodedEvents = allSortedEvents / 8

        allEventLengths = allSortedDecodedEvents[1:] - allSortedDecodedEvents[:-1]
        cumulativeCoverStatus = np.add.accumulate(allEventCodes)

        overlapIndexes = np.where(cumulativeCoverStatus[:-1] == 1)

        newStarts = allSortedDecodedEvents[overlapIndexes]
        newEnds = newStarts + allEventLengths[overlapIndexes]

        newIndex = combined[:,-2][overlapIndexes]

        # When two segments overlap totally, we get dangling points...
        # For now we fix it by removing all points. This is probably not the
        # way to go..
        danglingPoints = np.where(newStarts == newEnds)
        newStarts = np.delete(newStarts, danglingPoints)
        newEnds = np.delete(newEnds, danglingPoints)
        newIndex = np.delete(newIndex, danglingPoints)

        return newStarts, newEnds, newIndex
