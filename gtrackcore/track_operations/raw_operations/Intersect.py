import numpy as np

def intersect(t1Starts=None, t1Ends=None, t2Starts=None, t2Ends=None):
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

    if t1Ends is not None:
        assert len(t1Starts) == len(t1Ends)

    if t2Ends is not None:
        assert len(t2Starts) == len(t2Ends)

    resultIsTrack = False

    if t1Ends is None or t2Ends is None:
        # One or both of the input tracks are on the point type.
        # In this case the result will always be a new point track.

        # To make the calculation as simple as possible we convert the
        # segments to a series of points.
        # a segment from 5 -> 10 becomes 6 points (5,6,7,8,9,10)
        if t1Ends is not None:
            t1Starts = np.concatenate([np.arange(x,y) for x,y in zip(t1Starts,
                                                                     t1Ends)])
        elif t2Ends is not None:
            t2Starts = np.concatenate([np.arange(x,y) for x,y in zip(t2Starts,
                                                                     t2Ends)])

        match = np.in1d(t1Starts, t2Starts)

        index = np.arange(0, len(t1Starts), 1)
        encode = np.zeros(len(t1Starts), dtype=np.int) + 1

        starts = t1Starts[match]
        index = index[match]
        encode = encode[match]

        return starts, None, index, encode

    else:
        t1Index = np.arange(0, len(t1Starts), 1)
        t2Index = np.arange(0, len(t2Starts), 1)
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

        allStartIndexes = np.where(cumulativeCoverStatus[:-1] >= 3)

        print("******************")
        print(combined)
        print(allEventCodes)
        print(cumulativeCoverStatus)
        print(allStartIndexes)
        print("******************")

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

        if resultIsTrack:
            ends = None
        else:
            ends = starts + allEventLengths[allStartIndexes]

        trackIndex = tmpStarts[:,-1]
        trackEncoding = tmpStarts[:,-2]


        print("Return of intersect!")
        print("starts: {}".format(starts))
        print("ends: {}".format(ends))
        print("trackIndex: {}".format(trackIndex))
        print("trackEncoding: {}".format(trackEncoding))

        #if pointTrack:
        #    return starts, None, trackIndex, trackEncoding
        #else:
        return starts, ends, trackIndex, trackEncoding
