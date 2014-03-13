from gtrackcore.util.pytables.DatabaseQueries import BoundingRegionQueries, TrackQueries

def get_start_and_end_indices(region, track_name, allow_overlaps, track_format):
    br_queries = BoundingRegionQueries(region.genome, track_name, allow_overlaps)
    bounding_region = br_queries.enclosing_bounding_region_for_region(region)
    if len(bounding_region) > 0:
        br_start_index, br_end_index = (bounding_region[0]['start_index'], bounding_region[0]['end_index'])
    else:
        return 0, 0  # if region is empty

    if track_format.reprIsDense():
        start_index = br_start_index + (region.start - bounding_region[0]['start'])
        end_index = start_index + len(region)
    else:
        track_queries = TrackQueries(region.genome, track_name, allow_overlaps)
        start_index, end_index = track_queries.start_and_end_indices(region, br_start_index,
                                                                     br_end_index, track_format)

    return start_index, end_index