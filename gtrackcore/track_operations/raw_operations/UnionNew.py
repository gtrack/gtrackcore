
import numpy as np
from gtrackcore.track_operations.RawOperationContent import RawOperationContent
from gtrackcore.track.format.TrackFormat import TrackFormatReq

from gtrackcore.track_operations.RawOperationsTools import generateTrackFromResult

def union(track1, track2, resultReq):
    """
    Any input -> any output..
    calculate the union and return index.
    What do we do with overlap...
    Only points and segments overlap..
    """

    # Variables used by the class operation
    _ALLOW_OVERLAP = False
    _RES_ALLOW_OVERLAP = False

    assert isinstance(track1, RawOperationContent)
    assert isinstance(track2, RawOperationContent)
    assert isinstance(resultReq, TrackFormatReq)

    t1Index = np.arange(0, len(track1), 1)
    t2Index = np.arange(0, len(track2), 1)

    t1Encode = np.zeros(len(track1)) + 1
    t2Encode = np.zeros(len(track2)) + 2

    t1 = np.column_stack((track1.starts, track1.ends, t1Index, t1Encode))
    t2 = np.column_stack((track2.starts, track2.ends, t2Index, t2Encode))

    combined = np.concatenate((t1, t2))

    # Sort the new array on position and then on encoding.
    res = combined[np.lexsort((combined[:, -1], combined[:, 0]))]

    # Ignoring adjacent segments for now..
    # If we have more information then the starts/ends it makes more sense to
    #  keep both segments with all of the extra data.

    if not _RES_ALLOW_OVERLAP:
        # Check first is a segment is completely inside another segment
        # If it is we remove it.
        # if end[n] > end[n+1] => remover n
        totalOverlapIndex = np.where(res[:-1,1] > res[1:,1])

        if len(totalOverlapIndex[0]) > 0:
            # As there can be more then one segment inside another segment
            # we need to iterate over til we have no more total overlap.
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

#    generateTrackFromResult(res, [track1, track2], resultReq)

    return res
