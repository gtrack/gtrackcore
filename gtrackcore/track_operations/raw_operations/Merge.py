
import numpy as np

def _mergeIds(ids, overlapIndex, removeIndex, mergeNr, idsDict, debug=False):
    if debug:
        print("start _mergeIds")

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

    if debug:
        print("new ids dict: {}".format(newIdsDict))
        print("old ids dict: {}".format(idsDict))

    idsDict.update(newIdsDict)

    if debug:
        print("ids dict after update: {}".format(idsDict))

    # If we merge a already merged ids, we need update old mergeid
    k = np.array(idsDict.keys())
    v = np.array(idsDict.values())

    # Only update values, not keys..

    keysToUpdate = k[np.in1d(v, k)]

    if len(keysToUpdate) > 0:
        if debug:
            print("Updating ids")
            print("keysToUpdate: {}".format(keysToUpdate))

        oldValues = [idsDict[x] for x in keysToUpdate]
        newValues = [idsDict[x] for x in oldValues]

        if debug:
            print("oldValues: {}".format(oldValues))
            print("newValues: {}".format(newValues))

        idsDict.update({k:v for k,v in zip(keysToUpdate,newValues)})

        if debug:
            print("ids after update: {}".format(idsDict))

    ids[overlapIndex] = newIds
    ids = np.delete(ids, removeIndex)

    return ids, idsDict, mergeNr

def _mergeEdges(edges, overlapIndex, removeIndex, weight=None, debug=False):
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

    if debug:
        print("******DEBUG******")
        print("Mering edges!")
        print("edges[overlap]: {}".format(edges1))
        print("edges[remove]: {}".format(edges2))
        print("******END******")

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

def _mergeWeights(weights, overlapIndex, removeIndex, debug=False):
    """

    :param weights:
    :param overlapIndex:
    :param removeIndex:
    :param debug:
    :return:
    """

    assert weights is not None

    # Find all the edges n and n+1
    weights1 = weights[overlapIndex]
    weights2 = weights[removeIndex]

    if debug:
        print("******DEBUG******")
        print("Mering weights!")
        print("overlapIndex: {}".format(overlapIndex))
        print("removeIndex: {}".format(removeIndex))
        print("weights: {}".format(weights))
        print("weights[overlap]: {}".format(weights1))
        print("weights[remove]: {}".format(weights2))
        print("******END******")

    # Expand weights to weights*2
    if isinstance(weights[0], (list, np.ndarray)):
        if debug:
            print("Weights is array")
        # List of lists
        newWeights = np.column_stack((weights1,weights2))

        if debug:
            print("newWeights: {}".format(newWeights))

        # Edges are already lists. We expand with padding
        #padding = np.zeros((len(weights), len(weights[0])),
        #                   dtype=newWeights.dtype)

        # padding is a mXn matrix. m is the length of the weights, n is the
        # length of wights[0]

        padding = np.array([np.array([np.nan for x in range(len(weights[0]))],
                                     dtype=newWeights.dtype) for x in
                           range(len(weights))])

        # Extend all edges withe the padding
        weights = np.c_[weights, padding]
    else:
        # List of scalars
        # Weights is scalar. We need to convert it to a list
        # type. As we use ndarrays we need to pad the new
        # array with empty edges.

        newWeights = np.c_[weights1, weights2]
        weights = np.array([np.array([weight,''], dtype=newWeights.dtype)
                           for weight in weights])

    # Update weights
    weights[overlapIndex] = newWeights
    weights = np.delete(weights, removeIndex, 0)

    return weights


