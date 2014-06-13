from gtrackcore.track.pytables.database.Database import DatabaseReader
from gtrackcore.track.pytables.VirtualTrackColumn import VirtualTrackColumn
from gtrackcore.util.pytables.NameFunctions import get_database_filename, get_track_table_node_names, get_array_group_node_names
from gtrackcore.TestSettings import test_settings

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
        num_of_elements = table.nrows
        db_reader.close()

        array_group_node_names = get_array_group_node_names(genome, trackName, allowOverlaps)

        for column_name in column_names:
            if column_name not in self.track_data[allowOverlaps]:
                if test_settings['virtualtrackcolumn_uses_table']:
                    self.track_data[allowOverlaps][column_name] = VirtualTrackColumn(table_node_names, db_reader,
                                                                                     start_index=0, end_index=num_of_elements,
                                                                                     column_name=column_name)
                else:
                    array_node_names = array_group_node_names + [column_name]
                    self.track_data[allowOverlaps][column_name] = VirtualTrackColumn(array_node_names, db_reader,
                                                                                     start_index=0, end_index=num_of_elements)

        return self.track_data[allowOverlaps]
