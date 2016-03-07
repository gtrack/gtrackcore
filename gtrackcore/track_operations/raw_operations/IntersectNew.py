import numpy as np

from gtrackcore.track_operations.exeptions.Track import TrackIncompatibleException

def intersect(track1, track2, resultReq):

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

    print("new combined : ->{0}<-".format(combined))

    allSortedEvents = combined[:, 0]
    allEventCodes = (allSortedEvents % 8) - 4
    allSortedDecodedEvents = allSortedEvents / 8

    allEventLengths = allSortedDecodedEvents[1:] - allSortedDecodedEvents[:-1]
    cumulativeCoverStatus = np.add.accumulate(allEventCodes)

    allStartIndexes = np.where(cumulativeCoverStatus[:-2] >= 3)

    result = combined[allStartIndexes]

    print("**** Result before index update ****")
    print(result)
    print("------------------")
    # Find segments with index from track B
    wrongIndex = np.where(result[:,-2] == 2)
    elementsToUpdate = result[wrongIndex]

    while len(elementsToUpdate) > 0:
        updatedCombinedIndex = elementsToUpdate[:,-1]
        updatedCombinedIndex -= 1
        # TODO: check for underflow?

        newElements = combined[updatedCombinedIndex]

        updatedEncoding = newElements[:,-2]
        updatedIndex = newElements[:,-3]

        # Update result array
        result[wrongIndex,-1] = updatedCombinedIndex
        result[wrongIndex,-2] = updatedEncoding
        result[wrongIndex,-3] = updatedIndex

        # Update elementsToUpdate
        wrongIndex = np.where(result[:,-2] == 2)
        elementsToUpdate = combined[wrongIndex]

    print("**** Result after index update ****")
    starts = result[:,0]/8
    print("starts \n {0}".format(starts))
    ends = starts + allEventLengths[allStartIndexes]
    print("ends \n {0}".format(ends))
    print("index \n {0}".format(result[:,-3]))
    print("encode \n {0}".format(result[:,-2]))
    print("------------------")

    return result
