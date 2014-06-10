import os
import re
from gtrackcore_compressed.core.Config import Config
from gtrackcore_compressed.util.CommonFunctions import get_dir_path
from gtrackcore_compressed.util.CustomExceptions import DBNotExistError
from gtrackcore_compressed.util.pytables.Constants import GTRACKCORE_FORMAT_SUFFIX

WITH_OVERLAPS_NODE_NAME = 'with_overlaps'
NO_OVERLAPS_NODE_NAME = 'no_overlaps'
BOUNDING_REGIONS_NODE_NAME = 'bounding_regions'
TRACKINFO_NODE_NAME = 'trackinfo'

illegal_starts = re.compile(r'(^\d|^_[cfgv]_)')
non_alphanumeric = re.compile(r'\W')


def get_base_node_names(genome, track_name):
    return _convert_list_to_natural_naming([genome] + track_name)


def get_track_table_node_names(genome, track_name, allow_overlaps):
    return _get_table_node_names(genome, track_name, track_name[-1], allow_overlaps)


def get_br_table_node_names(genome, track_name, allow_overlaps):
    return _get_table_node_names(genome, track_name, BOUNDING_REGIONS_NODE_NAME, allow_overlaps)


def get_trackinfo_node_names(genome, track_name):
    return get_base_node_names(genome, track_name) + [TRACKINFO_NODE_NAME]


def _get_table_node_names(genome, track_name, table_name, allow_overlaps):
    node_names = get_base_node_names(genome, track_name) + [_convert_string_to_natural_naming(table_name)]
    node_names.insert(len(node_names)-1, WITH_OVERLAPS_NODE_NAME if allow_overlaps else NO_OVERLAPS_NODE_NAME)
    return node_names


def get_node_path(node_names):
    return '/%s' % ('/'.join(node_names))


def get_database_filename(genome, track_name, allow_overlaps=None, create_path=False):
    dir_path = get_dir_path(genome, track_name)
    if create_path:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    if not os.path.exists(dir_path):
        raise DBNotExistError('Track \'' + ':'.join(track_name) + '\' does not exist')

    db_path = "%s%s%s.%s" % (dir_path, os.sep, get_db_name(track_name[-1], None), GTRACKCORE_FORMAT_SUFFIX)
    if os.path.exists(db_path):
        return db_path
    else:
        return "%s%s%s.%s" % (dir_path, os.sep, get_db_name(track_name[-1], allow_overlaps),
                              GTRACKCORE_FORMAT_SUFFIX)


def get_db_name(track_name, allow_overlaps):
    track_name = track_name if allow_overlaps is None else \
        track_name + ('_with_overlaps' if allow_overlaps else '_no_overlaps')
    return _convert_string_to_natural_naming(track_name)


def _convert_list_to_natural_naming(name):
    return [re.sub(illegal_starts, r'_\g<1>', re.sub(non_alphanumeric, '_', part.lower())) for part in name]


def _convert_string_to_natural_naming(name):
    return re.sub(illegal_starts, r'_\g<1>', re.sub(non_alphanumeric, '_', name.lower()))


def get_genome_and_trackname(filename):
    genome_track_name_list = filename.split(Config.PROCESSED_DATA_PATH)[1][1:].split(os.sep)
    genome = genome_track_name_list[0]
    track_name = genome_track_name_list[1:-1]
    return genome, track_name
