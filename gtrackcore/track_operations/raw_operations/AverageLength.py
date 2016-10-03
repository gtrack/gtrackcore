

import numpy as np

def averageLength(starts, ends, customAverageFunction=None, deug=False):
    """
    Find the average length of the segments in a track.
    Possible extension: Support for weights.
    :param starts: Numpy array. Starts
    :param ends: Numpy array. Ends
    :return: The average length of segments in a track.
    """

    if customAverageFunction is None:
        averageFunction = np.average
    else:
        if deug:
            print("averageLength: Using a custom average!")
        averageFunction = customAverageFunction

    # Find the length of each segment.
    length = ends - starts

    return averageFunction(length)
