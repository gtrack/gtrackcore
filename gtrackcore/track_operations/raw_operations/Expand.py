import numpy as np

def expand(regionSize, starts=None, ends=None, strands=None, start=None,
           end=None, both=None, useFraction=False, useStrands=False,
           treatMissingAsNegative=False, debug=False):
    """

    :param regionSize:
    :param starts:
    :param ends:
    :param strands:
    :param start:
    :param end:
    :param both:
    :param useFraction:
    :param useStrands:
    :param treatMissingAsNegative:
    :param debug:
    :return:
    """

    assert (end is not None or start is not None) or both is not None

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
            assert start is None
            assert end is None

            both = lengths * both
            both.astype(int)
        else:
            if start is not None:
                start = lengths * start
                start.astype(int)

            if end is not None:
                end = lengths * end
                end.astype(int)

    if useStrands:
        positiveIndex = np.where(strands == '+')
        if len(positiveIndex[0]) == 0:
            positiveIndex = None

        negativeIndex = np.where(strands == '-')
        if len(negativeIndex[0]) == 0:
            negativeIndex = None

        missingIndex = np.where(strands == '.')

        if debug:
            print("In use strands")
            print("posIndex: {}".format(positiveIndex))
            print("negIndex: {}".format(negativeIndex))
            print("misIndex: {}".format(missingIndex))

        if len(missingIndex[0]) == 0:
            missingIndex = None

        if both is not None:
            # When using both, there is no difference in extending negative
            # and positive features.
            if positiveIndex is not None:
                starts[positiveIndex] = starts[positiveIndex] - both
                ends[positiveIndex] = ends[positiveIndex] + both
            if negativeIndex is not None:
                starts[negativeIndex] = starts[negativeIndex] - both
                ends[negativeIndex] = ends[negativeIndex] + both

            if missingIndex is not None:
                if treatMissingAsNegative:
                    starts[missingIndex] = starts[missingIndex] - both
                    ends[missingIndex] = ends[missingIndex] + both
                    strands[missingIndex] = '-'

                else:
                    starts[missingIndex] = starts[missingIndex] - both
                    ends[missingIndex] = ends[missingIndex] + both
                    strands[missingIndex] = '+'

        else:
            if start is not None:
                if debug:
                    print("Extending on start!")
                if positiveIndex is not None:
                    if debug:
                        print("Extending on positive")
                        print("Start before:")
                        print(starts)
                    starts[positiveIndex] = starts[positiveIndex] - start

                    if debug:
                        print("Start after:")
                        print(starts)

                if negativeIndex is not None:
                    if debug:
                        print("Extending on negative")
                        print("Ends before:")
                        print(ends)
                    ends[negativeIndex] = ends[negativeIndex] + start

                    if debug:
                        print("Ends after:")
                        print(ends)

                if missingIndex is not None:
                    if treatMissingAsNegative:
                        ends[missingIndex] = ends[missingIndex] + start
                        strands[missingIndex] = '-'
                    else:
                        starts[missingIndex] = starts[missingIndex] - start
                        strands[missingIndex] = '+'

            if end is not None:
                if positiveIndex is not None:
                    ends[positiveIndex] = ends[positiveIndex] + end
                if negativeIndex is not None:
                    starts[negativeIndex] = starts[negativeIndex] - end

                if missingIndex is not None:
                    if treatMissingAsNegative:
                        starts[missingIndex] = starts[missingIndex] - end
                        strands[missingIndex] = '-'
                    else:
                        ends[missingIndex] = ends[missingIndex] + end
                        strands[missingIndex] = '+'

    else:
        # No strand info or ignoring it.

        if both is not None:
            starts = starts - both
            ends = ends + both
        else:
            if start is not None:
                starts = starts - start
            if end is not None:
                ends = ends + end

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
        strands = strands[sortIndex]
        index = index[sortIndex]

    return starts, ends, strands, index
