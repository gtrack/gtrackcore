
import numpy as np


def shift(starts, ends, regionSize, strands=None, shift=None, positive=None,
          negative=None, fraction=False, useMissingStrand=False,
          treatMissingAsPositive=True, allowOverlap=True):
    """
    Shift elements in a track a give nr of BP.
    :param starts: numpy array. Starts
    :param ends: numpy array. Ends
    :param regionSize: Int. The regions max size.
    :param strands: numpy array. Strand info
    :param shift: Int. Nr of BP to shift if we want to shift all segments the
    equal
    :param positive: Int/Float. Nr of BP to shift segments with positive
    strand.
    :param negative: Int/Float. nr of BP to shift segments with negative
    strand.
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

    if strands is not None:
        if fraction:
            assert shift is None
            assert positive is None
            assert negative is None
            # TODO
            raise NotImplementedError

        elif shift != None:
            # Shifting all segments
            assert positive is None
            assert negative is None

            positiveIndex = np.where(strands == '+')
            negativeIndex = np.where(strands == '-')

            # Update the positive segments
            starts[positiveIndex] = starts[positiveIndex] + shift
            ends[positiveIndex] = ends[positiveIndex] + shift

            # Update the negative segments
            starts[negativeIndex] = starts[negativeIndex] - shift
            ends[negativeIndex] = ends[negativeIndex] - shift

            if useMissingStrand:
                # Update the rest
                missingIndex = np.where(strands == '.')

                if treatMissingAsPositive:
                    starts[missingIndex] = starts[missingIndex] + shift
                    ends[missingIndex] = ends[missingIndex] + shift
                else:
                    starts[missingIndex] = starts[missingIndex] - shift
                    ends[missingIndex] = ends[missingIndex] - shift

        else:
            # Shifting positive and/or negative segments
            assert positive is not None or negative is not None

            if positive is not None:
                # Updating positive segments
                positiveIndex = np.where(strands == '+')
                starts[positiveIndex] = starts[positiveIndex] + positive
                ends[positiveIndex] = ends[positiveIndex] + positive

                if useMissingStrand:
                    # Update segments with missing strand info
                    missingIndex = np.where(strands == '.')

                    if treatMissingAsPositive:
                        starts[missingIndex] = starts[missingIndex] + positive
                        ends[missingIndex] = ends[missingIndex] + positive

            if negative is not None:
                # Updating negative segments
                negativeIndex = np.where(strands == '-')
                starts[negativeIndex] = starts[negativeIndex] - negative
                ends[negativeIndex] = ends[negativeIndex] - negative

                if useMissingStrand:
                    # Update segments with missing strand info
                    missingIndex = np.where(strands == '.')

                    if not treatMissingAsPositive:
                        starts[missingIndex] = starts[missingIndex] - negative
                        ends[missingIndex] = ends[missingIndex] - negative

    else:
        # Strand is not given or we are to ignore it.
        # We will only use the shift value or fraction.
        if fraction:
            raise NotImplementedError
        else:
            # Using the shift value
            assert positive is None
            assert negative is None
            assert shift is not None

            starts = starts + shift
            ends = ends + shift

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

    if not allowOverlap:
        raise NotImplementedError

    return starts, ends, index, strands
