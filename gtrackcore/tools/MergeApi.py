import os
import shutil
import tables
from gtrackcore.core.Config import Config
from gtrackcore.track.pytables.database.Database import DatabaseReader, DatabaseWriter
from gtrackcore.util.pytables.Constants import GTRACKCORE_FORMAT_SUFFIX
from gtrackcore.util.pytables.NameFunctions import get_base_node_names, get_node_path


def append_to_file(from_h5_filename, to_h5_filename):
    from_h5_filename = os.path.abspath(from_h5_filename)
    to_h5_filename = os.path.abspath(to_h5_filename)

    if not _is_valid_files(from_h5_filename, to_h5_filename):
        return

    src_reader = DatabaseReader(from_h5_filename)
    dest_writer = DatabaseWriter(from_h5_filename)

    _copy_nodes_from_src_to_dest(src_reader, dest_writer)
    print 'Nodes of source filename has been copied to the destination'


# TODO: make it copy genome info
def extract_track(from_h5_filename, genome, track_name, to_h5_filename):
    from_h5_filename = os.path.abspath(from_h5_filename)
    to_h5_filename = os.path.abspath(to_h5_filename)

    if not _is_valid_files(from_h5_filename):
        return

    track_base_node_names = get_base_node_names(genome, track_name)
    track_base_path = get_node_path(track_base_node_names)

    src_reader = DatabaseReader(from_h5_filename)
    dest_writer = DatabaseWriter(to_h5_filename)
    dest_writer.open()
    dest_writer.create_groups(track_base_node_names)
    dest_writer.close()

    _copy_nodes_from_src_to_dest(src_reader, dest_writer, where=track_base_path)
    print 'Extraction complete.'


def extract_tracks_to_directory_tree(h5_filename, dest_directory):
    h5_filename = os.path.abspath(h5_filename)
    dest_directory = os.path.abspath(dest_directory)
    dest_directory = dest_directory[:-1] if dest_directory[-1] == '/' else dest_directory

    tracks = _get_tracks_to_be_extracted(h5_filename, dest_directory)

    total_tracks = len(tracks)
    i = 1
    for dir_path, track in tracks.iteritems():
        print 'Progress: %d/%d -- Current track: %s\r' % (i, total_tracks, ':'.join(track['track_name'])),
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
        dest_h5_filename = dir_path + '/' + track['track_name'][-1] + '.' + GTRACKCORE_FORMAT_SUFFIX
        extract_track(h5_filename, track['genome'], track['track_name'], dest_h5_filename)
        i += 1
    print 'Extraction complete.'


def merge_files_in_tree(src_directory, new_h5_filename):
    src_directory = os.path.abspath(src_directory)
    new_h5_filename = os.path.abspath(new_h5_filename)

    if not os.path.isdir(src_directory):
        print "Input is not a directory."

    dest_writer = DatabaseWriter(new_h5_filename)

    h5_filenames = _get_h5_filenames_to_copy(src_directory)
    total_files = len(h5_filenames)
    for i, h5_filename in enumerate(h5_filenames):
        print 'Progress: %d/%d -- Current file: %s\r' % (i+1, total_files, h5_filename),
        src_reader = DatabaseReader(h5_filename)
        _copy_nodes_from_src_to_dest(src_reader, dest_writer)
    print 'Tracks in directory tree merged.'


def merge_track_files(h5_filename1, h5_filename2, new_h5_filename, append_to_dest=False):
    h5_filename1 = os.path.abspath(h5_filename1)
    h5_filename2 = os.path.abspath(h5_filename2)
    new_h5_filename = os.path.abspath(new_h5_filename)

    if not _is_valid_files(h5_filename1, h5_filename2):
        return

    larger_filename, smaller_filename = _get_larger_and_smaller_filenames(h5_filename1, h5_filename2)

    larger_src_reader = DatabaseReader(larger_filename)
    smaller_src_reader = DatabaseReader(smaller_filename)
    dest_writer = DatabaseWriter(new_h5_filename)

    if not append_to_dest:
        shutil.copy(larger_filename, new_h5_filename)

    _copy_nodes_from_src_to_dest(larger_src_reader, dest_writer)
    _copy_nodes_from_src_to_dest(smaller_src_reader, dest_writer)
    print 'Tracks merged.'


def _copy_nodes_from_src_to_dest(src_reader, dest_writer, where='/'):
    src_reader.open()
    dest_writer.open()

    for node in src_reader.h5_file.walk_nodes(where):
        node_path = node._v_pathname
        if node_path not in dest_writer.h5_file:
            dest_target_path = '/'.join(node._v_pathname.split('/')[:-1])
            if dest_target_path == '':
                dest_target_path = '/'
            dest_target_node = dest_writer.h5_file.get_node(dest_target_path)
            src_reader.copy_node(node, target_node=dest_target_node, recursive=True)

    src_reader.close()
    dest_writer.close()


def _get_genome_and_trackname_from_node_path(node_path):
    genome = node_path.split('/')[1]
    track_name = node_path.split('/')[2:-1]
    return {'genome': genome, 'track_name': track_name}


def _get_h5_filenames_to_copy(directory):
    filepaths = []
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filename = os.path.join(dirpath, filename)
            if tables.is_pytables_file(filename):
                filepaths.append(filename)
    return filepaths


def _get_larger_and_smaller_filenames(h5_filename1, h5_filename2):
    filesize1 = os.stat(h5_filename1).st_size
    filesize2 = os.stat(h5_filename2).st_size

    if filesize1 >= filesize2:
        larger_filename = h5_filename1
        smaller_filename = h5_filename2
    else:
        larger_filename = h5_filename2
        smaller_filename = h5_filename1

    return larger_filename, smaller_filename


def _get_tracks_to_be_extracted(h5_filename, dest_directory):
    tracks = {}
    dir_path = dest_directory
    src_reader = DatabaseReader(h5_filename)
    src_reader.open()

    for node in src_reader.h5_file.walk_nodes():
        if node._v_name in ['no_overlaps', 'with_overlaps']:
            tracks[dir_path] = _get_genome_and_trackname_from_node_path(node._v_pathname)
        elif isinstance(node, tables.Group):
            dir_path = dest_directory + node._v_pathname

    src_reader.close()
    return tracks


def _is_valid_files(*h5_filenames):
    for h5_filename in h5_filenames:
        if not tables.is_pytables_file(h5_filename):
            print 'The file "' + h5_filename + '" is not a pytables file'
            return False

    any_filenames_equal = any(fn == h5_filenames[0] for fn in h5_filenames[1:])
    if any_filenames_equal:
        print "Error. Can't merge file with itself."
        return False

    return True


if __name__ == '__main__':
    src_dir = Config.PROCESSED_DATA_PATH + '/hg19'
    h5_fn = Config.PROCESSED_DATA_PATH + '/db_hg19.h5'
    merge_files_in_tree(src_dir, h5_fn)
