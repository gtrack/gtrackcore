import sys
import os
import cmd
from gtrackcore.tools import TrackTools
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track.core.Track import PlainTrack

from gtrackcore.core.Config import Config


def print_table(headers, data):
    col_widths = [4] * len(headers)
    for row in data:
        for i, col in enumerate(row):
            col_widths[i] = max(col_widths[i], len(col))

    row_format = '{:<4}' + ''.join(['{:<' + str(col + 4) + '}' for col in col_widths])
    print row_format.format('', *headers)
    print row_format.format('', *['-'*len(h) for h in headers])
    for i, row in enumerate(data):
        print row_format.format(str(i), *row)


class ToolShell(cmd.Cmd):

    prompt = 'gtracktools > '
    intro = '====Tools for gtrackcore====\n'

    def __init__(self):
        cmd.Cmd.__init__(self)
        self._available_tracks = None
        self._find_available_tracks()

    def _find_available_tracks(self):
        base_dir = Config.PROCESSED_DATA_PATH + '/noOverlaps'
        data = []
        for directory, dirnames, filenames in os.walk(base_dir):
            if len(filenames) > 0:
                track_name_list = directory.split(base_dir + '/')[1].split('/')

                genome = track_name_list[0]
                track_name = track_name_list[1:]
                track_type = self._extrack_track_type(track_name, genome)

                data.append([genome, ':'.join(track_name), track_type])

        self._available_tracks = sorted(data, key=lambda x: x[1])

    def _extrack_track_type(self, track_name, genome):
        track = PlainTrack(track_name)
        track_view = track.getTrackView(GenomeRegion(genome, '', 0, 0))
        track_type = track_view.trackFormat.getFormatName()

        return track_type

    def do_list(self, line):
        print_table(['Genome', 'Track name', 'Track type'], self._available_tracks)

    def do_exit(self, line):
        sys.exit()

    def do_coverage(self, line):
        """ coverage <genome> <track_name>
        """
        argv = line.split()
        if len(argv) < 2:
            print 'wrong usage'
            self.help_coverage()
            return

        track_name = argv[0]

        track_view = PlainTrack(track_name)

        TrackTools.coverage()

    def complete_coverage(self, text, line, begidx, endidx):
        command_length = len(line.split()[0] + 1)

        if begidx <= command_length:
            completions = [f[0] for f in self._available_tracks if text is None or f[0].startswith(text)]
        elif begidx > command_length:
            completions = [f[1] for f in self._available_tracks if text is None or f[1].startswith(text)]

        return completions

    def help_coverage(self):
        print '\n'.join(['coverage <genome> <track name>',
                         'Find coverage of a single track'])

if __name__ == '__main__':
    ToolShell().cmdloop()