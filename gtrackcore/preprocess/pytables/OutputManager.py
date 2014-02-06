import tables
import os

from stat import S_IRWXU, S_IRWXG, S_IROTH
from gtrackcore.util.CommonFunctions import getDirPath, getDatabaseFilename
from gtrackcore.track.pytables.DatabaseHandler import TrackTableCreator

class OutputManager(object):

    def __init__(self, genome, trackName, allowOverlaps, geSourceManager):

        self._create_single_track_database(genome, trackName, allowOverlaps, geSourceManager)


    def _create_single_track_database(self, genome, track_name, allow_overlaps, geSourceManager):
        dir_path = getDirPath(track_name, genome, allowOverlaps=allow_overlaps)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        self._database_filename = getDatabaseFilename(dir_path, track_name)

        self._table_creator = TrackTableCreator(track_name, genome, allow_overlaps)

        # Open db and create track table
        self._table_description = self._create_column_dictionary(geSourceManager)
        self._table_creator.open()
        self._table_creator.create_table(self._table_description,
                                      expectedrows=geSourceManager.getNumElements())

    def _create_column_dictionary(self, ge_source_manager):
        max_string_lengths = self._get_max_str_lens_over_all_chromosomes(ge_source_manager)
        data_type_dict = {}
        max_num_edges = self._get_max_num_edges_over_all_chromosomes(ge_source_manager)

        max_seqid_len = ge_source_manager.getMaxChrStrLen()
        data_type_dict['seqid'] = tables.StringCol(max_seqid_len)

        for column in ge_source_manager.getPrefixList():
            if column in ['start', 'end']:
                data_type_dict[column] = tables.Int32Col()
            elif column is 'strand':
                data_type_dict[column] = tables.Int8Col()
            elif column is 'id':
                data_type_dict[column] = tables.StringCol(max_string_lengths[column])
            elif column is 'edges':
                shape = self._get_shape(max_num_edges, 0)  # correct shape ??
                data_type_dict[column] = tables.StringCol(max_string_lengths[column], shape=shape)
            elif column in ['val', 'weights']:
                if column is 'val':
                    data_type = ge_source_manager.getValDataType()
                    data_type_dim = ge_source_manager.getValDim()
                elif column is 'weights':
                    data_type = ge_source_manager.getEdgeWeigthDataType()
                    data_type_dim = ge_source_manager.getEdgeWeigthDim()

                shape = self._get_shape(max_num_edges, data_type_dim)

                #TODO: fix shape hack...
                data_type_dict[column] = {
                    'int8': tables.Int8Col(shape=shape),
                    'int32': tables.Int32Col(),
                    'float32': tables.Float32Col(shape=shape),
                    'float64': tables.Float64Col(shape=shape),
                    'S': tables.StringCol(max(2, max_string_lengths[column]), shape=shape)
                }.get(data_type, tables.Float64Col(shape=shape))  # Defaults to Float64Col
            else:
                data_type_dict[column] = tables.StringCol(max(2, max_string_lengths[column]))

        return data_type_dict

    @staticmethod
    def _get_shape(max_num_edges, data_type_dim):
        return tuple(([max(1, max_num_edges)] if max_num_edges is not None else []) +
                    ([data_type_dim] if data_type_dim > 1 else []))

    @staticmethod
    def _get_max_str_lens_over_all_chromosomes(ge_source_manager):
        max_str_lens_dictionaries = [ge_source_manager.getMaxStrLensForChr(chr)\
                                  for chr in ge_source_manager.getAllChrs()]
        from collections import Counter
        from operator import or_

        max_string_lengths = reduce(or_, map(Counter, max_str_lens_dictionaries))
        return max_string_lengths

    @staticmethod #bytt med den som finnes i ge_source_manager
    def _get_max_num_edges_over_all_chromosomes(ge_source_manager):
        return max(ge_source_manager.getMaxNumEdgesForChr(chr) for chr in ge_source_manager.getAllChrs())


    def _add_element_as_row(self, genome_element):
        row = self._table_creator.get_row()
        for column in self._table_description.keys():
            if column in genome_element.__dict__ and column is not 'extra':
                row[column] = genome_element.__dict__[column]
            elif column is 'seqid':
                row['seqid'] = genome_element.__dict__['chr']
            else:  # Get extra column
                row[column] = genome_element.__dict__['extra'][column]
        row.append()
        self._table_creator.flush()

    def writeElement(self, genomeElement):
        self._add_element_as_row(genomeElement)

    def writeRawSlice(self, genomeElement):
        """What's the purpose of this?"""
        pass
        #self._outputDir.writeRawSlice(genomeElement)

    def close(self):
        self._table_creator.close()
        os.chmod(self._database_filename, S_IRWXU | S_IRWXG | S_IROTH)