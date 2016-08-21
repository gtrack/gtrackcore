
import numpy as np


def merge(starts, ends, strands=None, values=None, ids=None,
          edges=None, weights=None, useStrands=False,
          useMissingStrands=False, treatMissingAsPositive=True,
          useValues=False, valueFunction=None, useLinks=False):

    # Two types
    #
    # Where segment n+1 is totaly inside n
    # Remove n+1
    #
    # We assume that the tracks are sorted in order.
    #
    # -----
    #  --
    #
    # ---
    # -----
    #
    # -----
    #   ---
    #
    #
    #
    # Where start[n+1] > end[n]
    # Merge them
    #  end[n] = end[n+1]
    #  remove n+1
    #
    # -----
    #    ------
    #
    # -----
    # -----------

    print("start merge : vals {} ".format(values))
    if starts is not None and ends is not None:
        assert len(starts) == len(ends)

    if useStrands:
        # TODO: fix for points
        if useMissingStrands:
            raise NotImplementedError
        else:
            assert strands is not None
            assert len(strands) == len(starts)

            positiveIndex = np.where(strands == '+')
            negativeIndex = np.where(strands == '-')

            combined = np.column_stack((starts, ends))

            if len(positiveIndex) > 0:

                totalOverlapIndex = np.where((ends[1:] < ends[:-1]))
                while len(totalOverlapIndex[0]) > 0:
                    # As we are removing n+1 we need to shift the index.
                    removeIndex = totalOverlapIndex[0] + 1
                    starts = np.delete(starts, removeIndex[0])
                    ends = np.delete(ends, removeIndex[0])

                    totalOverlapIndex = np.where((ends[1:] < ends[:-1]))

                # Remove partial overlapping segments
                # start[n+1] <= end[n]
                partialOverlapIndex = np.where(starts[1:] <= ends[:-1] )
                while len(partialOverlapIndex[0]) > 0:
                    # Found partial overlap. Merge the two.
                    # end[n] = end[n+1]
                    # remove n+1

                    removeIndex = partialOverlapIndex[0] + 1
                    ends[partialOverlapIndex] = ends[removeIndex]
                    starts = np.delete(starts, removeIndex[0])
                    ends = np.delete(ends, removeIndex[0])

                    partialOverlapIndex = np.where(starts[1:] < ends[:-1] )

    else:
        if starts is None:
            # Partitions
            raise NotImplementedError

        elif ends is None:
            # Points
            overlapIndex = np.where((starts[1:] == starts[:-1]))
            while len(overlapIndex[0]) > 0:
                print("In remove overlap!")
                # As we are removing n+1 we need to shift the index.
                removeIndex = overlapIndex[0] + 1

                if useValues:
                    if valueFunction is None:
                        valueFunction = np.maximum
                    assert values is not None
                    assert len(values) == len(starts)

                    v1 = values[overlapIndex]
                    v2 = values[removeIndex]

                    values[overlapIndex] = valueFunction(v1, v2)
                    values = np.delete(values, removeIndex[0])

                if useLinks:
                    # We combine all links.
                    assert ids is not None
                    assert edges is not None

                    # We need to update the edges pointing to removed ids..
                    ids1 = ids[overlapIndex]
                    ids2 = ids[removeIndex]

                    edges1 = edges[overlapIndex]
                    edges2 = edges[removeIndex]

                    # Combining the edges. Numpy objects in all its glory..
                    newEdges = np.array([[np.concatenate((edges1[i], edges2[
                        i]))] for i in range(len(edges1))])

                    print("newEdges: {}".format(newEdges))

                    # TODO: update links with one of the deleted ids to the
                    # new id.
                    # remove merged ids
                    ids = np.delete(ids, removeIndex[0])

                    # Remove the old edges.
                    edges[overlapIndex] = newEdges
                    edges = np.deg2rad(edges, removeIndex[0])

                starts = np.delete(starts, removeIndex[0])

                overlapIndex = np.where((starts[1:] == starts[:-1]))

        else:
            # Segments
            # First we remove totally overlapping segments.
            # end[n] > end[n+1]
            totalOverlapIndex = np.where((ends[1:] < ends[:-1]))
            while len(totalOverlapIndex[0]) > 0:
                print("In remove total overlap!")
                # As we are removing n+1 we need to shift the index.
                removeIndex = totalOverlapIndex[0] + 1

                if useValues:
                    if valueFunction is None:
                        valueFunction = np.maximum
                    assert values is not None
                    assert len(values) == len(starts)

                    v1 = values[totalOverlapIndex]
                    v2 = values[removeIndex]

                    values[totalOverlapIndex] = valueFunction(v1, v2)
                    values = np.delete(values, removeIndex[0])

                starts = np.delete(starts, removeIndex[0])
                ends = np.delete(ends, removeIndex[0])

                totalOverlapIndex = np.where((ends[1:] < ends[:-1]))

            # Remove partially overlapping segments
            # start[n+1] <= end[n]
            partialOverlapIndex = np.where(starts[1:] < ends[:-1])
            while len(partialOverlapIndex[0]) > 0:
                print("In remove partial overlap!!!")
                # Found partial overlap. Merge the two.
                # end[n] = end[n+1]
                # remove n+1

                removeIndex = partialOverlapIndex[0] + 1
                if useValues:
                    print("test")
                    # Keeping values. Apply the given function and save result as new value.
                    if valueFunction is None:
                        valueFunction = np.maximum
                    assert values is not None
                    assert len(values) == len(starts)

                    v1 = values[partialOverlapIndex]
                    v2 = values[removeIndex]

                    values[partialOverlapIndex] = valueFunction(v1, v2)

                ends[partialOverlapIndex] = ends[removeIndex]
                starts = np.delete(starts, removeIndex[0])
                ends = np.delete(ends, removeIndex[0])

                if useValues:
                    values = np.delete(values, removeIndex[0])

                partialOverlapIndex = np.where(starts[1:] < ends[:-1])

    return starts, ends, values, strands, ids, edges, weights
