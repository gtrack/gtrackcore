"""
Help functions used by multiple raw operations
"""

import numpy as np


def mergeOverlap(starts, ends, strand=None, ignoreStrand=False):

    # We assume that the segments are sorted on start, then end

    # Equal
    # remove n+1
    # ----
    # ----

    # Partial overlap
    # start[n] < start[n+1], end[n] < end[n]
    # end[n] = end[n+1]
    # remove n+1
    # ----
    #   ----

    # Partial, star[n] == start[n+1], end[n] <  end[n+1]
    # remove n
    # --
    # ----

    # Inside
    # start[n] < start [n+1], end[n] < end[n+1]
    # Remove n+1
    # ----
    #  --

    # Touching..
    # End[n] == start[n+1]
    # Do nothing
    # ----
    #     ----

    pass
