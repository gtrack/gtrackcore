import os
import tarfile
import zipfile

from gtrackcore.core.Config import Config
from gtrackcore.tools.suite.FileParser import parse_track_resource_file
from gtrackcore.tools.suite.ResourceRetrieval import retrieve_resources
from gtrackcore.util.suite.CommonFunctions import custom_splitext, get_filename_and_file_ext, remove_file_or_dir, \
    copy_file_or_dir


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
    not_compressed_fetched_resources = [resource for resource in fetched_resources if not resource['compressed']]

    if len(not_compressed_fetched_resources) > 0:
        print 'Copying %d resources.' % len(not_compressed_fetched_resources)
        for resource in not_compressed_fetched_resources:
            to_file_path = temp_resource_dir + os.sep + resource['file_path'].split(os.sep)[-1]
            copy_file_or_dir(resource['file_path'], to_file_path)

    if len(compressed_fetched_resources) > 0:
        print 'Extracting %d archives.' % len(compressed_fetched_resources)
        for resource in compressed_fetched_resources:
            _decompress_archive(resource['file_path'], temp_resource_dir)


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

    file_name, file_ext =get_filename_and_file_ext(file_path)
    print 'Trying to extract "%s"...' % file_name,
    if tarfile.is_tarfile(file_path):
        _decompress_tarfile(file_path, dest_dir)
    elif zipfile.is_zipfile(file_path):
        _decompress_zipfile(file_path, dest_dir)
    else:
        raise TypeError('Archive type not supported: %s' % file_ext)

    print 'Done!'


def _decompress_tarfile(file_path, dest_dir):

    file_name, file_ext =get_filename_and_file_ext(file_path)

    if file_ext == '.gz':
        tar = tarfile.open(file_path, mode='r:gz')
    else:
        tar = tarfile.open(file_path, mode='r')
    members = tar.getmembers()
    if len(members) > 1:
        target_dir = dest_dir + '/' + custom_splitext(file_name)[0]
        os.makedirs(target_dir)
        for member in members:
            tar.extract(member, target_dir)
    else:
        tar.extractall(dest_dir)
        tar.close()


def _decompress_zipfile(file_path, dest_dir):
    file_name, file_ext =get_filename_and_file_ext(file_path)

    zip = zipfile.ZipFile(file_path, 'r')
    members = zip.namelist()
    if len(members) > 1:
        target_dir = dest_dir + '/' + custom_splitext(file_name)[0]
        os.makedirs(target_dir)
        for member in members:
            zip.extract(member, target_dir)
    else:
        zip.extractall(dest_dir)
        zip.close()


if __name__ == '__main__':
    load_track_suite('/Users/brynjar/lol.gsuite')
