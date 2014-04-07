import pickle
from tables.nodes import filenode

from gtrackcore.track.pytables.database.Database import DatabaseWriter, DatabaseReader
from gtrackcore.util.pytables.NameFunctions import TRACKINFO_NODE_NAME, get_database_filename, get_trackinfo_node_names, \
    get_base_node_names


class MetadataHandler(object):

    def __init__(self, genome, track_name):
        self._genome = genome
        self._track_name = track_name
        self._trackinfo_node_names = get_trackinfo_node_names(self._genome, self._track_name)


    def store(self, dynamic_trackinfo):
        database_filename = get_database_filename(self._genome, self._track_name, allow_overlaps=False)
        self.update_persisted_trackinfo(database_filename, dynamic_trackinfo)

    def _dynamic_trackinfo_is_newest(self, dynamic_trackinfo, persisted_trackinfo):
        return dynamic_trackinfo.timeOfLastUpdate is not None and dynamic_trackinfo.timeOfLastUpdate > persisted_trackinfo.timeOfLastUpdate

    def _persisted_trackinfo_is_newest(self, dynamic_trackinfo, persisted_trackinfo):
        return dynamic_trackinfo.timeOfLastUpdate is None or persisted_trackinfo.timeOfLastUpdate > dynamic_trackinfo.timeOfLastUpdate

    def get_newest_trackinfo(self, database_filename, dynamic_trackinfo):
        db_reader = DatabaseReader(database_filename)
        db_reader.open()

        persisted_ti_node = db_reader.get_node(self._trackinfo_node_names)
        if persisted_ti_node is None:
            trackinfo = dynamic_trackinfo
        else:
            trackinfo_file = filenode.open_node(persisted_ti_node, 'r')
            persisted_trackinfo = pickle.load(trackinfo_file)
            trackinfo_file.close()

            if dynamic_trackinfo is None:
                trackinfo = persisted_trackinfo
            else:
                if self._persisted_trackinfo_is_newest(dynamic_trackinfo, persisted_trackinfo):
                    trackinfo = persisted_trackinfo
                else:
                    trackinfo = dynamic_trackinfo

        db_reader.close(store_metadata=False)

        return trackinfo

    def update_persisted_trackinfo(self, database_filename, dynamic_trackinfo):
        db_writer = DatabaseWriter(database_filename)
        db_writer.open()

        persisted_ti_node = db_writer.get_node(self._trackinfo_node_names)
        if persisted_ti_node is not None:
            trackinfo_file = filenode.open_node(persisted_ti_node, 'a+')
            persisted_trackinfo = pickle.load(trackinfo_file)
            trackinfo_file.close()

            if self._dynamic_trackinfo_is_newest(dynamic_trackinfo, persisted_trackinfo):
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



