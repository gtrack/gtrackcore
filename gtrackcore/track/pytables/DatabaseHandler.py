from abc import ABCMeta, abstractmethod
import re
import numpy

import tables
from tables import ClosedFileError
from tables.exceptions import NodeError

from gtrackcore.third_party.portalocker import portalocker
from gtrackcore.util.CustomExceptions import DBNotOpenError, DBNotExistError
from gtrackcore.util.CommonFunctions import get_dir_path, getDatabasePath
from gtrackcore.util.pytables.DatabaseConstants import FLUSH_LIMIT
from gtrackcore.util.pytables.CommonNumpyFunctions import insert_into_array_of_larger_shape


BOUNDING_REGION_TABLE_NAME = 'bounding_regions'


class DatabaseHandler(object):
    __metaclass__ = ABCMeta

    def __init__(self, genome, track_name, allow_overlaps):
        dir_path = get_dir_path(genome, track_name, allow_overlaps=allow_overlaps)
        self._h5_filename = getDatabasePath(dir_path, track_name)
        self._track_name = self._convert_track_name_to_pytables_format(track_name)
        self._h5_file = None
        self._table = None

    def _convert_track_name_to_pytables_format(self, track_name):
        return [re.sub(r'\W*', '', re.sub(r'(\s|-)+', '_', part)).lower() for part in track_name]

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @abstractmethod
    def open(self, mode='r', lock_type=portalocker.LOCK_SH):
        try:
            self._h5_file = tables.open_file(self._h5_filename, mode=mode, title=self._track_name[-1])
            portalocker.lock(self._h5_file, lock_type)
        except IOError, e:
            raise DBNotExistError(e)

    def close(self):
        portalocker.unlock(self._h5_file)
        self._h5_file.close()
        self._table = None

    def get_columns(self):
        try:
            return self._table.colinstances
        except ClosedFileError, e:
            raise DBNotOpenError(e)

    def table_exists(self, table_path):
        try:
            self._h5_file.get_node(table_path)
            table_exists = True
        except tables.group.NoSuchNodeError:
            table_exists = False

        return table_exists

    @property
    def table(self):
        if self._table is None:
            raise DBNotOpenError
        return self._table

    def number_of_rows(self):
        try:
            return self._table.nrows
        except ClosedFileError, e:
            raise DBNotOpenError(e)

    def get_column_names(self):
        try:
            return self._table.colnames
        except ClosedFileError, e:
            raise DBNotOpenError(e)


    def _get_track_table_path(self):
        return '/%s/%s' % ('/'.join(self._track_name), self._track_name[-1])

    def _get_track_table(self):
        try:
            return self._h5_file.get_node(self._get_track_table_path())
        except ClosedFileError, e:
            raise DBNotOpenError(e)

    def _get_br_table_path(self):
        return '/%s/%s' % ('/'.join(self._track_name), BOUNDING_REGION_TABLE_NAME)

    def _get_br_table(self):
        try:
            return self._h5_file.get_node(self._get_br_table_path())
        except ClosedFileError, e:
            raise DBNotOpenError(e)


class TableReader(DatabaseHandler):
    __metaclass__ = ABCMeta

    def __init__(self, genome, track_name, allow_overlaps):
        super(TableReader, self).__init__(genome, track_name, allow_overlaps)

    @abstractmethod
    def open(self):
        super(TableReader, self).open(mode='r', lock_type=portalocker.LOCK_SH)


class TrackTableReader(TableReader):
    def __init__(self, genome, track_name, allow_overlaps):
        super(TrackTableReader, self).__init__(genome, track_name, allow_overlaps)

    def get_column(self, column_name):
        try:
            return self._table.colinstances[column_name]
        except ClosedFileError, e:
            raise DBNotOpenError(e)

    def open(self):
        super(TrackTableReader, self).open()
        self._table = self._get_track_table()

    def table_exists(self):
        return super(TrackTableReader, self).table_exists(self._get_track_table_path())


class BrTableReader(TableReader):
    def __init__(self, genome, track_name, allow_overlaps):
        super(BrTableReader, self).__init__(genome, track_name, allow_overlaps)

    def open(self):
        super(BrTableReader, self).open()
        self._table = self._get_br_table()

    def table_exists(self):
        return super(BrTableReader, self).table_exists(self._get_br_table_path())

class TableReadWriter(DatabaseHandler):
    __metaclass__ = ABCMeta

    def __init__(self, genome, track_name, allow_overlaps):
        super(TableReadWriter, self).__init__(genome, track_name, allow_overlaps)

    @abstractmethod
    def open(self):
        super(TableReadWriter, self).open(mode='r+', lock_type=portalocker.LOCK_EX)


class TrackTableReadWriter(TableReadWriter):
    def __init__(self, genome, track_name, allow_overlaps):
        super(TrackTableReadWriter, self).__init__(genome, track_name, allow_overlaps)

    def open(self):
        super(TrackTableReadWriter, self).open()
        self._table = self._get_track_table()

    def table_exists(self):
        return super(TrackTableReader, self).table_exists(self._get_track_table_path())


class BrTableReadWriter(TableReadWriter):
    def __init__(self, genome, track_name, allow_overlaps):
        super(BrTableReadWriter, self).__init__(genome, track_name, allow_overlaps)

    def open(self):
        super(BrTableReadWriter, self).open()
        self._table = self._get_br_table()

    def table_exists(self):
        return super(BrTableReadWriter, self).table_exists(self._get_br_table_path())


