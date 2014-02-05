import os
import tables

from gtrackcore.track.pytables.DatabaseHandler import BoundingRegionCreationDatabaseHandler
from gtrackcore.metadata.GenomeInfo import GenomeInfo
from gtrackcore.util.CustomExceptions import InvalidFormatError
from gtrackcore.util.CommonFunctions import getDirPath, getDatabaseFilename


class BoundingRegionHandler(object):
    def __init__(self, genome, track_name, allow_overlaps):
        assert allow_overlaps in [False, True]

        self._genome = genome
        self._track_name = track_name
        dir_path = getDirPath(track_name, genome, allowOverlaps=allow_overlaps)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        self._fn = getDatabaseFilename(dir_path, track_name)

        self._updated_chromosomes = set([])

        from gtrackcore.input.userbins.UserBinSource import MinimalBinSource
        minimal_bin_list = MinimalBinSource(genome)
        self._minimal_region = minimal_bin_list[0] if minimal_bin_list is not None else None

    def file_exists(self):
        return os.path.exists(self._fn)

    def store_bounding_regions(self, bounding_region_tuples, genome_element_chr_list, sparse):
        assert sparse in [False, True]

        temp_bounding_regions = self._create_bounding_regions_triples(bounding_region_tuples, genome_element_chr_list, sparse)

        table_description = self._create_table_description()
        db_handler = BoundingRegionCreationDatabaseHandler()
        db_handler.open()
        db_handler.create_table(table_description, len(bounding_region_tuples))

        row = db_handler.get_row()
        for br in temp_bounding_regions:
            row['seqid'] = br[0]
            row['start'] = br[1]
            row['end'] = br[2]
            row.append()

        db_handler.close()

    @staticmethod
    def _create_bounding_regions_triples(bounding_region_tuples, genome_element_chr_list, sparse):
        last_region = None
        temp_bounding_regions = []
        for br in bounding_region_tuples:
            if br.region < last_region:
                raise InvalidFormatError("Error: bounding regions in the same chromosome (sequence) are unsorted: %s > %s." % (last_region, br.region))
            if last_region.overlaps(br.region):
                raise InvalidFormatError("Error: bounding regions '%s' and '%s' overlap." % (last_region, br.region))
            if last_region.end == br.region.start:
                raise InvalidFormatError("Error: bounding regions '%s' and '%s' are adjoining (there is no gap between them)." % (last_region, br.region))
            if len(br.region) < 1:
                raise InvalidFormatError("Error: bounding region '%s' does not have positive length." % br.region)
            if not sparse and len(br.region) != br.elCount:
                raise InvalidFormatError("Error: track type representation is dense, but the length of bounding region '%s' is not equal to the element count: %s != %s" % (br.region, len(br.region), br.elCount))

            temp_bounding_regions.append((br.region.chr, br.region.start, br.region.end))

            last_region = br.region
        if sparse:
            diff = set(genome_element_chr_list) - set([br_triple[0] for br_triple in temp_bounding_regions])
            if len(diff) > 0:
                raise InvalidFormatError('Error: some chromosomes (sequences) contains data, but has no bounding regions: %s' % ', '.join(diff))

        return temp_bounding_regions

    @staticmethod
    def _create_table_description():
        return {
                'seqid': tables.StringCol(100),
                'start': tables.Int32Col(),
                'end': tables.Int32Col(),
               }

    def _update_contents_if_necessary(self, chr):
        raise NotImplementedError

    def get_bounding_region_info(self, region):
        raise NotImplementedError

    def _get_total_element_count_for_chr(self, chr):
        raise NotImplementedError

    def get_total_element_count(self):
        return sum(self._get_total_element_count_for_chr(chr) for chr in GenomeInfo.getExtendedChrList(self._genome))

    def get_all_bounding_regions_for_chr(self, chr):
        raise NotImplementedError

    def get_all_bounding_regions(self):
        raise NotImplementedError
