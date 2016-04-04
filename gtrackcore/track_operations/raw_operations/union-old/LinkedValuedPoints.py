
import numpy as np

def union(t1Starts, t1Ends, t1Values, t1Edges, t2Starts, t2Ends, t2Values,
          t2Edges, allowOverlaps = False, resOverlap = False):
    """
    Find the union of to Linked Valued Point tracks.

    Points are segments of length zero. As such we can treat them as a special
    case of the Segments case.

    A Point track will have a end array but it will be equal to the start
    array. When doing the calculation we only use the start and copy it to
    produce the output ends.

    :param t1Starts:Numpy array. Starts of track 1
    :param t1Ends:  Numpy array. Ends of track 1 (Not used)
    :param t1Values:Numpy array. Values of track 1
    :param t1Edges: Numpy array. Edges of track 1
    :param t2Starts:Numpy array. Starts of track 2
    :param t2Ends:  Numpy array. Ends of track 2 (Not used)
    :param t2Values:Numpy array. Values of track 2
    :param t2Edges: Numpy array. Edge of track 2
    :param allowOverlaps: Boolean. Inputs can overlap.
    :param resOverlap: Boolean. Output can overlap.
    :return: The union as to arrays, (starts, ends)
    """

    # Variables used by the class operation
    _ALLOW_OVERLAP = allowOverlaps
    _RES_ALLOW_OVERLAP = resOverlap

    t1Encode = np.zeros(len(t1Starts)) + 1
    t2Encode = np.zeros(len(t2Starts)) + 2

    # Bytte ut values og edges med range(0, len(t1Start)

    t1 = np.column_stack((t1Starts, t1Values, t1Edges, t1Encode))
    t2 = np.column_stack((t2Starts, t2Values, t2Edges, t2Encode))

    combined = np.concatenate((t1, t2))

    # Sort the new array on position and then on encoding.
    # TODO: Check runtime
    res = combined[np.lexsort((combined[:, -1], combined[:, 0]))]

    if not resOverlap:
        # Remove any overlapping points
        # Only values and edges from A are saved.
        # TODO: combine edges?
        res = res[np.unique(res[:, 0], return_index=True)[1]]

    # Extract the starts, values and links
    starts = res[:, 0]
    values = res[:, 1]
    edges = res[:, 2]
    ends = starts

    return starts, ends, values, edges