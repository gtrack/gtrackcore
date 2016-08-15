
import numpy as np


def merge(starts, ends, strands=None, values=None, useStrands=False,
          useMissingStrands=False, treatMissingAsPositive=True,
          useValues=False, valueFunction=None):

    # Two types
    #
    # Where segment n+1 is totaly inside n
    # Remove n+1
    #
    # We assume that the tracks are sorted in order.
    #
    # -----
    #  --
    #
    # ---
    # -----
    #
    # -----
    #   ---
    #
    #
    #
    # Where start[n+1] > end[n]
    # Merge them
    #  end[n] = end[n+1]
    #  remove n+1
    #
    # -----
    #    ------
    #
    # -----
    # -----------

    assert starts is not None
    assert ends is not None
    assert len(starts) == len(ends)

    if useStrands:
        if useMissingStrands:
            pass
        else:
            assert strands is not None
            assert len(strands) == len(starts)

            positiveIndex = np.where(strands == '+')
            negativeIndex = np.where(strands == '-')

            combined = np.column_stack((starts, ends))

            if len(positiveIndex) > 0:

                totalOverlapIndex = np.where((ends[1:] < ends[:-1]))
                while len(totalOverlapIndex[0]) > 0:
                    # As we are removeing n+1 we need to shift the index.
                    removeIndex = totalOverlapIndex[0] + 1
                    starts = np.delete(starts, removeIndex[0])
                    ends = np.delete(ends, removeIndex[0])

                    totalOverlapIndex = np.where((ends[1:] < ends[:-1]))

                # Remove partrial overlapping segments
                # start[n+1] <= end[n]
                partialOverlapIndex = np.where(starts[1:] <= ends[:-1] )
                while len(partialOverlapIndex[0]) > 0:
                    # Found partial overlap. Merge the two.
                    # end[n] = end[n+1]
                    # remove n+1

                    removeIndex = partialOverlapIndex[0] + 1
                    ends[partialOverlapIndex] = ends[removeIndex]
                    starts = np.delete(starts, removeIndex[0])
                    ends = np.delete(ends, removeIndex[0])

                    partialOverlapIndex = np.where(starts[1:] < ends[:-1] )

    else:
        # First we remove totaly overlapping segments.
        # end[n] > end[n+1]
        totalOverlapIndex = np.where((ends[1:] < ends[:-1]))
        while len(totalOverlapIndex[0]) > 0:
            print("In remove total overlap!")
            # As we are removing n+1 we need to shift the index.
            removeIndex = totalOverlapIndex[0] + 1

            if useValues:
                print("In useValues!")
                if valueFunction is None:
                    valueFunction = np.maximum
                assert values is not None
                assert len(values) == len(starts)

                v1 = values[totalOverlapIndex]
                v2 = values[removeIndex]

                values[totalOverlapIndex] = valueFunction(v1, v2)
                values = np.delete(values, removeIndex[0])

            starts = np.delete(starts, removeIndex[0])
            ends = np.delete(ends, removeIndex[0])

            totalOverlapIndex = np.where((ends[1:] < ends[:-1]))

        # Remove partrial overlapping segments
        # start[n+1] <= end[n]
        partialOverlapIndex = np.where(starts[1:] <= ends[:-1] )
        while len(partialOverlapIndex[0]) > 0:
            print("In remove partial overlap!!")
            # Found partial overlap. Merge the two.
            # end[n] = end[n+1]
            # remove n+1

            removeIndex = partialOverlapIndex[0] + 1
            if useValues:
                # Keeping values. Apply the given function and save result as new value.
                if valueFunction is None:
                    valueFunction = np.maximum
                assert values is not None
                assert len(values) == len(starts)

                v1 = values[partialOverlapIndex]
                v2 = values[removeIndex]

                values[partialOverlapIndex] = valueFunction(v1, v2)

            ends[partialOverlapIndex] = ends[removeIndex]
            starts = np.delete(starts, removeIndex[0])
            ends = np.delete(ends, removeIndex[0])

            if useValues:
                values = np.delete(values, removeIndex[0])

            partialOverlapIndex = np.where(starts[1:] <= ends[:-1] )

    return starts, ends, values



