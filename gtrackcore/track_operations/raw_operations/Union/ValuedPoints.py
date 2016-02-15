
import numpy as np

def union(t1Starts, t1Ends, t1Vals, t2Starts, t2Ends, t2Vals,
          allowOverlaps = False, resOverlap = False):
    """
    Find the union of to Valued Point tracks.

    Points are segments of length zero. As such we can treat them as a special
    case of the Segments case.

    A Point track will have a end array but it will be equal to the start
    array. When doing the calculation we only use the start and copy it to
    produce the output ends.

    :param t1Starts: Numpy starts array of track 1
    :param t1Ends1:  Numpy ends array of track 1
    :param t2Starts: Numpy starts array of track 2 (Not used)
    :param t2Ends2:  Numpy ends array of track 2 (Not used)
    :param allowOverlaps: Boolean. Inputs can overlap.
    :param resOverlap: Boolean. Output can overlap.
    :return: The union as to arrays, (starts, ends)
    """

    # Variables used by the class operation
    _ALLOW_OVERLAP = allowOverlaps
    _RES_ALLOW_OVERLAP = resOverlap

    # Combine the starts and values.
    t1Encode = np.zeros(len(t1Starts)) + 1
    t2Encode = np.zeros(len(t2Starts)) + 2

    t1 = np.column_stack((t1Starts, t1Vals, t1Encode))
    t2 = np.column_stack((t2Starts, t2Vals, t2Encode))

    combined = np.concatenate((t1, t2))

    # Sort the result on the first column.
    union = combined[combined[:, 0].argsort()]

    # TODO remove overlap
    #if not resOverlap:
    #    # Remove any overlapping points
    #    starts = np.unique(starts)
    #ends = starts

    starts = union[:, 0]
    values = union[:, 1]
    ends = starts

    print starts

    return starts, ends, values
