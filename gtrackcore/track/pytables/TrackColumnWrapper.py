class TrackColumnWrapper(object):

    def __init__(self, column_name, table_reader):
        self._column_name = column_name
        self._table_reader = table_reader
        self._start_index = -1
        self._end_index = -1

        self._set_column_metadata()

    def _set_column_metadata(self):
        self._table_reader.open()
        column = self._table_reader.get_column(self._column_name)
        self._shape = column.shape
        self._dtype = column.dtype
        self._table_reader.close()

    def __getitem__(self, val):
        is_slice = isinstance(val, slice)
        if is_slice:
            start_index, end_index, step = self._handle_slice(val)

        self._table_reader.open()
        column = self._table_reader.get_column(self._column_name)
        result = column[start_index:end_index:step] if is_slice else column[self._start_index + val]
        self._table_reader.close()

        return result

    def _handle_slice(self, slice_val):
        if slice_val.start is None:
            start_index = self._start_index
        else:
            if slice_val.start >= 0:
                start_index = self._start_index + slice_val.start
            else:
                start_index = self._end_index + slice_val.start

        if slice_val.stop is None:
            end_index = self._end_index
        else:
            if slice_val.start >= 0:
                end_index = self._start_index + slice_val.stop
            else:
                end_index = self._end_index + slice_val.stop

        step = slice_val.step if slice_val.step is not None else 1

        return start_index, end_index, step

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

    def change_offset(self, start, end):
        self._start_index += start
        self._end_index += end

    def getShape(self):
        return self._shape

    def getDType(self):
        return self._dtype

    def getFilename(self):
        raise NotImplementedError

    shape = property( getShape )
    dtype = property( getDType )
    filename = property( getFilename )