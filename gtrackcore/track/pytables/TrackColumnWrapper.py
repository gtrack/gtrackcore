import sys


class TrackColumnWrapper(object):

    def __init__(self, column_name, table_reader):
        self._column_name = column_name
        self._table_reader = table_reader
        self._start_index = -1
        self._end_index = -1

        self._table_reader.open()
        column = self._table_reader.get_column(self._column_name)
        self._shape = column.shape
        self._dtype = column.dtype
        self._table_reader.close()

    def __getitem__(self, val):
        print type(val)

        is_slice = isinstance(val, slice)
        if is_slice:
            start_index = self._start_index if val.start is None else self._start_index + val.start
            end_index = self._end_index if val.stop is None else self._start_index + val.stop

        self._table_reader.open()
        column = self._table_reader.get_column(self._column_name)
        result = column[start_index:end_index] if is_slice else column[self._start_index + val]
        self._table_reader.close()

        return result

    def __len__(self):
        return self._end_index - self._start_index

    def __iter__(self):
        self._table_reader.open()
        table = self._table_reader.table
        for row in table.iterrows(start=self._start_index, stop=self._end_index):
            yield row[self._column_name]
        self._table_reader.close()

    def __add__(self, other):
        self._table_reader.open()
        column = self._table_reader.get_column(self._column_name)
        cache = column[:] + other
        self._table_reader.close()
        return cache

    def set_offset(self, start, end):
        self._start_index = start
        self._end_index = end

    def getShape(self):
        return self._shape

    def getDType(self):
        return self._dtype

    def getFilename(self):
        raise NotImplementedError

    shape = property( getShape )
    dtype = property( getDType )
    filename = property( getFilename )