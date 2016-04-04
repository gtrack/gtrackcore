import numpy as np

def intersect(track1, track2):

    # A intersect only works on dense tracks.
    # If track1 do not have any starts the track is empty.
    assert track1.starts is not None

    # For debugging. Remove later..
    if len(track1.starts) == 0:
        return None

    t1Index = np.arange(0, len(track1), 1)
    t2Index = np.arange(0, len(track2), 1)
    t1Encode = np.zeros(len(track1), dtype=np.int) + 1
    t2Encode = np.zeros(len(track2), dtype=np.int) + 2

    t1CodedStarts = track1.starts * 8 + 5
    t1CodedEnds = track1.ends * 8 + 3
    t2CodedStarts = track2.starts * 8 + 6
    t2CodedEnds = track2.ends * 8 + 2

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

    allStartIndexes = np.where(cumulativeCoverStatus[:-2] >= 3)

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

    trackIndex = tmpStarts[:-1]

    return (starts, ends, trackIndex)
