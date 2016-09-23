
import numpy as np

def _mergeIds(ids, overlapIndex, removeIndex, mergeNr, idsDict):

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

    idsDict.update(newIdsDict)

    # If we merge a already merged ids, we need update old mergeid
    k = np.array(idsDict.keys())
    v = np.array(idsDict.values())

    keysToUpdate = k[np.in1d(v, k)]

    if len(keysToUpdate) > 0:
        oldValues = [idsDict[x] for x in keysToUpdate]
        newValues = [idsDict[x] for x in oldValues]

        idsDict.update({k:v for k,v in zip(keysToUpdate,newValues)})

    ids[overlapIndex] = newIds
    ids = np.delete(ids, removeIndex)

    return ids, newIdsDict, mergeNr

def _mergeEdges(edges, overlapIndex, removeIndex, weight=None):
    """

    TODO: When we change order of the edges, we need to do the same on the
    weights

    :param edges:
    :param overlapIndex:
    :return:
    """

    # Find all the edges n and n+1
    edges1 = edges[overlapIndex]
    edges2 = edges[removeIndex]

    # Expand edges to edges*2
    if isinstance(edges[0], (list, np.ndarray)):
        # List of lists
        newEdges = np.column_stack((edges1,edges2))

        # Edges are already lists. We expand with padding
        padding = np.zeros((len(edges), len(edges[0])),
                           dtype=newEdges.dtype)

        # Extend all edges withe the padding
        edges = np.c_[edges, padding]
    else:
        # List of scalars
        # Edges is scalar. We need to convert it to a list
        # type. As we use ndarrays we need to pad the new
        # array with empty edges.

        newEdges = np.c_[edges1, edges2]
        edges = np.array([np.array([edge,''], dtype=newEdges.dtype)
                          for edge in edges])

    # Update edges
    edges[overlapIndex] = newEdges
    edges = np.delete(edges, removeIndex, 0)

    return edges

