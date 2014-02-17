from gtrackcore.util.CustomDecorators import timeit


class DatabaseQueries(object):

    def __init__(self, db_handler):
        self._db_handler = db_handler


class BrQueries(DatabaseQueries):
    def __init__(self, db_handler):
        super(BrQueries, self).__init__(db_handler)

    def total_element_count_for_chr(self, chromosome):
        self._db_handler.open()
        table = self._db_handler.table

        result = [row['element_count'] for row in table.where('(seqid == chr)', condvars={'chr': chromosome})]

        self._db_handler.close()

        return result[0] if len(result) > 0 else 0


class TrackQueries(DatabaseQueries):

    def __init__(self, db_handler):
        super(TrackQueries, self).__init__(db_handler)

    def region_start_and_end_indices(self, genome_region):
        self._db_handler.open()
        table = self._db_handler.table

        region_indices = table.get_where_list('(seqid == chr) & (end > region_start) & (start < region_end)',
                                              sort=True, condvars={
                                              'chr': genome_region.chr,
                                              'region_start': genome_region.start,
                                              'region_end': genome_region.end
                                              })

        start_index = region_indices[0]
        end_index = region_indices[-1] + 1

        self._db_handler.close()

        return start_index, end_index