from gtrackcore.track.core.VirtualNumpyArray import VirtualNumpyArray


class VirtualTrackColumn(VirtualNumpyArray):

    def __init__(self, column_name, table_reader, start_index=-1, end_index=-1):
        VirtualNumpyArray.__init__(self)
        self._column_name = column_name
        self._table_reader = table_reader
        self._start_index = start_index
        self._end_index = end_index
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

    def update_offset(self, start=None, stop=None, step=None):
        if start is not None:
            if start >= 0:
                self._start_index = self._start_index + start
            else:
                self._start_index = self._end_index + start

        if stop is not None:
            if start >= 0:
                self._end_index = self._start_index + stop
            else:
                self._end_index = self._end_index + stop

        self._step = step if step is not None else 1


    def __copy__(self):
        vtc = VirtualTrackColumn(self._column_name, self._table_reader)
        vtc.offset = self.offset
        return vtc

    def __len__(self):
        return self._end_index - self._start_index

    def as_numpy_array(self):
        self._table_reader.open()
        column = self._table_reader.get_column(self._column_name)
        result = column[self._start_index:self._end_index]
        self._table_reader.close()
        return result

    def ends_as_numpy_array_points_func(self):
        """
        Used for points tracks for ends (== starts + 1)
        """
        self._table_reader.open()
        column = self._table_reader.get_column(self._column_name)
        result = column[self._start_index:self._end_index] + 1
        self._table_reader.close()
        return result
