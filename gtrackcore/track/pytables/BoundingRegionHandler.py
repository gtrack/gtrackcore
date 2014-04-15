import tables
from gtrackcore.track.pytables.database.CommonTableFunctions import create_table_indices

from gtrackcore.track.pytables.database.Database import DatabaseReader, DatabaseWriter
from gtrackcore.util.CommonFunctions import prettyPrintTrackName
from gtrackcore.util.pytables.NameFunctions import get_database_filename, get_br_table_node_names
from gtrackcore.track.pytables.database.Queries import BoundingRegionQueries
from gtrackcore.metadata.GenomeInfo import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.util.CustomExceptions import InvalidFormatError, BoundingRegionsNotAvailableError, DBNotExistError, \
    OutsideBoundingRegionError


class BoundingRegionHandler(object):
    def __init__(self, genome, track_name, allow_overlaps):
        assert allow_overlaps in [False, True]
        self._genome = genome
        self._track_name = track_name
        self._allow_overlaps = allow_overlaps
        self._max_chr_len = 1

        self._database_filename = get_database_filename(genome, track_name, allow_overlaps=allow_overlaps)
        self._db_reader = DatabaseReader(self._database_filename)
        self._br_node_names = get_br_table_node_names(genome, track_name, allow_overlaps)

        self._br_queries = BoundingRegionQueries(genome, track_name, allow_overlaps)

    def table_exists(self):
        try:
            self._db_reader.open()
            table_exist = self._db_reader.table_exists(self._br_node_names)
            self._db_reader.close()
        except DBNotExistError:
            table_exist = False
        return table_exist

    def store_bounding_regions(self, bounding_region_tuples, genome_element_chr_list, sparse):
        assert sparse in [False, True]

        temp_bounding_regions = self._create_bounding_regions_triples(bounding_region_tuples, genome_element_chr_list, sparse)

        table_description = self._create_table_description()
        db_writer = DatabaseWriter(self._database_filename)
        db_writer.open()
        table = db_writer.create_table(self._br_node_names, table_description, len(bounding_region_tuples))

        row = table.row
        for br in temp_bounding_regions:
            row['chr'] = br[0]
            row['start'] = br[1]
            row['end'] = br[2]
            row['start_index'] = br[3]
            row['end_index'] = br[4]
            row['element_count'] = br[5]
            row.append()
        table.flush()
        db_writer.close()

    def _create_bounding_regions_triples(self, bounding_region_tuples, genome_element_chr_list, sparse):
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

            start_index, end_index = (total_elements, total_elements + br.elCount)
            total_elements += br.elCount

            self._max_chr_len = max(self._max_chr_len, len(br.region.chr))

            temp_bounding_regions.append((br.region.chr, br.region.start, br.region.end, start_index, end_index, br.elCount))

            last_region = br.region
        if sparse:
            diff = set(genome_element_chr_list) - set([br_sextuple[0] for br_sextuple in temp_bounding_regions])
            if len(diff) > 0:
                raise InvalidFormatError('Error: some chromosomes (sequences) contains data, but has no bounding regions: %s' % ', '.join(diff))

        return temp_bounding_regions

    def _create_table_description(self):
        return {
            'chr': tables.StringCol(self._max_chr_len, pos=0),
            'start': tables.Int32Col(pos=1),
            'end': tables.Int32Col(pos=2),
            'start_index': tables.Int32Col(pos=3),
            'end_index': tables.Int32Col(pos=4),
            'element_count': tables.Int32Col(pos=5)
        }

    def get_enclosing_bounding_region(self, region):
        bounding_regions = self._br_queries.enclosing_bounding_region_for_region(region)

        if len(bounding_regions) != 1:
            raise OutsideBoundingRegionError("The analysis region '%s' is outside the bounding regions of track: %s"\
                                             % (region, prettyPrintTrackName(self._track_name)))

        return GenomeRegion(chr=bounding_regions[0]['chr'], start=bounding_regions[0]['start'], end=bounding_regions[0]['end'])

    def get_all_enclosing_bounding_regions(self, region):
        bounding_regions = self._br_queries.all_bounding_regions_enclosed_by_region(region)

        if len(bounding_regions) == 0:
            raise OutsideBoundingRegionError("The analysis region '%s' is outside the bounding regions of track: %s" \
                                             % (region, prettyPrintTrackName(self._track_name)))

        return [GenomeRegion(chr=br['chr'], start=br['start'], end=br['end']) for br in bounding_regions]

    def get_all_touching_bounding_regions(self, region):
        bounding_regions = self._br_queries.all_bounding_regions_touched_by_region(region)

        if len(bounding_regions) == 0:
            raise OutsideBoundingRegionError("The analysis region '%s' is outside the bounding regions of track: %s" \
                                             % (region, prettyPrintTrackName(self._track_name)))

        return [GenomeRegion(chr=br['chr'], start=br['start'], end=br['end']) for br in bounding_regions]

    def get_all_bounding_regions(self):
        if not self.table_exists():
            from gtrackcore.util.CommonFunctions import prettyPrintTrackName
            raise BoundingRegionsNotAvailableError('Bounding regions not available for track: ' + \
                                                   prettyPrintTrackName(self._track_name))

        self._db_reader.open()
        br_table = self._db_reader.get_table(self._br_node_names)
        table_iterator = br_table.iterrows()

        for row in table_iterator:
            yield GenomeRegion(self._genome, row['chr'], row['start'], row['end'])

        self._db_reader.close()

    def get_total_element_count(self):
        return sum(self.get_total_element_count_for_chr(chr) for chr in GenomeInfo.getExtendedChrList(self._genome))

    def get_total_element_count_for_chr(self, chr):
        return self._br_queries.total_element_count_for_chr(chr)
