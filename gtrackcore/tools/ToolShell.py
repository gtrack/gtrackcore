import re
import sys
import os
import cmd

from gtrackcore.tools import TrackTools
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track.core.Track import PlainTrack
from gtrackcore.core.Config import Config
from gtrackcore.track.pytables.BoundingRegionHandler import BoundingRegionHandler
from gtrackcore.util.CustomExceptions import BoundingRegionsNotAvailableError


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
        self._update_available_tracks()
        self._cached_bounding_regions = {}

    def cmdloop(self):
        try:
            cmd.Cmd.cmdloop(self)
        except KeyboardInterrupt as e:
            self.do_exit(None)

    def print_result(self, tool, track_name, result):
        print
        print tool, 'for', ":".join(track_name)
        print 'Result:', result
        print

    def _get_track_view(self, track_name, genome_region):
        track = PlainTrack(track_name)
        return track.getTrackView(genome_region)

    def _update_available_tracks(self):
        data = []
        base_dirs = os.listdir(Config.PROCESSED_DATA_PATH)

        for base_dir in base_dirs:
            for directory, dirnames, filenames in os.walk(Config.PROCESSED_DATA_PATH + os.sep + base_dir):
                if len(filenames) > 0:
                    track_name_list = directory.split(base_dir)[1].split('/')
                    genome = base_dir
                    track_name = track_name_list[1:]
                    track_format = self._get_track_format(genome, track_name)
                    track_type = track_format.getFormatName()

                    data.append([genome, ':'.join(track_name), track_type])

        self._available_tracks = sorted(data, key=lambda x: (x[0], x[1]))

    def _get_track_format(self, genome, track_name):
        track = PlainTrack(track_name)
        track_view = track.getTrackView(GenomeRegion(genome, '', 0, 0))
        return track_view.trackFormat

    def _extract_bounding_regions(self, genome, track_name):
        cache_key = genome + ':' + ':'.join(track_name)
        if cache_key in self._cached_bounding_regions:
            return self._cached_bounding_regions[cache_key]

        bounding_regions = {}
        for allow_overlaps in [True, False]:
            bounding_region_handler = BoundingRegionHandler(genome, track_name, allow_overlaps)
            try:
                regions = [region for region in bounding_region_handler.get_all_bounding_regions()]

                if allow_overlaps:
                    bounding_regions['with overlaps'] = regions
                else:
                    bounding_regions['no overlaps'] = regions
            except BoundingRegionsNotAvailableError:
                pass

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

        for key, allow_overlaps_regions in bounding_regions.iteritems():
            for bounding_region in allow_overlaps_regions:
                if region.chr == bounding_region.chr:
                    if region.start >= bounding_region.start:
                        if region.end <= bounding_region.end:
                            if region.end is None:
                                region.end = bounding_region.end
                            return True

                    elif region.start is None:
                        region.start = bounding_region.start
                        region.end = bounding_region.end
                        return True
        return False

    def _parse_region(self, genome, textual_region):
        all_regex = r'\w+:\d+-\d+$'
        seqid_and_start_regex = r'\w+:\d+-$'
        seqid_regex = r'\w+$'

        region_tuple = tuple(textual_region.replace('-', ':').split(':'))
        start = end = None

        from re import match
        if match(all_regex, textual_region) is not None:
            seqid, start, end = region_tuple
        elif match(seqid_and_start_regex, textual_region) is not None:
            seqid = region_tuple[0]
            start = region_tuple[1]
        elif match(seqid_regex, textual_region) is not None:
            seqid = region_tuple[0]
        else:
            return None

        if start is not None:
            start = int(start)
        if end is not None:
            end = int(end)

        return GenomeRegion(genome=genome, chr=seqid, start=start, end=end)

    def _autocomplete_genome_and_track_name(self, command, text, line, begidx, endidx):
        command_length = len(command) + 1
        number_of_typed_commands = len(re.findall(r'\s+', line))
        if begidx <= command_length:
            completions = [f[0] for f in self._available_tracks if text is None or f[0].startswith(text)]
        elif number_of_typed_commands is 1:
            completions = [f[1] for f in self._available_tracks if text is None or f[1].startswith(text)]
        elif number_of_typed_commands is 2:
            if line[-1] == ':' or len(text) > 0:
                written = line.split()[2]
                completions = [f[1][len(written) - len(text):] for f in self._available_tracks if f[1].startswith(written)]
                if len(completions) == 1 and completions[0] == text:
                    completions.remove(text)
            else:
                completions = [f[1] for f in self._available_tracks if text is None or f[1].startswith(text)]

        return completions

    def _is_valid_region(self, genome, track_name, genome_region):
        if genome_region is None:
            print 'Region is in wrong format'
            print 'Example region: chr21:0-46944323.\nWhere seqid = chr21, start = 0, end = 46944323\n'
            return False

        if not self._is_legal_region(genome, track_name, genome_region):
            print 'Region is not bounded by a bounding region and is thus not legal.'
            return False
        return True

    def _is_valid_track_name(self, genome, track_name):
        if not self._is_track_available(genome, track_name):
            print 'Track "' + ':'.join(track_name) + '" not available for genome "' + genome + '".'
            return False
        return True

    def do_list(self, line):
        print_table(['Genome', 'Track name', 'Track type'], self._available_tracks)

    def do_exit(self, line):
        print "Exiting..."
        sys.exit()

    def do_EOF(self, line):
        self.do_exit(line)

    def do_coverage(self, line):
        argv = line.split()
        if len(argv) < 3:
            print 'Wrong usage'
            print self._usage_coverage()
            return

        genome = argv[0]
        track_name = argv[1].split(":")
        textual_region = argv[2]
        genome_region = self._parse_region(genome, textual_region)

        if not self._is_valid_region(genome, track_name, genome_region):
            return
        if not self._is_valid_track_name(genome, track_name):
            return

        track_view = self._get_track_view(track_name, genome_region)
        coverage = TrackTools.coverage(track_view)
        self.print_result('coverage', track_name, coverage)

    def complete_coverage(self, text, line, begidx, endidx):
        return self._autocomplete_genome_and_track_name('coverage', text, line, begidx, endidx)

    def help_coverage(self):
        print '\n'.join([self._usage_coverage(),
                         'Find coverage of a single track'])

    def _usage_coverage(self):
        return 'Usage: coverage <genome> <track name> <region>\n'


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
            textual_bounding_regions = {allow_overlaps_string: [[region.chr + ':' + str(region.start) + '-' +
                                                                 str(region.end)] for region in bounding_regions]
                                        for allow_overlaps_string, bounding_regions in bounding_regions.iteritems()}

            print 'Example: chr21:0-46944323, seqid = chr21, start = 0, end = 46944323\n'
            for allow_overlaps_string, bounding_regions in textual_bounding_regions.iteritems():
                print allow_overlaps_string.capitalize() + ':'
                print_table(['Available regions'], bounding_regions)
                print
        else:
            print 'Track ' + ':'.join(track_name) + ' does not exist.'

    def complete_regions(self, text, line, begidx, endidx):
        return self._autocomplete_genome_and_track_name('regions', text, line, begidx, endidx)

    def help_regions(self):
        print '\n'.join([self._usage_regions(),
                        'Find all available regions for a track'])

    def _usage_regions(self):
        return 'Usage: regions <genome> <track name>\n'

    def do_k_highest(self, line):
        argv = line.split()
        if len(argv) < 3:
            print 'Wrong usage'
            print self._usage_coverage()
            return

        try:
            k = int(raw_input('Input k: '))
        except ValueError:
            print 'k is not an integer'
            return

        genome = argv[0]
        track_name = argv[1].split(":")
        textual_region = argv[2]
        genome_region = self._parse_region(genome, textual_region)

        if not self._is_valid_region(genome, track_name, genome_region):
            return

        if not self._is_valid_track_name(genome, track_name):
            return

        track_view = self._get_track_view(track_name, genome_region)
        k_elements_with_highest_values = TrackTools.k_highest_values(track_view, k)
        self.print_result('k_highest_values', track_name, k_elements_with_highest_values)

    def complete_k_highest(self, text, line, begidx, endidx):
        return self._autocomplete_genome_and_track_name('k_highest', text, line, begidx, endidx)

    def _usage_k_highest(self):
        print 'Usage: k_highest <genome> <track name>'

    def help_k_highest(self):
        print '\n'.join([self._usage_k_highest(),
                         'Get the GenomeElements with the k highest values'])

if __name__ == '__main__':
    ToolShell().cmdloop()