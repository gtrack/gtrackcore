from abc import ABCMeta, abstractmethod

import tables
from tables import ClosedFileError
from gtrackcore.third_party.portalocker import portalocker

from gtrackcore.util.CustomExceptions import DBNotOpenError
from gtrackcore.util.CommonFunctions import getDirPath, getDatabasePath

BOUNDING_REGION_TABLE_NAME = 'bounding_regions'


class DatabaseHandler(object):
    __metaclass__ = ABCMeta

    def __init__(self, track_name, genome, allow_overlaps):
        dir_path = getDirPath(track_name, genome, allowOverlaps=allow_overlaps)
        self._h5_filename = getDatabasePath(dir_path, track_name)
        self._track_name = track_name
        self._h5_file = None
        self._table = None

    @abstractmethod
    def open(self, mode='r', lock_type=portalocker.LOCK_SH):
        self._h5_file = tables.open_file(self._h5_filename, mode=mode, title=self._track_name[-1])
        portalocker.lock(self._h5_file, lock_type)

    def close(self):
        portalocker.unlock(self._h5_file)
        self._h5_file.close()
        self._table = None

    def get_columns(self):
        try:
            return self._table.colinstances
        except ClosedFileError, e:
            raise DBNotOpenError(e)

    def _get_track_table_path(self):
        return '/%s/%s' % ('/'.join(self._track_name), self._track_name[-1])

    def _get_track_table(self):
        try:
            return self._h5_file.get_node(self._get_track_table_path())
        except ClosedFileError, e:
            raise DBNotOpenError(e)

    def _get_track_br_path(self):
        return '/%s/%s' % ('/'.join(self._track_name), BOUNDING_REGION_TABLE_NAME)

    def _get_br_table(self):
        try:
            return self._h5_file.get_node(self._get_track_br_path())
        except ClosedFileError, e:
            raise DBNotOpenError(e)


class TableReader(DatabaseHandler):
    __metaclass__ = ABCMeta

    def __init__(self, track_name, genome, allow_overlaps):
        super(TableReader, self).__init__(track_name, genome, allow_overlaps)

    @abstractmethod
    def open(self):
        super(TableReader, self).open(mode='r', lock_type=portalocker.LOCK_SH)

    @property
    def table(self):
        if self._table is None:
            raise DBNotOpenError
        return self._table


class TrackTableReader(TableReader):
    def __init__(self, track_name, genome, allow_overlaps):
        super(TrackTableReader, self).__init__(track_name, genome, allow_overlaps)

    def get_column(self, column_name):
        try:
            return self._table.colinstances[column_name]
        except ClosedFileError, e:
            raise DBNotOpenError(e)

    def get_column_names(self):
        try:
            return self._table.colnames
        except ClosedFileError, e:
            raise DBNotOpenError(e)

    def open(self):
        super(TrackTableReader, self).open()
        self._table = self._get_track_table()


class BrTableReader(TableReader):
    def __init__(self, track_name, genome, allow_overlaps):
        super(BrTableReader, self).__init__(track_name, genome, allow_overlaps)

    def open(self):
        super(BrTableReader, self).open()
        self._table = self._get_br_table()


class TableReadWriter(DatabaseHandler):
    __metaclass__ = ABCMeta

    def __init__(self, track_name, genome, allow_overlaps):
        super(TableReadWriter, self).__init__(track_name, genome, allow_overlaps)

    @abstractmethod
    def open(self):
        super(TableReadWriter, self).open(mode='r+', lock_type=portalocker.LOCK_EX)


class TrackTableReadWriter(TableReadWriter):
    def __init__(self, track_name, genome, allow_overlaps):
        super(TrackTableReadWriter, self).__init__(track_name, genome, allow_overlaps)

    def open(self):
        super(TrackTableReadWriter, self).open()
        self._table = self._get_track_table()


class BrTableReadWriter(TableReadWriter):
    def __init__(self, track_name, genome, allow_overlaps):
        super(BrTableReadWriter, self).__init__(track_name, genome, allow_overlaps)

    def open(self):
        super(BrTableReadWriter, self).open()
        self._table = self._get_br_table()


class TableCreator(DatabaseHandler):
    __metaclass__ = ABCMeta

    def __init__(self, track_name, genome, allow_overlaps):
        super(TableCreator, self).__init__(track_name, genome, allow_overlaps)

    def create_table(self, table_description, expectedrows, table_name):
        group = self._create_groups()

        try:
            table = self._h5_file.create_table(group, table_name,
                                                        table_description, table_name,
                                                        expectedrows=expectedrows)
        except ClosedFileError, e:
            raise DBNotOpenError(e)

        return table

    @abstractmethod
    def open(self):
        super(TableCreator, self).open(mode='a', lock_type=portalocker.LOCK_EX)

    def get_row(self):
        return self._table.row

    def _create_groups(self):
        group = self._get_track_group()
        if group is None:
            group = self._h5_file.create_group(self._h5_file.root, self._track_name[0], self._track_name[0])

            for track_name_part in self._track_name[1:]:
                group = self._h5_file.create_group(group, track_name_part, track_name_part)

        return group

    def _get_track_group(self):
        try:
            return self._h5_file.get_node(self._get_track_group_path())
        except tables.group.NoSuchNodeError:
            return None

    def _get_track_group_path(self):
        return '/%s' % ('/'.join(self._track_name))


class TrackTableCreator(TableCreator):
    def __init__(self, track_name, genome, allow_overlaps):
        super(TrackTableCreator, self).__init__(track_name, genome, allow_overlaps)
        self._flush_counter = 0

    def create_table(self, table_description, expectedrows):
        self._table = super(TrackTableCreator, self).create_table(
            table_description, expectedrows, self._track_name[-1])
        self._create_indices()

    def open(self):
        super(TrackTableCreator, self).open()

    def flush(self):
        self._flush_counter += 1

        from gtrackcore.util.pytables.DatabaseConstants import FLUSH_LIMIT
        try:
            if self._flush_counter == FLUSH_LIMIT:
                self._table.flush()
                self._flush_counter = 0
        except ClosedFileError, e:
            raise DBNotOpenError(e)

    def _create_indices(self):
        self._table.cols.seqid.create_index()
        if 'start' in self._table.colinstances:
            self._table.cols.start.create_index()
        if 'end' in self._table.colinstances:
            self._table.cols.end.create_index()

class BoundingRegionTableCreator(TableCreator):
    def __init__(self, track_name, genome, allow_overlaps):
        super(BoundingRegionTableCreator, self).__init__(track_name, genome, allow_overlaps)

    def create_table(self, table_description, expectedrows):
        self._table = super(BoundingRegionTableCreator, self).create_table(
            table_description, expectedrows, BOUNDING_REGION_TABLE_NAME)
        self._create_indices()

    def open(self):
        super(BoundingRegionTableCreator, self).open()

    def _create_indices(self):
        self._table.cols.seqid.create_csindex()
