from gtrackcore.tools.ToolExceptions import OperationNotSupportedError
from gtrackcore.track.core.Track import PlainTrack
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track.pytables.BoundingRegionHandler import BoundingRegionHandler


def get_track_view(track_name, genome_region):
    track = PlainTrack(track_name)
    return track.getTrackView(genome_region)


def count_elements(track_view):
    return track_view.getNumElements()


def k_highest_values(track_view, k):
    format_name = track_view.trackFormat.getFormatName()
    if format_name not in ['Function', 'Linked function', 'Valued points', 'Linked valued segments', 'Valued segments',
                       'Linked valued segments']:
        raise OperationNotSupportedError
    print len(track_view)
    if k > track_view.getNumElements():
        raise ValueError('The given k is larger than the number of elements of the TrackView')

    values = track_view.valsAsNumpyArray()

    return values.argsort()[-k:]


def coverage(track_view):
    format_name = track_view.trackFormat.getFormatName()
    if format_name in ['Segments', 'Valued segments', 'Linked segments', 'Linked valued segments']:
        return track_view.endsAsNumpyArray().sum() - track_view.startsAsNumpyArray().sum()
    elif format_name in ['Points', 'Valued points', 'Linked points', 'Linked valued points', 'Function', 'Linked function']:
        return track_view.getNumElements()
    elif format_name in ['Genome partition', 'Step function', 'Linked genome partition', 'Linked step function', 'Linked base pairs']:
        return len(track_view)
    else:
        raise OperationNotSupportedError


def intersection(track_view_1, track_view_2):
    pass


def count_elements_in_all_bounding_regions(track_name, genome='testgenome', allow_overlaps=False):
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
    genome = 'testgenome'
    track_name = ['testcat', 'point']
    func_track =['testcat', 'test', 'function']
    genome_region_list = [genome, 'chr21', 0, 46944323]

    tv = get_track_view(func_track, GenomeRegion(*genome_region_list))

    print k_highest_values(tv, 3)


