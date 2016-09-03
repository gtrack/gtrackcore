import numpy as np

def removeDeadLinks(ids, edges, weights, newId=None, debug=False):
    """
    Checks and remove any dead links.
    A dead links is one that has one that points to a non existing id.

    As we are only removing edges, the overall length and positions of the
    track stays the same. The edge arrays can become shorter.

    :param ids: Numpy array: Ids of the track
    :param edges: Numpy array: Edges of the track
    :param weights: Numpy array: Weights of the track.
    :param debug: Boolean: Debug print.
    :return:
    """

    assert ids is not None and edges is not None

    if weights is not None:
        assert len(weights) == len(edges)

    index = np.arange(0, len(ids), 1, dtype='int32')
    updateId = ''
    newDtype = None

    if newId is not None:
        updateId = newId
        newDtype = np.dtype(('string', len(newId)))

    if isinstance(edges[0], (list, np.ndarray)):
        # More then one edge per id. Each "edge" is a list of edges

        if newId is not None and newDtype > edges[0].dtype:
            # newId is lager then the the edges dtype.
            # Updating the dtype of edges.
            edges = edges.astype(newDtype)

        if weights is not None:
            for edge, weight in zip(edges, weights):
                matches = np.in1d(edge, ids)
                edge[~matches] = updateId
                if newId is None:
                    weight[~matches] = np.nan
        else:
            for edge in edges:
                matches = np.in1d(edge, ids)
                edge[~matches] = updateId

        if newId is None:
            # After removing edges there may be to much padding left in edges.
            # We also need to move any padding to the end of the list.
            newEdges = np.array([None] * len(edges))

            for i, edge in enumerate(edges):
                newEdges[i] = edge[np.where(edge != '')]

            # Find the larges nr of out edges on any node.
            maxLength = max(len(x) for x in newEdges)

            if maxLength == 0:
                edges = np.zeros(len(edges), dtype=edges.dtype)
                edges[:] = ''
                if weights is not None:
                    weights = np.zeros(len(weights), dtype=weights.dtype)
                    weights[:] = np.nan
            else:
                # Recreate the edges with correct padding
                edges = np.array([np.pad(e, (0,maxLength-len(e)),
                                         mode='constant')
                                 for e in newEdges])

                if weights is not None:
                    newWeights = np.array([None] * len(weights))
                    for i, weight in enumerate(weights):
                        newWeights[i] = weight[~np.isnan(weight)]

                    weights = np.array([np.pad(w, (0,maxLength-len(w)),
                                      mode='constant',
                                      constant_values=(np.nan,))
                                        for w in newWeights])

    else:
        # Max one edge per id. Edge is scalar.
        # Find all edges that points to nodes in ids
        matches = np.in1d(edges, ids)
        # Set the rest to no edge

        if newId is not None and newDtype > edges.dtype:
            # The new id is bigger then dtype of edges.
            # Updating the dtype to make space for the longer string.
            edges = edges.astype(newDtype)
        edges[~matches] = updateId

        if newId is None and weights is not None:
            weights[~matches] = np.nan

    return ids, edges, weights, index
