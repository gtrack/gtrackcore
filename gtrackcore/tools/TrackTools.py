import numpy

from gtrackcore.tools.ToolExceptions import OperationNotSupportedError
from gtrackcore.track.core.Track import Track, PlainTrack
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track.graph.GraphView import LazyProtoGraphView
from gtrackcore.track.pytables.BoundingRegionHandler import BoundingRegionHandler


def get_track_view(track_name, genome_region, allow_overlaps=False):
    track = Track(track_name)
    track.addFormatReq(TrackFormatReq(allowOverlaps=allow_overlaps, borderHandling='crop'))
    return track.getTrackView(genome_region)


def count_elements(track_view):
    return track_view.getNumElements()


def sum_of_values(track_view):
    if not track_view.trackFormat.isValued():
        raise OperationNotSupportedError

    return track_view.valsAsNumpyArray().sum()


def k_highest_values(track_view, k):
    if not track_view.trackFormat.isValued():
        raise OperationNotSupportedError
    print len(track_view)
    if k > track_view.getNumElements():
        raise ValueError('The given k is larger than the number of elements of the TrackView')

    values = track_view.valsAsNumpyArray()

    return values.argsort()[-k:]


def coverage(track_view):
    format = track_view.trackFormat
    if format.isSegment():
        return track_view.endsAsNumpyArray().sum() - track_view.startsAsNumpyArray().sum()
    elif format.isPoint():
        return track_view.getNumElements()
    elif format.isPartition() or format.reprIsDense():
        return len(track_view)
    else:
        raise OperationNotSupportedError


def intersection_iter(track_view_1, track_view_2):
    base_pair_counter = 0
    track_element_iterator1 = iter(track_view_1)
    track_element_iterator2 = iter(track_view_2)
    try:
        track_el1 = track_element_iterator1.next()
        track_el2 = track_element_iterator2.next()
        while True:

            overlap = min(track_el1.end(), track_el2.end()) - max(track_el1.start(), track_el2.start())

            if overlap > 0:
                base_pair_counter += overlap

            if track_el1.end() < track_el2.end():
                track_el1 = track_element_iterator1.next()
            elif track_el1.end() > track_el2.end():
                track_el2 = track_element_iterator2.next()
            else:
                track_el1 = track_element_iterator1.next()
                track_el2 = track_element_iterator2.next()
    except StopIteration:
        return base_pair_counter


def intersection(track_view1, track_view2):
    t1_coded_starts = track_view1.startsAsNumpyArray() * 8 + 5
    t1_coded_ends = track_view1.endsAsNumpyArray() * 8 + 3
    t2_coded_starts = track_view2.startsAsNumpyArray() * 8 + 6
    t2_coded_ends = track_view2.endsAsNumpyArray() * 8 + 2

    all_sorted_coded_events = numpy.concatenate((t1_coded_starts, t1_coded_ends, t2_coded_starts, t2_coded_ends))
    all_sorted_coded_events.sort()

    all_event_codes = (all_sorted_coded_events % 8) - 4

    all_sorted_decoded_events = all_sorted_coded_events / 8
    all_event_lengths = all_sorted_decoded_events[1:] - all_sorted_decoded_events[:-1]

    cumulative_cover_status = numpy.add.accumulate(all_event_codes)

    return (all_event_lengths[cumulative_cover_status[:-1] == 3]).sum()


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

    track_name = ['testcat', 'big']
    track_name2 = ['testcat', 'big']
    genome_region_list = [genome, 'chr21', 0, 46944323]

    segment_tv1 = get_track_view(track_name, GenomeRegion(*genome_region_list))
    segment_tv2 = get_track_view(track_name2, GenomeRegion(*genome_region_list))

    print_result('intersection', track_name + ['--'] + track_name2, intersection(segment_tv1, segment_tv2))
    print_result('intersection_iter', track_name + ['--'] + track_name2, intersection_iter(segment_tv1, segment_tv2))

