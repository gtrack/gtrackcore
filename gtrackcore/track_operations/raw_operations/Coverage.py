__author__ = 'skh'

import numpy


def coverage(starts, ends):
    """
    Find the coverage of a track.

    :param starts: A numpy array of the starts.
    :param ends: A nympy array of the ends.
    :return: The coverage of the track
    """

    return ends.sum() - starts.sum()
