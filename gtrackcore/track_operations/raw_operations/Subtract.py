import numpy as np
import sys

def _subtract(t1Starts, t1Ends, t2Starts, t2Ends, t1Index, createIndex=True,
             debug=False):
    """
    Subtract a track from another. A-B
    Equal to the set operation relative complement of B in A.

    :param t1Starts: Numpy array: Start positions of track A
    :param t1Ends: Numpy array: End positions of track A
    :param t2Starts: Numpy array: Start positions of track B
    :param t2Ends: Numpy array: End positions of track B
    :return:
    """

    t2Index = np.full([len(t2Starts)], -1, dtype='int32')

    if len(t2Starts) == 0:
        # Nothing to subtract, returning track 1
        return t1Starts, t1Ends, t1Index

    t1CodedStarts = t1Starts * 8 + 5
    t1CodedEnds = t1Ends * 8 + 3
    t2CodedStarts = t2Starts * 8 + 6
    t2CodedEnds = t2Ends * 8 + 2

    allCodedEvents = np.concatenate((t1CodedStarts, t1CodedEnds,
                                     t2CodedStarts, t2CodedEnds))

    index = np.concatenate((t1Index,t1Index,t2Index,t2Index))

    combined = np.column_stack((allCodedEvents, index))
    combined = combined[np.lexsort((combined[:, -1], combined[:, 0]))]

    allSortedEvents = combined[:, 0]
    allEventCodes = (allSortedEvents % 8) - 4
    allSortedDecodedEvents = allSortedEvents / 8

    allEventLengths = allSortedDecodedEvents[1:] - allSortedDecodedEvents[:-1]
    cumulativeCoverStatus = np.add.accumulate(allEventCodes)

    overlapIndexes = np.where(cumulativeCoverStatus[:-1] == 1)

    newStarts = allSortedDecodedEvents[overlapIndexes]
    newEnds = newStarts + allEventLengths[overlapIndexes]

    if createIndex:
        # When the cover status goes from 3->1 we are going to use a point
        # from track B. We need to update the index so it reflect witch
        # element i track A to use.
        # As we are at status 1, the end point from track A will be
        # somewhere down the cover status.
        # We find this point by setting the index for these points to the
        # index of the next element.
        # If there are multiple segments from B that overlap one from A,
        # then we need to do this updating until all elements are updated.
        # We can do this by only updating the points that do not have a
        # valid index. All elements from trackB have a non valid index of -1.
        # We need to update where the cover status goes from 1 to 3 as well.
        # This is done to "push" the correct index down the array.

        # We check first if there are any any points where we need to find
        # the index

        if len(np.where(combined[:,-1][overlapIndexes] == -1)[0]) > 0:
            # There are points with incorrect indexes
            # find points to fix..

            # Find the points where we go from status 3 -> 1
            atEndIndex = np.where((cumulativeCoverStatus[:-1] == 3) &
                                   (cumulativeCoverStatus[1:] == 1))[0]
            atEndIndex = atEndIndex + 1

            # Find the points where we go from status 1 -> 3
            atStartIndex = np.where((cumulativeCoverStatus[:-1] == 1) &
                                    (cumulativeCoverStatus[1:] == 3))[0]
            atStartIndex = atStartIndex + 1

            index = combined[:,-1]
            startsToUpdate = atStartIndex[
                np.where(combined[:,-1][atStartIndex] == -1)]
            endsToUpdate = atEndIndex[
                np.where(combined[:,-1][atEndIndex] == -1)]

            while len(startsToUpdate) > 0 or len(endsToUpdate) > 0:
                # As the last element will always be a 0, we do not need to
                # check for overflow of the cumulativeCoverStatus array

                if len(startsToUpdate) > 0:
                    startsFromIndex = startsToUpdate + 1
                    combined[:,-1][startsToUpdate] = index[startsFromIndex]

                if len(endsToUpdate) > 0:
                    endsFromIndex = endsToUpdate + 1
                    combined[:,-1][endsToUpdate] = index[endsFromIndex]

                startsToUpdate = atStartIndex[np.where(
                    combined[:,-1][atStartIndex] == -1)]
                endsToUpdate = atEndIndex[np.where(
                    combined[:,-1][atEndIndex] == -1)]
        else:
            if debug:
                print("No points with incorrect index")

    newIndex = combined[:,-1][overlapIndexes]

    if debug:
        print(combined)
        print("newIndex: {}".format(newIndex))

    # When two segments overlap totally, we get dangling points...
    # For now we fix it by removing all points. This is probably not the
    # way to go..
    # if (newStarts == newEnds).any():
    danglingPoints = np.where(newStarts == newEnds)
    newStarts = np.delete(newStarts, danglingPoints)
    newEnds = np.delete(newEnds, danglingPoints)
    newIndex = np.delete(newIndex, danglingPoints)

    return newStarts, newEnds, newIndex

