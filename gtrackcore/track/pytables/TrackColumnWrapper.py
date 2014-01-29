class TrackColumnWrapper(object):
    """
    Column wrapper per chromosome
    """

    def __init__(self, column_name, db_handler):
        self._column_name = column_name
        self._db_handler = db_handler
        self._db_handler.open()
        column = self._db_handler.get_column(self._column_name)
        self._shape = column.shape
        self._dtype = column.dtype
        self._db_handler.close()


    def __getslice__(self, i, j):
        self._db_handler.open()
        column = self._db_handler.get_column(self._column_name)
        column_slice = column[i:j]
        self._db_handler.close()
        return column_slice

    def __getitem__(self, i):
        self._db_handler.open()
        column = self._db_handler.get_column(self._column_name)
        column_item = column[i]
        self._db_handler.close()
        return column_item

    def getShape(self):
        return self._shape

    def getDType(self):
        return self._dtype

    def getFilename(self):
        raise NotImplementedError

    shape = property( getShape )
    dtype = property( getDType )
    filename = property( getFilename )