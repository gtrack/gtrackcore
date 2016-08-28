
import numpy as np
import logging
from gtrackcore.track_operations.RawOperationContent import RawOperationContent

def union(t1Starts, t1Ends, t2Starts, t2Ends, allowOverlap=False):
    """
    Any input -> any output..
    calculate the union and return index.
    What do we do with overlap...
    Only points and segments overlap..
    """

    print("************TEST UNINON***************")
    print("t1Starts: {}".format(t1Starts))
    print("t1Ends: {}".format(t1Ends))
    print("t2Starts: {}".format(t2Starts))
    print("t2Ends {}".format(t2Ends))

    resIsPoints=False
    resIsPartition=False
    resIsSegment=False
    # Create common index and encoding
    if t1Starts is not None:
        t1Index = np.arange(0, len(t1Starts), 1, dtype='int32')
        t1Encode = np.zeros(len(t1Starts), dtype='int32') + 1
    else:
        t1Index = np.arange(0, len(t1Ends), 1, dtype='int32')
        t1Encode = np.zeros(len(t1Ends), dtype='int32') + 1

    if t2Starts is not None:
        t2Index = np.arange(0, len(t2Starts), 1, dtype='int32')
        t2Encode = np.zeros(len(t2Starts), dtype='int32') + 2
    else:
        t2Index = np.arange(0, len(t2Ends), 1, dtype='int32')
        t2Encode = np.zeros(len(t2Ends), dtype='int32') + 2

    if t1Starts is None:
        # t1 is partition
        if t2Starts is None:
            # t2 is partition
            t1 = np.column_stack((t1Ends, t1Index, t1Encode))
            t2 = np.column_stack((t2Ends, t2Index, t2Encode))
            resIsPartition = True
        elif t2Ends is None:
            # t2 is points
            # Converting t1 and t2 to segments

            t1Starts = np.insert(t1Ends, 0, 0)
            t1Starts = t1Starts[:-1]
            t2Ends = np.copy(t2Starts)

            t1 = np.column_stack((t1Starts, t1Ends, t1Index, t1Encode))
            t2 = np.column_stack((t2Starts, t2Ends, t2Index, t2Encode))
            resIsSegment = True
        else:
            # t2 is segment
            # We convert t1 into segments
            # Creating the starts array by inserting a 0 and deleting the
            # last element
            t1Starts = np.insert(t1Ends, 0, 0)
            t1Starts = t1Starts[:-1]
            t1 = np.column_stack((t1Starts, t1Ends, t1Index, t1Encode))
            t2 = np.column_stack((t2Starts, t2Ends, t2Index, t2Encode))
            resIsSegment = True

    elif t1Ends is None:
        # t1 is points
        if t2Starts is None:
            # t2 is partition
            # Converting t1 and t2 to segments
            # A possible extension is to enable more options her.
            # A union of points and partitions can be a new partition where
            # the points is new partitions.

            t1Ends = np.copy(t1Starts)
            t2Starts = np.insert(t2Ends, 0, 0)
            t2Starts = t2Starts[:-1]

            t1 = np.column_stack((t1Starts, t1Ends, t1Index, t1Encode))
            t2 = np.column_stack((t2Starts, t2Ends, t2Index, t2Encode))
            resIsSegment = True

        elif t2Ends is None:
            # t2 is points
            t1 = np.column_stack((t1Starts, t1Index, t1Encode))
            t2 = np.column_stack((t2Starts, t2Index, t2Encode))
            resIsPoints = True
        else:
            # t2 is segment
            # We convert t1 to segments with length 0
            t1Ends = np.copy(t1Starts)
            t1 = np.column_stack((t1Starts, t1Ends, t1Index, t1Encode))
            t2 = np.column_stack((t2Starts, t2Ends, t2Index, t2Encode))
            resIsSegment = True
    else:
        # t1 is segment
        # If t2 is something other then a segment. We need to convert the
        # tracks to segments
        if t2Starts is None:
            # t2 is partition
            # We convert the partition into segments
            # Creating the starts array by inserting a 0 and deleting the
            # last element
            t2Starts = np.insert(t2Ends, 0, 0)
            t2Starts = t2Starts[:-1]

        elif t2Ends is None:
            print("T2 is POINT!")
            # t2 is points
            # We convert the points to segments of length 0
            t2Ends = np.copy(t2Starts)

        # t2 is segment
        t1 = np.column_stack((t1Starts, t1Ends, t1Index, t1Encode))
        t2 = np.column_stack((t2Starts, t2Ends, t2Index, t2Encode))
        print(t2)
        resIsSegment = True

    combined = np.concatenate((t1, t2))
    # Sort the new array on position and then on encoding.
    res = combined[np.lexsort((combined[:, -1], combined[:, 0]))]

    # Ignoring adjacent segments for now..
    # If we have more information then the starts/ends it makes more
    # sense to keep both segments with all of the extra data.

    if resIsPoints:
        starts = res[:,0]
        ends = None
    elif resIsPartition:
        ends = res[:,0]
        starts = None
    elif resIsSegment:
        starts = res[:, 0]
        ends = res[:, 1]
    else:
        import sys
        sys.exit(1)

    index = res[:, -2]
    enc = res[:,-1]

    return starts, ends, index, enc
