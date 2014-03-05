from gtrackcore.track.core.Track import PlainTrack
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track.pytables.BoundingRegionHandler import BoundingRegionHandler

def get_track_view(track_name, genome_region):
    track = PlainTrack(track_name)
    return track.getTrackView(genome_region)


def count_elements(track_view):
    return track_view.getNumElements()


def coverage(track_view):
    return track_view.endsAsNumpyArray().sum() - track_view.startsAsNumpyArray().sum()


def intersection(track_view_1, track_view_2):
    pass


def count_elements_in_all_bounding_regions(track_name, genome='TestGenome', allow_overlaps=False):
    bounding_regions = BoundingRegionHandler(genome, track_name, allow_overlaps).get_all_bounding_regions()
    track = PlainTrack(track_name)

    num_elements = 0
    for tv in [track.getTrackView(region) for region in bounding_regions]:
        num_elements += count_elements(tv)
    return num_elements

def print_result(tool, track_name, result):
    print
    print tool, 'for', ":".join(track_name)
    print 'Result:', result
    print


if __name__ == '__main__':
    track_name = ['testcat', 'kmer-point']
    genome_region_list = ['testgenome', 'chr21', 0, 46944323]

    genome_region = GenomeRegion(* genome_region_list)
    track_view = get_track_view(track_name, genome_region)

    num_elements = count_elements(track_view)
    num_all_elements = count_elements_in_all_bounding_regions(track_name)
    bp_coverage = coverage(track_view)

    print_result("count_elements", track_name, num_elements)
    print_result("count_all_elements", track_name, num_all_elements)
    print_result("coverage", track_name, bp_coverage)
