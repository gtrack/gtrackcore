import tables
import os

from stat import S_IRWXU, S_IRWXG, S_IROTH
from gtrackcore.util.CommonFunctions import getDirPath, getDatabaseFilename
from gtrackcore.track.pytables.DatabaseHandler import DatabaseCreationHandler

class OutputManager(object):

    def __init__(self, genome, trackName, allowOverlaps, geSourceManager):

        self._create_single_track_database(genome, trackName, allowOverlaps, geSourceManager)


    def _create_single_track_database(self, genome, track_name, allow_overlaps, geSourceManager):
        dir_path = getDirPath(track_name, genome, allowOverlaps=allow_overlaps)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        self._database_filename = getDatabaseFilename(dir_path, track_name)

        self._db_handler = DatabaseCreationHandler(track_name, genome, allow_overlaps)

        # Open db and create track table
        self._table_description = self._create_column_dictionary(geSourceManager)
        self._db_handler.open()
        self._db_handler.create_table(self._table_description, \
                                                    expectedrows=geSourceManager.getNumElements())


        #weightDim : geSourceManager.getEdgeWeightDim() = dataTypeDim
        #maxNumEdges : geSourceManager.getMaxNumEdgesForChr(chr) = elementDim
        #weightDataType : geSourceManager.getEdgeWeightDataType()
        #valDim : geSourceManager.getValDim() = dataTypeDim
        #valDataType : geSourceManager.getValDataType()
        #size : geSourceManager.getNumElementsForChr(chr)

    def _create_column_dictionary(self, ge_source_manager):
        max_string_lengths = self._get_max_str_lens_over_all_chromosomes(ge_source_manager)
        data_type_dict = {}

        maxNumEdges = self._get_max_num_edges_over_all_chromosomes(ge_source_manager)
        for column in ge_source_manager.getPrefixList():
            if column in ['start', 'end']:
                data_type_dict[column] = tables.UInt32Col()
            elif column is 'strand':
                data_type_dict[column] = tables.UInt8Col()
            elif column is 'id':
                data_type_dict[column] = tables.StringCol(max_string_lengths[column])
            elif column is 'edges':
                data_type_dict[column] = tables.StringCol(max_string_lengths[column], shape=(maxNumEdges, 1))
            elif column in ['val', 'weights']:
                if column is 'val':
                    data_type = ge_source_manager.getValDataType()
                    data_type_dim = ge_source_manager.getValDim()
                elif column is 'weights':
                    data_type = ge_source_manager.getEdgeWeigthDataType()
                    data_type_dim = ge_source_manager.getEdgeWeigthDim()

                shape = tuple(([max(1, maxNumEdges)] if maxNumEdges is not None else []) + \
                        ([data_type_dim] if data_type_dim > 1 else []))

                data_type_dict[column] = {
                    'int8': tables.Int8Col(shape=shape),
                    'int32': tables.Int32Col(shape=shape),
                    'float32': tables.Float32Col(shape=shape),
                    'float64': tables.Float64Col(shape=shape),
                    'S': tables.StringCol(max(2, max_string_lengths[column]), shape=shape)
                }.get(data_type, tables.Float64Col(shape=shape))  # Defaults to Float64Col
            else:
                data_type_dict[column] = tables.StringCol(max(2, max_string_lengths[column]))
        return data_type_dict

    def _get_max_str_lens_over_all_chromosomes(self, ge_source_manager):
        max_str_lens_dictionaries = [ge_source_manager.getMaxStrLensForChr(chr)\
                                  for chr in ge_source_manager.getAllChrs()]
        from collections import Counter
        from operator import or_

        max_string_lengths = reduce(or_, map(Counter, max_str_lens_dictionaries))
        return max_string_lengths

    def _get_max_num_edges_over_all_chromosomes(self, ge_source_manager):
        return max(ge_source_manager.getMaxNumEdgesForChr(chr) for chr in ge_source_manager.getAllChrs())


    def _add_element_as_row(self, genome_element):
        row = self._db_handler.get_row()
        for column in self._table_description.keys():
            if column in genome_element.__dict__ and column is not 'extra':
                row[column] = genome_element.__dict__[column]
            else:  # Get extra column
                row[column] = genome_element.__dict__['extra'][column]
        row.append()
        self._db_handler.flush()

    def writeElement(self, genomeElement):
        self._add_element_as_row(genomeElement)

    def writeRawSlice(self, genomeElement):
        """What's the purpose of this?"""
        pass
        #self._outputDir.writeRawSlice(genomeElement)

    def close(self):
        self._db_handler.close()
        os.chmod(self._database_filename, S_IRWXU|S_IRWXG|S_IROTH)