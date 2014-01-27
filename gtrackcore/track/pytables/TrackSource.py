from gtrackcore.track.pytables.DatabaseTrackHandler import DatabaseTrackHandler
from gtrackcore.track.pytables.TrackColumnWrapper import TrackColumnWrapper

class TrackData(dict):
    def __init__(self, other=None):
        if other is not None:
            dict.__init__(self, other)
        else:
            dict.__init__(self)

class TrackSource:
    def __init__(self):
        self._chrInUse = None
        self._fileDict = {}

    def getTrackData(self, trackName, genome, chr, allowOverlaps, forceChrFolders=False):
        track_data = TrackData()

        db_handler = DatabaseTrackHandler(trackName, genome, chr, allowOverlaps)
        db_handler.open()

        for column in db_handler.column_names():
            track_data[column] = TrackColumnWrapper(column, db_handler)

        db_handler.close()

        return track_data

