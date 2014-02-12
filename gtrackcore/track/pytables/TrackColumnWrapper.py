import sys

class TrackColumnWrapper(object):

    def __init__(self, column_name, db_handler):
        self._column_name = column_name
        self._db_handler = db_handler
        self._db_handler.open()
        column = self._db_handler.get_column(self._column_name)
        self._shape = column.shape
        self._dtype = column.dtype
        self._db_handler.close()
        self._start_index = -1
        self._end_index = -1

    def __getslice__(self, i, j):

        self._db_handler.open()
        column = self._db_handler.get_column(self._column_name)
        #TODO: fix hacky solution
        if j == sys.maxint:
            column_slice = column[self._start_index+i:self._end_index]
        else:
            column_slice = column[self._start_index+i:self._start_index+j]
        self._db_handler.close()
        return column_slice

    def __getitem__(self, i):
        self._db_handler.open()
        column = self._db_handler.get_column(self._column_name)
        column_item = column[self._start_index+i]
        self._db_handler.close()
        return column_item

    def __len__(self):
        return self._end_index - self._start_index

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