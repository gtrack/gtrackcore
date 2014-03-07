import os
import sys
from gtrackcore.core.Config import Config
from gtrackcore.track.core.Track import PlainTrack
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track.pytables.BoundingRegionHandler import BoundingRegionHandler
from gtrackcore.util.CommonFunctions import createOrigPath, createPath, convertTNstrToTNListFormat



def get_track_view(track_name, genome_region):
    track = PlainTrack(track_name)
    return track.getTrackView(genome_region)


def count_elements(track_view):
    return track_view.getNumElements()


def coverage(track_view):
    if not track_view.trackFormat.isDense() and track_view.trackFormat.isInterval():
        return track_view.endsAsNumpyArray().sum() - track_view.startsAsNumpyArray().sum()
    elif not track_view.trackFormat.isDense():
        return count_elements(track_view)
    elif track_view.trackFormat.isInterval():
        return len(track_view)
    else:
        return count_elements_in_all_bounding_regions(track_view._track_name)


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
    genome_region_list = [genome, 'chr21', 0, 36944323]

    tv = get_track_view(track_name, GenomeRegion(*genome_region_list))

    print coverage(tv)

