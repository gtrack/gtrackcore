import os
import shutil
import tables
from gtrackcore.track.pytables.database.Database import DatabaseReader, DatabaseWriter

def merge_track_files(h5_filename1, h5_filename2, new_h5_filename, append_to_dest=False):

    if not _is_valid_files(h5_filename1, h5_filename2):
        return

    larger_filename, smaller_filename = _get_larger_and_smaller_filenames(h5_filename1, h5_filename2)

    larger_source_reader = DatabaseReader(larger_filename)
    smaller_source_reader = DatabaseReader(smaller_filename)
    dest_writer = DatabaseWriter(new_h5_filename)

    if not append_to_dest:
        shutil.copy(larger_filename, new_h5_filename)

    _copy_nodes_from_source_to_dest(larger_source_reader, dest_writer)
    _copy_nodes_from_source_to_dest(smaller_source_reader, dest_writer)


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


def append_to_file(from_h5_filename, to_h5_filename):

    if not _is_valid_files(from_h5_filename, to_h5_filename):
        return

    source_reader = DatabaseReader(from_h5_filename)
    dest_writer = DatabaseWriter(from_h5_filename)

    if _copy_nodes_from_source_to_dest(source_reader, dest_writer):
        print 'Nodes of source filename has been copied to the destination'
    else:
        print 'Nothing to copy...'

def _copy_nodes_from_source_to_dest(source_reader, dest_writer):
    source_reader.open()
    dest_writer.open()
    dirty = False
    for node in source_reader.h5_file.walk_nodes():
        node_path = node._v_pathname

        if node_path not in dest_writer.h5_file:
            dest_target_path = '/'.join(node._v_pathname.split('/')[:-1])
            if dest_target_path == '':
                dest_target_path = '/'
            dest_target_node = dest_writer.h5_file.get_node(dest_target_path)
            source_reader.copy_node(node, target_node=dest_target_node, recursive=True)
            dirty = True

    source_reader.close()
    dest_writer.close()

    return dirty

def _is_valid_files(h5_filename1, h5_filename2):

    for h5_filename in [h5_filename1, h5_filename2]:
        if not tables.is_pytables_file(h5_filename):
            print 'The file "' + h5_filename + '" is not a pytables file'
            return False

    if h5_filename1 == h5_filename2:
        print "Error. Can't merge file with itself."
        return False

    return True

def merge_files_in_tree(directory, new_h5_filename):
    if not os.path.isdir(directory):
        print "Input is not a directory."

    dest_writer = DatabaseWriter(new_h5_filename)

    for dirpath, dirnames, filenames in os.path.walk(directory):
        for filename in filenames:
            if tables.is_pytables_file(filename):
                source_reader = DatabaseReader(filename)
                _copy_nodes_from_source_to_dest(source_reader, dest_writer)


if __name__ == '__main__':
    import tables

    source_h5_file = tables.open_file("source", 'w', title='test')

    source_h5_file.create_group("/", "teste")
    source_h5_file.create_group("/teste", "med")
    source_h5_file.create_group("/teste/med", "mange")
    source_h5_file.create_group("/teste/med/mange", "grupper")
    source_h5_file.create_group("/", "hallo")
    source_h5_file.create_table("/teste/med/mange/grupper", "tabbisTABELL", {"chr": tables.StringCol(10),  "start": tables.Int32Col()})
    source_h5_file.create_group("/hallo", "hey")
    source_h5_file.create_table("/hallo", "noemedpytables", {"chr": tables.StringCol(10),  "start": tables.Int32Col()})

    dest_h5_file = tables.open_file("dest", 'w', title='test')
    dest_h5_file.create_group("/", "teste")
    dest_h5_file.create_group("/teste", "med")
    dest_h5_file.create_group("/teste", "er")
    dest_h5_file.create_group("/teste/er", "kult")
    dest_h5_file.create_group("/", "feste")
    table = dest_h5_file.create_table("/teste/er", "kultTABELL", {"chr": tables.StringCol(10),  "start": tables.Int32Col()}, "test")

    row = table.row
    row['chr'] = 'chr1'
    row['start'] = 3
    row.append()
    row['chr'] = 'chr2'
    row['start'] = 2
    row.append()
    row['chr'] = 'chr1'
    row['start'] = 1
    row.append()
    table.flush()

    source_h5_file.close()
    dest_h5_file.close()

    merge_track_files("source", "dest", "new_file")
