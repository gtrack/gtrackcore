from gtrackcore.track.pytables.database.DatabaseUtils import DatabaseUtils
from gtrackcore.track.pytables.database.Database import DatabaseReader
from gtrackcore.util.pytables.DatabaseQueries import BoundingRegionQueries, TrackQueries

def get_start_and_end_indices(region, track_name, allow_overlaps, track_format):

    database_filename = DatabaseUtils.get_database_filename(region.genome, track_name,
                                                            allow_overlaps=allow_overlaps)

    br_node_names = DatabaseUtils.get_br_table_node_names(region.genome, track_name, allow_overlaps)
    db_reader = DatabaseReader(database_filename)
    br_queries = BoundingRegionQueries(db_reader, br_node_names)

    bounding_region = br_queries.enclosing_bounding_region_for_region(region)
    if len(bounding_region) > 0:
        br_start_index, br_end_index = (bounding_region[0]['start_index'], bounding_region[0]['end_index'])
    else:
        return 0, 0  # if region is empty

    if track_format.reprIsDense():
        start_index = br_start_index + (region.start - bounding_region[0]['start'])
        end_index = start_index + len(region)
    else:
        track_table_node_names = DatabaseUtils.get_track_table_node_names(region.genome, track_name, allow_overlaps)
        track_queries = TrackQueries(db_reader, track_table_node_names)
        start_index, end_index = track_queries.start_and_end_indices(region, br_start_index,
                                                                     br_end_index, track_format)

    return start_index, end_index