from copy import copy
import os
import re
import urllib2
from urlparse import urlparse


def retrieve_resources(track_resources, download_path):

    fetched_paths = []
    for resource in track_resources:
        parsed_url = urlparse(resource['URL'])
        scheme = parsed_url.scheme

        if scheme in ['http', 'file', 'ftp']:
            if not _path_is_dir(parsed_url.path):
                file_path = _retrieve_file_using_urllib2(parsed_url, download_path)
            else:
                raise NotImplementedError

            if file_path is None:
                continue
            else:
                file_resource = copy(resource)
                file_resource['file_path'] = file_path
                fetched_paths.append(file_resource)
    return fetched_paths


def _path_is_dir(path):
    return path[-1] == '/'


def _retrieve_file_using_urllib2(parsed_url, dest_dir):
    dest_dir = dest_dir if dest_dir[-1] is not '/' else dest_dir[:-1]

    filename = dest_dir + '/' + parsed_url.path.split('/')[-1]

    if os.path.exists(filename):
        filename = _get_new_filename(filename)
    try:
        open_url = urllib2.urlopen(parsed_url.geturl())
    except urllib2.HTTPError, e:
        print e
        return None
    except urllib2.URLError, e:
        print e
        return None

    h5_file = open(filename, 'wb')
    meta = open_url.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print 'Downloading: %s Bytes: %s' % (filename, file_size)

    file_size_dl = 0
    block_size = 8192
    while True:
        buffer = open_url.read(block_size)
        if not buffer:
            break

        file_size_dl += len(buffer)
        h5_file.write(buffer)
        status = '%10d bytes,  [%3.2f%%]' % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status + '\r',

    h5_file.close()
    return filename


def _get_new_filename(filename):
    filename_no_ext, file_ext = _custom_splitext(filename)
    trailing_digits = re.compile('.+(\(\d+\))$')
    match = re.match(trailing_digits, filename_no_ext)
    if match:
        group = match.groups()[0]
        new_number = str(int(group[1:-1]) + 1)
        filename = filename_no_ext[:-len(group)] + '(' + new_number + ')' + file_ext
    else:
        filename = filename_no_ext + '(1)' + file_ext
    return filename


def _custom_splitext(filename):
    cur_filename_no_ext, cur_file_ext = os.path.splitext(filename)
    while True:
        filename_no_ext, file_ext = os.path.splitext(cur_filename_no_ext)
        if file_ext == '':
            return cur_filename_no_ext, cur_file_ext
        else:
            cur_filename_no_ext = filename_no_ext
            cur_file_ext = file_ext + cur_file_ext
