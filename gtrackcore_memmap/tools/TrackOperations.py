from functools import partial
import math
import sys

import numpy

from gtrackcore_memmap.metadata import GenomeInfo
from gtrackcore_memmap.track.core.GenomeRegion import GenomeRegion

from gtrackcore_memmap.track.core.Track import Track
from gtrackcore_memmap.track.format.TrackFormat import TrackFormatReq
from gtrackcore_memmap.track.graph.GraphView import LazyProtoGraphView
from gtrackcore_memmap.track.memmap.BoundingRegionShelve import BoundingRegionShelve
from gtrackcore_memmap.util.tools.ToolExceptions import OperationNotSupportedError


def get_track_format(track_name, allow_overlaps, genome_regions):
    pass


def get_track_view(track_name, allow_overlaps, genome_region):
    track = Track(track_name)
    track.addFormatReq(TrackFormatReq(allowOverlaps=allow_overlaps, borderHandling='crop'))
    return track.getTrackView(genome_region)


def get_graph_view(track_name, allow_overlaps, genome_regions):
    proto_graph_views = []

    for region in genome_regions:
        track_view = get_track_view(track_name, allow_overlaps, region)
        proto_graph_view = LazyProtoGraphView.createInstanceFromTrackView(track_view)
        proto_graph_views.append(proto_graph_view)

    merged_proto_graph_views = LazyProtoGraphView.mergeProtoGraphViews(proto_graph_views)
    graph_view = merged_proto_graph_views.getClosedGraphVersion()

    return graph_view


def count_elements(track_name, allow_overlaps, genome_regions):
    count_sum = numpy.int64(0)
    for region in genome_regions:
        track_view = get_track_view(track_name, allow_overlaps, region)
        count_sum += track_view.getNumElements()
    return count_sum


def sum_of_values(track_name, allow_overlaps, genome_regions):
    value_sum = numpy.float128(0)
    for region in genome_regions:
        track_view = get_track_view(track_name, allow_overlaps, region)
        value_sum += track_view.valsAsNumpyArray().sum()
    return value_sum


def sum_of_weights(track_name, allow_overlaps, genome_regions):
    weight_sum = numpy.float128(0)
    for region in genome_regions:
        track_view = get_track_view(track_name, allow_overlaps, region)
        weight_sum += numpy.nansum(track_view.weightsAsNumpyArray())
    return weight_sum


def sum_of_weights_iter(track_name, allow_overlaps, genome_regions):
    graph_view = get_graph_view(track_name, allow_overlaps, genome_regions)
    weight_sum = numpy.float128(0)
    for edge in graph_view.getEdgeIter():
        if not math.isnan(edge.weight):
            weight_sum += edge.weight
    return weight_sum


def coverage(track_name, allow_overlaps, genome_regions):
    coverage_sum = numpy.int64(0)
    for region in genome_regions:
        track_view = get_track_view(track_name, allow_overlaps, region)
        coverage_sum += track_view.endsAsNumpyArray().sum() - track_view.startsAsNumpyArray().sum()
    return coverage_sum


def overlap_of_track_views_iter(track_view_1, track_view_2):
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


def overlap_of_track_views(track_view1, track_view2):
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


def overlap_iter(track_name1, allow_overlaps1, track_name2, allow_overlaps2, genome_regions):
    intersection_sum = numpy.int64(0)
    for region in genome_regions:
        track_view1 = get_track_view(track_name1, allow_overlaps1, region)
        track_view2 = get_track_view(track_name2, allow_overlaps2, region)
        intersection_sum += overlap_of_track_views_iter(track_view1, track_view2)
    return intersection_sum


def overlap(track_name1, allow_overlaps1, track_name2, allow_overlaps2, genome_regions):
    intersection_sum = numpy.int64(0)
    for region in genome_regions:
        track_view1 = get_track_view(track_name1, allow_overlaps1, region)
        track_view2 = get_track_view(track_name2, allow_overlaps2, region)
        intersection_sum += overlap_of_track_views(track_view1, track_view2)
    return intersection_sum


def count_elements_in_all_bounding_regions(genome, track_name, allow_overlaps):
    bounding_regions = BoundingRegionShelve(genome, track_name, allow_overlaps).get_all_bounding_regions()
    return count_elements(track_name, allow_overlaps, bounding_regions)


def k_highest_values(track_view, k):
    if not track_view.trackFormat.isValued():
        raise OperationNotSupportedError
    print len(track_view)
    if k > track_view.getNumElements():
        raise ValueError('The given k is larger than the number of elements of the TrackView')

    values = track_view.valsAsNumpyArray()

    return values.argsort()[-k:]


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'usage: TrackTools <tool name>'
        sys.exit(1)

    operation = sys.argv[1]

    chromosomes = (GenomeRegion('hg19', chr, 0, len)
                   for chr, len in GenomeInfo.GENOMES['hg19']['size'].iteritems())

    oper_func = lambda: 'N/A'

    if operation.startswith('overlap'):
        tn1 = 'Sequence:Repeating elements'.split(':')
        tn2 = 'Chromatin:Roadmap Epigenomics:H3K27me3:ENCODE_wgEncodeBroadHistoneGm12878H3k27me3StdPk'.split(':')
        if operation == 'overlap_iter':
            oper_func = partial(overlap_iter, tn1, False, tn2, False, chromosomes)
        elif operation == 'overlap':
            oper_func = partial(overlap, tn1, False, tn2, False, chromosomes)

    elif operation == 'count':
        tn = 'Phenotype and disease associations:GWAS:NHGRI GWAS Catalog:Parkinson\'s disease'.split(':')
        oper_func = partial(count_elements, tn, False, chromosomes)

    from time import time
    print 'Running', operation + '...'
    start = time()
    res = oper_func()
    end = time()
    print 'Result for', operation + ':', res
    print 'Time used:', end - start