
import numpy

def union(t1Starts, t1Ends1, t2Starts, t2Ends2):
    """
    Find the union of to tracs
    :param t1Starts: Numpy starts array of track 1
    :param t1Ends1:  Numpy ends array of track 1
    :param t2Starts: Numpy starts array of track 2
    :param t2Ends2:  Numpy ends array of track 2
    :return: The union as to arrays, (starts, ends)
    """

    _ALLOW_OVERLAP = False
    _RES_ALLOW_OVERLAP = False

    # TODO index, add in the coded part.
    t1CodedStarts = t1Starts * 8 + 5
    t1CodedEnds = t1Ends1 * 8 + 3
    t2CodedStarts = t2Starts * 8 + 6
    t2CodedEnds = t2Ends2 * 8 + 2

    #TODO finne ut hvilke track verdien kommer fra
    allSortedCodedEvents = numpy.concatenate((t1CodedStarts, t1CodedEnds, t2CodedStarts, t2CodedEnds))
    allSortedCodedEvents.sort()
    allEventCodes = (allSortedCodedEvents % 8) - 4

    allSortedDecodedEvents = allSortedCodedEvents / 8

    allEventLengths = allSortedDecodedEvents[1:] - allSortedDecodedEvents[:-1]
    cumulativeCoverStatus = numpy.add.accumulate(allEventCodes)

    # Find the overlap starts, lengths and ends
    allStarts = allSortedDecodedEvents[cumulativeCoverStatus[:-1] >= 1]
    allLengths = allEventLengths[cumulativeCoverStatus[:-1] >= 1]
    allEnds = allStarts + allLengths

    # find adjacent sections
    # The value for starts is the index + 1
    allAdjacentIndexes = numpy.where(allStarts[1:] == allEnds[:-1])

    if len(allAdjacentIndexes) > 0:
        # Create masks
        allStartsMask = numpy.ones(len(allStarts), dtype=bool)
        allStartsMask[[allAdjacentIndexes[0]+1]] = False
        allEndsMask = numpy.ones(len(allEnds), dtype=bool)
        allEndsMask[[allAdjacentIndexes[0]]] = False

        # Use the masks to join adjacent sections
        unionStarts = allStarts[allStartsMask]
        unionEnds = allEnds[allEndsMask]

        return unionStarts, unionEnds
    else:
        return allStarts, allEnds

