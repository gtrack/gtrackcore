import tables
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


    def _create_database(self, genome, chr, track_name, allow_overlaps, geSourceManager):

        database_filename = getDirPath(track_name, genome, chr, allow_overlaps) + track_name[-1] + '.h5'

        self._h5file = tables.open_file(self._database_filename, mode = "w", title = track_name[-1])

        group = self._h5file.create_group(self._h5file.root, track_name[0], track_name[0])
        #Create all groups
        for track_name_part in track_name[1:-1]:
            group = self._h5file.create_group(group, track_name_part, track_name_part)

        datatype_dict = _create_columns_dictionary(geSourceManager, chr)
        print datatype_dict

        self._table = self._h5file.create_table(group, track_name[-1], datatype_dict, track_name[-1])


    def _create_columns_dictionary(geSourceManager, chr):
        datatype_dict = {}
        max_string_lengths = geSourceManager.getMaxStrLensForChr(chr)

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

    def _create_table(self, genome, chr, trackName, allowOverlaps, geSourceManager):

        from gtrackcore.metadata.GenomeInfo import GenomeInfo
        GenomeInfo.getChrLen(genome, chr)

    def writeElement(self, genomeElement):
        raise AbstractClassError()

    def writeRawSlice(self, genomeElement):
        raise AbstractClassError()

    def close(self):
        raise AbstractClassError()

class OutputManagerSingleChr(OutputManager):
    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)

    def __init__(self, genome, trackName, allowOverlaps, geSourceManager):
        allChrs = geSourceManager.getAllChrs()
        assert len(allChrs) == 1

        self._create_table(genome, allChrs[0], trackName, allowOverlaps, geSourceManager)

    def writeElement(self, genomeElement):
        self._outputDir.writeElement(genomeElement)

    def writeRawSlice(self, genomeElement):
        self._outputDir.writeRawSlice(genomeElement)

    def close(self):
        self._outputDir.close()


class OutputManagerSeveralChrs(OutputManager):
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
