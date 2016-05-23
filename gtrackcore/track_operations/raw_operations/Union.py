
import numpy as np
import logging
from gtrackcore.track_operations.RawOperationContent import RawOperationContent

def union(t1Starts, t1Ends, t2Starts, t2Ends, allowOverlap):
    """
    Any input -> any output..
    calculate the union and return index.
    What do we do with overlap...
    Only points and segments overlap..
    """

    assert len(t1Starts) == len(t1Ends)
    assert len(t2Starts) == len(t2Ends)

    t1Index = np.arange(0, len(t1Starts), 1, dtype='int32')
    t2Index = np.arange(0, len(t2Starts), 1, dtype='int32')

    t1Encode = np.zeros(len(t1Starts), dtype='int32') + 1
    t2Encode = np.zeros(len(t2Starts), dtype='int32') + 2

    t1 = np.column_stack((t1Starts, t1Ends, t1Index, t1Encode))
    t2 = np.column_stack((t2Starts, t2Ends, t2Index, t2Encode))

    combined = np.concatenate((t1, t2))

    # Sort the new array on position and then on encoding.
    res = combined[np.lexsort((combined[:, -1], combined[:, 0]))]

    # Ignoring adjacent segments for now..
    # If we have more information then the starts/ends it makes more sense to
    #  keep both segments with all of the extra data.

    if not allowOverlap:
        # Check first is a segment is completely inside another segment
        # If it is we remove it.
        # if end[n] > end[n+1] => remover n
        totalOverlapIndex = np.where(res[:-1,1] >= res[1:,1])

        if len(totalOverlapIndex[0]) > 0:
            # As there can be more then one segment inside another segment
            # we need to iterate over it until we have no more total overlap.
            while len(totalOverlapIndex[0]) != 0:
                removeIndex = totalOverlapIndex[0]
                res[:, -1][removeIndex] = -1

                removeIndex += 1
                res = np.delete(res, totalOverlapIndex, 0)

                totalOverlapIndex = np.where(res[:-1,1] > res[1:,1])

        # Find partially overlapping segments
        # end[n] > start[n+1]
        partialOverlapIndex = np.where(res[:-1, 1] > res[1:, 0])

        if len(partialOverlapIndex[0]) > 0:
            # Creating masks to merge the overlapping segments
            overlapStartMask = np.ones(len(res), dtype=bool)
            overlapStartMask[[partialOverlapIndex[0]+1]] = False

            overlapEndMask = np.ones(len(res), dtype=bool)
            overlapEndMask[partialOverlapIndex[0]] = False

            # Saving the updated ends
            ends = res[:, 1]
            ends = ends[overlapEndMask]

            encodingMask = np.invert(overlapEndMask)
            encoding = res[:, -1]
            encoding[encodingMask] = -1
            encoding = encoding[overlapStartMask]
            res = res[overlapStartMask]
            res[:, 1] = ends
            res[:, -1] = encoding

    # Replace index, encoding with -> value, link, strand, extra ect.
    # Extract the starts, values and links
    starts = res[:, 0]
    ends = res[:, 1]
    index = res[:, -2]
    enc = res[:,-1]

    return starts, ends, index, enc
