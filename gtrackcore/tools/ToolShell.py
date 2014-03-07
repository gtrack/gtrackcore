import sys
import os
import cmd

from gtrackcore.tools import TrackTools
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track.core.Track import PlainTrack
from gtrackcore.core.Config import Config
from gtrackcore.track.pytables.BoundingRegionHandler import BoundingRegionHandler


def print_table(headers, data):
    col_widths = [4] * len(headers)
    for row in data:
        for i, col in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(col)))

    row_format = '{:<4}' + ''.join(['{:<' + str(col + 4) + '}' for col in col_widths])
    print row_format.format('#', *headers)
    print row_format.format('-', *['-'*len(h) for h in headers])
    for i, row in enumerate(data):
        print row_format.format(str(i), *row)


class ToolShell(cmd.Cmd):

    prompt = 'gtracktools > '
    intro = '====Tools for gtrackcore====\n'

    def __init__(self):
        cmd.Cmd.__init__(self)
        self._available_tracks = None
        self._cached_bounding_regions = {}
        self._find_available_tracks()

    def print_result(self, tool, track_name, result):
        print
        print tool, 'for', ":".join(track_name)
        print 'Result:', result
        print

    def _get_track_view(self, track_name, genome_region):
        track = PlainTrack(track_name)
        return track.getTrackView(genome_region)

    def _find_available_tracks(self):
        base_dir = Config.PROCESSED_DATA_PATH + '/noOverlaps'
        data = []
        for directory, dirnames, filenames in os.walk(base_dir):
            if len(filenames) > 0:
                track_name_list = directory.split(base_dir + '/')[1].split('/')

                genome = track_name_list[0]
                track_name = track_name_list[1:]
                track_type = self._extract_track_type(genome, track_name)

                data.append([genome, ':'.join(track_name), track_type])

        self._available_tracks = sorted(data, key=lambda x: (x[0], x[1]))

    def _extract_track_type(self, genome, track_name):
        track = PlainTrack(track_name)
        track_view = track.getTrackView(GenomeRegion(genome, '', 0, 0))
        track_type = track_view.trackFormat.getFormatName()

        return track_type

    def _extract_bounding_regions(self, genome, track_name):
        cache_key = genome + ':' + ':'.join(track_name)
        if cache_key in self._cached_bounding_regions:
            return self._cached_bounding_regions[cache_key]

        bounding_regions = {}
        for allow_overlaps in [True, False]:
            bounding_region_handler = BoundingRegionHandler(genome, track_name, allow_overlaps)
            regions = [[region.chr + ':' + str(region.start) + '-' + str(region.end)]
                       for region in bounding_region_handler.get_all_bounding_regions()]

            if allow_overlaps:
                bounding_regions['with_overlaps'] = regions
            else:
                bounding_regions['no_overlaps'] = regions

        self._cached_bounding_regions[cache_key] = bounding_regions

        return bounding_regions

    def _is_track_available(self, genome, track_name):
        track_name_str = ':'.join(track_name)
        for track in self._available_tracks:
            if genome == track[0] and track_name_str == track[1]:
                return True
        return False

    def _is_legal_region(self, genome, track_name, region):
        bounding_regions = self._extract_bounding_regions(genome, track_name)
        for allow_overlaps_regions in bounding_regions:
            for bounding_region in allow_overlaps_regions:
                if region == bounding_region:
                    return True
        return False

    def _is_valid_region_format(self, region):
        valid_region_format_regex = r'\w+:\d+-\d*'
        from re import match
        return match(valid_region_format_regex, region) is not None

    def do_list(self, line):
        print_table(['Genome', 'Track name', 'Track type'], self._available_tracks)

    def do_exit(self, line):
        sys.exit()

    def do_coverage(self, line):
        argv = line.split()
        if len(argv) < 3:
            print 'Wrong usage'
            print self._usage_coverage()
            return

        genome = argv[0]
        track_name = argv[1].split(":")
        region = argv[2]

        if not self._is_valid_region_format(region):
            print 'Region has wrong format'
            print 'Example region: chr21:0-46944323.\nWhere seqid = chr21, start = 0, end = 46944323\n'
            return

        if not self._is_track_available(genome, track_name):
            print 'Track not available'
            return

        seqid, start, end = tuple(region.replace('-', ':').split(':'))
        genome_region = GenomeRegion(genome, seqid, int(start), int(end))
        track_view = self._get_track_view(track_name, genome_region)

        coverage = TrackTools.coverage(track_view)

        self.print_result('coverage', track_name, coverage)

    def complete_coverage(self, text, line, begidx, endidx):
        command_length = len(line.split()[0] + 1)

        if begidx <= command_length:
            completions = [f[0] for f in self._available_tracks if text is None or f[0].startswith(text)]
        elif begidx > command_length:
            completions = [f[1] for f in self._available_tracks if text is None or f[1].startswith(text)]

        return completions

    def help_coverage(self):
        print '\n'.join([self._usage_coverage(),
                         'Find coverage of a single track'])

    def _usage_coverage(self):
        return 'coverage <genome> <track name> <region>\n'


    def do_regions(self, line):
        argv = line.split()
        if len(argv) < 2:
            print 'Wrong usage'
            print self._usage_regions()
            return

        genome = argv[0]
        track_name = argv[1].split(":")

        if self._is_track_available(genome, track_name):
            bounding_regions = self._extract_bounding_regions(genome, track_name)
            print 'Example: chr21:0-46944323, seqid = chr21, start = 0, end = 46944323\n'
            for allow_overlaps_string, bounding_regions in bounding_regions.iteritems():
                print allow_overlaps_string.replace('_', ' ').capitalize() + ":"
                print_table(['Available regions'], bounding_regions)
                print
        else:
            print 'Track ' + ':'.join(track_name) + ' does not exist.'

    def help_regions(self):
        print '\n'.join([self._usage_regions(),
                        'Find all available regions for a track'])

    def _usage_regions(self):
        return 'regions <genome> <track name>\n'

if __name__ == '__main__':
    ToolShell().cmdloop()