
import numpy as np

def removeOverlap(starts, ends, index)
    # Check first is a segment is completely inside another segment
    # If it is we remove it.
    # if start[n+1] > end[n] => remover n
    # if

    # [1,3,6]
    # [5,4,8]
    totalOverlapIndex = np.where(ends[:-1] >= ends[:1])

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