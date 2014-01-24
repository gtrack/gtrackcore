import tables
import os

from stat import S_IRWXU, S_IRWXG, S_IROTH
from collections import OrderedDict
from gtrackcore.util.CustomExceptions import AbstractClassError
from gtrackcore.util.CommonFunctions import getDirPath

class OutputManager(object):

    def __new__(cls, genome, trackName, allowOverlaps, geSourceManager):
        if len(geSourceManager.getAllChrs()) == 1:
            return OutputManagerSingleChr.__new__(OutputManagerSingleChr, genome, trackName, \
                                                  allowOverlaps, geSourceManager)
        else:
            return OutputManagerSeveralChrs.__new__(OutputManagerSeveralChrs, genome, trackName, \
                                                    allowOverlaps, geSourceManager)


    def _create_single_track_database(self, genome, chr, track_name, allow_overlaps, geSourceManager):

        self._database_filename = getDirPath(track_name, genome, chr, allow_overlaps) + track_name[-1] + '.h5'

        self._h5file = tables.open_file(self._database_filename, mode="w", title=track_name[-1])

        #Create all groups
        group = self._h5file.create_group(self._h5file.root, track_name[0], track_name[0])
        for track_name_part in track_name[1:-1]:
            group = self._h5file.create_group(group, track_name_part, track_name_part)

        #Setup table
        self._column_descriptions = self._create_column_dictionary(geSourceManager, chr)
        self._table = self._h5file.create_table(group, track_name[-1], self.column_descriptions, track_name[-1], \
                                                expectedrows=geSourceManager.getNumElements())

        #Create index for start and end columns
        self._table.cols.start.create_index()
        self._table.cols.end.create_index()


    def _create_column_dictionary(self, geSourceManager, chr):
        max_string_lengths = geSourceManager.getMaxStrLensForChr(chr)
        datatype_dict = {}

        for column in geSourceManager.getPrefixList():
            if column in ['start', 'end']:
                datatype_dict[column] = tables.UInt32Col()
            elif column is 'strand':
                datatype_dict[column] = tables.UInt8Col()
            elif column in ['id', 'edges']:
                datatype_dict[column] = tables.StringCol(max_string_lengths[column])
            elif column is 'val':
                if geSourceManager.getValDataType() == 'S':
                    datatype_dict[column] = tables.StringCol(max(2, max_string_lengths[column]))
                else:
                    datatype_dict[column] = tables.Float64Col()
            elif column is 'weights':
                if geSourceManager.getEdgeWeightDataType() == 'S':
                    datatype_dict[column] = tables.StringCol(max(2, max_string_lengths[column]))
                else:
                    datatype_dict[column] = tables.Float64Col()

        return datatype_dict

    def _add_element_as_row(self, genome_element):
        """can probably be optimized"""
        row = self._table.row
        for column in self._column_descriptions.keys():
            row[column] = genome_element.__dict__[column]

        row.append()

    def _close_and_flush_DB_file(self):
        self._h5file.close()
        os.chmod(self._database_filename, S_IRWXU|S_IRWXG|S_IROTH)

    def writeElement(self, genomeElement):
        raise AbstractClassError()

    def writeRawSlice(self, genomeElement):
        raise AbstractClassError()

    def close(self):
        raise AbstractClassError()

class OutputManagerSingleChr(OutputManager):
    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)

    def __init__(self, genome, track_name, allow_overlaps, geSourceManager):
        allChrs = geSourceManager.getAllChrs()
        assert len(allChrs) == 1
        self._create_single_track_database(genome, allChrs[0], track_name, allow_overlaps, geSourceManager)

    def writeElement(self, genomeElement):
        print "writeElement"
        self._add_element_as_row(genomeElement)

    def writeRawSlice(self, genomeElement):
        """What's the purpose of this?"""
        pass
        #self._outputDir.writeRawSlice(genomeElement)

    def close(self):
        self._close_and_flush_DB_file()


class OutputManagerSeveralChrs(OutputManager):
    """Check if we need this class.  will we get a performance boost if each chromosome is in its own table? """
    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)

    def __init__(self, genome, trackName, allowOverlaps, geSourceManager):
        allChrs = geSourceManager.getAllChrs()
        assert len(allChrs) > 1

        self._outputDirs = OrderedDict()
        for chr in allChrs:
            self._outputDirs[chr] = self._create_table \
                    (genome, chr, trackName, allowOverlaps, geSourceManager)

    def writeElement(self, genomeElement):
        self._outputDirs[genomeElement.chr].writeElement(genomeElement)

    def writeRawSlice(self, genomeElement):
        self._outputDirs[genomeElement.chr].writeRawSlice(genomeElement)

    def close(self):
        for dir in self._outputDirs.values():
            dir.close()
