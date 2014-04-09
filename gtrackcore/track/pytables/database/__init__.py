import tables
import atexit
from gtrackcore.metadata.TrackInfo import DynamicTrackInfo
from gtrackcore.util.CustomExceptions import DBNotExistError
from gtrackcore.track.pytables.database.MetadataHandler import MetadataHandler
from gtrackcore.util.pytables.NameFunctions import get_genome_and_trackname


@atexit.register
def close_pytables_files():
    filenames = []

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
    else:
        filenames = []
        for filename, fileh in tables.file._open_files.items():
            fileh.close()
            filenames.append(filename)
        for filename in filenames:
            if filename in tables.file._open_files:
                del tables.file._open_files[filename]

    _persist_metadata(filenames)


def _persist_metadata(filenames):
    for filename in filenames:
        try:
            genome, track_name = get_genome_and_trackname(filename)
            if not track_name:
                continue
        except IndexError:
            continue
        dynamic_trackinfo = DynamicTrackInfo(genome, track_name)
        metadata_handler = MetadataHandler(genome, track_name)
        try:
            metadata_handler.update_persisted_trackinfo(dynamic_trackinfo)
        except DBNotExistError:
            pass
