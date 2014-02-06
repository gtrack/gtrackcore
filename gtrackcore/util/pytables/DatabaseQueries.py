import tables

class DatabaseQueries(object):

    def __init__(self, db_handler):
        self._db_handler = db_handler

    def total_element_count_for_chr(self, chromosome):
        self._db_handler.open()
        table = self._db_handler.br_table

        result = [row['element_count'] for row in table.where('(seqid == chr)', condvars={'chr': chromosome})]

        self._db_handler.close()

        return result[0] if len(result) > 0 else 0

