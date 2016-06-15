import numpy as np

def slop(starts, ends, genomeSize, strands=None, ignoreStrands=False,
         start=None, end=None, both=None, useFraction=False,
         allowOverlap=False,
         resultAllowOverlap=False, debug=False):

    assert starts is not None
    assert ends is not None
    assert isinstance(starts, np.ndarray)
    assert isinstance(ends, np.ndarray)
    assert len(starts) == len(ends)
    assert (end is not None or start is not None) or both is not None

    if not ignoreStrands:
        assert strands is not None

    index = np.arange(0, len(starts), 1, dtype='int32')

    if useFraction:

        raise NotImplementedError
    else:

        if ignoreStrands is True or both is not None:
            # When we are adding to both sides we can ignore strands.
            # Strands not defined.
            if both is not None:
                starts = starts - both
                ends = ends + both
            else:
                if start is not None:
                    starts = starts - start
                if end is not None:
                    ends = ends + end

        else:
             # TODO

            # When strand information is missing or irrelevant, we treat is as
            # positiv.

            # The strand of the track element. "+" for positive, "-" for negative
            # strand, and "." when strand information is missing or irrelevant.

            # Strand will be a array if "+", "-" or "."

            # create two indexes, one for "+" and ".", and one for "-"

            # flip start and and for the "-"

            # profit.

            # TODO: Support that user can select that '.' can be '-'
            positiveIndex = np.where((strands == '+' or strands == '.'))
            negativeIndex = np.where(strands == '-')

            if start is not None:
                if len(positiveIndex[0]) > 0:
                    if debug:
                        print("***")
                        print(starts)
                        print(starts[positiveIndex])
                        print(starts[positiveIndex]-starts)
                        print("***")
                    starts[positiveIndex] = starts[positiveIndex] - start
                    if debug:
                        print(starts)
                if len(negativeIndex[0]) > 0:
                    ends[negativeIndex] = ends[negativeIndex] + start

            if end is not None:
                if debug:
                    print("***")
                    print("in end!")
                    print(starts)
                    print(ends)
                    print("***")
                if len(positiveIndex[0]) > 0:
                    if debug:
                        print("in positive")
                    ends[positiveIndex] = ends[positiveIndex] + end
                if len(negativeIndex[0]) > 0:
                    if debug:
                        print("in negative")
                    starts[negativeIndex] = starts[negativeIndex] - end

                if debug:
                    print("****")
                    print("after end")
                    print(starts)
                    print(ends)
                    print("***")


    # Check if the slop over/under flows the genome size.
    underFlowIndex = np.where(starts < 0)
    overFlowIndex = np.where(ends > genomeSize)

    if len(underFlowIndex[0]) > 0:
        starts[underFlowIndex] = 0
    if len(overFlowIndex[0]) > 0:
        ends[overFlowIndex] = genomeSize

    if not resultAllowOverlap:
        # Check, equal starts?
        # Check first is a segment is completely inside another segment
        # If it is we remove it.
        # if end[n] > end[n+1] => remover n
        totalOverlapIndex = np.where(ends[:-1] >= ends[1:])

        if len(totalOverlapIndex[0]) > 0:
            # As there can be more then one segment inside another segment
            # we need to iterate over it until we have no more total overlap.
            while len(totalOverlapIndex[0]) != 0:
                ends = np.delete(ends, totalOverlapIndex, 0)
                starts = np.delete(starts, totalOverlapIndex, 0)
                index = np.delete(index, totalOverlapIndex, 0)
                totalOverlapIndex = np.where(ends[:-1] >= ends[:1])

        # Find partially overlapping segments
        # end[n] > start[n+1]
        partialOverlapIndex = np.where(ends[:-1] > starts[1:])

        if len(partialOverlapIndex[0]) > 0:
            # Creating masks to merge the overlapping segments
            overlapStartMask = np.ones(len(starts), dtype=bool)
            overlapStartMask[[partialOverlapIndex[0]+1]] = False

            overlapEndMask = np.ones(len(ends), dtype=bool)
            overlapEndMask[partialOverlapIndex[0]] = False

            starts = starts[overlapStartMask]
            ends = ends[overlapEndMask]

        # Do we need to save strands?
        index = None

    return starts, ends, index
