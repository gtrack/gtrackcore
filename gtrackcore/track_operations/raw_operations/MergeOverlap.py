
import numpy as np

def mergeOverlap(starts, ends, strands=None, useStands=False, both=False,
          positive=False, negative=False, distance=0,
          positiveDistance=None, negativeDistance=None,
          useMissingStrands=False, treatMissingAsPositive=True):
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

    pass