class TableCreator(DatabaseHandler):
    __metaclass__ = ABCMeta

    def __init__(self, genome, track_name, allow_overlaps):
        super(TableCreator, self).__init__(genome, track_name, allow_overlaps)

    def create_table(self, table_description, expectedrows, table_name):
        group = self._create_groups()

        try:
            table = self._h5_file.create_table(group, table_name,
                                               table_description, table_name,
                                               expectedrows=expectedrows)
        except ClosedFileError, e:
            raise DBNotOpenError(e)
        except NodeError:
            return None

        return table

    @abstractmethod
    def open(self):
        super(TableCreator, self).open(mode='a', lock_type=portalocker.LOCK_EX)
        self._flush_counter = 0

    def flush(self, table):
        self._flush_counter += 1

        if self._flush_counter == FLUSH_LIMIT:
            try:
                table.flush()
                self._flush_counter = 0
            except ClosedFileError, e:
                raise DBNotOpenError(e)

    def get_row(self):
        return self._table.row

    def _create_indices(self):
        if 'chr' in self._table.colinstances:
            self._table.cols.chr.create_index()
        if 'start' in self._table.colinstances:
            self._table.cols.start.create_index()
        if 'end' in self._table.colinstances:
            self._table.cols.end.create_index()

    def _create_groups(self):
        group = self._get_track_group()
        if group is None:
            group = self._h5_file.create_group(self._h5_file.root, self._track_name[0], self._track_name[0])

            for track_name_part in self._track_name[1:]:
                group = self._h5_file.create_group(group, track_name_part, track_name_part)

        return group

    def remove_table(self, table_name):
        group = self._get_track_group()
        self._h5_file.remove_node(group, table_name)

    def _get_track_group(self):
        try:
            return self._h5_file.get_node(self._get_track_group_path())
        except tables.group.NoSuchNodeError:
            return None

    def _get_track_group_path(self):
        return '/%s' % ('/'.join(self._track_name))


class TrackTableCreator(TableCreator):
    def __init__(self, genome, track_name, allow_overlaps):
        super(TrackTableCreator, self).__init__(genome, track_name, allow_overlaps)

    def create_table(self, table_description, expectedrows):
        self._table = super(TrackTableCreator, self).create_table(
            table_description, expectedrows, self._track_name[-1])

        #Get existing table
        if self._table is None:
            self._table = self._get_track_table()
        else:
            self._create_indices()

    def open(self):
        super(TrackTableCreator, self).open()

    def table_exists(self):
        return super(TrackTableCreator, self).table_exists(self._get_track_table_path())

    def flush(self):
        super(TrackTableCreator, self).flush(self._table)

class TrackTableCopier(TableCreator):
    def __init__(self, genome, track_name, allow_overlaps):
        super(TrackTableCopier, self).__init__(genome, track_name, allow_overlaps)
        self._old_table = None

    def open(self):
        super(TrackTableCopier, self).open()
        self._old_table = self._get_track_table()

    def create_table(self, table_description, expectedrows):
        self._old_table.rename(self._old_table.name + '_tmp')

        self._table = super(TrackTableCopier, self).create_table(
            table_description, expectedrows + self._old_table.nrows, self._track_name[-1])
        self._create_indices()

        self._copy_content_from_old_to_new_table()

        self.remove_table(self._old_table.name)
        self._old_table = None

    def _copy_content_from_old_to_new_table(self):
        new_row = self._table.row
        for old_row in self._old_table.iterrows():
            for column_name in self.get_column_names():
                if isinstance(old_row[column_name], numpy.ndarray):
                    new_row[column_name] = insert_into_array_of_larger_shape(old_row[column_name],
                                                                             new_row[column_name].shape)
                else:
                    new_row[column_name] = old_row[column_name]
            new_row.append()
            self.flush()

    def flush(self):
        super(TrackTableCopier, self).flush(self._table)


class TrackTableSorter(TableCreator):
    def __init__(self, genome, track_name, allow_overlaps):
        super(TrackTableSorter, self).__init__(genome, track_name, allow_overlaps)
        self._old_table = None

    def open(self):
        super(TrackTableSorter, self).open()
        self._table = self._get_track_table()
        self._old_table = self._table

    def sort_table(self, sort_order):
        table_description = self._old_table.coldescrs
        if 'chr' in table_description:
            del table_description['chr']

        self._old_table.rename(self._old_table.name + '_tmp')

        self._table = super(TrackTableSorter, self).create_table(
            table_description, self._old_table.nrows, self._track_name[-1])
        self._create_indices()

        self._copy_content_from_old_to_new_table_in_sorted_order(sort_order, table_description)

        self.remove_table(self._old_table.name)
        self._old_table = None

    def _copy_content_from_old_to_new_table_in_sorted_order(self, sort_order, table_description):
        new_row = self._table.row
        for old_row in self._old_table.itersequence(sort_order):
            for col in table_description:
                new_row[col] = old_row[col]
            new_row.append()
            self.flush(self._table)


class BoundingRegionTableCreator(TableCreator):
    def __init__(self, genome, track_name, allow_overlaps):
        super(BoundingRegionTableCreator, self).__init__(genome, track_name, allow_overlaps)

    def create_table(self, table_description, expectedrows):
        self._table = super(BoundingRegionTableCreator, self).create_table(
            table_description, expectedrows, BOUNDING_REGION_TABLE_NAME)

        if self._table is None:
            self._table = self._get_br_table()
        else:
            self._create_indices()

    def open(self):
        super(BoundingRegionTableCreator, self).open()

    def table_exists(self):
        return super(BoundingRegionTableCreator, self).table_exists(self._get_br_table_path())

    def _create_indices(self):
        self._table.cols.chr.create_csindex()
