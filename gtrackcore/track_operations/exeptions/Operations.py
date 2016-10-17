__author__ = 'skh'


class OutputTrackTypeNotSupportedError(Exception):
    """
    Exception used when the a operation do not support the given output
    TrackFormat.
    """

    def __init__(self, trackType, operation):
        self.message = "Track type {0} not supported by operation {" \
                       "1}".format(trackType, operation)

class InvalidArgumentError(Exception):
    pass
