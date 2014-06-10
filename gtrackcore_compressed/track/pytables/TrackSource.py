from gtrackcore_compressed.track.pytables.database.Database import DatabaseReader
from gtrackcore_compressed.track.pytables.VirtualTrackColumn import VirtualTrackColumn
from gtrackcore_compressed.util.pytables.NameFunctions import get_database_filename, get_track_table_node_names


class TrackData(dict):
    def __init__(self, other=None):
        if other is not None:
            dict.__init__(self, other)
        else:
            dict.__init__(self)


class TrackSource:

    def __init__(self):
        self.track_data = {key: TrackData() for key in [True, False]}

    def get_track_data(self, genome, trackName, allowOverlaps):
        database_filename = get_database_filename(genome, trackName, allow_overlaps=allowOverlaps)
        table_node_names = get_track_table_node_names(genome, trackName, allowOverlaps)

        db_reader = DatabaseReader(database_filename)
        db_reader.open()
        table = db_reader.get_table(table_node_names)

        column_names = table.colnames
        num_of_rows = table.nrows
        db_reader.close()

        for column_name in column_names:
            if column_name not in self.track_data[allowOverlaps]:
                self.track_data[allowOverlaps][column_name] = VirtualTrackColumn(column_name, db_reader, table_node_names,
                                                                                 start_index=0, end_index=num_of_rows)

        return self.track_data[allowOverlaps]
