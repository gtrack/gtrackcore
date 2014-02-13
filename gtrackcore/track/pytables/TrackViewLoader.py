from collections import OrderedDict

from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track.format.TrackFormat import TrackFormat
from gtrackcore.track.memmap.BoundingRegionShelve import BoundingRegionShelve
from gtrackcore.util.CompBinManager import CompBinManager
from gtrackcore.util.CommonConstants import RESERVED_PREFIXES
from gtrackcore.track.pytables.DatabaseHandler import TrackTableReader
from gtrackcore.util.CustomDecorators import print_args
from gtrackcore.util.pytables.DatabaseQueries import TrackQueries


class TrackViewLoader:

    @staticmethod
    def loadTrackView(trackData, region, borderHandling, allowOverlaps, trackName=[]):
        """
        trackData : see TrackSource.getTrackData {'id' : smartmemmap}
        region : see GenomeRegion
        """

        queries = TrackQueries(TrackTableReader(trackName, region.genome, allowOverlaps))
        start_index, end_index = queries.region_start_and_end_indices(region)

        extra_column_names = [column_name for column_name in trackData if column_name not in RESERVED_PREFIXES.keys()]
        reserved_columns = [trackData[column_name] if column_name in trackData else None
                            for column_name in RESERVED_PREFIXES]
        extra_columns = [trackData[column_name] if column_name in trackData else None
                         for column_name in extra_column_names]

        for column in reserved_columns + extra_columns:
            if column is not None:
                column.set_offset(start_index, end_index)

        arg_list = [region] + reserved_columns + [borderHandling, allowOverlaps] + \
                   [OrderedDict(zip(extra_column_names, extra_columns))]

        return TrackView( *(arg_list) )

