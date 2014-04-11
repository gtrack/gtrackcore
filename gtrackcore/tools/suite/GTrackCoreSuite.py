import os
import shutil
import tarfile
import zipfile

from gtrackcore.core.Config import Config
from gtrackcore.tools.suite.FileParser import parse_track_resource_file
from gtrackcore.tools.suite.ResourceRetrieval import retrieve_resources


def load_track_suite(suite_filename):
    resources = parse_track_resource_file(suite_filename)

    download_dir, temp_resource_dir = _setup_dirs()
    fetched_resources = retrieve_resources(resources, download_dir)

    if len(resources) != len(fetched_resources):
        unfetched_resources = list(set([res['URL'] for res in resources]) -
                                   set([res['URL'] for res in fetched_resources]))

        print "Failed to fetch the following resources:"
        print '\n'.join(unfetched_resources)

    for resource in fetched_resources:
        if resource['compressed']:
            _decompress_archive(resource, temp_resource_dir)
        else:
            shutil.copytree(resource['file_path'], temp_resource_dir)


def _setup_dirs():
    download_dir = Config.RESOURCE_DONWLOAD_DIR
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    temp_resource_dir = Config.RESOURCE_DIR
    if os.path.exists(temp_resource_dir):
        shutil.rmtree(temp_resource_dir)
        os.makedirs(temp_resource_dir)

    return download_dir, temp_resource_dir


def _decompress_archive(file_path, dest_dir):
    _, file_ext = os.path.splitext(file_path)

    file_name = file_path.split('/')[-1]
    print 'Trying to extract "%s".' % file_name

    if tarfile.is_tarfile(file_path):
        if file_ext == '.gz':
            tar = tarfile.open(file_path, mode='r:gz')
        else:
            tar = tarfile.open(file_path, mode='r')
        tar.extractall(dest_dir)
        tar.close()
    elif zipfile.is_zipfile(file_path):
        zip = zipfile.ZipFile(file_path, 'r')
        zip.extractall(dest_dir)
        zip.close()
    else:
        raise TypeError('Archive type not supported: %s' % file_ext)

    print 'Archive extracted!'


if __name__ == '__main__':
    load_track_suite('/Users/brynjar/lol.gsuite')