def _merge(starts, ends, strands=None, values=None, ids=None, edges=None,
           weights=None, mergeValuesFunction=np.maximum, newIdsDict=None,
           debug=False):
    if debug:
        print("start _merge")
        print("starts: {}".format(starts))
        print("ends: {}".format(ends))
    # Ignoring or missing strand info

    # Segments
    # First we remove totally overlapping segments.
    # end[n] > end[n+1]

    mergeNr = 1

    totalOverlapIndex = np.where((ends[1:] <= ends[:-1]))

    # If we have multiple

    while len(totalOverlapIndex[0]) > 0:
        if debug:
            print("Removing total overlap")
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
                                                 newIdsDict, debug)
            newIdsDict.update(tmpIdsDict)

            if edges is not None:
                # Found edges, merging them
                edges = _mergeEdges(edges, totalOverlapIndex, removeIndex,
                                    debug)

            if weights is not None:
                # Found weights, merging them
                weights = _mergeWeights(weights, totalOverlapIndex,
                                        removeIndex, debug)

        starts = np.delete(starts, removeIndex)
        ends = np.delete(ends, removeIndex)

        totalOverlapIndex = np.where((ends[1:] <= ends[:-1]))

    # Remove partially overlapping segments
    # start[n+1] <= end[n]
    partialOverlapIndex = np.where(starts[1:] < ends[:-1])
    while len(partialOverlapIndex[0]) > 0:
        partialOverlapIndex = partialOverlapIndex[0]
        removeIndex = partialOverlapIndex + 1

        if debug:
            print("Removing partial overlap")
            print("PartialOverlapIndex: {}".format(partialOverlapIndex))
            print("RemoveIndex: {}".format(removeIndex))

        # If we have multiple overlap, we only remove the last element.
        inRemove = np.in1d(removeIndex, partialOverlapIndex, invert=True)
        if len(inRemove > 0):
            if debug:
                print("We have multiple overlap. Removing some of the "
                      "overlap for now.")
            # We have multiple overlap
            inOverlap = np.in1d(partialOverlapIndex, removeIndex,
                                invert=True)

            # We save the starts and ends by pushing them down the array.

            starts[partialOverlapIndex[~inOverlap]] = \
                starts[partialOverlapIndex[~inOverlap] +1]

            ends[partialOverlapIndex[~inOverlap]] = \
                ends[partialOverlapIndex[~inOverlap] +1]

            # Remove multiple overlap from the index.
            removeIndex = removeIndex[inRemove]
            partialOverlapIndex = partialOverlapIndex[inOverlap]

        if strands is not None:
            # Found, strands, merging them.
            if debug:
                print("Found strands, merging them")

            s1 = strands[partialOverlapIndex]
            s2 = strands[removeIndex]

            sNew = [a if a == b else '.' for a,b in zip(s1,s2)]

            strands[partialOverlapIndex] = sNew
            strands = np.delete(strands, removeIndex)

        if values is not None:
            # Found values, merging them
            if debug:
                print("Found values, merging them")

            v1 = values[partialOverlapIndex]
            v2 = values[removeIndex]

            values[partialOverlapIndex] = mergeValuesFunction(v1, v2)
            values = np.delete(values, removeIndex)
        if ids is not None:
            if debug:
                print("Found links, merging them")
                print("ids: {}".format(ids))
                print("edges: {}".format(edges))
                print("weights: {}".format(weights))
                print("newIdsDict: {}".format(newIdsDict))
            # Found ids, merging them
            ids, newIdsDict, mergeNr = _mergeIds(ids, partialOverlapIndex,
                                                 removeIndex, mergeNr,
                                                 newIdsDict, debug)
            if debug:
                print("After mergeIds")
                print("ids: {}".format(ids))
                print("newIdsDict: {}".format(newIdsDict))

            if edges is not None:
                if debug:
                    print("Merging edges")
                    print("edges before: {}".format(edges))
                # Found edges, merging them
                edges = _mergeEdges(edges, partialOverlapIndex,
                                    removeIndex, debug)
                if debug:
                    print("edges after: {}".format(edges))

            if weights is not None:
                # Found Weights, merging them
                if debug:
                    print("Merging weights")
                    print("Weights before: {}".format(weights))
                weights = _mergeWeights(weights, partialOverlapIndex,
                                        removeIndex, debug)
                if debug:
                    print("Weights after: {}".format(weights))

        ends[partialOverlapIndex] = ends[removeIndex]
        starts = np.delete(starts, removeIndex)
        ends = np.delete(ends, removeIndex)

        partialOverlapIndex = np.where(starts[1:] < ends[:-1])

    if edges is not None:
        # Updating edges with the new ids using the newIdsDict.
        if isinstance(edges[0], (list, np.ndarray)):
            # The merging of edges creates excessive padding.
            # Removing it.
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

    if weights is not None:
        if isinstance(weights[0], (list, np.ndarray)):
            if debug:
                print("Fixing weights padding")
            # The merging of weights creates excessive padding.
            # Removing it.

            # Remove all of the padding
            newWeights = [weight[np.where(~np.isnan(weight))] for weight in weights]

            # Find the longest edge
            maxLength = max(len(x) for x in newWeights)

            # Create the minimum padding according to the longest one
            padding = np.array([np.array([np.nan for y in
                                          range(0,maxLength-len(x))],
                                dtype=weights.dtype) for x in newWeights])

            oldDtype = weights.dtype
            # Extend all edges withe the padding
            weights = np.c_[newWeights, padding]

            if oldDtype != weights.dtype:
                if debug:
                    print("Updating dtype!")
                weights = weights.astype(oldDtype)

    return starts, ends, values, strands, ids, edges, weights, newIdsDict

