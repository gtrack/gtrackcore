import numpy as np

def intersect(t1Starts=None, t1Ends=None, t2Starts=None, t2Ends=None,
              resultIsPoints=False):
    """
    Find the intersect of two none dense tracks.

    TODO: Add support for strands.
    TODO: Add support for "minimum overlap"

    :param t1Starts:
    :param t1Ends:
    :param t2Starts:
    :param t2Ends:
    :return:
    """

    assert t1Starts is not None
    assert t2Starts is not None

    assert len(t1Starts) == len(t1Ends)
    assert len(t2Starts) == len(t2Ends)

    t1Index = np.arange(0, len(t1Starts), 1)
    t2Index = np.arange(0, len(t2Starts), 1)
    t1Encode = np.zeros(len(t1Starts), dtype=np.int) + 1
    t2Encode = np.zeros(len(t2Starts), dtype=np.int) + 2

    t1CodedStarts = t1Starts * 8 + 5
    t1CodedEnds = t1Ends * 8 + 3
    t2CodedStarts = t2Starts * 8 + 6
    t2CodedEnds = t2Ends * 8 + 2

    print("t1Index: {}".format(t1Index))

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

    allStartIndexes = np.where(cumulativeCoverStatus[:-1] >= 3)

    tmpStarts = combined[allStartIndexes]

    # Find segments with index from track B
    wrongIndex = np.where(tmpStarts[:, -2] == 2)
    elementsToUpdate = tmpStarts[wrongIndex]

    while len(elementsToUpdate) > 0:
        combinedIndex = elementsToUpdate[:,-1]
        updatedCombinedIndex = combinedIndex - 1

        # TODO: check for underflow?
        newElements = combined[updatedCombinedIndex]

        # Update combined index
        tmpStarts[wrongIndex,-1] = newElements[:,-1]
        # Update encoding
        tmpStarts[wrongIndex,-2] = newElements[:,-2]
        # Update index
        tmpStarts[wrongIndex,-3] = newElements[:,-3]

        # Update elementsToUpdate
        wrongIndex = np.where(tmpStarts[:,-2] == 2)
        elementsToUpdate = tmpStarts[wrongIndex]

    # Res
    # Codedvalue, index, encoding, combinedIndex

    starts = tmpStarts[:,0]/8
    ends = starts + allEventLengths[allStartIndexes]

    trackIndex = tmpStarts[:,-2]
    trackEncoding = tmpStarts[:,-1]

    print("**********")
    print(tmpStarts)
    print("**********")

    print("Return of intersect!")
    print("starts: {}".format(starts))
    print("ends: {}".format(ends))
    print("trackIndex: {}".format(trackIndex))
    print("trackEncoding: {}".format(trackEncoding))

    #if pointTrack:
    #    return starts, None, trackIndex, trackEncoding
    #else:
    return starts, ends, trackIndex, trackEncoding
