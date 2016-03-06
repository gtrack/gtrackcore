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
    print("combined ->{0}<-".format(combined))
    combined = combined[np.lexsort((combined[:, -1], combined[:, 0]))]

    allSortedEvents = combined[:, 0]

    print("allSortedEvents : ->{0}<-".format(allSortedEvents))
    print(allSortedEvents / 8)


    allEventCodes = (allSortedEvents % 8) - 4
    allSortedDecodedEvents = allSortedEvents / 8

    print("allEventCodes : ->{0}<-".format(allEventCodes))
    print("allSotedDecodedEventes : ->{0}<-".format(allSortedDecodedEvents))

    allEventLengths = allSortedDecodedEvents[1:] - allSortedDecodedEvents[:-1]
    print("allEventLengths : ->{0}<-".format(allEventLengths))
    cumulativeCoverStatus = np.add.accumulate(allEventCodes)

    print("cumulativeCoverStatus : ->{}<-".format(cumulativeCoverStatus))

    allStartIndexes = np.where(cumulativeCoverStatus[:-1] >= 3)

    # TODO: update indexes, to reflect track A onty
    # If track A starts inside track B -> Index OK
    # If track B starts inside track A -> Index needs to be updated.
    # If track A start is equal to track B -> Update?

    result = combined[allStartIndexes]

    starts = result[:,0] / 8
    ends = starts + allEventLengths[allStartIndexes]

    index = result[:,-2]
    encode = result[:,-1]

    print("starts : ->{0}<-".format(starts))
    print("ends : ->{0}<-".format(ends))
    print("index : ->{0}<-".format(index))
    print("encode : ->{0}<-".format(encode))


    return combined
