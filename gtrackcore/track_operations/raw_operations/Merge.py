
import numpy as np


def _mergeMultipleValues(values, start, end, mergeFunction=None):
    """
    Used when we need to merge the values of more then two features.


    :param values:
    :param start:
    :param end:
    :param mergeFunction:
    :return:
    """
    pass


def _mergeIds(ids, overlapIndex, mergeNr, multipleOverlap=None, i=None):

    removeIndex = overlapIndex + 1
    # Create new ids for the merged features
    newIds = np.array(["merge-{}".format(x) for x in
                       range(mergeNr, mergeNr+len(overlapIndex))])

    mergeNr += len(overlapIndex)

    if newIds.dtype > ids.dtype:
        # New dtype is bigger. Recreating the ids array with
        # the new dtype
        ids = ids.astype(newIds.dtype)

    # Saving the old ids so we can update the edges later.
    newIdsDict = {k:v for k,v in zip(ids[overlapIndex],newIds)}

    newIdsDict.update({k:v for k,v in zip(ids[removeIndex], newIds)})

    if multipleOverlap != None and len(multipleOverlap) > 0:
        # rename i..
        assert i is not None
        # If we have multiple overlap we need to update the
        # ids is the dict. We need to do this here as we create
        # the merge-ids here.
        for p in i:
            first = newIdsDict[ids[p[0]]]
            for t in p[1:]:
                newIdsDict[ids[t]] = first

    ids[overlapIndex] = newIds
    ids = np.delete(ids, removeIndex)

    return ids, newIdsDict, mergeNr

def _mergeEdges(edges, overlapIndex, weight=None):
    """

    TODO: When we change order of the edges, we need to do the same on the
    weights

    :param edges:
    :param overlapIndex:
    :return:
    """

    removeIndex = overlapIndex + 1
    # Find all the edges n and n+1
    edges1 = edges[overlapIndex]
    edges2 = edges[removeIndex]

    # New edges for the merged feature
    newEdges = np.c_[edges1,edges2]

    # Expand edges to edges*2
    if isinstance(edges[0], (list, np.ndarray)):
        # Edges are already lists. We expand it needed
        padding = np.zeros((len(edges), len(edges[0])),dtype=edges.dtype)

        # Extend all edges withe the padding
        edges = np.c_[edges, padding]
    else:
        # Edges is scalar. We need to convert it to a list
        # type. As we use ndarrays we need to pad the new
        # array with empty edges.

        edges = np.array([np.array([edge,''], dtype=newEdges.dtype)
                          for edge in edges])

    # Update edges

    edges[overlapIndex] = newEdges
    edges = np.delete(edges, removeIndex, 0)

    return edges

