
import numpy as np

def flank(starts, ends, nrBp, chromoLength, before=False, after=False):
    """
    Create a new flanking track.
    :param starts: Starts as a numpy array.
    :param ends: Ends as a numpy array.
    :param nrBp: The size of the flank (nr of base pares).
    :param chromoLength: The length of the chromosome. We need this to not create
        flanks at the outside of the chromosome.
    :param before: Only create flanks at the start.
    :param after: Only create flanks at the ends.
    :return: A new segmented track
    """

    if before:
        # Create flank at the start of the segments
        flankStarts = starts - nrBp
        flankEnds = starts

        if (flankStarts < 0).all():
            # Starts outside the genome..
            # As the list will always be sorted we just set the negative ones to zero.
            flankStarts[flankStarts<0] = 0

        return flankStarts, flankEnds

    elif after:
        # Create flank at the end of the segments
        flankStarts = ends
        flankEnds = ends + nrBp

        if (flankEnds > chromoLength).all():
            # Ends outside the genome..
            # As the list will always be sorted we just set the negative ones to chromoLength.
            flankStarts[flankStarts<0] = chromoLength

        return flankStarts, flankEnds
    else:
        # Flanks at both ends

        beforeStarts = starts
        beforeEnds = starts - nrBp
        afterStarts = ends
        afterEnds = ends + nrBp

        if (beforeStarts < 0).all():
            # Starts outside the genome..
            # As the list will always be sorted we just set the negative ones to zero.
            beforeStarts[beforeStarts<0] = 0

        if (afterEnds > chromoLength).all():
            # Ends outside the genome..
            # As the list will always be sorted we just set the negative ones to chromoLength.
            afterStarts[afterStarts<0] = chromoLength


        # TODO, merge the two

        return



