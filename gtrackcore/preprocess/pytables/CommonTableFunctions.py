from functools import partial
import os

import numpy
import tables

from gtrackcore.track.pytables.database.Database import DatabaseWriter, DatabaseReader
from gtrackcore.util.pytables.NameFunctions import get_database_filename, get_base_node_names, \
    WITH_OVERLAPS_NODE_NAME, get_br_table_node_names
from gtrackcore.util.pytables.NumpyFunctions import insert_into_array_of_larger_shape
from gtrackcore.util.pytables.Constants import FLUSH_LIMIT


def sort_table(h5_filename, node_names, sort_order):
    db_writer = DatabaseWriter(h5_filename)
    db_writer.open()
    old_table = db_writer.get_table(node_names)

    table_description = old_table.coldescrs
    if 'chr' in table_description:
        del table_description['chr']

    copy_func = partial(_copy_content_from_old_to_new_table_in_sorted_order, old_table, sort_order=sort_order)
    _update_new_table(db_writer, old_table, node_names, table_description, 0, copy_func)

    db_writer.close()


def resize_table_columns(h5_filename, node_names, table_description, expected_new_rows):
    db_writer = DatabaseWriter(h5_filename)
    db_writer.open()
    old_table = db_writer.get_table(node_names)

    copy_func = partial(_copy_content_from_old_to_new_table, old_table)
    _update_new_table(db_writer, old_table, node_names, table_description, expected_new_rows, copy_func)

    db_writer.close()


def _update_new_table(db_writer, old_table, node_names, table_description, expected_new_rows, copy_func):
    old_table.rename(old_table.name + '_tmp')
    old_table_node_names = node_names[:-1]
    old_table_node_names.append(old_table.name)

    new_table = db_writer.create_table(node_names, table_description, old_table.nrows + expected_new_rows)

    copy_func(new_table)

    db_writer.remove_table(old_table_node_names)


def _copy_content_from_old_to_new_table_in_sorted_order(old_table, new_table, sort_order=None):
    new_row = new_table.row
    for i, old_row in enumerate(old_table.itersequence(sort_order)):
        for col in new_table.colnames:
            new_row[col] = old_row[col]
        new_row.append()
        flush_table(new_table, i)
    new_table.flush()


def _copy_content_from_old_to_new_table(old_table, new_table):
    new_row = new_table.row
    for flush_counter, old_row in enumerate(old_table.iterrows()):
        for column_name in old_table.colnames:
            if isinstance(old_row[column_name], numpy.ndarray):
                new_row[column_name] = insert_into_array_of_larger_shape(old_row[column_name],
                                                                         new_row[column_name].shape)
            else:
                new_row[column_name] = old_row[column_name]
        new_row.append()
        flush_table(new_table, flush_counter)
    new_table.flush()


def merge_and_rename_overlap_tables(genome, track_name):
    """
    Merge the no_overlaps and_with_overlaps tables into a single h5-file.
    The tables doesn't need to be separated after the pre-processing, since they're accessed independent of each
    other. In the pre-processing step the with_overlaps table is open in read-only mode, while the no_overlaps
    table is being open in append mode. Thus, the tables cannot be in the same file before the
    pre-processing is done.
    """
    no_overlap_db_path = get_database_filename(genome, track_name, allow_overlaps=False)
    with_overlap_db_path = get_database_filename(genome, track_name, allow_overlaps=True)
    if os.path.isfile(with_overlap_db_path):
        db_writer = DatabaseWriter(no_overlap_db_path)
        db_writer.open()
        db_reader = DatabaseReader(with_overlap_db_path)
        db_reader.open()

        base_node_names = get_base_node_names(genome, track_name)
        with_overlap_base = base_node_names + [WITH_OVERLAPS_NODE_NAME]

        with_overlap_base_node = db_reader.get_node(with_overlap_base)
        target_base_node = db_writer.get_node(base_node_names)

        db_reader.copy_node(with_overlap_base_node, target_node=target_base_node, recursive=True)
        db_reader.close()

        os.remove(with_overlap_db_path)
        db_writer.close()

    db_path = get_database_filename(genome, track_name)
    os.rename(no_overlap_db_path, db_path)

    #There might be some remaining open file handlers that are using the new db_path, so these must be closed
    _close_file_handlers(db_path)


def _close_file_handlers(db_path):
    current_version = tuple(map(int, tables.__version__.split('.')))
    if current_version >= (3, 1, 0):
        handlers = list(tables.file._open_files.get_handlers_by_name(db_path))
        if len(handlers) > 0:
            for fileh in handlers:
                fileh.close()
    else:
        filenames = []
        open_files = tables.file._open_files.items()
        for filename, file in open_files:
            if filename == db_path:
                file.close()
                filenames.append(filename)
        for filename in filenames:
            if filename in tables.file._open_files:
                del tables.file._open_files[filename]


def create_table_indices(table, cols=None):
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


def flush_table(table, number_of_operations):
    if (number_of_operations + 1) % FLUSH_LIMIT == 0:
        try:
            table.flush()
        except:
            raise  # TODO: raise correct error
