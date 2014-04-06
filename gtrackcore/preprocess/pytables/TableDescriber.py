from itertools import izip_longest

import tables

from gtrackcore.util.CommonConstants import RESERVED_PREFIXES
from gtrackcore.util.pytables.NumpyFunctions import get_default_numpy_value


class TableDescriber(object):

    def __init__(self, ge_source_manager, track_format):
        self._ge_source_manager = ge_source_manager
        self._track_format = track_format

    def create_new_table_description(self):
        max_string_lengths = self._get_max_str_lens_over_all_chromosomes()
        max_num_edges = self._get_max_num_edges_over_all_chromosomes()
        max_chr_len = self._ge_source_manager.getMaxChrStrLen()

        data_type_dict = {}
        if not self._track_format.reprIsDense():
            data_type_dict['chr'] = tables.StringCol(max_chr_len)

        for column in self._ge_source_manager.getPrefixList():
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
                    data_type = self._ge_source_manager.getValDataType()
                    val_dim = self._ge_source_manager.getValDim()
                    shape = val_dim if val_dim > 1 else tuple()
                elif column == 'weights':
                    data_type = self._ge_source_manager.getEdgeWeightDataType()
                    data_type_dim = self._ge_source_manager.getEdgeWeightDim()
                    shape = self._get_shape(max_num_edges, data_type_dim)

                data_type = 'S' if data_type.startswith('S') else data_type

                data_type_dict[column] = {
                    'int8': tables.Int8Col(shape=shape, dflt=get_default_numpy_value('int')),
                    'int32': tables.Int32Col(shape=shape, dflt=get_default_numpy_value('int')),
                    'float32': tables.Float32Col(shape=shape, dflt=get_default_numpy_value('float')),
                    'float64': tables.Float64Col(shape=shape, dflt=get_default_numpy_value('float')),
                    'float128': tables.Float128Col(shape=shape, dflt=get_default_numpy_value('float')),
                    'S': tables.StringCol(max(1, max_string_lengths[column]), shape=shape, dflt=get_default_numpy_value('str'))
                }.get(data_type, tables.Float64Col(shape=shape, dflt=get_default_numpy_value('float')))  # Defaults to Float64Col
            else:
                data_type_dict[column] = tables.StringCol(max(2, max_string_lengths[column]), dflt=get_default_numpy_value('str'))

        return data_type_dict

    def get_updated_column_descriptions(self, old_table_description, new_table_description):
        new_column_descriptions = {}
        columns = [extra_col_names for extra_col_names in new_table_description if extra_col_names not in RESERVED_PREFIXES] + \
                  [column_name for column_name in ('id', 'val', 'edges', 'weights') if column_name in new_table_description]

        if len(columns) > 0:
            new_column_descriptions = self._get_new_column_descriptions(old_table_description,
                                                                        new_table_description,
                                                                        columns)
        return new_column_descriptions

    def _get_max_str_lens_over_all_chromosomes(self):
        max_str_lens_dictionaries = [self._ge_source_manager.getMaxStrLensForChr(chr)
                                     for chr in self._ge_source_manager.getAllChrs()]
        from collections import Counter
        from operator import or_

        max_string_lengths = reduce(or_, map(Counter, max_str_lens_dictionaries))
        return max_string_lengths

    def _get_max_num_edges_over_all_chromosomes(self):
        return max(self._ge_source_manager.getMaxNumEdgesForChr(chr) for chr in self._ge_source_manager.getAllChrs())

    @classmethod
    def _get_shape(cls, max_num_edges, data_type_dim):
        return tuple([max(1, max_num_edges)] + ([data_type_dim] if data_type_dim > 1 else []))

    @classmethod
    def _get_new_column_descriptions(cls, old_table_description, new_table_description, columns):
        new_descriptions = {}

        itemsize = None
        shape = None
        for column_name in columns:
            assert column_name in new_table_description
            old_column_description = old_table_description[column_name]
            new_column_description = new_table_description[column_name]
            dtype = old_table_description[column_name].type

            if column_name in ('val', 'edges', 'weights'):
                shape = cls._get_new_shape(old_column_description, new_column_description)
            if dtype == 'string':
                itemsize = cls._get_new_itemsize(old_column_description, new_column_description)

            if itemsize is not None or shape is not None:
                new_descriptions[column_name] = cls._get_new_column_description(old_column_description, itemsize, shape)

            itemsize = None
            shape = None

        return new_descriptions

    @classmethod
    def _get_new_column_description(cls, old_column_description, itemsize, shape):
        assert itemsize is not None or shape is not None

        dtype = old_column_description.type
        if itemsize is not None:
            if shape is not None:
                return tables.StringCol(itemsize, shape=shape)
            else:
                if old_column_description.shape == ():
                    return tables.StringCol(itemsize)
                else:
                    return tables.StringCol(itemsize, shape=old_column_description.shape)
        elif shape is not None:
            if dtype == 'string':
                return tables.StringCol(old_column_description.itemsize, shape=shape)
            else:
                return tables.Col.from_type(dtype, shape=shape, dflt=old_column_description.dflt)

    @classmethod
    def _get_new_itemsize(cls, old_column_description, new_column_description):
        old_itemsize = old_column_description.itemsize
        new_itemsize = new_column_description.itemsize

        if new_itemsize > old_itemsize:
            return new_itemsize

        return None

    @classmethod
    def _get_new_shape(cls, old_column_description, new_column_description):
        old_val_shape = old_column_description.shape
        new_val_shape = new_column_description.shape
        result_val_shape = tuple([max(x, y) for x, y in izip_longest(old_val_shape, new_val_shape)])

        if cls._should_use_new_shape(old_val_shape, result_val_shape):
            return result_val_shape

        return None

    @classmethod
    def _should_use_new_shape(cls, old_shape, new_shape):
        return any([x < y for x, y in izip_longest(old_shape, new_shape)])