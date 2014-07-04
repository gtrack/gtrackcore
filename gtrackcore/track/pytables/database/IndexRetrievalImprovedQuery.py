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


def _get_first_index(table, query, condvars, start, stop):
    for row in table.where(query, start=start, stop=stop, condvars=condvars):
        return row.nrow
    return None


def _get_region_start_and_end_indices(genome_region, table, br_start, br_stop, track_format):
    start_index_query, end_index_query = _build_start_and_end_index_queries(track_format)

    condvars = {
        'region_start': genome_region.start,
        'region_end': genome_region.end
    }

    start_index = _get_first_index(table, start_index_query, condvars, br_start, br_stop)
    end_index = _get_first_index(table, end_index_query, condvars, br_start, br_stop)

    if track_format.isPartition() and end_index is not None:
        end_index += 1

    if start_index is not None and end_index is None:
        end_index = br_stop

    if start_index is None and end_index is None:
        return 0, 0
    else:
        return start_index, end_index


def _build_start_and_end_index_queries(track_format):
    if track_format.isSegment():
        start_index_query = '(start >= region_start) | ((end > region_start) & (start < region_end))'
        end_index_query = '(start > region_end)'

    elif track_format.isPoint():
        start_index_query = '(start >= region_start) & (start < region_end)'
        end_index_query = '(start > region_end)'

    elif track_format.isPartition():
        start_index_query = '(end >= region_start) & (end <= region_end)'
        end_index_query = '(end >= region_end)'

    else:
        raise ShouldNotOccurError

    return start_index_query, end_index_query
