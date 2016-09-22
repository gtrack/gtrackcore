
import numpy as np

def complement(starts, ends, regionSize, allowOverlap=False):
    """
    Creates a complemented track. Create a segment for all area not covered
    by the input track

    Input :    -----       --- -------         ---
    Result:----     -------   -       ---------

    :param starts:
    :param ends:
    :param regionSize:
    :param allowOverlap:
    :return:
    """

    assert starts is not None
    assert ends is not None
    # Merge and flip?

    if len(starts) == 0:
        # Nothing in input, returning 0 -> regionSize
        cStarts = np.array([0])
        cEnds = np.array([regionSize])
        return cStarts, cEnds, None

    if allowOverlap:
        raise NotImplementedError
    else:
        # Check first if the track starts at 0 or ends at the genome size
        startAtZero = False
        endAtGenomeSize = False

        if starts[0] == 0:
            startAtZero = True

        if ends[-1] == regionSize:
            endAtGenomeSize = True

        # Flip starts and ends
        startsTmp = ends
        ends = starts
        starts = startsTmp

        if startAtZero:
            # Input track start at 0.
            # We do not add a 0 to the new starts and we remove the first
            # element from the new ends
            ends = np.delete(ends, 0)

        else:
            # Track does not start at 0. Add a 0 to get the start of the track.
            starts = np.insert(starts, 0, 0)

        if endAtGenomeSize:
            # Input track ends at genomeSize.
            # We do not add a genomeSize to the new ends and we remove the
            # last element from the new starts
            starts = np.delete(starts, -1)
        else:
            # Track does not end at genomeSize. Add a genomeSize to get the
            # end part for the track
            ends = np.append(ends, regionSize)

        # When we have two segments where start[n+1] = end[n], we get
        # dangling segments with length zero.
        # For now we fix it by removing all segments with length 0.
        # if (newStarts == newEnds).any():
        danglingPoints = np.where(starts == ends)
        starts = np.delete(starts, danglingPoints)
        ends = np.delete(ends, danglingPoints)

        return starts, ends, None
