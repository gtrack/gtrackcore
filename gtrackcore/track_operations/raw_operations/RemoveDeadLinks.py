import numpy as np

def removeDeadLinks(ids, edges, weights, globalIds=None, debug=False):
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

    index = np.arange(0, len(ids), 1, dtype='int32')

    # Check if there are dead links.
    # Remove them, and the corresponding weight (if any).

    if isinstance(edges[0], (list, np.ndarray)):
        # More then one edge per id. Each edge is a list
        for edge in edges:
            matches = np.in1d(edge, ids)
            edges[~matches] = ''
    else:
        # Max one edge per id. Edge is scalar.

        # Find all edges that points to nodes in ids
        matches = np.in1d(edges, ids)
        # Set the rest to no edge
        edges[~matches] = ''

    # TODO, "Clip" any trailing '' if possible.

    return ids, edges, weights, index
