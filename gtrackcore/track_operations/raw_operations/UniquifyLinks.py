import numpy as np

def uniquifyLinks(ids, edges, trackIdentifier=None,
                allowOverlap=True, debug=False):

    assert ids is not None

    if debug:
        print("In uniquifyLinks!")
        print("ids: {}".format(ids))
        print("edges: {}".format(edges))

    index = np.arange(0,len(ids))

    # Ids first
    # We assuming that the ids is some kind of character/string..

    # Combine with ids to create the new
    newIds = np.array(["{}-{}".format(i,trackIdentifier) for i in ids])

    if edges is not None:
        first = edges[0]
        if isinstance(first, np.ndarray) or isinstance(first, list):
            # More then one list.
            newEdges = [['' if e == '' else "{}-{}".format(e, trackIdentifier)
                        for e in edge] for edge in edges]
        else:
            # Update the edges
            newEdges = ['' if edge == '' else
                        "{}-{}".format(edge, trackIdentifier) for edge in
                        edges]
    else:
        newEdges = None

    return newIds, newEdges, index
