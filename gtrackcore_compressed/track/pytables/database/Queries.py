from gtrackcore_compressed.track.pytables.database.Database import DatabaseReader
from gtrackcore_compressed.util.pytables.NameFunctions import get_database_filename, get_br_table_node_names


class DatabaseQueries(object):

    def __init__(self, genome, track_name, allow_overlaps):
        self._genome = genome
        self._track_name = track_name
        self._allow_overlaps = allow_overlaps

        database_filename = get_database_filename(genome, track_name, allow_overlaps=allow_overlaps)
        self._db_reader = DatabaseReader(database_filename)


class BoundingRegionQueries(DatabaseQueries):

    def __init__(self, genome, track_name, allow_overlaps):
        super(BoundingRegionQueries, self).__init__(genome, track_name, allow_overlaps)
        self._table_node_names = get_br_table_node_names(genome, track_name, allow_overlaps)

    def total_element_count_for_chr(self, chromosome):
        self._db_reader.open()
        table = self._db_reader.get_table(self._table_node_names)

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
        table = self._db_reader.get_table(self._table_node_names)

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
        table = self._db_reader.get_table(self._table_node_names)

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
