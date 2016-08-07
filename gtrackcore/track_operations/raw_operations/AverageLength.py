

import numpy as np

def averageLength(starts, ends):
    """
    Find the average length of the segments in a track.
    Possible extension: Support for weights.
    :param starts: Numpy array. Starts
    :param ends: Numpy array. Ends
    :return: The average length of segments in a track.
    """
    # Find the length of each segment.
    length = ends - starts

    return np.average(length)