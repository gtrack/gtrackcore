from gtrackcore.track.pytables.DatabaseHandler import TrackTableReader
from gtrackcore.track.pytables.VirtualTrackColumn import VirtualTrackColumn

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

    def wrap_track_data(self, genome, trackName, allowOverlaps):
        track_data = TrackData()

        table_reader = TrackTableReader(genome, trackName, allowOverlaps)
        table_reader.open()

        column_names = table_reader.get_column_names()
        table_reader.close()

        for column_name in column_names:
            track_data[column_name] = VirtualTrackColumn(column_name, table_reader)

        return track_data

