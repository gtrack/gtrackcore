import os
from itertools import izip_longest
from stat import S_IRWXU, S_IRWXG, S_IROTH

import numpy
import tables

from gtrackcore.track.pytables.PytablesDatabase import DatabaseWriter
from gtrackcore.track.pytables.PytablesDatabaseUtils import PytablesDatabaseUtils
from gtrackcore.util.CommonConstants import BINARY_MISSING_VAL
from gtrackcore.util.pytables.CommonNumpyFunctions import insert_into_array_of_larger_shape


class OutputManager(object):
    def __init__(self, genome, track_name, allow_overlaps, ge_source_manager, track_format):
        self._track_format = track_format
        self._database_filename = PytablesDatabaseUtils.get_database_filename(genome, track_name,
                                                                              allow_overlaps=allow_overlaps,
                                                                              create_path=True)
        self._db_writer = None
        self._table = None
        self._insert_counter = 0

        self._create_single_track_database(track_name, allow_overlaps, ge_source_manager)

    def _create_single_track_database(self, track_name, allow_overlaps, ge_source_manager):
        new_table_description = self._create_track_table_description(ge_source_manager)

        self._db_writer = DatabaseWriter(self._database_filename)
        self._db_writer.open()
        table_node_names = PytablesDatabaseUtils.get_track_table_node_names(track_name, allow_overlaps)

        if self._db_writer.table_exists(table_node_names):
            old_table = self._db_writer.get_table(table_node_names)
            old_table_description = old_table.coldescrs

            assert set(new_table_description.keys()) == set(old_table_description.keys())

            if 'val' in new_table_description.keys() or 'edges' in new_table_description.keys():
                self._update_table_description(old_table_description, new_table_description)
        else:
            self._db_writer.create_table(table_node_names, new_table_description, ge_source_manager.getNumElements())

        self._table = self._db_writer.get_table(table_node_names)

    @classmethod
    def _update_table_description(cls, old_table_description, new_table_description):
            new_column_descriptions = cls._get_new_column_descriptions(old_table_description, new_table_description)
            if len(new_column_descriptions) > 0:  # need to create new table and copy content from old
                for column_name, description in new_column_descriptions.iteritems():
                    new_table_description[column_name] = description

    @classmethod
    def _should_use_new_shape(cls, old_shape, new_shape):
        return any([x < y for x, y in izip_longest(old_shape, new_shape)])

    @classmethod
    def _get_new_column_descriptions(cls, old_table_description, new_table_description):
        new_descriptions = {}

        for column_name in ('val', 'edges', 'weights'):
            if column_name in old_table_description:
                old_val_shape = old_table_description[column_name].shape
                new_val_shape = new_table_description[column_name].shape
                result_val_shape = tuple([max(x, y) for x, y in izip_longest(old_val_shape, new_val_shape)])

                if cls._should_use_new_shape(old_val_shape, result_val_shape):
                    dtype = old_table_description[column_name].type
                    if dtype == 'string':
                        new_descriptions[column_name] = tables.StringCol(old_table_description[column_name].itemsize,
                                                                         shape=result_val_shape)
                    else:
                        new_descriptions[column_name] = tables.Col.from_type(dtype, shape=result_val_shape)

        return new_descriptions

    def _create_track_table_description(self, ge_source_manager):
        max_string_lengths = self._get_max_str_lens_over_all_chromosomes(ge_source_manager)
        max_num_edges = self._get_max_num_edges_over_all_chromosomes(ge_source_manager)
        max_chr_len = ge_source_manager.getMaxChrStrLen()

        data_type_dict = {}
        if not self._track_format.reprIsDense():
            data_type_dict['chr'] = tables.StringCol(max_chr_len)

        for column in ge_source_manager.getPrefixList():
            if column in ['start', 'end']:
                data_type_dict[column] = tables.Int32Col()
            elif column == 'strand':
                data_type_dict[column] = tables.Int8Col()
            elif column == 'id':
                data_type_dict[column] = tables.StringCol(max_string_lengths[column])
            elif column == 'edges':
                shape = self._get_shape(max_num_edges, 1)
                data_type_dict[column] = tables.StringCol(max_string_lengths[column], shape=shape)
            elif column in ['val', 'weights']:
                if column == 'val':
                    data_type = ge_source_manager.getValDataType()
                    val_dim = ge_source_manager.getValDim()
                    shape = val_dim if val_dim > 1 else tuple()
                elif column == 'weights':
                    data_type = ge_source_manager.getEdgeWeightDataType()
                    data_type_dim = ge_source_manager.getEdgeWeightDim()
                    shape = self._get_shape(max_num_edges, data_type_dim)

                data_type = 'S' if data_type.startswith('S') else data_type

                data_type_dict[column] = {
                    'int8': tables.Int8Col(shape=shape, dflt=BINARY_MISSING_VAL),
                    'int32': tables.Int32Col(shape=shape, dflt=BINARY_MISSING_VAL),
                    'float32': tables.Float32Col(shape=shape, dflt=numpy.nan),
                    'float64': tables.Float64Col(shape=shape, dflt=numpy.nan),
                    'float128': tables.Float128Col(shape=shape, dflt=numpy.nan),
                    'S': tables.StringCol(max(1, max_string_lengths[column]), shape=shape, dflt='')
                }.get(data_type, tables.Float64Col(shape=shape, dflt=numpy.nan))  # Defaults to Float64Col
            else:
                data_type_dict[column] = tables.StringCol(max(2, max_string_lengths[column]), dflt='')

        return data_type_dict

    @staticmethod
    def _get_shape(max_num_edges, data_type_dim):
        return tuple([max(1, max_num_edges)] + ([data_type_dim] if data_type_dim > 1 else []))

    @staticmethod
    def _get_max_str_lens_over_all_chromosomes(ge_source_manager):
        max_str_lens_dictionaries = [ge_source_manager.getMaxStrLensForChr(chr)
                                     for chr in ge_source_manager.getAllChrs()]
        from collections import Counter
        from operator import or_

        max_string_lengths = reduce(or_, map(Counter, max_str_lens_dictionaries))
        return max_string_lengths

    @staticmethod
    def _get_max_num_edges_over_all_chromosomes(ge_source_manager):
        return max(ge_source_manager.getMaxNumEdgesForChr(chr) for chr in ge_source_manager.getAllChrs())

    #Todo: refactor...
    def _add_element_as_row(self, genome_element):
        row = self._table.row
        for column in self._table.colnames:
            if column in genome_element.__dict__ and column != 'extra':
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
        PytablesDatabaseUtils.flush(self._table, self._insert_counter)

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
            PytablesDatabaseUtils.flush(self._table, self._insert_counter)

    def writeElement(self, genome_element):
        self._add_element_as_row(genome_element)

    def writeRawSlice(self, genome_element):
        """What's the purpose of this?"""
        self._add_slice_element_as_rows(genome_element)

    def close(self):
        self._db_writer.close()
        os.chmod(self._database_filename, S_IRWXU | S_IRWXG | S_IROTH)
