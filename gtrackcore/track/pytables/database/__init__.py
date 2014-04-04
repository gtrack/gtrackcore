import tables
import atexit
from gtrackcore.util.CustomExceptions import DBNotExistError
from gtrackcore.util.pytables.CommonFunctions import genome_and_trackname
from gtrackcore.track.pytables.database.MetadataHandler import MetadataHandler


@atexit.register
def close_pytables_files():
    current_version = tuple(map(int, tables.__version__.split('.')))
    if current_version >= (3, 1, 0):
        open_files = tables.file._open_files

        # make a copy of the open_files.handlers container for the iteration
        handlers = list(open_files.handlers)
        any_open_files = len(open_files.handlers) > 0

        if any_open_files:
            filenames = tables.file._open_files.filenames
            for fileh in handlers:
                fileh.close()
            for filename in filenames:
                genome, track_name = genome_and_trackname(filename)
                metadata_handler = MetadataHandler(genome, track_name)
                try:
                    metadata_handler.store()
                except DBNotExistError:
                    pass
    else:
        filenames = []
        for filename, file in tables.file._open_files.items():
            file.close()
            filenames.append(filename)
        for filename in filenames:
            if filename in tables.file._open_files:
                del tables.file._open_files[filename]
                genome, track_name = genome_and_trackname(filename)
                metadata_handler = MetadataHandler(genome, track_name)
                metadata_handler.store()
