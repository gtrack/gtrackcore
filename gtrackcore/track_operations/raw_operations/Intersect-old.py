import numpy as np

from gtrackcore.track_operations.exeptions.Track import TrackIncompatibleException

def intersect(t1Starts, t2Starts, **kwargs):

    if 't1Ends' not in kwargs:
        # A point type

        if 't1Vals' not in kwargs or kwargs['t1Vals'] is not None:
            # Points (P)
            return np.intersect1d(t1Starts,t2Starts)
        else:
            # Valued Points (VP)

            if len(t1Starts) == 0 or len(t2Starts) == 0:
                # If t1 or t2 is empty, then can not be a intersect.
                return (np.array([]), np.array([]))

            else:
                inter = np.intersect1d(t1Starts, t2Starts)

                if len(inter) == 0:
                    # If there is no intersect we return
                    # two empty numpy arrays
                    return np.array([]), np.array([])

                outVal = []
                j = 0
                for i, v in enumerate(t1Starts):
                    while j < len(inter) and v >= inter[j]:
                        if v == inter[j]:
                            outVal.append(kwargs['t1Val'][i])
                            j += 1

                    if j >= len(inter):
                        break

                return inter, np.array(outVal)

    elif 't1Val' not in kwargs:
        # Segments (S) or Genome Partition (GP)

        # Check if t2Ends are defined.
        if 't2Ends' not in kwargs:
            raise TrackIncompatibleException("Comparing segments with points")

        t1CodedStarts = t1Starts * 8 + 5
        t1CodedEnds = kwargs['t1Ends'] * 8 + 3
        t2CodedStarts = t2Starts * 8 + 6
        t2CodedEnds = kwargs['t2Ends'] * 8 + 2

        allSortedCodedEvents = np.concatenate((t1CodedStarts, t1CodedEnds, t2CodedStarts, t2CodedEnds))
        allSortedCodedEvents.sort()

        allEventCodes = (allSortedCodedEvents % 8) - 4

        allSortedDecodedEvents = allSortedCodedEvents / 8
        allEventLengths = allSortedDecodedEvents[1:] - allSortedDecodedEvents[:-1]

        cumulativeCoverStatus = np.add.accumulate(allEventCodes)

        allStarts = allSortedDecodedEvents[cumulativeCoverStatus[:-1] >= 3]
        allLengths = allEventLengths[cumulativeCoverStatus[:-1] >= 3]
        allEnds = allStarts + allLengths

        return (allStarts, allEnds)

    else:
        # Valued Segments (VS) og Step Function (SF)
        return False