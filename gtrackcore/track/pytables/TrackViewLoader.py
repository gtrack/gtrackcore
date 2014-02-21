from collections import OrderedDict

from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track.format.TrackFormat import TrackFormat
from gtrackcore.track.memmap.BoundingRegionShelve import BoundingRegionShelve
from gtrackcore.util.CompBinManager import CompBinManager
from gtrackcore.util.CommonConstants import RESERVED_PREFIXES
from gtrackcore.track.pytables.DatabaseHandler import TrackTableReader, BrTableReader
from gtrackcore.util.CustomDecorators import print_args
from gtrackcore.util.pytables.DatabaseQueries import TrackQueries, BrQueries


class TrackViewLoader:

    @staticmethod
    def loadTrackView(trackData, region, borderHandling, allowOverlaps, trackName):
        """
        trackData : see TrackSource.getTrackData
        region : see GenomeRegion
        """

        extra_column_names = [column_name for column_name in trackData if column_name not in RESERVED_PREFIXES.keys()]
        reserved_columns = [trackData[column_name] if column_name in trackData else None
                            for column_name in RESERVED_PREFIXES]
        extra_columns = [trackData[column_name] if column_name in trackData else None
                         for column_name in extra_column_names]

        track_format = TrackFormat(*(reserved_columns + [OrderedDict(zip(extra_column_names, extra_columns))]))
        start_index, end_index = TrackViewLoader._get_start_and_end_indices(
            region, trackName, allowOverlaps, track_format)

        for column in reserved_columns + extra_columns:
            if column is not None:
                column.set_offset(start_index, end_index)

        arg_list = [region] + reserved_columns + [borderHandling, allowOverlaps] + \
                   [OrderedDict(zip(extra_column_names, extra_columns))]

        return TrackView(* arg_list, track_name=trackName)

    @staticmethod
    def _get_start_and_end_indices(region, track_name, allow_overlaps, track_format):
        br_queries = BrQueries(track_name, region.genome, allow_overlaps)
        if track_format.getFormatName() in ['Function', 'Linked function']:
            start_index, end_index = br_queries.start_and_end_indices(region)
        else:
            track_queries = TrackQueries(track_name, region.genome, allow_overlaps)
            start_index, end_index = track_queries.start_and_end_indices(region, track_format)

        return start_index, end_index