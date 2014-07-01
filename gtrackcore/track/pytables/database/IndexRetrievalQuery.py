from gtrackcore.track.pytables.database.Database import DatabaseReader
from gtrackcore.track.pytables.database.Queries import BoundingRegionQueries
from gtrackcore.util.CustomExceptions import ShouldNotOccurError
from gtrackcore.util.pytables.NameFunctions import get_database_filename, get_track_table_node_names


def start_and_end_indices(genome_region, track_name, allow_overlaps, track_format):
    br_queries = BoundingRegionQueries(genome_region.genome, track_name, allow_overlaps)
    bounding_region = br_queries.enclosing_bounding_region_for_region(genome_region)

    if len(bounding_region) > 0:
        br_start_index, br_end_index = (bounding_region[0]['start_index'], bounding_region[0]['end_index'])
    else:
        return 0, 0  # if region is empty

    if track_format.reprIsDense():
        start_index = br_start_index + (genome_region.start - bounding_region[0]['start'])
        end_index = start_index + len(genome_region)
    else:
        database_filename = get_database_filename(genome_region.genome, track_name, allow_overlaps=allow_overlaps)
        db_reader = DatabaseReader(database_filename)
        db_reader.open()
        track_table_node_names = get_track_table_node_names(genome_region.genome, track_name, allow_overlaps)
        table = db_reader.get_table(track_table_node_names)
        start_index, end_index = _get_region_start_and_end_indices(genome_region, table, br_start_index,
                                                                   br_end_index, track_format)
        db_reader.close()

    return start_index, end_index


def _get_region_start_and_end_indices(genome_region, table, br_start, br_stop, track_format):
    query = _build_start_and_end_indices_query(track_format)

    region_indices = table.get_where_list(query, start=br_start, stop=br_stop,
                                          condvars={
                                              'region_start': genome_region.start,
                                              'region_end': genome_region.end
                                          })

    # start_index, end_index
    return (region_indices[0], region_indices[-1] + 1) if len(region_indices) > 0 else (0, 0)


def _build_start_and_end_indices_query(track_format):
    if track_format.isSegment():
        query = '(end > region_start) & (start < region_end)'

    elif track_format.isPoint():
        query = '(start >= region_start) & (start < region_end)'

    elif track_format.isPartition():
        query = '(end >= region_start) & (end <= region_end)'

    else:
        raise ShouldNotOccurError

    return query
