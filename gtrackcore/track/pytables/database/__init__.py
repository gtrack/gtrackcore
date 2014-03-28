import tables
import atexit

@atexit.register
def close_pytables_files():
    current_version = tuple(map(int, tables.__version__.split('.')))
    if current_version >= (3, 1, 0):
        open_files = tables.file._open_files

        # make a copy of the open_files.handlers container for the iteration
        handlers = list(open_files.handlers)
        any_open_files = len(open_files.handlers) > 0

        if any_open_files:
            for fileh in handlers:
                fileh.close()
    else:
        for file in tables.file._open_files.values():
            file.close()
