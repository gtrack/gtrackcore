import os
import re
import urllib2
from urlparse import urlparse
from ftplib import FTP

from gtrackcore.core.Config import Config


def parse_track_resource_file(resource_filename):
    resources = []
    with open(resource_filename, 'r') as resource_file:
        for line in resource_file:
            line = line.strip()
            if line.startswith('#') or line == '':
                continue

            parts = [part for part in line.split('\t') if part != '']  # split line and ignore empty strings

            if len(parts) < 5:
                print 'Error. File is not in correct format'

            url = _validate_url(parts[0])
            genome = _validate_genome(parts[1])
            track_name = _convert_track_name_str_to_list(parts[2])
            preprocessed = _convert_to_boolean(parts[3])
            compressed = _convert_to_boolean(parts[4])

            resource = {'URL': url, 'genome': genome, 'track_name': track_name,
                        'compressed': False, 'preprocessed': True}  # default values for compressed and preprocessed
            if preprocessed is not None:
                resource['preprocessed'] = preprocessed
            if compressed is not None:
                resource['compressed'] = compressed

            resources.append(resource)

    return resources


def _validate_url(url):
    regex = re.compile(r'\A(https?|ftp|file)://.+\Z')
    match = re.match(regex, url)

    if match:
        return url
    else:
        raise TypeError('Invalid specification of url: %s' % url)


def _validate_genome(genome):
    if genome == '.':
        return None
    return genome


def _convert_track_name_str_to_list(track_name_str):
    if track_name_str == '.':
        return None

    track_name_str = track_name_str.strip()
    track_name_list = re.split(':|\^|\|', track_name_str)
    track_name_list = [urllib2.unquote(part) for part in track_name_list]
    return track_name_list


def _convert_to_boolean(text):
    text_lower = text.lower()
    if text_lower == 'true':
        return True
    elif text_lower == 'false':
        return False
    elif text_lower == '.':  # use default
        return None
    else:
        raise TypeError


def retrieve_resources(track_resources):
    if not os.path.exists(Config.RESOURCE_PATH):
        os.makedirs(Config.RESOURCE_PATH)

    for resource in track_resources:
        parsed_url = urlparse(resource['URL'])
        scheme = parsed_url.scheme

        if scheme in ['http', 'file', 'ftp']:

            if _resource_is_dir(resource):
                if resource['compressed']:
                    pass
                else:
                    raise NotImplementedError
            else:
                if resource['compressed']:
                    _retrieve_file_using_urllib2(parsed_url, Config.RESOURCE_PATH)

def _resource_is_dir(resource):
    return resource['URL'][-1] == '/'

def _retrieve_from_file(parsed_url):
    return parsed_url.path


def _retrieve_from_ftp(parsed_url):
    ftp = FTP(parsed_url.geturl())
    ftp.login()
    #ftp.cwd(parsed_url.path)
    #ftp.retrbinary('RETR README', open('README', 'wb').write)
    ftp.quit()


def _retrieve_file_using_urllib2(parsed_url, dest_dir):
    dest_dir = dest_dir if dest_dir[-1] is not '/' else dest_dir[:-1]

    filename = dest_dir + '/' + parsed_url.path.split('/')[-1]

    try:
        open_url = urllib2.urlopen(parsed_url.geturl())
    except urllib2.HTTPError, e:
        print e
        return
    except urllib2.URLError, e:
        print e
        return

    h5_file = open(filename, 'wb')
    meta = open_url.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (filename, file_size)

    file_size_dl = 0
    block_size = 8192
    while True:
        buffer = open_url.read(block_size)
        if not buffer:
            break

        file_size_dl += len(buffer)
        h5_file.write(buffer)
        status = "%10d bytes,  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status + "\r",

    h5_file.close()


if __name__ == '__main__':
    track_resources = [{'URL': 'http:///Users/brynjar/gtrackcore_data/Processed/hg19/Sequence/Repeating elements/repeating_elements.h5', 'genome': 'hg19',
                        'track_name': 'testcat:test',  'format': True}]

    retrieve_resources(track_resources)