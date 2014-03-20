from gtrackcore.util.CustomExceptions import ShouldNotOccurError


class DatabaseQueries(object):
    def __init__(self, db_reader):
        self._db_reader = db_reader


class BoundingRegionQueries(DatabaseQueries):
    def __init__(self, db_reader, br_node_names):
        super(BoundingRegionQueries, self).__init__(db_reader)
        self._br_node_names = br_node_names

    def total_element_count_for_chr(self, chromosome):
        self._db_reader.open()
        table = self._db_reader.get_table(self._br_node_names)

        result = [row['element_count'] for row in table.where('(chr == region_chr)',
                                                              condvars={'region_chr': chromosome})]

        self._db_reader.close()

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
        self._db_reader.open()
        table = self._db_reader.get_table(self._br_node_names)

        bounding_regions = [{'chr': row['chr'],
                             'start': row['start'],
                             'end': row['end'],
                             'start_index': row['start_index'],
                             'end_index': row['end_index']}
                            for row in table]

        self._db_reader.close()

        return bounding_regions

    def _all_bounding_regions_for_region(self, genome_region, query):
        self._db_reader.open()
        table = self._db_reader.get_table(self._br_node_names)

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

        self._db_reader.close()

        return bounding_regions


class TrackQueries(DatabaseQueries):

    def __init__(self, db_reader, track_table_node_names):
        super(TrackQueries, self).__init__(db_reader)
        self._track_table_node_names = track_table_node_names

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

        self._db_reader.open()
        table = self._db_reader.get_table(self._track_table_node_names)
        region_indices = table.get_where_list(query, sort=True, start=br_start, stop=br_stop,
                                              condvars={
                                                  'region_start': genome_region.start,
                                                  'region_end': genome_region.end
                                              })
        self._db_reader.close()

        # start_index, end_index
        return (region_indices[0], region_indices[-1] + 1) if len(region_indices) > 0 else (0, 0)

