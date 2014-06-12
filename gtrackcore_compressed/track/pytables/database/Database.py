from abc import abstractmethod, ABCMeta
import os

import tables
from tables.exceptions import ClosedFileError, NodeError

import gtrackcore_compressed.preprocess
from gtrackcore_compressed.third_party.portalocker import portalocker
from gtrackcore_compressed.util.CustomExceptions import DBNotOpenError, DBNotExistError
from gtrackcore_compressed.util.pytables.Constants import GTRACKCORE_FORMAT_SUFFIX
from gtrackcore_compressed.util.pytables.NameFunctions import get_node_path


FILTERS = tables.Filters(complib='blosc', complevel=5)


class Database(object):
    __metaclass__ = ABCMeta

    def __init__(self, h5_filename):
        self._h5_filename = h5_filename
        self._db_name = h5_filename.split(os.sep)[-1][:-len(GTRACKCORE_FORMAT_SUFFIX)]
        self._h5_file = None
        self._cached_nodes = {}

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def h5_file(self):
        return self._h5_file

    @abstractmethod
    def open(self, mode='r', lock_type=portalocker.LOCK_SH):
        try:
            self._h5_file = tables.open_file(self._h5_filename, mode=mode, filters=FILTERS)
        except IOError, e:
            raise DBNotExistError(e)
        portalocker.lock(self._h5_file, lock_type)

    def close(self):
        self._cached_nodes = {}
        self._h5_file.close()

    def table_exists(self, node_names):
        table_path = get_node_path(node_names)
        try:
            self._h5_file.get_node(table_path)
            return True
        except tables.group.NoSuchNodeError:
            return False

    def get_table(self, node_names):
        return self.get_node(node_names)

    def get_node(self, node_names):
        node_path = get_node_path(node_names)
        if node_path in self._cached_nodes:
            return self._cached_nodes[node_path]
        try:
            node = self._h5_file.get_node(node_path)
            self._cached_nodes[node_path] = node
            return node
        except tables.group.NoSuchNodeError:
            return None

    def copy_node(self, node, target_node=None, recursive=True):
        self._h5_file.copy_node(node, newparent=target_node, recursive=recursive)


class DatabaseWriter(Database):

    def __init__(self, h5_filename):
        super(DatabaseWriter, self).__init__(h5_filename)
        self._flush_counter = 0

    def open(self):
        super(DatabaseWriter, self).open(mode='a', lock_type=portalocker.LOCK_EX)

    def create_table(self, node_names, table_description, expectedrows):
        table_name = node_names[-1]
        group = self.create_groups(node_names[:-1])

        try:
            table = self._h5_file.create_table(group, table_name,
                                               table_description, table_name,
                                               expectedrows=expectedrows)
        except ClosedFileError, e:
            raise DBNotOpenError(e)

        return table

    def create_c_array_from_array(self, node_names, array):
        c_array_name = node_names[-1]
        group = self.create_groups(node_names[:-1])

        self._h5_file.create_carray(group, c_array_name, obj=array, filters=None)

    def remove_table(self, node_names):
        table_name = node_names[-1]
        group = self.get_node(node_names[:-1])
        self._h5_file.remove_node(group, table_name)

    def create_groups(self, node_names):
        current_groups = '/' + node_names[0]
        try:
            group = self._h5_file.create_group(self._h5_file.root, node_names[0], node_names[0])
        except NodeError:
            group = self._h5_file.get_node(current_groups)

        for node_name in node_names[1:]:
            try:
                group = self._h5_file.create_group(group, node_name, node_name)
            except NodeError:
                current_groups += '/' + node_name
                group = self._h5_file.get_node(current_groups)

        return group


class DatabaseReader(Database):

    def __new__(cls, h5_filename):
        if not hasattr(cls, '_db_readers'):
            cls._db_readers = {}

        try:
            return cls._db_readers[h5_filename]
        except KeyError:
            new_db_readers = object.__new__(cls, h5_filename)
            cls._db_readers[h5_filename] = new_db_readers
            return new_db_readers

    def __init__(self, h5_filename):
        if not hasattr(self, '_h5_file'):
            super(DatabaseReader, self).__init__(h5_filename)

    def open(self):
        if self._h5_file is None or not self._h5_file.isopen:
            super(DatabaseReader, self).open(mode='r', lock_type=portalocker.LOCK_SH)

    def close(self):
        if gtrackcore_compressed.preprocess.is_preprocessing:
            super(DatabaseReader, self).close()
