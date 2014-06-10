from itertools import izip
import os
from stat import S_IRWXU, S_IRWXG, S_IROTH

import numpy

from gtrackcore_compressed.preprocess.pytables.TableDescriber import TableDescriber
from gtrackcore_compressed.track.pytables.database.Database import DatabaseWriter
from gtrackcore_compressed.preprocess.pytables.CommonTableFunctions import resize_table_columns, flush_table
from gtrackcore_compressed.util.pytables.NameFunctions import get_database_filename, get_track_table_node_names
from gtrackcore_compressed.util.pytables.NumpyFunctions import insert_into_array_of_larger_shape


class OutputManager(object):
    def __init__(self, genome, track_name, allow_overlaps, ge_source_manager, track_format):
        self._track_format = track_format
        self._database_filename = get_database_filename(genome, track_name,
                                                        allow_overlaps=allow_overlaps, create_path=True)
        self._db_writer = None
        self._table = None
        self._insert_counter = 0

        self._setup_track_table_database(genome, track_name, allow_overlaps, ge_source_manager)

    def _setup_track_table_database(self, genome, track_name, allow_overlaps, ge_source_manager):
        table_describer = TableDescriber(ge_source_manager, self._track_format)
        new_table_description = table_describer.create_new_table_description()

        self._db_writer = DatabaseWriter(self._database_filename)
        self._db_writer.open()
        table_node_names = get_track_table_node_names(genome, track_name, allow_overlaps)

        if self._db_writer.table_exists(table_node_names):
            old_table = self._db_writer.get_table(table_node_names)
            old_table_description = old_table.coldescrs

            assert set(new_table_description.keys()) == set(old_table_description.keys())

            updated_column_descriptions = table_describer.get_updated_column_descriptions(old_table_description,
                                                                                          new_table_description)

            if len(updated_column_descriptions) > 0:  # need to create new table and copy content from old
                new_table_description.update(updated_column_descriptions)
                self._db_writer.close()
                resize_table_columns(self._database_filename, table_node_names,
                                     new_table_description, ge_source_manager.getNumElements())
                self._db_writer.open()
        else:
            self._db_writer.create_table(table_node_names, new_table_description, ge_source_manager.getNumElements())

        self._table = self._db_writer.get_table(table_node_names)

    def _add_ge_dict_as_row(self, ge_dict):
        row = self._table.row
        for column in self._table.colnames:
            if column in ge_dict:
                if column in ['edges', 'weights'] or (column == 'val' and isinstance(row['val'], numpy.ndarray)):
                    if len(ge_dict[column]) > 0:
                        row[column] = self._convert_list_attr_to_array(ge_dict[column], row[column].shape)
                else:
                    row[column] = ge_dict[column]
            else:  # Get extra column
                row[column] = ge_dict['extra'][column]
            self._insert_counter += 1
        row.append()
        flush_table(self._table, self._insert_counter)

    def _convert_list_attr_to_array(self, list, row_field_shape):
        ndarray_col = numpy.asarray(list)
        if ndarray_col.shape == row_field_shape:
            return ndarray_col
        else:
            return insert_into_array_of_larger_shape(ndarray_col, row_field_shape)

    def _add_slice_element_as_chunk(self, chunk):
        self._table.append(chunk)
        self._insert_counter += 1
        flush_table(self._table, self._insert_counter)  # flush for each chuck

    def writeElement(self, genome_element):
        self._add_ge_dict_as_row(genome_element.__dict__)

    def writeRawSlice(self, genome_element):
        if 'val' in self._table.colnames and len(self._table.colnames) == 1:
            self._add_slice_element_as_chunk(genome_element.__dict__['val'])
        else:
            raw_slices = {column: genome_element.__dict__[column] for column in self._table.colnames
                          if column not in ['orderedExtraKeys', 'genome']}

            keys = raw_slices.keys()
            assert self._table.colnames == keys

            for genome_element_dict in [dict(izip(keys, vals)) for vals in izip(*(raw_slices[k] for k in keys))]:
                self._add_ge_dict_as_row(genome_element_dict)

    def close(self):
        self._db_writer.close()
        os.chmod(self._database_filename, S_IRWXU | S_IRWXG | S_IROTH)
