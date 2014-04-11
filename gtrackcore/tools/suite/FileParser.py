import re

from gtrackcore.util.suite.CommonFunctions import convert_to_boolean, convert_track_name_str_to_list


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
            track_name = convert_track_name_str_to_list(parts[2])
            preprocessed = convert_to_boolean(parts[3])
            compressed = convert_to_boolean(parts[4])

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

