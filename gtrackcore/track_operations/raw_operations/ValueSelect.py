import numpy as np

def valueSelect(starts, ends, values, limit, compareFunction=None,
                allowOverlap=True, debug=False):

    assert values is not None

    if starts is not None:
        assert isinstance(starts, np.ndarray)
        assert len(starts) == len(values)
    if ends is not None:
        assert isinstance(ends, np.ndarray)
        assert len(ends) == len(values)

    if debug:
        print("In valuedSelect!")
        print("starts: {}".format(starts))
        print("ends: {}".format(ends))
        print("values: {}".format(values))

    # Create a mask
    # create starts and end arrays

    if compareFunction is None:
        # No custom compare function given.

        if isinstance(limit, bool):
            # Special case for boolean. When limit is false we only want the
            # false parts not the true one. If we use the int method we
            # would get both
            select = np.where(values == limit)

        elif isinstance(limit, (int, float)):
            # This covers booleans as well. Bool is a subtype of int
            select = np.where(values >= limit)

        if debug:
            print("Default compare: number")
            print("limit: {}".format(limit))
            print("select: {}".format(select))

    else:
        select = compareFunction(values, limit)

    if starts is None:
        if ends is None:
            # F, LF, LBP
            # We have no starts or ends.
            # The resulting track will be a point type.
            # We create the assumed starts and ends.
            starts = np.arange(1, len(values)+1)
            ends = np.arange(1, len(values)+1)
        else:
            # SF, LSF
            # Creating the starts array by inserting a 0 and deleting the
            # last element
            starts = np.insert(ends, 0, 0)
            starts = starts[:-1]

    print(select)

    if ends is not None:
        newEnds = ends[select]
    else:
        newEnds = None
    if starts is not None:
        newStarts = starts[select]
    else:
        newStarts = None

    #newValues = values[select]
    return newStarts, newEnds, select
