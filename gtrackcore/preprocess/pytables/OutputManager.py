import numpy
import tables
import os

from itertools import izip_longest, izip
from stat import S_IRWXU, S_IRWXG, S_IROTH

from gtrackcore.core.LogSetup import logMessage
from gtrackcore.util.CommonFunctions import get_dir_path, getDatabasePath
from gtrackcore.track.pytables.DatabaseHandler import TrackTableCreator, TrackTableReader, TrackTableCopier
from gtrackcore.util.CustomExceptions import DBNotExistError


class OutputManager(object):
    def __init__(self, genome, track_name, allow_overlaps, ge_source_manager):
        dir_path = get_dir_path(genome, track_name, allow_overlaps=allow_overlaps)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        self._database_filename = getDatabasePath(dir_path, track_name)

        self._create_single_track_database(genome, track_name, allow_overlaps, ge_source_manager)

    def _create_single_track_database(self, genome, track_name, allow_overlaps, ge_source_manager):
        table_exists, current_table_description = self._extract_table_info(genome, track_name, allow_overlaps)
        self._table_description = self._create_track_table_description(ge_source_manager)

        self._table_creator = None
        if table_exists:
            if 'val' in self._table_description.keys() or 'edges' in self._table_description.keys():
                assert set(self._table_description.keys()) == set(current_table_description.keys())  # new and old has same attributes

                shape_dict = self._should_create_new_table(current_table_description, self._table_description)
                if len(shape_dict) > 0:  # need to create new table and copy content from old
                    for column_name, shape in shape_dict.iteritems():
                        self._table_description[column_name].shape = shape

                    self._table_creator = TrackTableCopier(genome, track_name, allow_overlaps)

        if self._table_creator is None:
            self._table_creator = TrackTableCreator(genome, track_name, allow_overlaps)

        self._table_creator.open()
        self._table_creator.create_table(self._table_description,
                                                      expectedrows=ge_source_manager.getNumElements())

    def _extract_table_info(self, genome, track_name, allow_overlaps):
        table_info_reader = TrackTableReader(genome, track_name, allow_overlaps)
        table_description = None
        try:
            table_info_reader.open()
            table_exists = table_info_reader.table_exists()
            if table_exists:
                table_description = table_info_reader.table.coldescrs
            table_info_reader.close()
        except DBNotExistError, e:
            table_exists = False

        return table_exists, table_description

    def _should_create_new_table(self, old_table_description, new_table_description):
        def should_use_new_shape(old_shape, new_shape):
            return not all([x > y for x, y in izip_longest(old_shape, new_shape)])

        shape_dict = {}

        for column_name in ('val', 'edges', 'weights'):
            if column_name in old_table_description:
                old_val_shape = old_table_description[column_name].shape
                new_val_shape = new_table_description[column_name].shape
                result_val_shape = tuple([max(x, y) for x, y in izip_longest(old_val_shape, new_val_shape)])

                if should_use_new_shape(old_val_shape, result_val_shape):
                    shape_dict[column_name] = result_val_shape

        return shape_dict

    def _create_track_table_description(self, ge_source_manager):
        max_string_lengths = self._get_max_str_lens_over_all_chromosomes(ge_source_manager)
        max_num_edges = self._get_max_num_edges_over_all_chromosomes(ge_source_manager)
        max_chr_len = ge_source_manager.getMaxChrStrLen()

        data_type_dict = {}
        if not ge_source_manager.isSorted():
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
                    'int8': tables.Int8Col(shape=shape),
                    'int32': tables.Int32Col(shape=shape),
                    'float32': tables.Float32Col(shape=shape),
                    'float64': tables.Float64Col(shape=shape),
                    'float128': tables.Float128Col(shape=shape),
                    'S': tables.StringCol(max(1, max_string_lengths[column]), shape=shape)
                }.get(data_type, tables.Float64Col(shape=shape))  # Defaults to Float64Col
            else:
                data_type_dict[column] = tables.StringCol(max(2, max_string_lengths[column]))

        return data_type_dict

    def _get_shape(self, max_num_edges, data_type_dim):
        return tuple([max(1, max_num_edges)] + ([data_type_dim] if data_type_dim > 1 else []))

    def _get_max_str_lens_over_all_chromosomes(self, ge_source_manager):
        max_str_lens_dictionaries = [ge_source_manager.getMaxStrLensForChr(chr)
                                     for chr in ge_source_manager.getAllChrs()]
        from collections import Counter
        from operator import or_

        max_string_lengths = reduce(or_, map(Counter, max_str_lens_dictionaries))
        return max_string_lengths

    # bytt med den som finnes i ge_source_manager
    def _get_max_num_edges_over_all_chromosomes(self, ge_source_manager):
        return max(ge_source_manager.getMaxNumEdgesForChr(chr) for chr in ge_source_manager.getAllChrs())

    #Todo: refactor...
    def _add_element_as_row(self, genome_element):
        row = self._table_creator.get_row()
        for column in self._table_description:
            if column in genome_element.__dict__ and column != 'extra':
                if column in ['edges', 'weights']:
                    ge_len = sum(1 for x in genome_element.__dict__[column])
                    if ge_len >= 1:
                        row[column] = numpy.array(genome_element.__dict__[column] + list(row[column][ge_len:]))
                else:
                    row[column] = genome_element.__dict__[column]

            else:  # Get extra column
                row[column] = genome_element.__dict__['extra'][column]
        row.append()
        self._table_creator.flush()

    def _add_slice_element_as_rows(self, genome_element):

        slice_dict = {key: val for key, val in genome_element.__dict__.iteritems()
                      if ((isinstance(val, numpy.ndarray) and val.any()) or val)
                      and key not in ['extra', 'orderedExtraKeys', 'genome']}

        slice_dict.update(genome_element.__dict__['extra'])
        keys = slice_dict.keys()

        assert self._table_description.keys() == keys

        ge_dicts = [dict(zip(keys, vals)) for vals in zip(*(slice_dict[k] for k in keys))]

        for el in ge_dicts:
            row = self._table_creator.get_row()
            for key in keys:
                row[key] = el[key]
            row.append()
            self._table_creator.flush()

    def writeElement(self, genome_element):
        self._add_element_as_row(genome_element)

    def writeRawSlice(self, genome_element):
        """What's the purpose of this?"""
        self._add_slice_element_as_rows(genome_element)


    def close(self):
        self._table_creator.close()
        os.chmod(self._database_filename, S_IRWXU | S_IRWXG | S_IROTH)
