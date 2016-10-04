
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


class TrackNameExistsError(Exception):
    """
    Used when trying to save a track using an existing track name
    """

    def __init__(self):
        self.message = "Track name already in use, try using a different name."
