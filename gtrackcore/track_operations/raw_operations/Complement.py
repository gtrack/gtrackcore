
import numpy as np

def complement(starts, ends, regionSize, allowOverlap=False):

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

        return starts, ends, None
