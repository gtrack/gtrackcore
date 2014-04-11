from copy import copy
import os
import urllib2
from urlparse import urlparse

from gtrackcore.util.suite.CommonFunctions import get_new_enumerated_filename, path_is_dir


def retrieve_resources(track_resources, download_path):

    fetched_paths = []
    for resource in track_resources:
        parsed_url = urlparse(resource['URL'])
        scheme = parsed_url.scheme

        if scheme in ['http', 'file', 'ftp']:
            if not path_is_dir(parsed_url.path):
                file_path = _retrieve_file_using_urllib2(parsed_url, download_path)
            else:
                raise NotImplementedError

            if file_path is None:
                continue
            else:
                file_resource = copy(resource)
                file_resource['download_path'] = file_path
                fetched_paths.append(file_resource)
    return fetched_paths


def _retrieve_file_using_urllib2(parsed_url, dest_dir):
    dest_dir = dest_dir if dest_dir[-1] is not '/' else dest_dir[:-1]

    filename = dest_dir + '/' + parsed_url.path.split('/')[-1]

    if os.path.exists(filename):
        filename = get_new_enumerated_filename(filename)
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
        progress = int(file_size_dl * 100. / file_size) / 2
        status = status + ' |' + '#'*progress + '-'*(50-progress) + '|'
        print status + '\r',

    h5_file.close()
    return filename

