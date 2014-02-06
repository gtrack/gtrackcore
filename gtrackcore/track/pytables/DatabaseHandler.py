from abc import ABCMeta, abstractmethod

import tables
from tables import ClosedFileError

from gtrackcore.util.CustomExceptions import DBNotOpenError
from gtrackcore.util.CommonFunctions import getDirPath, getDatabaseFilename

BOUNDING_REGION_TABLE_NAME = 'bounding_regions'

class DatabaseHandler(object):
    __metaclass__ = ABCMeta

    def __init__(self, track_name, genome, allow_overlaps):
        dir_path = getDirPath(track_name, genome, allowOverlaps=allow_overlaps)
        self._h5_filename = getDatabaseFilename(dir_path, track_name)
        self._track_name = track_name
        self._h5_file = None
        self._track_table = None
        self._br_table = None

    @abstractmethod
    def open(self, mode='r'):
        self._h5_file = tables.open_file(self._h5_filename, mode=mode, title=self._track_name[-1])

    def close(self):
        self._h5_file.close()
        self._track_table = None
        self._br_table = None

    def get_columns(self):
        try:
            return self._track_table.colinstances
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
    def __init__(self, track_name, genome, allow_overlaps):
        super(TableReader, self).__init__(track_name, genome, allow_overlaps)

        def open(self):
            super(TrackTableReader, self).open('r')


class TrackTableReader(TableReader):

    def __init__(self, track_name, genome, allow_overlaps):
        super(TrackTableReader, self).__init__(track_name, genome, allow_overlaps)

    def get_column(self, column_name):
        try:
            return self._track_table.colinstances[column_name]
        except ClosedFileError, e:
            raise DBNotOpenError(e)

    def get_column_names(self):
        try:
            return self._track_table.colnames
        except ClosedFileError, e:
            raise DBNotOpenError(e)

    def open(self):
        super(TrackTableReader, self).open()
        self._track_table = self._get_track_table()

    @property
    def track_table(self):
        if self._track_table is None:
            raise DBNotOpenError
        return self._track_table

class BrTableReader(TableReader):

    def __init__(self, track_name, genome, allow_overlaps):
        super(BrTableReader, self).__init__(track_name, genome, allow_overlaps)

    def open(self):
        super(BrTableReader, self).open()
        self._br_table = self._get_br_table()

    @property
    def br_table(self):
        if self._br_table is None:
            raise DBNotOpenError
        return self._br_table

class TrackTableReadWriter(DatabaseHandler):

    def __init__(self, track_name, genome, allow_overlaps):
        super(TrackTableReadWriter, self).__init__(track_name, genome, allow_overlaps)

    def open(self):
        super(TrackTableReadWriter, self).open('r+')
        self._track_table = self._get_track_table()

class TableCreator(DatabaseHandler):
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

    def open(self):
        super(TableCreator, self).open('w')

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
        self._track_table = super(TrackTableCreator, self).create_table(
            table_description, expectedrows, self._track_name[-1])
        self._create_indices()

    def get_row(self):
        return self._track_table.row

    def open(self):
        super(TrackTableCreator, self).open()

    def flush(self):
        self._flush_counter += 1

        from gtrackcore.util.pytables.DatabaseConstants import FLUSH_LIMIT
        try:
            if self._flush_counter == FLUSH_LIMIT:
                self._track_table.flush()
                self._flush_counter = 0
        except ClosedFileError, e:
            raise DBNotOpenError(e)

    def _create_groups(self):
        group = self._h5_file.create_group(self._h5_file.root, self._track_name[0], self._track_name[0])

        for track_name_part in self._track_name[1:]:
            group = self._h5_file.create_group(group, track_name_part, track_name_part)

        return group

    def _create_indices(self):
        self._track_table.cols.start.create_index()
        self._track_table.cols.end.create_index()


class BoundingRegionTableCreator(TableCreator):

    def __init__(self, track_name, genome, allow_overlaps):
        super(BoundingRegionTableCreator, self).__init__(track_name, genome, allow_overlaps)

    def create_table(self, table_description, expectedrows):
        self._br_table = super(BoundingRegionTableCreator, self).create_table(
            table_description, expectedrows, BOUNDING_REGION_TABLE_NAME)
        self._create_indices()

    def get_row(self):
        return self._br_table.row

    def open(self):
        super(BoundingRegionTableCreator, self).open()

    def _create_indices(self):
        pass
