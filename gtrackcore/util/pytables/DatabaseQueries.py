class DatabaseQueries(object):

    def __init__(self, db_handler):
        self._db_handler = db_handler

    def total_element_count_for_chr(self, chromosome):
        self._db_handler.open()
        table = self._db_handler.br_table

        result = [row['element_count'] for row in table.where('(seqid == chr)', condvars={'chr': chromosome})]

        self._db_handler.close()

        return result[0] if len(result) > 0 else 0

    def get_start_end_indices(self, genome_region):
        self._db_handler.open()
        table = self._db_handler.track_table

        start_index = table.get_where_list('(seqid == chr) & (end > region_start)',
                                           sort=True, condvars={
                                               'chr': genome_region.chr,
                                               'region_start': genome_region.start
                                           })[0]

        end_index = table.get_where_list('(seqid == chr) & (start < region_end)',
                                         sort=True, condvars={
                                             'chr': genome_region.chr,
                                             'region_end': genome_region.end,
                                         })[-1] + 1  # end exclusive

        self._db_handler.close()

        return start_index, end_index