import numpy as np

def slop(genomeSize, starts=None, ends=None, strands=None, start=None,
         end=None, both=None, useFraction=False, useStrands=False,
         useMissingStrands=False, treatMissingAsPositive=True,
         ignorePositive=False, ignoreNegative=False, updateMissingStrand=False,
         debug=False):
    """

    :param genomeSize:
    :param starts:
    :param ends:
    :param strands:
    :param start:
    :param end:
    :param both:
    :param useFraction:
    :param useStrands:
    :param useMissingStrands:
    :param treatMissingAsPositive:
    :param debug:
    :return:
    """

    assert (end is not None or start is not None) or both is not None

    if ends is None:
        # A point track. We convert it to a segment track where all elements
        #  have a length of zero.
        ends = np.copy(starts)

    if useStrands:
        assert strands is not None

    index = np.arange(0, len(starts), 1, dtype='int32')

    if useFraction:
        print("In useFractions!")
        # Using a fraction of the segments length as a basis for the flank.
        # To do this we need to calculate the flank length for each segment.
        # The new arrays are converted to ints.

        lengths = ends - starts
        print("lengths: {}".format(lengths))

        if both is not None:
            assert start is None
            assert end is None

            # We can ignore strand when calculating length

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
        if ignorePositive:
            positiveIndex = None
        else:
            positiveIndex = np.where(strands == '+')
            if len(positiveIndex[0]) == 0:
                positiveIndex = None

        if ignoreNegative:
            negativeIndex = None
        else:
            negativeIndex = np.where(strands == '-')
            if len(negativeIndex[0]) == 0:
                negativeIndex = None

        if useMissingStrands:
            missingIndex = np.where(strands == '.')

            if len(missingIndex[0]) == 0:
                useMissingStrands = False
        else:
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

            if useMissingStrands:
                if treatMissingAsPositive and not ignorePositive:
                    print("in add missing as positive!")
                    starts[missingIndex] = starts[missingIndex] - both
                    ends[missingIndex] = ends[missingIndex] + both
                    if updateMissingStrand:
                        print("setting strand to pos")
                        strands[missingIndex] = '+'

                elif not treatMissingAsPositive and not ignoreNegative:
                    starts[missingIndex] = starts[missingIndex] - both
                    ends[missingIndex] = ends[missingIndex] + both

                    if updateMissingStrand:
                        strands[missingIndex] = '-'

        else:
            if start is not None:
                print("Strand! start!")
                if positiveIndex is not None:
                    print("updating positive starts!")
                    starts[positiveIndex] = starts[positiveIndex] - start

                if negativeIndex is not None:
                    print("updating negative starts ")
                    ends[negativeIndex] = ends[negativeIndex] + start

                if useMissingStrands:
                    print("updating missing starts")
                    if treatMissingAsPositive and not ignorePositive:
                        print("in update!")
                        starts[missingIndex] = starts[missingIndex] - start
                        print("test: {}".format(updateMissingStrand))
                        if updateMissingStrand:
                            print("Updating start!")
                            strands[missingIndex] = '+'

                    elif not treatMissingAsPositive and not ignoreNegative:
                        ends[missingIndex] = ends[missingIndex] + start
                        if updateMissingStrand:
                            strands[missingIndex] = '-'

            if end is not None:
                if positiveIndex is not None:
                    ends[positiveIndex] = ends[positiveIndex] + end
                if negativeIndex is not None:
                    starts[negativeIndex] = starts[negativeIndex] - end

                if useMissingStrands:
                    if treatMissingAsPositive and not ignorePositive:
                        ends[missingIndex] = ends[missingIndex] + end
                        if updateMissingStrand:
                            strands[missingIndex] = '+'

                    elif not treatMissingAsPositive and not ignoreNegative:
                        starts[missingIndex] = starts[missingIndex] - end
                        if updateMissingStrand:
                            strands[missingIndex] = '-'

    else:
        # No strand info or ignoring it.

        if both is not None:
            starts = starts - both
            ends = ends + both
        else:
            if start is not None:
                print("in start")
                starts = starts - start
            if end is not None:
                ends = ends + end

    # Check if the slop over/under flows the genome size.
    underFlowIndex = np.where(starts < 0)
    overFlowIndex = np.where(ends > genomeSize)

    if len(underFlowIndex[0]) > 0:
        starts[underFlowIndex] = 0
    if len(overFlowIndex[0]) > 0:
        ends[overFlowIndex] = genomeSize

    print(strands)

    # TODO sort! We can in some cases lose the ordering of the track.
    # Sort them before returning.

    # Slop at start of positive segments.
    #
    #       ----
    #            ++++
    # Res
    #       ----
    #     +++++++++++
    #
    # The second segment is now before the first

    return starts, ends, strands, index
