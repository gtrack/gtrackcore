
import numpy as np

from gtrackcore.track_operations.RawOperationContent import RawOperationContent

from gtrackcore.track.format.TrackFormat import TrackFormatReq

"""
Misc tools used by raw operations
"""


def generateTrackFromResult(res, initialTracks, trackReq):
    """

    TODO
    Change initialTracks to OrderedDict ect.

    :param res: The result array from the raw operations
    :param initialTracks: Array of the initial tracks.
    :param trackReq: Track requirement
    :return:
    """

    assert len(initialTracks) > 0

    genome = initialTracks[0].genome
    region = initialTracks[0].region

    track = RawOperationContent(genome,region)

    track.starts = res[:, 0]
    track.ends = res[:, 1]

    encoding = res[:, -1]
    indexes = res[:, -2]

    indexesEncoded = res[0:,-2:]

    deletedIndexes = np.where(encoding == -1)

    print(deletedIndexes)
    trackIndexes = []

    for i, v in enumerate(initialTracks):
        tmp = np.where(encoding == i+1)
        trackIndexes.append(tmp)

    print(trackIndexes)

    # Split into len(initialTracks) indexes. Use the enocding
    # Remove any parts with encoding -1

    # TODO: How do we represent missing data?

    if trackReq._val is not None:

        vals = np.zeros(len(track.starts))

        # Set deleted ones to some value..

        # Iterate over trackIndexs end retrieve the correct values


