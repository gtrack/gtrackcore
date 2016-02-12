
import numpy as np

def union(t1Starts, t1Ends, t2Starts, t2Ends, allowOverlaps = False,
          resOverlap = False):
    """
    Find the union of to Points tracks.
    This is

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

    starts = np.concatenate((t1Starts,t2Starts))
    starts.sort()

    if not resOverlap:
        # Remove any overlapping points
        starts = np.unique(starts)

    ends = starts

    return starts, ends
