import tables
import numpy

from gtrackcore.track.pytables.DatabaseHandler import BoundingRegionTableCreator, BrTableReader
from gtrackcore.util.pytables.DatabaseQueries import BrQueries
from gtrackcore.metadata.GenomeInfo import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.util.CustomExceptions import InvalidFormatError, BoundingRegionsNotAvailableError, DBNotExistError


class BoundingRegionHandler(object):
    def __init__(self, genome, track_name, allow_overlaps):
        assert allow_overlaps in [False, True]

        self._genome = genome
        self._track_name = track_name
        self._allow_overlaps = allow_overlaps

        self._table_reader = BrTableReader(genome, track_name, allow_overlaps)
        self._queries = BrQueries(genome, track_name, allow_overlaps)

        self._updated_chromosomes = set([])

        from gtrackcore.input.userbins.UserBinSource import MinimalBinSource
        minimal_bin_list = MinimalBinSource(genome)
        self._minimal_region = minimal_bin_list[0] if minimal_bin_list is not None else None

    def table_exists(self):
        try:
            self._table_reader.open()
            table_exist = self._table_reader.table_exists()
            self._table_reader.close()
        except DBNotExistError:
            table_exist = False
        return table_exist

    def store_bounding_regions(self, bounding_region_tuples, genome_element_chr_list, sparse):
        assert sparse in [False, True]

        temp_bounding_regions = self._create_bounding_regions_triples(bounding_region_tuples, genome_element_chr_list, sparse)

        table_description = self._create_table_description()
        db_creator = BoundingRegionTableCreator(self._genome, self._track_name, self._allow_overlaps)
        db_creator.open()
        db_creator.create_table(table_description, len(bounding_region_tuples))

        row = db_creator.get_row()
        for br in temp_bounding_regions:
            row['chr'] = br[0]
            row['start'] = br[1]
            row['end'] = br[2]
            row['start_index'] = br[3]
            row['end_index'] = br[4]
            row['element_count'] = br[5]
            row.append()

        db_creator.close()

    @staticmethod
    def _create_bounding_regions_triples(bounding_region_tuples, genome_element_chr_list, sparse):
        last_region = None
        total_elements = 0
        temp_bounding_regions = []
        for br in bounding_region_tuples:
            if last_region is None or br.region.chr != last_region.chr:
                if br.region.chr in [bounding_region[0] for bounding_region in temp_bounding_regions]:
                    raise InvalidFormatError("Error: bounding region (%s) is not grouped with previous bounding regions of the same chromosome (sequence)." % br.region)
            else:
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

            # TODO: Should end_index be +1 ?!
            start_index, end_index = (total_elements, total_elements + br.elCount)
            total_elements += br.elCount

            temp_bounding_regions.append((br.region.chr, br.region.start, br.region.end, start_index, end_index, br.elCount))

            last_region = br.region
        if sparse:
            diff = set(genome_element_chr_list) - set([br_sextuple[0] for br_sextuple in temp_bounding_regions])
            if len(diff) > 0:
                raise InvalidFormatError('Error: some chromosomes (sequences) contains data, but has no bounding regions: %s' % ', '.join(diff))

        return temp_bounding_regions

    def _create_table_description(self):
        return {
                'chr': tables.StringCol(self._max_len_chr(), pos=0),
                'start': tables.Int32Col(pos=1),
                'end': tables.Int32Col(pos=2),
                'start_index': tables.Int32Col(pos=3),
                'end_index': tables.Int32Col(pos=4),
                'element_count': tables.Int32Col(pos=5),
               }

    # TODO: find max len
    def _max_len_chr(self):
        return 100

    def _update_contents_if_necessary(self, chr):
        raise NotImplementedError

    def get_bounding_region_info(self, region):
        raise NotImplementedError

    def get_total_element_count(self):
        return sum(self._queries.total_element_count_for_chr(chr) for chr in GenomeInfo.getExtendedChrList(self._genome))

    def get_all_bounding_regions_for_chr(self, chr):
        raise NotImplementedError

    def get_all_bounding_regions(self):
        if not self.table_exists():
            from gtrackcore.util.CommonFunctions import prettyPrintTrackName
            raise BoundingRegionsNotAvailableError('Bounding regions not available for track: ' + \
                                                   prettyPrintTrackName(self._track_name))

        self._table_reader.open()
        table_iterator = self.table_reader.table.iterrows()

        for row in table_iterator:
            yield GenomeRegion(self._genome, row['chr'], row['start'], row['end'])

        self._table_reader.close()



