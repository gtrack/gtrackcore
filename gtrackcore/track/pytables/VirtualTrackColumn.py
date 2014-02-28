from gtrackcore.track.core.VirtualNumpyArray import VirtualNumpyArray


class VirtualTrackColumn(VirtualNumpyArray):

    def __init__(self, column_name, table_reader):
        VirtualNumpyArray.__init__(self)
        self._column_name = column_name
        self._table_reader = table_reader
        self._start_index = -1
        self._end_index = -1
        self._step = 1

        self._table_reader.open()
        column = self._table_reader.get_column(self._column_name)
        self._shape = column.shape
        self._dtype = column.dtype
        self._table_reader.close()

    @property
    def offset(self):
        return self._start_index, self._end_index

    @offset.setter
    def offset(self, start_end_tuple):
        self._start_index = start_end_tuple[0]
        self._end_index = start_end_tuple[1]

    @property
    def shape(self):
        return self._shape

    @property
    def dtype(self):
        return self._dtype

    @property
    def filename(self):
        raise NotImplementedError

    def __getitem__(self, val):
        if isinstance(val, slice):
            self._update_offset(val)
            return self
        else:
            self._table_reader.open()
            column = self._table_reader.get_column(self._column_name)
            result = column[self._start_index + val]
            self._table_reader.close()
            return result

    def __iter__(self):
        self._table_reader.open()
        table = self._table_reader.table
        for row in table.iterrows(start=self._start_index, stop=self._end_index):
            yield row[self._column_name]
        self._table_reader.close()

    def __copy__(self):
        vtc = VirtualTrackColumn(self._column_name, self._table_reader)
        vtc.offset = self.offset
        return vtc

    def __len__(self):
        return self._end_index - self._start_index

    def _asNumpyArray(self):
        self._table_reader.open()
        column = self._table_reader.get_column(self._column_name)
        result = column[self._start_index:self._end_index]
        self._table_reader.close()
        return result

    def _update_offset(self, slice_val):
        if slice_val.start is not None:
            if slice_val.start >= 0:
                self._start_index = self._start_index + slice_val.start
            else:
                self._start_index = self._end_index + slice_val.start

        if slice_val.stop is not None:
            if slice_val.start >= 0:
                self._end_index = self._start_index + slice_val.stop
            else:
                self._end_index = self._end_index + slice_val.stop

        self._step = slice_val.step if slice_val.step is not None else 1

    def ends_as_numpy_array_points_func(self):
        """
        Used for points tracks for ends (== starts + 1)
        """
        self._table_reader.open()
        column = self._table_reader.get_column(self._column_name)
        result = column[self._start_index:self._end_index] + 1
        self._table_reader.close()
        return result
