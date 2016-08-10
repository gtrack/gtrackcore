import numpy as np

def flank(starts, ends, genomeSize, strands=None, ignoreStrands=False,
          start=None, end=None, both=None, useFraction=False,
          useMissingStrands=False, treatMissingAsPositive=True,
          allowOverlap=False, debug=False):

    assert starts is not None
    assert ends is not None
    assert isinstance(starts, np.ndarray)
    assert isinstance(ends, np.ndarray)
    assert len(starts) == len(ends)
    assert (end is not None or start is not None) or both is not None

    if not ignoreStrands:
        assert strands is not None

    index = np.arange(0, len(starts), 1, dtype='int32')
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

    if ignoreStrands:
        # Ignoring strand. Every element is treated like it has a positive
        # strand.
        if both is not None:
            # Both flank given..
            # !STRAND->BOTH
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
        # STRAND
        # We have and use strand information.
        assert strands is not None

        if both is not None:
            # STRAND -> BOTH
            assert start is None
            assert end is None

            # Find and create flanks for the positive segments
            positiveStrand = np.where(strands == '+')

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

            # Find and create flanks for the negative segments
            negativeStrand = np.where(strands == '-')

            negativeStartStarts = ends[negativeStrand]
            negativeStartEnds =  ends[negativeStrand] + both

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

            missingFlank = None
            if useMissingStrands:
                # STRAND->BOTH->MISSING
                missingStrand = np.where(strands == '.')

                if treatMissingAsPositive:

                    # STRAND->BOTH->MISSING->POS
                    # Treat the missing strands as if they weare positive.
                    missingStartEnds = starts[missingStrand]
                    missingStartStarts = starts[missingStrand] - both

                    # 0 = '+'
                    missingStartFlank = \
                        np.column_stack((missingStartStarts,
                                         missingStartEnds,
                                         np.zeros(len(missingStartStarts),
                                                  dtype=np.int) + 0))

                    missingEndStarts = ends[missingStrand]
                    missingEndEnds = ends[missingStrand] + both

                    # 0 = '+'
                    missingEndFlank = \
                        np.column_stack((missingEndStarts, missingEndEnds,
                                         np.zeros(len(
                                             missingEndStarts),
                                             dtype=np.int) + 0))

                    missingFlank = np.concatenate((missingStartFlank,
                                                   missingEndFlank))

                else:
                    # STRAND->BOTH->MISSING->NEG
                    # Treat the missing strands as if they are negative.
                    missingStartStarts = ends[missingStrand]
                    missingStartEnds =  ends[missingStrand] + both

                    # 1 == '-'
                    missingStartFlank = \
                        np.column_stack((missingStartStarts,
                                         missingStartEnds,
                                         np.zeros(len(
                                             missingStartStarts),
                                             dtype=np.int) + 1))

                    missingEndEnds = starts[missingStrand]
                    missingEndStarts = starts[missingStrand] - both

                    # 1 == '-'
                    missingEndFlank = \
                        np.column_stack((missingEndStarts, missingEndEnds,
                                         np.zeros(len(
                                             missingEndStarts),
                                             dtype=np.int) + 1))

                    missingFlank = np.concatenate((missingStartFlank,
                                                   missingEndFlank))

            if missingFlank is not None:
                # combine and sort
                res = np.concatenate((positiveFlank, negativeFlank,
                                      missingFlank))
                # TODO check sort
                res = res[np.lexsort((res[:,0], res[:,1]))]
            else:
                # combine and sort
                res = np.concatenate((positiveFlank, negativeFlank))

                # TODO check sort
                res = res[np.lexsort((res[:,0], res[:,1]))]

            flankStarts = res[:,0]
            flankEnds = res[:,1]
            flankStrands = res[:,2]

        else:
            # STRAND->END/START
            assert (start is not None or end is not None)

            # if start, add to start
            # if end, add to end

            startFlank = None
            endFlank = None
            missingFlank = None

            positiveStrand = np.where(strands == '+')
            negativeStrand = np.where(strands == '-')
            missingStrand = np.where(strands == '.')

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

            if useMissingStrands:
                # STRAND->END/START->MISSING
                missingStartFlank = None
                missingEndFlank = None

                if treatMissingAsPositive:
                    # STRAND->END/START->MISSING->POS

                    if start is not None:
                        missingPosStartEnds = starts[missingStrand]
                        missingPosStartStarts = starts[missingStrand] - \
                                               start

                        # 0 == '+'
                        missingStartFlank = \
                            np.column_stack((missingPosStartStarts,
                                             missingPosStartEnds,
                                             np.zeros(len(
                                                 missingPosStartStarts),
                                                 dtype=np.int) + 0))

                    if end is not None:
                        missingPosEndStarts = ends[missingStrand]
                        missingPosEndEnds = ends[missingStrand] + end

                        # 0 == '+'
                        missingEndFlank = \
                            np.column_stack((missingPosEndStarts,
                                            missingPosEndEnds,
                                            np.zeros(len(
                                                 missingPosEndStarts),
                                                dtype=np.int) + 0))

                else:
                    # STRAND->END/START->MISSING->NEG
                    if start is not None:
                        missingNegStartStarts = ends[missingStrand]
                        missingNegStartEnds = ends[missingStrand] + start

                        # 1 == '-'
                        missingStartFlank = \
                            np.column_stack((missingNegStartStarts,
                                            missingNegStartEnds,
                                            np.zeros(len(
                                                missingNegStartStarts),
                                                dtype=np.int) + 1))

                    if end is not None:
                        missingNegEndEnds = starts[missingStrand]
                        missingNegEndStarts = starts[missingStrand] - end

                        # 1 == '-'
                        missingEndFlank = \
                            np.column_stack((missingNegEndStarts,
                                            missingNegEndEnds,
                                            np.zeros(len(
                                                missingNegEndStarts),
                                                dtype=np.int) + 1))

                if missingStartFlank is not None and missingEndFlank is \
                        not None:
                    missingFlank = np.concatenate((missingStartFlank,
                                                   missingEndFlank))
                elif missingStartFlank is not None:
                    missingFlank = missingStartFlank
                elif missingEndFlank is not None:
                    missingFlank = missingEndFlank

                # Calculate start, end, strand..

                res = None
                if startFlank is not None and endFlank is not None:
                    res = np.concatenate((startFlank, endFlank))

                elif startFlank is not None:
                    res = startFlank
                elif endFlank is not None:
                    res = endFlank

                if missingFlank is not None:
                    # Add the missing flank
                    if res is not None:
                        res = np.concatenate((res, missingFlank))
                    else:
                        res = missingFlank

                # TODO check sort
                res = res[np.lexsort((res[:,0], res[:,1]))]
                flankStarts = res[:,0]
                flankEnds = res[:,1]
                flankStrands = res[:,2]

            else:
                if startFlank is not None and endFlank is not None:
                    res = np.concatenate((startFlank, endFlank))
                    res = res[np.lexsort((res[:,0], res[:,1]))]
                    flankStarts = res[:,0]
                    flankEnds = res[:,1]
                    flankStrands = res[:,2]

                elif startFlank is not None:
                    flankStarts = startFlank[:,0]
                    flankEnds = startFlank[:,1]
                    flankStrands = startFlank[:,2]
                else:
                    flankStarts = endFlank[:,0]
                    flankEnds = endFlank[:,1]
                    flankStrands = endFlank[:,2]

    if flankStarts is None:
        return [], [], []

    # Check if the flank over/under flows the genome size.
    underflowIndex = np.where(flankStarts < 0)
    overflowIndex = np.where(flankEnds > genomeSize)

    if len(underflowIndex[0]) > 0:
        flankStarts[underflowIndex] = 0
    if len(overflowIndex[0]) > 0:
        flankEnds[overflowIndex] = genomeSize

    if not allowOverlap:
        # Fix later..
        raise NotImplementedError
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

    # TODO add index...

    if flankStrands is not None:
        # Convert the flankStrands to a gtrack strand array
        flankStrands = np.array(['+' if i == 0 else '-' for i in flankStrands])

    return flankStarts, flankEnds, flankStrands
