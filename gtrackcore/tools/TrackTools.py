from gtrackcore.track.core.Track import PlainTrack
from gtrackcore.track.core.GenomeRegion import GenomeRegion

def get_track_view(track_name, genome_region):
    track = PlainTrack(track_name)
    return track.getTrackView(genome_region)


def count_elements(track_view):
    return track_view.getNumElements()


def coverage(track_view):
    return track_view.endsAsNumpyArray().sum() - track_view.startsAsNumpyArray().sum()


def intersection(track_view_1, track_view_2):
    pass



def print_result(tool, track_name, result):
    print
    print tool, 'for', ":".join(track_name)
    print 'Result:', result
    print


if __name__ == '__main__':
    track_name = ['testcat', 'kmerpoint']
    genome_region_list = ['testgenome', 'chr21', 0, 46944323]

    genome_region = GenomeRegion(* genome_region_list)
    track_view = get_track_view(track_name, genome_region)

    num_elements = count_elements(track_view)
    bp_coverage = coverage(track_view)

    print_result("count_elements", track_name, num_elements)
    print_result("coverage", track_name, bp_coverage)
