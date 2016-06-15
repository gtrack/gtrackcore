import numpy as np

from gtrackcore.track_operations.exeptions.Track import TrackIncompatibleException

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

    assert len(t1Starts) == len(t1Ends)
    assert len(t2Starts) == len(t2Ends)

    t1Index = np.arange(0, len(t1Starts), 1, dtype='int32')
    t1Encode = np.zeros(len(t1Starts), dtype='int32') + 1

    # In a points/segments subtract we are never interested in track B.
    # Setting the to -1 to make debugging easier.
    t2Index = np.arange(0, len(t1Starts), 2, dtype='int32')
    t2Encode = np.zeros(len(t2Starts), dtype='int32') + 2

    # We first remove any totally overlapping segments
    # Doing this at the start saves us some work at the end.

    t1 = np.column_stack((t1Starts, t1Ends, t1Index, t1Encode))
    t2 = np.column_stack((t2Starts, t2Ends, t2Index, t2Encode))
    combined = np.concatenate((t1, t2))

    # Sort the new array on position and then on encoding.
    res = combined[np.lexsort((combined[:, -1], combined[:, 1],
                               combined[:, 0]))]

    updated = False
    totalOverlapIndex = np.where((res[:-1,1] == res[1:,1]) and
                                 res[:-1,0] == res[1:,0])
    if totalOverlapIndex[0].size > 0:
        print("Removing overlap!")
        deleteIndex = np.concatenate((totalOverlapIndex[0],
                                  totalOverlapIndex[0] + 1))

        # Remove possible duplicates.
        deleteIndex = np.unique(deleteIndex)

        # Removing the total overlap
        res = np.delete(res, deleteIndex, 0)
        updated = True

        # Find index of the updated tracks
        t1Updated = np.where((res[:,-1] == 1))
        t2Updated = np.where((res[:,-2] == 2))

        t1 = res[t1Updated]
        t1Starts = t1[:,0]
        t1Ends = t1[:,1]
        t1Index = t1[:,2]

        if t1Starts.size == 0:
            # If there is nothing left of t1 at this point we just return
            # the empty arrays.
            assert t1Ends.size == 0
            assert t1Index.size == 0
            return [], [], []

        t2 = res[t2Updated]

        t2Starts = t2[:,0]
        t2Ends = t2[:,1]

    if t2Starts.size == 0:
        # t2 is now empty, returning t1 as it stands.
        return t1Starts, t1Ends, t1Index
    else:
        t2Index = np.zeros(len(t2Starts), dtype='int32') - 1


    # TODO:
    # Problem: we get dangling points whit this method..
    # It can not be removed with the same method as total overlap.

    t1CodedStarts = t1Starts * 8 + 5
    t1CodedEnds = t1Ends * 8 + 3
    t2CodedStarts = t2Starts * 8 + 6
    t2CodedEnds = t2Ends * 8 + 2

    # Concat all of the coded events
    allCodedEvents = np.concatenate((t1CodedStarts, t1CodedEnds,
                                     t2CodedStarts, t2CodedEnds))

    # Create indexes and encoding for the coded events.
    # Index is the index in the base track
    # Encoding identifies which track is the base.
    index = np.concatenate((t1Index,t1Index,t2Index,t2Index))
    #encode = np.concatenate((t1Encode,t1Encode,t2Encode,t2Encode))

    # Combine and sort the coded events with the indexes and encoding
    combined = np.column_stack((allCodedEvents, index))
    combined = combined[np.lexsort((combined[:, -1], combined[:, 0]))]

    # Adding a index. We use this index when updating the track index in
    # starts from track B.
    combinedIndex = np.arange(0,len(combined))
    combined = np.column_stack((combined, combinedIndex))

    allSortedCodedEvents = combined[:, 0]
    allEventCodes = (allSortedCodedEvents % 8) - 4
    allSortedDecodedEvents = allSortedCodedEvents / 8
    allEventLengths = allSortedDecodedEvents[1:] - allSortedDecodedEvents[:-1]

    # We find the starts of the new track by the use of the cumulative cover
    #  status. We want the starts with cover status 1.
    cumulativeCoverStatus = np.add.accumulate(allEventCodes)
    allIntersectStartIndexes = np.where(cumulativeCoverStatus[:-1] == 1)

    res = combined[allIntersectStartIndexes]

    # If a start is from track B, we need to update its index to the
    # corresponding index i track A.
    wrongIndex = np.where(res[:,-2] == -1)
    elementsToUpdate = res[wrongIndex]

    while len(elementsToUpdate) > 0:
        # Get the next element in the combined matrix.
        newCombinedIndex = elementsToUpdate[:,-1] + 1

        # Update the combined index in res and get the corresponding track
        # index
        res[wrongIndex,-1] = newCombinedIndex
        res[wrongIndex,1] = combined[newCombinedIndex,1]

        indexesToUpdate = np.where(res[:,-2] == -1)
        elementsToUpdate = res[indexesToUpdate]

    starts = res[:,0]/8

    ends = starts + allEventLengths[allIntersectStartIndexes]
    trackIndex = res[:,-2]

    return starts, ends, trackIndex
