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

    if edges is not None and len(edges) > 0:
        print("Updating edges!")
        first = edges[0]
        if isinstance(first, np.ndarray) or isinstance(first, list):
            print("edges is list")
            # More then one list.
            newEdges = np.array([['' if e == '' else
                                  "{}-{}".format(e,trackIdentifier)
                                  for e in edge] for edge in edges])
        else:
            print("edges is scalar!")
            # Update the edges
            print("edges before: {}".format(edges))
            newEdges = np.array(['' if edge == '' else
                                "{}-{}".format(edge, trackIdentifier)
                                for edge in edges])
            print("edges after: {}".format(newEdges))
    else:
        print("No edges to update!")
        newEdges = []

    return newIds, newEdges, index
