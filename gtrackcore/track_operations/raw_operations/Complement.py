
import numpy as np

def _createComplement(starts, ends, regionSize):
    """
    Move to its own module to reduce code
    :param starts:
    :param ends:
    :param regionSize:
    :return:
    """
    assert len(starts) == len(ends)

    if len(starts) == 0:
        return None, None, None

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


def complement(starts, ends, strands, regionSize, useStrands=False,
               treatMissingAsNegative=False):
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

    if useStrands:

        assert strands is not None
        assert len(strands) == len(starts)

        if treatMissingAsNegative:
            positiveIndex = np.where(strands == '+')
            negativeIndex = np.where((strands == '-') | (strands == '.'))
        else:
            positiveIndex = np.where((strands == '+') | (strands == '.'))
            negativeIndex = np.where(strands == '-')

        if len(positiveIndex[0]) > 0:
            posStarts = starts[positiveIndex]
            posEnds = ends[positiveIndex]
            posFound = True
        else:
            posStarts = None
            posEnds = None
            posFound = False

        if len(negativeIndex[0]) > 0:
            negStarts = starts[negativeIndex]
            negEnds = ends[negativeIndex]
            negFound = True
        else:
            negStarts = None
            negEnds = None
            negFound = False

        if not posFound and not negFound:
            # Something is probably wrong..
            return None
        elif posFound and negFound:
            # Mix of positive and negative strands
            posRes = _createComplement(posStarts, posEnds, regionSize)
            negRes = _createComplement(negStarts, negEnds, regionSize)

            starts = np.concatenate((posRes[0], negRes[0]))
            ends = np.concatenate((posRes[1], negRes[1]))

            posStrands = np.array(['+' for x in range(len(posRes[0]))])
            negStrands = np.array(['-' for x in range(len(negRes[0]))])

            strands = np.concatenate((posStrands, negStrands))

            combined = np.column_stack((starts, ends, strands))
            sortIndex = np.lexsort((combined[:,1], combined[:,0]))

            starts = starts[sortIndex]
            ends = ends[sortIndex]
            strands = strands[sortIndex]

        elif posFound:
            # Only positive strands
            res = _createComplement(posStarts, posEnds, regionSize)
            starts = res[0]
            ends = res[1]
            strands = np.array(['+' for x in range(len(starts))])
        else:
            # Only negative strands
            res = _createComplement(negStarts, negEnds, regionSize)
            starts = res[0]
            ends = res[1]
            strands = np.array(['-' for x in range(len(starts))])

        return starts, ends, strands
    else:
        return _createComplement(starts, ends, regionSize)
