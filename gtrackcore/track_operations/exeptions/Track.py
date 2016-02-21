
class TrackIncompatibleException(Exception):
    """
    Exception cast when two incompatible tracks are used
    in a operation.
    """

    def __init__(self, message):
        self.message = message


class TrackContentsEmptyError(Exception):
    """
    Used when calling methods on a empty Track Contents object.
    """

    def __init__(self):
        self.message = "Track Content is empty!"
