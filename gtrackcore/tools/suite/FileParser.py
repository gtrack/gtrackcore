import re
import urllib2


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
