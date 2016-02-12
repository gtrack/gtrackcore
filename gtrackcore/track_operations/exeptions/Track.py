
class TrackIncompatibleException(Exception):
    """
    Exception cast when two incompatible tracks are used
    in a operation.
    """

    def __init__(self, message):
        self.message = message
