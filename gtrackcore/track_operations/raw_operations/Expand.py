import numpy as np

def expand(regionSize, starts=None, ends=None, strands=None, downstream=None,
           upstream=None, both=None, useFraction=False, useStrands=False,
           treatMissingAsNegative=False, debug=False):
    """

    :param regionSize:
    :param starts:
    :param ends:
    :param strands:
    :param downstream:
    :param upstream:
    :param both:
    :param useFraction:
    :param useStrands:
    :param treatMissingAsNegative:
    :param debug:
    :return:
    """

    if debug:
        print("starts: {}".format(starts))
        print("ends: {}".format(ends))

    assert (downstream is not None or upstream is not None) or both is not None

    assert starts is not None
    assert ends is not None

    if useStrands:
        assert strands is not None

    index = np.arange(0, len(starts), 1, dtype='int32')

    if useFraction:
        # Using a fraction of the segments length as a basis for the flank.
        # To do this we need to calculate the flank length for each segment.
        # The new arrays are converted to ints.

        lengths = ends - starts

        if both is not None:
            both = lengths * both
            both = both.astype(int)
        else:
            if downstream is not None:
                downstream = lengths * downstream
                downstream = downstream.astype(int)

            if upstream is not None:
                upstream = lengths * upstream
                upstream = upstream.astype(int)

    if useStrands:
        if treatMissingAsNegative:
            positiveStrand = np.where(strands == '+')
            negativeStrand = np.where((strands == '-') | (strands == '.'))
        else:
            positiveStrand = np.where((strands == '+') | (strands == '.'))
            negativeStrand = np.where(strands == '-')

        if debug:
            print("In use strands")
            print("posStrand: {}".format(positiveStrand))
            print("negStrand: {}".format(negativeStrand))

        if both is not None:
            # When using both, there is no difference in extending negative
            # and positive features.
            starts[positiveStrand] = starts[positiveStrand] - both
            ends[positiveStrand] = ends[positiveStrand] + both

            starts[negativeStrand] = starts[negativeStrand] - both
            ends[negativeStrand] = ends[negativeStrand] + both

        else:
            if downstream is not None:
                if debug:
                    print("Extending on start!")
                starts[positiveStrand] = starts[positiveStrand] - downstream
                ends[negativeStrand] = ends[negativeStrand] + downstream

            if upstream is not None:
                ends[positiveStrand] = ends[positiveStrand] + upstream
                starts[negativeStrand] = starts[negativeStrand] - upstream
    else:
        # No strand info or ignoring it.

        if both is not None:
            starts = starts - both
            ends = ends + both
        else:
            if downstream is not None:
                starts = starts - downstream
            if upstream is not None:
                ends = ends + upstream

    # The new segments may over/underflow the region.
    # Check that we have no starts bellow 0 and no ends > region size
    underFlowIndex = np.where(starts < 0)
    overFlowIndex = np.where(ends > regionSize)

    if len(underFlowIndex[0]) > 0:
        starts[underFlowIndex] = 0
    if len(overFlowIndex[0]) > 0:
        ends[overFlowIndex] = regionSize

    # Extend at start of positive segments.
    #
    #        Start = 6
    #    Input: starts=[5,10], ends=[8,15]
    #          a    b
    #        ---- ++++++
    #
    #    Result: starts=[5,4], ends=[14,15]
    #        ----------
    #       ++++++++++++
    #
    # Here segment b has moved in front of segment a.
    # To fix this we need to resort the segments.

    unSorted = np.where(starts[1:] <= starts[:-1])
    if len(unSorted[0]) > 0:
        # Track is no longer sorted.
        # Sorting it and all of the other arrays.

        comb = np.column_stack((starts,ends))
        sortIndex = np.lexsort((comb[:,1], comb[:,0]))

        starts = starts[sortIndex]
        ends = ends[sortIndex]
        index = index[sortIndex]

    return starts, ends, index
