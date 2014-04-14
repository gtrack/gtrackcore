from gtrackcore.track.pytables.database.Database import DatabaseReader
from gtrackcore.track.pytables.database.Queries import BoundingRegionQueries
from gtrackcore.util.CustomExceptions import ShouldNotOccurError
from gtrackcore.util.pytables.NameFunctions import get_database_filename, get_track_table_node_names


ITERATION_THRESHOLD = 1000  # the critical region length where iteration is better performance-wise:


def start_and_end_indices(genome_region, track_name, allow_overlaps, track_format):
    assert genome_region.genome == genome_region.genome

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
    if track_format.isSegment():
        start_index = _start_index_for_segments(table, genome_region, br_start, br_stop)
        if start_index is not None:
            end_index = _end_index_for_segments_and_points(table, genome_region, start_index, br_stop)
        else:
            return 0, 0

    elif track_format.isPoint():
        start_index = _start_index_for_points(table, genome_region, br_start, br_stop)
        if start_index is not None:
            end_index = _end_index_for_segments_and_points(table, genome_region, start_index, br_stop)
        else:
            return 0, 0

    elif track_format.isPartition():
        start_index = _start_index_for_partitions(table, genome_region, br_start, br_stop)
        if start_index is not None:
            end_index = _end_index_for_partitions(table, genome_region, start_index, br_stop)
        else:
            return 0, 0

    else:
        raise ShouldNotOccurError

    if end_index is None:
        end_index = br_stop

    return start_index, end_index


def _start_index_for_segments(table, genome_region, min_index, max_index):
    min_index, max_index = _improve_min_and_max_index(table, min_index, max_index, 'start', genome_region.start)

    for row in table.iterrows(start=min_index, stop=max_index):
        if (row['start'] < genome_region.start < row['end']) or (genome_region.start <= row['start'] < genome_region.end):
            return row.nrow
    return None


def _start_index_for_points(table, genome_region, min_index, max_index):
    min_index, max_index = _improve_min_and_max_index(table, min_index, max_index, 'start', genome_region.start)

    for row in table.iterrows(start=min_index, stop=max_index):
        if genome_region.start <= row['start'] < genome_region.end:
            return row.nrow
    return None


def _start_index_for_partitions(table, genome_region, min_index, max_index):
    min_index, max_index = _improve_min_and_max_index(table, min_index, max_index, 'end', genome_region.start)

    for row in table.iterrows(start=min_index, stop=max_index):
        if genome_region.start <= row['end'] < genome_region.end:
            return row.nrow
    return None


def _end_index_for_segments_and_points(table, genome_region, min_index, max_index):
    min_index, max_index = _improve_min_and_max_index(table, min_index, max_index, 'start', genome_region.end)

    for row in table.iterrows(start=min_index, stop=max_index):
        if row['start'] >= genome_region.end:
            return row.nrow
    return None


def _end_index_for_partitions(table, genome_region, min_index, max_index):
    min_index, max_index = _improve_min_and_max_index(table, min_index, max_index, 'end', genome_region.end)

    for row in table.iterrows(start=min_index, stop=max_index):
        if row['end'] >= genome_region.end:
            return row.nrow + 1
    return None


def _improve_min_and_max_index(table, min_index, max_index, column, region_side):
    while max_index - min_index > ITERATION_THRESHOLD:
        mid_index = min_index + ((max_index - min_index) / 2)
        row = table[mid_index]

        if row[column] < region_side:
            min_index = mid_index + 1
        else:
            max_index = mid_index

    return min_index, max_index
