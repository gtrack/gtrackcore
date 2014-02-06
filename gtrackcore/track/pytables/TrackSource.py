from gtrackcore.track.pytables.DatabaseHandler import TrackTableReader
from gtrackcore.track.pytables.TrackColumnWrapper import TrackColumnWrapper
from gtrackcore.track.pytables.BoundingRegionHandler import BoundingRegionHandler

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

        table_reader = TrackTableReader(trackName, genome, allowOverlaps)
        table_reader.open()

        column_names = table_reader.get_column_names()
        table_reader.close()

        for column_name in column_names:
            track_data[column_name] = TrackColumnWrapper(column_name, table_reader)

        return track_data

