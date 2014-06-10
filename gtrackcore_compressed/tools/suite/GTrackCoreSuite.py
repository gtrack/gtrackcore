import os
import tarfile
import zipfile

from gtrackcore_compressed.core.Config import Config
from gtrackcore_compressed.tools.suite.FileParser import parse_track_resource_file
from gtrackcore_compressed.tools.suite.ResourceRetrieval import retrieve_resources
from gtrackcore_compressed.util.suite.CommonFunctions import custom_splitext, get_filename_and_file_ext, remove_file_or_dir, \
    copy_file_or_dir, path_is_dir


def load_track_suite(suite_filename):
    resources = parse_track_resource_file(suite_filename)

    download_dir, temp_resource_dir = _setup_dirs()
    fetched_resources = retrieve_resources(resources, download_dir)

    if len(resources) != len(fetched_resources):
        unfetched_resources = list(set([res['URL'] for res in resources]) -
                                   set([res['URL'] for res in fetched_resources]))

        print "Failed to fetch the following resources:"
        print '\n'.join(unfetched_resources)

    compressed_fetched_resources = [resource for resource in fetched_resources if resource['compressed']]
    decompressed_fetched_resources = [resource for resource in fetched_resources if not resource['compressed']]

    if len(decompressed_fetched_resources) > 0:
        print 'Copying %d resources.' % len(decompressed_fetched_resources)
        for resource in decompressed_fetched_resources:
            if path_is_dir(resource['download_path']):
                tmp_location = temp_resource_dir + os.sep + resource['download_path'].split(os.sep)[-2]
            else:
                tmp_location = temp_resource_dir + os.sep + resource['download_path'].split(os.sep)[-1]

            copy_file_or_dir(resource['download_path'], tmp_location)
            resource['tmp_location'] = tmp_location

    if len(compressed_fetched_resources) > 0:
        print 'Extracting %d archives.' % len(compressed_fetched_resources)
        for resource in compressed_fetched_resources:
            tmp_location =_decompress_archive(resource['download_path'], temp_resource_dir)
            resource['tmp_location'] = tmp_location

    return fetched_resources


def _setup_dirs():
    download_dir = Config.RESOURCE_DONWLOAD_DIR
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    temp_resource_dir = Config.RESOURCE_DIR
    if os.path.exists(temp_resource_dir):
        remove_file_or_dir(temp_resource_dir)
    os.makedirs(temp_resource_dir)

    return download_dir, temp_resource_dir


def _decompress_archive(file_path, dest_dir):

    file_name, file_ext = get_filename_and_file_ext(file_path)
    print 'Trying to extract "%s"...' % file_name,
    if tarfile.is_tarfile(file_path):
        destination = _decompress_tarfile(file_path, dest_dir)
    elif zipfile.is_zipfile(file_path):
        destination = _decompress_zipfile(file_path, dest_dir)
    else:
        raise TypeError('Archive type not supported: %s' % file_ext)

    print 'Done!'
    return destination


def _decompress_tarfile(file_path, dest_dir):
    _, file_ext = get_filename_and_file_ext(file_path)

    if file_ext == '.gz':
        tar = tarfile.open(file_path, mode='r:gz')
    else:
        tar = tarfile.open(file_path, mode='r')
    members = tar.getmembers()
    return _decompress_common(file_path, dest_dir, tar, members)


def _decompress_zipfile(file_path, dest_dir):
    zip = zipfile.ZipFile(file_path, 'r')
    members = zip.namelist()
    return _decompress_common(file_path, dest_dir, zip, members)


def _decompress_common(file_path, dest_dir, decompressor, members):
    file_name, file_ext =get_filename_and_file_ext(file_path)

    if len(members) > 1:
        dest_dir = dest_dir + os.sep + custom_splitext(file_name)[0] + os.sep
        os.makedirs(dest_dir)
        for member in members:
            decompressor.extract(member, dest_dir)
    elif len(members) == 1:
        decompressor.extract(members[0], dest_dir)
        decompressor.close()
        dest_dir = dest_dir + os.sep + file_name
    else:
        print 'Archive is empty.',
        return None

    return dest_dir


if __name__ == '__main__':
    load_track_suite('/Users/brynjar/lol.gsuite')