def merge2(starts, ends, strands=None, useStands=False, both=False,
          positive=False, negative=False, distance=0,
          positiveDistance=None, negativeDistance=None,
          useMissingStrands=False, treatMissingAsPositive=True,
          mergeValues=False):
    """

    Future expansion: Add support for doing a operations on values etc..

    :param starts: Numpy array: Starts of the track
    :param ends: Numpy array: Ends of the track
    :param strands: Numpy array: Strands of the track (optional)
    :param useStands: Boolean: Only merge segments with equal strand
    :param both: Boolean: Use both negative and positive segments
    :param positive: Boolean: Merge the positive segments
    :param negative: Boolean: Merge the negative segments
    :param distance: Int: Minimum distance between segments before we
    merge them. Default is 0.
    :param positiveDistance: Int: Minimum distance before merge of the
    positive segments. Used when we want a different merge distance on the
    positive and negative segments. Distance is used when not set.
    :param negativeDistance: Int: Minimum distance before we merge the
    negative segments. Used when we want a different merge distance on the
    positive and negative segments. Distance is used when not set.
    :param useMissingStrands: Boolean: Use segments with missing strand
    information.
    :param treatMissingAsPositive: Boolean: Treat the missing segments as
    positive. Default i True. Set to False if you want to treat the segments
    as negative.
    :return: The merged track as a start, end and index array.
    """

    assert starts is not None
    assert ends is not None
    assert len(starts) == len(ends)

    print("Start MERGE!")
    print("starts: {}".format(starts))
    print("ends: {}".format(ends))

    if useStands:
        raise NotImplementedError

        if useMissingStrands:
            pass
    else:
        if mergeValues:
            # TODO. implement support for a "merge function" that can be
            # applied to the values ext of the track.

            # For values on can use sum or average etc..
            raise NotImplementedError
        # Must be sorted..
        #
        #
        # Remove equal or total overlapping segments first.

        # Ignoring strands


        # As the segments are sorted, if end[n+1] is smaller or equal to n[
        # n] then the n+1 is completely inside e[n]. We just remove [n+1]
        # if end[n] > end[n+1] => remover n+1
        totalOverlapIndex = np.where(ends[:-1] >= ends[1:])

        if len(totalOverlapIndex[0]) > 0:
            # As there can be more then one segment inside another segment
            # we need to iterate over it until we have no more total overlap.
            # TODO: I think it will take all in the first iteration. Test it!
            while len(totalOverlapIndex[0]) != 0:
                removeIndex = totalOverlapIndex[0]

                starts = np.delete(starts, totalOverlapIndex, 0)
                ends = np.delete(starts, totalOverlapIndex, 0)

                # TODO, index for values ect.

                totalOverlapIndex = np.where(ends[:-1] >= ends[1:])

        # ---
        # ------


        # Find partially overlapping segments
        # end[n] > start[n+1]
        #
        # ----
        #   ------

        # remove end[n] and remove start[n+1]
        partialOverlapIndex = np.where(ends[:-1] > starts[1:])

        if len(partialOverlapIndex[0]) > 0:
            # Creating masks to merge the overlapping segments
            overlapStartMask = np.ones(len(starts), dtype=bool)
            overlapStartMask[partialOverlapIndex[0]] = False

            overlapEndMask = np.ones(len(ends), dtype=bool)
            overlapEndMask[partialOverlapIndex[0]] = False


            starts = starts
            # Saving the updated ends
            ends = ends[overlapEndMask]

            encodingMask = np.invert(overlapEndMask)
            encoding = res[:, -1]
            encoding[encodingMask] = -1
            encoding = encoding[overlapStartMask]

            res = res[overlapStartMask]
            res[:, 1] = ends
            res[:, -1] = encoding



        index = np.arange(0, len(starts)*2, 1)

        codedStarts = starts * 8 + 5
        codedEnds = ends * 8 + 3

        allCodedEvents = np.concatenate((codedStarts, codedEnds))

        combined = np.column_stack((allCodedEvents, index))
        combined = combined[np.lexsort((combined[:, -1], combined[:, 0]))]

        allSortedEvents = combined[:, 0]
        allEventCodes = (allSortedEvents % 8) - 4
        allSortedDecodedEvents = allSortedEvents / 8

        allEventLengths = allSortedDecodedEvents[1:] - allSortedDecodedEvents[:-1]
        cumulativeCoverStatus = np.add.accumulate(allEventCodes)

        allStartIndexes = np.where(cumulativeCoverStatus[:-1] >= 1)

        tmpStarts = combined[allStartIndexes]

        print("**** DEBUG ****")
        print("coverStatus: {}".format(cumulativeCoverStatus))
        print("allEventCodes: {}".format(allSortedEvents))
        print("combined: {}".format(combined))
        print("tmpStarts: {}".format(tmpStarts))
        print("**** DEBUG END ****")

        # Res
        # Codedvalue, index, encoding, combinedIndex

        starts = tmpStarts[:,0]/8
        ends = starts + allEventLengths[allStartIndexes]
        index = tmpStarts[:,-1]

        # Merge "touching" ones


        print("**** RES ****")
        print("starts: {}".format(starts))
        print("ends: {}".format(ends))
        print("index: {}".format(index))
        print("**** RES ****")

        return starts, ends, index
