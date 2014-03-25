from functools import partial
import os
import numpy

from gtrackcore.track.pytables.database.Database import DatabaseWriter, DatabaseReader
from gtrackcore.util.CommonConstants import GTRACKCORE_FORMAT_SUFFIX
from gtrackcore.util.CommonFunctions import get_dir_path, convert_to_natural_naming
from gtrackcore.util.pytables.CommonNumpyFunctions import insert_into_array_of_larger_shape
from gtrackcore.util.pytables.DatabaseConstants import FLUSH_LIMIT


class DatabaseUtils(object):

    @classmethod
    def _get_node_names(cls, track_name, table_name, allow_overlaps):
        node_names = convert_to_natural_naming(track_name + [table_name])
        node_names.insert(0, 'with_overlaps' if allow_overlaps else 'no_overlaps')
        return node_names

    @classmethod
    def get_track_table_node_names(cls, track_name, allow_overlaps):
        return cls._get_node_names(track_name, track_name[-1], allow_overlaps)

    @classmethod
    def get_br_table_node_names(cls, track_name, allow_overlaps):
        return cls._get_node_names(track_name, 'bounding_regions', allow_overlaps)

    @classmethod
    def create_indices(cls, table, cols=None):
        if cols is None:
            if 'chr' in table.colinstances:
                if not table.cols.chr.is_indexed:
                    table.cols.chr.create_index()
            if 'start' in table.colinstances:
                if not table.cols.start.is_indexed:
                    table.cols.start.create_index()
            if 'end' in table.colinstances:
                if not table.cols.end.is_indexed:
                    table.cols.end.create_index()
        else:
            raise NotImplementedError

    @classmethod
    def sort_table(cls, h5_filename, node_names, sort_order):
        db_writer = DatabaseWriter(h5_filename)
        db_writer.open()
        old_table = db_writer.get_table(node_names)

        table_description = old_table.coldescrs
        if 'chr' in table_description:
            del table_description['chr']

        copy_func = partial(cls.copy_content_from_old_to_new_table_in_sorted_order, old_table, sort_order=sort_order)
        cls.copy_from_old_to_new_table(db_writer, old_table, node_names, table_description, 0, copy_func)

        db_writer.close()

    @classmethod
    def resize_table_columns(cls, h5_filename, node_names, new_column_descriptions, expected_new_rows):
        db_writer = DatabaseWriter(h5_filename)
        db_writer.open()
        old_table = db_writer.get_table(node_names)

        table_description = old_table.coldescrs
        for column_name, description in new_column_descriptions.iteritems():
            table_description[column_name] = description

        copy_func = partial(cls.copy_content_from_old_to_new_table, old_table)
        cls.copy_from_old_to_new_table(node_names, table_description, expected_new_rows, copy_func)

        db_writer.close()

    @classmethod
    def copy_from_old_to_new_table(cls, db_writer, old_table, node_names, table_description, expected_new_rows, copy_func):
        old_table.rename(old_table.name + '_tmp')
        old_table_node_names = node_names[:-1]
        old_table_node_names.append(old_table.name)

        new_table = db_writer.create_table(node_names, table_description, old_table.nrows + expected_new_rows)
        cls.create_indices(new_table)

        copy_func(new_table)

        db_writer.remove_table(old_table_node_names)

    @classmethod
    def copy_content_from_old_to_new_table_in_sorted_order(cls, old_table, new_table, sort_order=None):
        new_row = new_table.row
        for i, old_row in enumerate(old_table.itersequence(sort_order)):
            for col in new_table.colnames:
                new_row[col] = old_row[col]
            new_row.append()
            cls.flush(new_table, i)
        new_table.flush()

    @classmethod
    def copy_content_from_old_to_new_table(cls, old_table, new_table):
        new_row = new_table.row
        for i, old_row in enumerate(old_table.iterrows()):
            for column_name in old_table.colnames:
                if isinstance(old_row[column_name], numpy.ndarray):
                    new_row[column_name] = insert_into_array_of_larger_shape(old_row[column_name],
                                                                             new_row[column_name].shape)
                else:
                    new_row[column_name] = old_row[column_name]
            new_row.append()
            cls.flush(new_table, i)
        new_table.flush()

    @classmethod
    def flush(cls, table, number_of_operations):
        if (number_of_operations + 1) % FLUSH_LIMIT == 0:
            try:
                table.flush()
            except:
                raise  # TODO: raise correct error

    @classmethod
    def get_database_filename(cls, genome, track_name, allow_overlaps=None, create_path=False):
        dir_path = get_dir_path(genome, track_name)
        if create_path:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

        assert os.path.exists(dir_path)

        db_path = "%s%s%s.%s" % (dir_path, os.sep, cls.get_db_name(track_name[-1], None), GTRACKCORE_FORMAT_SUFFIX)
        if os.path.exists(db_path):
            return db_path
        else:
            return "%s%s%s.%s" % (dir_path, os.sep, cls.get_db_name(track_name[-1], allow_overlaps),
                                  GTRACKCORE_FORMAT_SUFFIX)

    @classmethod
    def get_db_name(cls, track_name, allow_overlaps):
        track_name = track_name if allow_overlaps is None else \
            track_name + ('_with_overlaps' if allow_overlaps else '_no_overlaps')
        return convert_to_natural_naming(track_name)

    @classmethod
    def merge_and_rename_overlap_tables(cls, genome, track_name):
        """
        Merge the no_overlaps and_with_overlaps tables into a single h5-file.
        The tables doesn't need to be separated after the pre-processing, since they're accessed independent of each
        other. In the pre-processing step the with_overlaps table is open in read-only mode, while the no_overlaps
        table is being open in append mode. Thus, the tables cannot be in the same file before the
        pre-processing is done.
        """
        no_overlaps_db_path = DatabaseUtils.get_database_filename(genome, track_name, allow_overlaps=False)
        with_overlaps_db_path = DatabaseUtils.get_database_filename(genome, track_name, allow_overlaps=True)

        db_writer = DatabaseWriter(no_overlaps_db_path)
        db_writer.open()
        if os.path.isfile(with_overlaps_db_path):
            db_reader = DatabaseReader(with_overlaps_db_path)
            db_reader.open()
            with_overlaps_tree_node = db_reader.get_node(['with_overlaps'])
            no_overlaps_tree_node = db_writer.get_node([])  # root node

            db_reader.copy_node(with_overlaps_tree_node, target_node=no_overlaps_tree_node, recursive=True)
            db_reader.close()

            os.remove(with_overlaps_db_path)

            with_overlaps_node_names = cls.get_track_table_node_names(track_name, True)
            with_overlaps_table = db_writer.get_table(with_overlaps_node_names)
            cls.create_indices(with_overlaps_table)

        db_path = cls.get_database_filename(genome, track_name, allow_overlaps=None)
        os.rename(no_overlaps_db_path, db_path)

        no_overlaps_node_names = cls.get_track_table_node_names(track_name, False)
        no_overlaps_table = db_writer.get_table(no_overlaps_node_names)
        cls.create_indices(no_overlaps_table)

        db_writer.close()