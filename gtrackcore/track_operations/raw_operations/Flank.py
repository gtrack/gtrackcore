import numpy as np

def flank(starts, ends, genomeSize, strands=None, useStrands=True,
          start=None, end=None, both=None, useFraction=False,
          treatMissingAsNegative=False, debug=False):

    assert starts is not None
    assert ends is not None
    assert len(starts) == len(ends)
    assert (end is not None or start is not None) or both is not None

    if useStrands:
        assert strands is not None

    flankStarts = None
    flankEnds = None

    if useFraction:
        # Using a fraction of the segments length as a basis for the flank.
        # To do this we need to calculate the flank length for each segment.
        # The new arrays are converted to ints.

        lengths = ends - starts

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

    if not useStrands:
        # Ignoring strand. Every element is treated like it has a positive
        # strand.
        if both is not None:
            # Both flank given.
            assert start is None
            assert end is None

            # Flank at the start side
            startEnds = starts
            startStarts = starts - both
            startFlank = np.column_stack((startStarts, startEnds))

            # Flank at the end side
            endStarts = ends
            endEnds = ends + both
            endFlank = np.column_stack((endStarts, endEnds))

            # combine and sort the two flank arrays
            res = np.concatenate((startFlank, endFlank))
            res = res[np.lexsort((res[:,1], res[:,0]))]

            # Split into start and end arrays
            flankStarts = res[:,0]
            flankEnds = res[:,1]
            flankStrands = None

        else:
            # !STRAND -> END/START
            assert (start is not None or end is not None)

            startFlank = None
            endFlank = None

            if start is not None:
                # Start flank given.
                startEnds = starts
                startStarts = starts - start
                startFlank = np.column_stack((startStarts, startEnds))

            if end is not None:
                # End flank given
                endStarts = ends
                endEnds = ends + end
                endFlank = np.column_stack((endStarts, endEnds))

            if startFlank is not None and endFlank is not None:
                # Flank at start and end.
                # Combining and sorting
                # combine and sort
                res = np.concatenate((startFlank, endFlank))
                res = res[np.lexsort((res[:,1], res[:,0]))]

                flankStarts = res[:,0]
                flankEnds = res[:,1]
                flankStrands = None

            elif startFlank is not None:
                # Only flank at start
                flankStarts = startFlank[:,0]
                flankEnds = startFlank[:,1]
                flankStrands = None

            else:
                # Only flank at end
                assert endFlank is not None
                flankStarts = endFlank[:,0]
                flankEnds = endFlank[:,1]
                flankStrands = None
    else:
        # We have and use strand information.
        assert strands is not None

        if treatMissingAsNegative:
            positiveStrand = np.where(strands == '+')
            negativeStrand = np.where((strands == '-') | (strands == '.'))
        else:
            positiveStrand = np.where((strands == '+') | (strands == '.'))
            negativeStrand = np.where(strands == '-')

        if both is not None:
            # STRAND -> BOTH
            assert start is None
            assert end is None

            positiveStartEnds = starts[positiveStrand]
            positiveStartStarts = starts[positiveStrand] - both

            # 0 == '+'
            positiveStartFlank = \
                        np.column_stack((positiveStartStarts,
                                         positiveStartEnds,
                                         np.zeros(len(positiveStartStarts),
                                                  dtype=np.int) + 0))

            positiveEndStarts = ends[positiveStrand]
            positiveEndEnds = ends[positiveStrand] + both

            # 0 = '+'
            positiveEndFlank = \
                        np.column_stack((positiveEndStarts,
                                         positiveEndEnds,
                                         np.zeros(len(positiveEndStarts),
                                                  dtype=np.int) + 0))
            positiveFlank = np.concatenate((positiveStartFlank,
                                            positiveEndFlank))

            negativeStartStarts = ends[negativeStrand]
            negativeStartEnds = ends[negativeStrand] + both

            # 1 = '-'
            negativeStartFlank = \
                        np.column_stack((negativeStartStarts,
                                         negativeStartEnds,
                                         np.zeros(len(negativeStartStarts),
                                                  dtype=np.int) + 1))

            negativeEndEnds = starts[negativeStrand]
            negativeEndStarts = starts[negativeStrand] - both

            # 1 = '-'
            negativeEndFlank = \
                        np.column_stack((negativeEndStarts,
                                         negativeEndEnds,
                                         np.zeros(len(negativeEndStarts),
                                                  dtype=np.int) + 1))

            negativeFlank = np.concatenate((negativeStartFlank,
                                            negativeEndFlank))

            # combine and sort
            res = np.concatenate((positiveFlank, negativeFlank))

            res = res[np.lexsort((res[:,0], res[:,1]))]

            flankStarts = res[:,0]
            flankEnds = res[:,1]
            flankStrands = res[:,2]

        else:
            # STRAND->END/START
            assert (start is not None or end is not None)

            startFlank = None
            endFlank = None

            if start is not None:
                # Find and create flanks for the positive segments
                positiveStartEnds = starts[positiveStrand]
                positiveStartStarts = starts[positiveStrand] - start

                # 0 == '+'
                positiveStartFlank = \
                        np.column_stack((positiveStartStarts,
                                         positiveStartEnds,
                                         np.zeros(len(
                                             positiveStartStarts),
                                             dtype=np.int) + 0))

                # Find and create flanks for the negative segments
                negativeStartStarts = ends[negativeStrand]
                negativeStartEnds = ends[negativeStrand] + start

                # 1 == '-'
                negativeStartFlank = \
                        np.column_stack((negativeStartStarts,
                                         negativeStartEnds,
                                         np.zeros(len(
                                             negativeStartStarts),
                                             dtype=np.int) + 1))

                startFlank = np.concatenate((positiveStartFlank,
                                             negativeStartFlank))
            if end is not None:
                positiveEndStarts = ends[positiveStrand]
                positiveEndEnds = ends[positiveStrand] + end

                # 0 == '+'
                positiveEndFlank = \
                        np.column_stack((positiveEndStarts,
                                         positiveEndEnds,
                                         np.zeros(len(
                                             positiveEndStarts),
                                             dtype=np.int) + 0))

                negativeEndEnds = starts[negativeStrand]
                negativeEndStarts = starts[negativeStrand] - end

                # 1 == '-'
                negativeEndFlank = \
                        np.column_stack((negativeEndStarts,
                                         negativeEndEnds,
                                         np.zeros(len(
                                             negativeEndStarts),
                                             dtype=np.int) + 1))
                endFlank = np.concatenate((positiveEndFlank,
                                           negativeEndFlank))

            # Calculate start, end, strand..
            res = None
            if startFlank is not None and endFlank is not None:
                res = np.concatenate((startFlank, endFlank))
            elif startFlank is not None:
                res = startFlank
            elif endFlank is not None:
                res = endFlank

            res = res[np.lexsort((res[:,0], res[:,1]))]
            flankStarts = res[:,0]
            flankEnds = res[:,1]
            flankStrands = res[:,2]

    if flankStarts is None:
        return None, None, None

    # Check if the flank over/under flows the genome size.
    underflowIndex = np.where(flankStarts < 0)
    overflowIndex = np.where(flankEnds > genomeSize)

    if len(underflowIndex[0]) > 0:
        flankStarts[underflowIndex] = 0
    if len(overflowIndex[0]) > 0:
        flankEnds[overflowIndex] = genomeSize

    if flankStrands is not None:
        # Convert the flankStrands to a gtrack strand array
        flankStrands = np.array(['+' if i == 0 else '-' for i in flankStrands])

    return flankStarts, flankEnds, flankStrands
