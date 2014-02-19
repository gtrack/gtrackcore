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

    def _build_start_and_end_indices_query(self, track_format):
        if track_format.isInterval() and not track_format.isDense():  # has start and end
            query = '(end > region_start) & (start < region_end)'
        elif track_format.isInterval():  # has start but not end
            query = '(start >= region_start) & (start < region_end)'
        elif not track_format.isDense():  # has end but not start
            query = '(end >= region_start) & (end < region_end)'
        else:  # has neither start nor end
            query = ''
        return '(seqid == chr) & ' + query

    def start_and_end_indices(self, genome_region, track_format):
        query = self._build_start_and_end_indices_query(track_format)

        self._db_handler.open()
        table = self._db_handler.table
        
        region_indices = table.get_where_list(query, sort=True,
                                              condvars={
                                                  'chr': genome_region.chr,
                                                  'region_start': genome_region.start,
                                                  'region_end': genome_region.end
                                              })

        start_index = region_indices[0]
        end_index = region_indices[-1] + 1

        self._db_handler.close()

        return start_index, end_index