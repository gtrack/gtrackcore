from gtrackcore.track.pytables.DatabaseHandler import BrTableReader, TrackTableReader
from gtrackcore.util.CustomExceptions import ShouldNotOccurError


class DatabaseQueries(object):
    def __init__(self, db_handler):
        self._db_handler = db_handler


class BoundingRegionQueries(DatabaseQueries):
    def __init__(self, genome, track_name, allow_overlaps):
        db_handler = BrTableReader(genome, track_name, allow_overlaps)
        super(BoundingRegionQueries, self).__init__(db_handler)
        self._track_name = track_name

    def total_element_count_for_chr(self, chromosome):
        self._db_handler.open()
        table = self._db_handler.table

        result = [row['element_count'] for row in table.where('(chr == region_chr)',
                                                              condvars={'region_chr': chromosome})]

        self._db_handler.close()

        return sum(result) if len(result) > 0 else 0

    def enclosing_bounding_region_for_region(self, genome_region):
        query = '(chr == region_chr) & (start <= region_start) & (end >= region_end)'
        return self._all_bounding_regions_for_region(genome_region, query)

    def all_bounding_regions_enclosed_by_region(self, genome_region):
        query = '(chr == region_chr) & (start >= region_start) & (end < region_end)'
        return self._all_bounding_regions_for_region(genome_region, query)

    def all_bounding_regions_touched_by_region(self, genome_region):
        query = '(chr == region_chr) & (start < region_end) & (end > region_start)'
        return self._all_bounding_regions_for_region(genome_region, query)

    def all_bounding_regions(self):
        self._db_handler.open()
        table = self._db_handler.table

        bounding_regions = [{'chr': row['chr'],
                             'start': row['start'],
                             'end': row['end'],
                             'start_index': row['start_index'],
                             'end_index': row['end_index']}
                            for row in table]

        self._db_handler.close()

        return bounding_regions

    def _all_bounding_regions_for_region(self, genome_region, query):
        self._db_handler.open()
        table = self._db_handler.table

        bounding_regions = [{'chr': row['chr'],
                             'start': row['start'],
                             'end': row['end'],
                             'start_index': row['start_index'],
                             'end_index': row['end_index']}
                            for row in table.where(query,
                                                   condvars={
                                                       'region_chr': genome_region.chr,
                                                       'region_start': genome_region.start,
                                                       'region_end': genome_region.end
                                                   })]

        self._db_handler.close()

        return bounding_regions


class TrackQueries(DatabaseQueries):

    def __init__(self, genome, track_name, allow_overlaps):
        db_handler = TrackTableReader(genome, track_name, allow_overlaps)
        super(TrackQueries, self).__init__(db_handler)

    @staticmethod
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

    def start_and_end_indices(self, genome_region, br_start, br_stop, track_format):
        query = self._build_start_and_end_indices_query(track_format)

        self._db_handler.open()
        table = self._db_handler.table
        region_indices = table.get_where_list(query, sort=True, start=br_start, stop=br_stop,
                                              condvars={
                                                  'region_start': genome_region.start,
                                                  'region_end': genome_region.end
                                              })
        self._db_handler.close()

        # start_index, end_index
        return (region_indices[0], region_indices[-1] + 1) if len(region_indices) > 0 else (0, 0)

