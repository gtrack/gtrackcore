import pickle
from tables.nodes import filenode

from gtrackcore.metadata.TrackInfo import TrackInfo
from gtrackcore.track.pytables.database.Database import DatabaseWriter
from gtrackcore.util.pytables.NameFunctions import TRACKINFO_NODE_NAME, get_database_filename, get_trackinfo_node_names, \
    get_base_node_names


class MetadataHandler(object):

    def __init__(self, genome, track_name):
        self._genome = genome
        self._track_name = track_name
        self._trackinfo_node_names = get_trackinfo_node_names(self._genome, self._track_name)


    def store(self):
        database_filename = get_database_filename(self._genome, self._track_name, allow_overlaps=False)
        self.update_db_trackinfo(database_filename)

    def update_db_trackinfo(self, database_filename):
        dynamic_trackinfo = TrackInfo(self._genome, self._track_name)

        db_writer = DatabaseWriter(database_filename)
        db_writer.open()

        persisted_ti_node = db_writer.get_node(self._trackinfo_node_names)
        if persisted_ti_node is not None:
            trackinfo_file = filenode.open_node(persisted_ti_node, 'a+')
            persisted_trackinfo = pickle.load(trackinfo_file)
            trackinfo_file.close()

            if dynamic_trackinfo.timeOfLastUpdate is not None and dynamic_trackinfo.timeOfLastUpdate > persisted_trackinfo.timeOfLastUpdate:
                self._remove_persisted_trackinfo(db_writer)
                self._dump_dynamic_trackinfo(dynamic_trackinfo, db_writer)
        else:
            trackinfo_base_nodes = get_base_node_names(self._genome, self._track_name)
            db_writer.create_groups(trackinfo_base_nodes)
            self._dump_dynamic_trackinfo(dynamic_trackinfo, db_writer)

        db_writer.close(store_metadata=False)

    def _dump_dynamic_trackinfo(self, dynamic_ti, db_writer):
        ti_group_path = '/' + '/'.join(self._trackinfo_node_names[:-1])
        ti_file = filenode.new_node(db_writer.h5_file, where=ti_group_path, name=TRACKINFO_NODE_NAME)
        pickle.dump(dynamic_ti, ti_file)
        ti_file.close()

    def _remove_persisted_trackinfo(self, db_writer):
        ti_path = '/' + '/'.join(self._trackinfo_node_names)
        db_writer.h5_file.remove_node(ti_path, recursive=True)



