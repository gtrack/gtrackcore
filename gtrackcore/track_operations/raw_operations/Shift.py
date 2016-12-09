
import numpy as np


def shift(starts, ends, regionSize, strands=None, shiftLength=None,
          useFraction=False, useStrands=True, treatMissingAsNegative=False):
    """
    Shift elements in a track a give nr of BP.
    :param starts: numpy array. Starts
    :param ends: numpy array. Ends
    :param regionSize: Int. The regions max size.
    :param strands: numpy array. Strand info
    :param shift: Int. Nr of BP to shift if we want to shift all segments
    :param fraction: Boolean. Shift is a fraction of the size of the segment.
    :param useMissingStrand: Boolean. If we are to use segment with missing
    strand information.
    :param treatMissingAsPositive: Boolean. If the missing segments with
    missing strand information as negative or positive. Default is true. Set
    to false if you want to treat them as negative.
    :param allowOverlap: Boolean. If we allow overlapping segments in the
    result.
    :return: New shifted track as start, ends, strand and index
    """

    assert shiftLength is not None

    if useStrands and strands is None:
        # We need strand info to follow it.
        useStrands = False


    if useStrands:
        # Shift in the strand direction.

        if treatMissingAsNegative:
            positiveIndex = np.where(strands == '+')
            negativeIndex = np.where((strands == '-') | (strands == '.'))
        else:
            positiveIndex = np.where((strands == '+') | (strands == '.'))
            negativeIndex = np.where(strands == '-')

        if useFraction:
            positiveLengths = ends[positiveIndex] - starts[positiveIndex]
            negativeLengths = ends[negativeIndex] - starts[negativeIndex]

            positiveShift = positiveLengths * shiftLength
            #positiveShift = positiveShift.astype(int)
            positiveShift = np.around(positiveShift).astype(int)

            negativeShift = negativeLengths * shiftLength
            #negativeShift = negativeShift.astype(int)
            negativeShift = np.around(negativeShift).astype(int)

        else:
            positiveShift = shiftLength
            negativeShift = shiftLength

        # Update the positive segments
        starts[positiveIndex] = starts[positiveIndex] + positiveShift
        ends[positiveIndex] = ends[positiveIndex] + positiveShift

        # Update the negative segments
        starts[negativeIndex] = starts[negativeIndex] - negativeShift
        ends[negativeIndex] = ends[negativeIndex] - negativeShift

    else:
        if useFraction:
            # Using a fraction of the length as a basis for the shift.
            # Round to int

            lengths = ends - starts
            shiftLength = lengths * shiftLength
            shiftLength = np.around(shiftLength).astype(int)
            #shiftLength = shiftLength.astype(int)
            # Strand is not given or we are to ignore it.

        starts = starts + shiftLength
        ends = ends + shiftLength

    # We now check and fix any underflow/overflow
    # This is where one of the segments is shifted under 0 or over the size
    # of the region.

    # Create a index to use in the trackView creation
    index = np.arange(0, len(starts), 1, dtype='int32')

    # Find end underflow and start overflow first. These segments can be
    # removed directly.
    endUnderflowIndex = np.where(ends < 0)
    starts = np.delete(starts, endUnderflowIndex)
    ends = np.delete(ends, endUnderflowIndex)
    index = np.delete(index, endUnderflowIndex)

    startOverflowIndex = np.where(starts > regionSize)
    starts = np.delete(starts, startOverflowIndex)
    ends = np.delete(ends, startOverflowIndex)
    index = np.delete(index, startOverflowIndex)

    # Find start underflow and set it to 0.
    startUnderflowIndex = np.where(starts < 0)
    starts[startUnderflowIndex] = 0

    # Find end overflow and set i to regionSize.
    endOverflowIndex = np.where(ends > regionSize)
    ends[endOverflowIndex] = regionSize

    # When two segments overlap totally, we get dangling points...
    # For now we fix it by removing all points. This is probably not the
    # way to go..
    # if (newStarts == newEnds).any():
    danglingPoints = np.where(starts == ends)
    starts = np.delete(starts, danglingPoints)
    ends = np.delete(ends, danglingPoints)

    if strands is not None:
        strands = np.delete(strands, danglingPoints)
    index = np.delete(index, danglingPoints)

    return starts, ends, index, strands