def merge(starts, ends, strands=None, values=None, ids=None,
          edges=None, weights=None, useStrands=False,
          useMissingStrands=False, treatMissingAsPositive=True,
          mergeValues=False, mergeValuesFunction=None,
          mergeStrands=True, mergeLinks=False):

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

    newIdsDict = {}

    print("start merge : vals {} ".format(values))
    if starts is not None and ends is not None:
        assert len(starts) == len(ends)

    if mergeValues and mergeValuesFunction is None:
        # Set the default mergeValue function
        assert values is not None
        mergeValuesFunction= np.maximum

    if mergeStrands and strands is None:
        mergeStrands = False

    if useStrands:
        # TODO: fix for points
        if useMissingStrands:
            # TODO!!
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
        # Ignoring or missing strand info
        if starts is None:
            # Partitions
            raise NotImplementedError

        elif ends is None:
            # Points

            # Nr used in naming of merged points
            mergeNr = 1
            overlapIndex = np.where((starts[1:] == starts[:-1]))

            print("overlapIndex: {}".format(overlapIndex))
            while len(overlapIndex[0]) > 0:
                print("In remove overlap!")
                # As we are removing n+1 we need to shift the index.
                removeIndex = np.array(overlapIndex[0] + 1)

                overlap, index, count = np.unique(starts, return_counts=True,
                                                  return_index=True)

                # Fine elements with more then one overlapping element
                multipleOverlap = np.where(count > 2)

                if len(multipleOverlap[0]) > 0:
                    # Merge all values from index -> index+count
                    # Save new value to index
                    # Remove all values from index+1 -> index+count

                    print("Multiple overlapping points!!")

                    # Merge all values from index -> index+count

                    overlapStart = index
                    overlapEnd = index + count

                    # Generate select index
                    i = [[i for i in np.arange(x,y)] for (x,y) in
                         zip(overlapStart,overlapEnd)]

                    for p in i:
                        # p is now the index of all elements to merge.
                        # TODO, fix the mergeFunction. This brakes the
                        # usage of np.max ect.

                        if mergeValues:
                            newValue = np.amax(values[p])
                            values[p[0]] = newValue

                        if mergeLinks:

                            # Merge all into edges[p[0]]
                            # edges[p[0]] = edges[p]
                            # set rest to ''
                            tmpEdge = edges[p]
                            tmpEdge = tmpEdge[tmpEdge != '']

                            newEdge = tmpEdge.flatten()

                            if isinstance(edges[p[0]], (list, np.ndarray)):
                                print("There")
                                # Edges are already lists. We expand it needed
                                if newEdge.dtype > edges[0].dtype:
                                    edges = edges.astype(newEdge.dtype)
                            else:
                                print("Here!")
                                padding = np.zeros((len(edges), len(newEdge) -
                                                len(edges[0])),
                                               dtype=edges.dtype)
                                # Extend all edges withe the padding

                                print("edges: {}".format(edges))
                                print("padding: {}".format(padding))

                                edges = np.c_[edges, padding]
                                print("edges: {}".format(edges))

                            print(edges)
                            print(newEdge)
                            edges[p[0]] = newEdge
                            edges[p[1:]] = np.zeros((edges[p[1:]].shape),
                                                    dtype=edges.dtype)

                if mergeValues:
                    v1 = values[overlapIndex]
                    v2 = values[removeIndex]
                    values[overlapIndex] = mergeValuesFunction(v1, v2)
                    values = np.delete(values, removeIndex)

                # Merging Strands
                if mergeStrands:
                    print(strands)
                    s1 = strands[overlapIndex]
                    s2 = strands[removeIndex]

                    strands[overlapIndex] = [x if x == y else '.'
                                             for x,y in zip(s1,s2)]
                    strands = np.delete(strands, removeIndex)

                if mergeLinks:
                    # We combine all links.
                    assert ids is not None
                    assert edges is not None

                    # We only need to update ids in overlapIndex
                    # removeIndex will be deleted

                    if len(multipleOverlap[0]) > 0:
                        ids, newIdsDict, mergeNr = \
                            _mergeIds(ids, overlapIndex[0], mergeNr,
                                      multipleOverlap=multipleOverlap[0],i=i)
                    else:
                        ids, newIdsDict, mergeNr = \
                            _mergeIds(ids, overlapIndex[0], mergeNr)

                    edges = _mergeEdges(edges, overlapIndex[0])

                starts = np.delete(starts, removeIndex)
                overlapIndex = np.where((starts[1:] == starts[:-1]))
        else:
            # Segments
            # First we remove totally overlapping segments.
            # end[n] > end[n+1]

            mergeNr = 1

            totalOverlapIndex = np.where((ends[1:] < ends[:-1]))
            while len(totalOverlapIndex[0]) > 0:
                print("In remove total overlap!")
                # As we are removing n+1 we need to shift the index.
                removeIndex = totalOverlapIndex[0] + 1

                if mergeValues:
                    v1 = values[totalOverlapIndex]
                    v2 = values[removeIndex]

                    values[totalOverlapIndex] = mergeValuesFunction(v1, v2)
                    values = np.delete(values, removeIndex[0])

                if mergeLinks:

                    ids, tmpIdsDict, mergeNr = _mergeIds(ids,
                                                         totalOverlapIndex[0],
                                                         mergeNr)

                    newIdsDict.update(tmpIdsDict)

                    edges = _mergeEdges(edges, totalOverlapIndex[0])

                starts = np.delete(starts, removeIndex[0])
                ends = np.delete(ends, removeIndex[0])

                totalOverlapIndex = np.where((ends[1:] < ends[:-1]))

            # Remove partially overlapping segments
            # start[n+1] <= end[n]
            partialOverlapIndex = np.where(starts[1:] < ends[:-1])
            while len(partialOverlapIndex[0]) > 0:
                print("Start of partial!")
                print("partialOverlapIndex: {}".format(partialOverlapIndex))
                print("In remove partial overlap!!!")
                # Found partial overlap. Merge the two.
                # end[n] = end[n+1]
                # remove n+1

                multipleOverlap = np.where(partialOverlapIndex[1:] ==
                                partialOverlapIndex[:-1])

                if len(multipleOverlap[0]) > 0:
                    print("MULTIPLE!!")
                    print(multipleOverlap)
                    print(starts)
                    print(ends)

                removeIndex = partialOverlapIndex[0] + 1
                print("removeIndex: {}".format(removeIndex))
                if mergeValues:
                    # Keeping values. Apply the given function and save result as new value.

                    v1 = values[partialOverlapIndex]
                    v2 = values[removeIndex]

                    values[partialOverlapIndex] = mergeValuesFunction(v1, v2)
                    values = np.delete(values, removeIndex[0])

                if mergeLinks:
                    ids, newIdsDict, mergeNr = _mergeIds(ids,
                                                         partialOverlapIndex[0],
                                                         mergeNr)

                    edges = _mergeEdges(edges, partialOverlapIndex[0])

                print("starts before: {}".format(starts))
                print("")
                ends[partialOverlapIndex] = ends[removeIndex]
                starts = np.delete(starts, removeIndex)
                ends = np.delete(ends, removeIndex)
                print("starts after: {}".format(starts))

                print("*******IN PARTIAL*********")
                print("starts: {}".format(starts))
                print("ends: {}".format(ends))
                print("values: {}".format(values))
                print("strands: {}".format(strands))
                print("ids: {}".format(ids))
                print("edges: {}".format(edges))
                print("weights: {}".format(weights))
                print("*******IN PARTIAL*********")

                partialOverlapIndex = np.where(starts[1:] < ends[:-1])

    if mergeLinks:

        # Remove excessive padding
        newEdges = np.array([None] * len(edges))

        for i, edge in enumerate(edges):
            ind = np.where(edge != '')
            newEdges[i] = edge[ind[0]]

        # Find the longest edge
        maxLength = max(len(x) for x in newEdges)

        # Recreate the edges with correct padding
        edges = np.array([np.pad(x, (0,maxLength-len(x)), mode='constant')
                          for x in newEdges])


        # Updating edges that points to the now merge features
        # Cast the edges array to the same type as the ids array
        edges = edges.astype(ids.dtype)

        print(newIdsDict)
        for k,v in newIdsDict.iteritems():
            edges[np.where(edges == k)] = v

    print("*******************RETURN MERGE************************")
    print("starts: {}".format(starts))
    print("ends: {}".format(ends))
    print("values: {}".format(values))
    print("strands: {}".format(strands))
    print("ids: {}".format(ids))
    print("edges: {}".format(edges))
    print("weights: {}".format(weights))
    print("*******************RETURN MERGE************************")
    return starts, ends, values, strands, ids, edges, weights