def merge(starts, ends, strands=None, values=None, ids=None, edges=None,
          weights=None, useStrands=False, treatMissingAsNegative=True,
          mergeValuesFunction=None, debug=False):
    """
    Merge all overlapping features of a track.
    :param starts:
    :param ends:
    :param strands:
    :param values:
    :param ids:
    :param edges:
    :param weights:
    :param useStrands:
    :param treatMissingAsNegative:
    :param mergeValuesFunction:
    :param debug:
    :return:
    """

    assert len(starts) == len(ends)

    if debug:
        print("**** Raw Merge start ****")

    newIdsDict = {}

    if useStrands and strands is None:
        useStrands = False

    if mergeValuesFunction is None:
        # Set the default mergeValue function
        mergeValuesFunction= np.maximum

    if useStrands:
        if debug:
            print("Merging using the strand information")
        assert strands is not None
        assert len(strands) == len(starts)

        if treatMissingAsNegative:
            positiveIndex = np.where(strands == '+')
            negativeIndex = np.where((strands == '-') | (strands == '.'))
        else:
            positiveIndex = np.where((strands == '+') | (strands == '.'))
            negativeIndex = np.where(strands == '-')

        posRes = None
        negRes = None

        if len(positiveIndex[0]) > 0:
            posStarts = starts[positiveIndex]
            posEnds = ends[positiveIndex]
            posStrands = strands[positiveIndex] if strands is not None else None
            posValues = values[positiveIndex] if values is not None else None
            posIds = ids[positiveIndex] if ids is not None else None
            posEdges = edges[positiveIndex] if edges is not None else None
            posWeights  = weights[positiveIndex] if weights is not None else None
            #posExtras = extras[positiveIndex]

            posRes = _merge(posStarts, posEnds, strands=posStrands,
                            values=posValues, ids=posIds, edges=posEdges,
                            weights=posWeights,
                            mergeValuesFunction=mergeValuesFunction,
                            newIdsDict=newIdsDict,
                            debug=debug)

            newIdsDict = posRes[-1]

        if len(negativeIndex[0]) > 0:
            negStarts = starts[negativeIndex]
            negEnds = ends[negativeIndex]
            negStrands = strands[negativeIndex] if strands is not None else None
            negValues = values[negativeIndex] if values is not None else None
            negIds = ids[negativeIndex] if ids is not None else None
            negEdges = edges[negativeIndex] if edges is not None else None
            negWeights = weights[negativeIndex] if weights is not None else None
            #posExtras = extras[negativeIndex]

            negRes = _merge(negStarts, negEnds, strands=negStrands,
                            values=negValues, ids=negIds, edges=negEdges,
                            weights=negWeights,
                            mergeValuesFunction=mergeValuesFunction,
                            newIdsDict=newIdsDict,
                            debug=debug)

            newIdsDict = negRes[-1]

        combined = False
        # Combine and return
        if posRes is not None and negRes is not None:
            combined = True
            starts = np.concatenate((posRes[0], negRes[0]))
            ends = np.concatenate((posRes[1], negRes[1]))

            combined = np.column_stack((starts, ends))
            sortIndex = np.lexsort((combined[:,1], combined[:,0]))

            starts = starts[sortIndex]
            ends = ends[sortIndex]

            if posRes[2] is not None:
                strands = np.concatenate((posRes[2], negRes[2]))
                strands = strands[sortIndex]
            else:
                strands = None

            if posRes[3] is not None:
                values = np.concatenate((posRes[3], negRes[3]))
                values = values[sortIndex]
            else:
                values = None

            if posRes[4] is not None:
                ids = np.concatenate((posRes[4], negRes[4]))
                ids = ids[sortIndex]
            else:
                ids = None

            if posRes[5] is not None:
                edges = np.concatenate((posRes[5], negRes[5]))
                edges = edges[sortIndex]
            else:
                edges = None

            if posRes[6] is not None:
                weights = np.concatenate((posRes[6], negRes[6]))
                weights = weights[sortIndex]
            else:
                weights = None
        elif posRes is not None:
            starts = posRes[0]
            ends = posRes[1]
            strands = posRes[2]
            values = posRes[3]
            ids = posRes[4]
            edges = posRes[5]
            weights = posRes[6]
            # extras = posRes[7]

        elif negRes is not None:
            starts = negRes[0]
            ends = negRes[1]
            strands = negRes[2]
            values = negRes[3]
            ids = negRes[4]
            edges = negRes[5]
            weights = negRes[6]
            # extras = negRes[7]
        else:
            # Something is wrong with the input track.
            import sys
            sys.exit(1)

        if edges is not None and combined:
            # We need to do a final update on edges if they are combined
            if isinstance(edges[0], (list, np.ndarray)):
                # The merging of edges creates excessive padding.
                # Removing it.
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

        return starts, ends, strands, values, ids, edges, weights

    else:
        if debug:
            print("Merging without using strands")
            print("weights: {}".format(weights))
        res = _merge(starts, ends, strands=strands, values=values, ids=ids,
                     edges=edges, weights=weights,
                     mergeValuesFunction=mergeValuesFunction,
                     newIdsDict=newIdsDict, debug=debug)

        return res[:-1]
