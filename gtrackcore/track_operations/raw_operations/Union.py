
import numpy as np

def union(t1Starts, t1Ends, t2Starts, t2Ends, allowOverlap=False):
    """
    Any input -> any output..
    calculate the union and return index.
    What do we do with overlap...
    Only points and segments overlap..
    """
    # Create common index and encoding
    t1Index = np.arange(0, len(t1Starts), 1, dtype='int32')
    t1Encode = np.zeros(len(t1Starts), dtype='int32') + 1
    t2Index = np.arange(0, len(t2Starts), 1, dtype='int32')
    t2Encode = np.zeros(len(t2Starts), dtype='int32') + 2

    t1 = np.column_stack((t1Starts, t1Ends, t1Index, t1Encode))
    t2 = np.column_stack((t2Starts, t2Ends, t2Index, t2Encode))

    combined = np.concatenate((t1, t2))
    # Sort the new array on position and then on encoding.
    res = combined[np.lexsort((combined[:, -1], combined[:, 0]))]

    starts = res[:, 0]
    ends = res[:, 1]
    index = res[:, -2]
    enc = res[:,-1]

    return starts, ends, index, enc
