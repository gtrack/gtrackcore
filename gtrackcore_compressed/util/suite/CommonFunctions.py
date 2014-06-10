import errno
import os
import re
import shutil
import urllib2


def custom_splitext(filename):
    cur_filename_no_ext, cur_file_ext = os.path.splitext(filename)
    while True:
        filename_no_ext, file_ext = os.path.splitext(cur_filename_no_ext)
        if file_ext == '':
            return cur_filename_no_ext, cur_file_ext
        else:
            cur_filename_no_ext = filename_no_ext
            cur_file_ext = file_ext + cur_file_ext


def get_new_enumerated_filename(filename):
    filename_no_ext, file_ext = custom_splitext(filename)
    trailing_digits = re.compile('.+(\(\d+\))$')
    match = re.match(trailing_digits, filename_no_ext)
    if match:
        group = match.groups()[0]
        new_number = str(int(group[1:-1]) + 1)
        filename = filename_no_ext[:-len(group)] + '(' + new_number + ')' + file_ext
    else:
        filename = filename_no_ext + '(1)' + file_ext
    return filename


def path_is_dir(path):
    return path[-1] == '/'


def get_filename_and_file_ext(file_path):
    _, file_ext = os.path.splitext(file_path)
    file_name = file_path.split('/')[-1]
    return file_name, file_ext


def remove_file_or_dir(path):
    try:
        shutil.rmtree(path)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            os.remove(path)
        else:
            print('Unable to delete %s. Error: %s' % (path, e))


def copy_file_or_dir(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print('Unable to copy %s to %s. Error: %s' % (e, src, dest))


def convert_track_name_str_to_list(track_name_str):
    if track_name_str == '.':
        return None

    track_name_str = track_name_str.strip()
    track_name_list = re.split(':|\^|\|', track_name_str)
    track_name_list = [urllib2.unquote(part) for part in track_name_list]
    return track_name_list


def convert_to_boolean(text):
    text_lower = text.lower()
    if text_lower == 'true':
        return True
    elif text_lower == 'false':
        return False
    elif text_lower == '.':  # use default
        return None
    else:
        raise TypeError