def subtract(t1Starts, t1Ends, t2Starts, t2Ends, t1Strands=None,
             t2Strands=None, createIndex=True, useStrands=True,
             treatMissingAsNegative=False, debug=False):
    """
    Subtract a track from another. A-B
    Equal to the set operation relative complement of B in A.

    :param t1Starts: Numpy array: Start positions of track A
    :param t1Ends: Numpy array: End positions of track A
    :param t2Starts: Numpy array: Start positions of track B
    :param t2Ends: Numpy array: End positions of track B
    :return:
    """

    assert len(t1Starts) == len(t1Ends)
    assert len(t2Starts) == len(t2Ends)

    t1Index = np.arange(0, len(t1Starts), 1, dtype='int32')

    if t1Strands is None or t2Strands is None:
        # Not enough strand information.
        useStrands = False
    else:
        assert len(t1Strands) == len(t1Starts)
        assert len(t2Strands) == len(t2Starts)

    if len(t2Starts) == 0:
        # Nothing to subtract, returning track 1
        return t1Starts, t1Ends, t1Strands, t1Index

    if useStrands:
        if treatMissingAsNegative:
            t1PositiveStrand = np.where(t1Strands == '+')
            t1NegativeStrand = np.where((t1Strands == '-') |
                                        (t1Strands == '.'))

            t2PositiveStrand = np.where(t2Strands == '+')
            t2NegativeStrand = np.where((t2Strands == '-') |
                                        (t2Strands == '.'))

        else:
            t1PositiveStrand = np.where((t1Strands == '+') |
                                        (t1Strands == '.'))
            t1NegativeStrand = np.where(t1Strands == '-')

            t2PositiveStrand = np.where((t2Strands == '+') |
                                        (t2Strands == '.'))
            t2NegativeStrand = np.where(t2Strands == '-')

        posRes = _subtract(t1Starts[t1PositiveStrand],
                           t1Ends[t1PositiveStrand],
                           t2Starts[t2PositiveStrand],
                           t2Ends[t2PositiveStrand],
                           t1Index[t1PositiveStrand],
                           createIndex=createIndex, debug=debug)

        negRes = _subtract(t1Starts[t1NegativeStrand],
                           t1Ends[t1NegativeStrand],
                           t2Starts[t2NegativeStrand],
                           t2Ends[t2NegativeStrand],
                           t1Index[t1NegativeStrand],
                           createIndex=createIndex, debug=debug)

        if len(posRes[0]) > 0 and len(negRes[0]) > 0:
            # result on both strands

            pos = np.column_stack((posRes[0], posRes[1], posRes[2]))
            neg = np.column_stack((negRes[0], negRes[1], negRes[2]))
            res = np.concatenate((pos,neg))

            # Sort on start, then end
            res = res[np.lexsort((res[:,0], res[:,1]))]

            starts = res[:,0]
            ends = res[:,1]
            indexes = res[:,2]

            return starts, ends, indexes

        elif len(posRes[0]) == 0 and len(negRes[0]) == 0:
            # Nothing left to return
            return None, None, None

        elif len(posRes[0]) > 0:
            # Only positive left, returning it
            return posRes
        else:
            # Only negative left, returning it
            return negRes

    else:

        return _subtract(t1Starts, t1Ends, t2Starts, t2Ends, t1Index,
                         createIndex=createIndex, debug=debug)