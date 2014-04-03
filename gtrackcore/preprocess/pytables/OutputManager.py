import os
from stat import S_IRWXU, S_IRWXG, S_IROTH

import numpy

from gtrackcore.preprocess.pytables.TableDescriber import TableDescriber
from gtrackcore.track.pytables.database.Database import DatabaseWriter
from gtrackcore.track.pytables.database.DatabaseUtils import DatabaseUtils
from gtrackcore.util.pytables.CommonNumpyFunctions import insert_into_array_of_larger_shape


class OutputManager(object):
    def __init__(self, genome, track_name, allow_overlaps, ge_source_manager, track_format):
        self._track_format = track_format
        self._database_filename = DatabaseUtils.get_database_filename(genome, track_name,
                                                                      allow_overlaps=allow_overlaps, create_path=True)
        self._db_writer = None
        self._table = None
        self._insert_counter = 0

        self._create_track_table_database(genome, track_name, allow_overlaps, ge_source_manager)

    def _create_track_table_database(self, genome, track_name, allow_overlaps, ge_source_manager):
        table_describer = TableDescriber(ge_source_manager, self._track_format)
        new_table_description = table_describer.create_new_table_description()

        self._db_writer = DatabaseWriter(self._database_filename)
        self._db_writer.open()
        table_node_names = DatabaseUtils.get_track_table_node_names(genome, track_name, allow_overlaps)

        if self._db_writer.table_exists(table_node_names):
            old_table = self._db_writer.get_table(table_node_names)
            old_table_description = old_table.coldescrs

            assert set(new_table_description.keys()) == set(old_table_description.keys())
            
            updated_column_descriptions = table_describer.get_updated_column_descriptions(old_table_description, new_table_description)

            if len(updated_column_descriptions) > 0:  # need to create new table and copy content from old
                new_table_description.update(updated_column_descriptions)
                self._db_writer.close()
                DatabaseUtils.resize_table_columns(self._database_filename, table_node_names,
                                                   updated_column_descriptions, ge_source_manager.getNumElements())
                self._db_writer.open()
        else:
            self._db_writer.create_table(table_node_names, new_table_description, ge_source_manager.getNumElements())

        self._table = self._db_writer.get_table(table_node_names)

    #Todo: refactor...
    def _add_element_as_row(self, genome_element):
        row = self._table.row
        for column in self._table.colnames:
            if column in genome_element.__dict__:
                if column in ['edges', 'weights']:
                    ge_len = sum(1 for _ in genome_element.__dict__[column])
                    if ge_len >= 1:
                        row[column] = numpy.array(genome_element.__dict__[column] + list(row[column][ge_len:]))
                elif column == 'val' and isinstance(row['val'], numpy.ndarray):
                    new_val = genome_element.__dict__['val']
                    if isinstance(new_val, list) or isinstance(new_val, tuple):
                        new_val = numpy.array(new_val)
                    row['val'] = insert_into_array_of_larger_shape(new_val, row['val'].shape)
                else:
                    row[column] = genome_element.__dict__[column]
            else:  # Get extra column
                row[column] = genome_element.__dict__['extra'][column]
            self._insert_counter += 1
        row.append()
        DatabaseUtils.flush(self._table, self._insert_counter)

    def _add_slice_element_as_rows(self, genome_element):

        slice_dict = {key: val for key, val in genome_element.__dict__.iteritems()
                      if ((isinstance(val, numpy.ndarray) and val.any()) or val)
                      and key not in ['extra', 'orderedExtraKeys', 'genome']}

        slice_dict.update(genome_element.__dict__['extra'])
        keys = slice_dict.keys()

        assert self._table.colnames == keys

        ge_dicts = [dict(zip(keys, vals)) for vals in zip(*(slice_dict[k] for k in keys))]

        for el in ge_dicts:
            row = self._table.row
            for key in keys:
                row[key] = el[key]
            row.append()
            self._insert_counter += 1
            DatabaseUtils.flush(self._table, self._insert_counter)

    def writeElement(self, genome_element):
        self._add_element_as_row(genome_element)

    def writeRawSlice(self, genome_element):
        """What's the purpose of this?"""
        self._add_slice_element_as_rows(genome_element)

    def close(self):
        self._db_writer.close()
        os.chmod(self._database_filename, S_IRWXU | S_IRWXG | S_IROTH)
