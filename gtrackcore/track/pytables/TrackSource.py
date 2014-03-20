from gtrackcore.track.pytables.PytablesDatabase import DatabaseReader
from gtrackcore.track.pytables.PytablesDatabaseUtils import PytablesDatabaseUtils
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

    def get_track_data(self, genome, trackName, allowOverlaps):
        track_data = TrackData()
        database_filename = PytablesDatabaseUtils.get_database_filename(genome, trackName, allow_overlaps=allowOverlaps)
        table_node_names = PytablesDatabaseUtils.get_track_table_node_names(trackName, allowOverlaps)

        db_reader = DatabaseReader(database_filename)
        db_reader.open()
        table = db_reader.get_table(table_node_names)

        column_names = table.colnames
        number_of_rows = table.nrows
        db_reader.close()

        for column_name in column_names:
            track_data[column_name] = VirtualTrackColumn(column_name, db_reader, table_node_names,
                                                         start_index=0, end_index=number_of_rows)

        return track_data