def merge(starts, ends, strands=None, values=None, ids=None,
          edges=None, weights=None, useStrands=False,
          treatMissingAsNegative=True,
          mergeValuesFunction=None):

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

    assert len(starts) == len(ends)

    if useStrands and strands is None:
        useStrands = False

    if mergeValuesFunction is None:
        # Set the default mergeValue function
        mergeValuesFunction= np.maximum

    if useStrands:
        # TODO: fix for points
        # TODO
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

        # Segments
        # First we remove totally overlapping segments.
        # end[n] > end[n+1]

        mergeNr = 1

        totalOverlapIndex = np.where((ends[1:] <= ends[:-1]))

        # If we have multiple

        while len(totalOverlapIndex[0]) > 0:
            # As we are removing n+1 we need to shift the index.
            totalOverlapIndex = totalOverlapIndex[0]
            removeIndex = totalOverlapIndex + 1

            # If we have multiple overlap, we only remove the last element.
            inRemove = np.in1d(removeIndex, totalOverlapIndex, invert=True)
            if len(inRemove > 0):
                # We have multiple overlap
                inOverlap = np.in1d(totalOverlapIndex, removeIndex, invert=True)

                # Remove multiple overlap for now:
                removeIndex = removeIndex[inRemove]
                totalOverlapIndex = totalOverlapIndex[inOverlap]

            if strands is not None:
                # Found strands, merging them.

                s1 = strands[totalOverlapIndex]
                s2 = strands[removeIndex]

                sNew = [a if a == b else '.' for a,b in zip(s1,s2)]
                strands[totalOverlapIndex] = sNew
                strands = np.delete(strands, removeIndex)

            if values is not None:
                # Found values, merging them
                v1 = values[totalOverlapIndex]
                v2 = values[removeIndex]

                values[totalOverlapIndex] = mergeValuesFunction(v1, v2)
                values = np.delete(values, removeIndex)

            if ids is not None:
                # Found ids, merging them

                ids, tmpIdsDict, mergeNr = _mergeIds(ids,
                                                     totalOverlapIndex,
                                                     removeIndex,
                                                     mergeNr,
                                                     newIdsDict)
                newIdsDict.update(tmpIdsDict)

                if edges is not None:
                    # Found edges, merging them
                    edges = _mergeEdges(edges, totalOverlapIndex, removeIndex)

                if weights is not None:
                    # Found weights, merging them
                    raise NotImplementedError

            starts = np.delete(starts, removeIndex)
            ends = np.delete(ends, removeIndex)

            totalOverlapIndex = np.where((ends[1:] <= ends[:-1]))

        # Remove partially overlapping segments
        # start[n+1] <= end[n]
        partialOverlapIndex = np.where(starts[1:] < ends[:-1])
        while len(partialOverlapIndex[0]) > 0:
            print("In remove partial!")
            partialOverlapIndex = partialOverlapIndex[0]

            removeIndex = partialOverlapIndex + 1

            # If we have multiple overlap, we only remove the last element.
            inRemove = np.in1d(removeIndex, partialOverlapIndex, invert=True)
            if len(inRemove > 0):
                # We have multiple overlap
                inOverlap = np.in1d(partialOverlapIndex, removeIndex,
                                    invert=True)

                # We save the starts and ends bye pushing then down the array.

                starts[partialOverlapIndex[~inOverlap]] = \
                    starts[partialOverlapIndex[~inOverlap] +1]

                ends[partialOverlapIndex[~inOverlap]] = \
                    ends[partialOverlapIndex[~inOverlap] +1]

                # Remove multiple overlap from the index.
                removeIndex = removeIndex[inRemove]
                partialOverlapIndex = partialOverlapIndex[inOverlap]

            if strands is not None:
                # Found, strands, merging them.

                s1 = strands[partialOverlapIndex]
                s2 = strands[removeIndex]

                sNew = [a if a == b else '.' for a,b in zip(s1,s2)]

                strands[partialOverlapIndex] = sNew
                strands = np.delete(strands, removeIndex)

            if values is not None:
                # Found values, merging them

                v1 = values[partialOverlapIndex]
                v2 = values[removeIndex]

                values[partialOverlapIndex] = mergeValuesFunction(v1, v2)
                values = np.delete(values, removeIndex)
            if ids is not None:
                # Found ids, merging them
                ids, newIdsDict, mergeNr = _mergeIds(ids,
                                                     partialOverlapIndex,
                                                     removeIndex,
                                                     mergeNr,
                                                     newIdsDict)

                if edges is not None:
                    # Found edges, merging them
                    edges = _mergeEdges(edges, partialOverlapIndex,
                                        removeIndex)

                if weights is not None:
                    # Found Weights, merging them
                    raise NotImplementedError

            ends[partialOverlapIndex] = ends[removeIndex]
            starts = np.delete(starts, removeIndex)
            ends = np.delete(ends, removeIndex)

            partialOverlapIndex = np.where(starts[1:] < ends[:-1])

        """
        if starts is None:
            # Partitions
            raise NotImplementedError

        elif ends is None:
            # Points

            # Nr used in naming of merged points
            mergeNr = 1
            overlapIndex = np.where((starts[1:] == starts[:-1]))

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
                                # Edges are already lists. We expand it needed
                                if newEdge.dtype > edges[0].dtype:
                                    edges = edges.astype(newEdge.dtype)
                            else:
                                padding = np.zeros((len(edges), len(newEdge) -
                                                len(edges[0])),
                                               dtype=edges.dtype)
                                # Extend all edges withe the padding
                                edges = np.c_[edges, padding]

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

    """

    if edges is not None:

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

        # Cast the edges array to the same type as the ids array
        edges = edges.astype(ids.dtype)

        # Update the edges
        for k,v in newIdsDict.iteritems():
            edges[np.where(edges == k)] = v

    return starts, ends, values, strands, ids, edges, weights
