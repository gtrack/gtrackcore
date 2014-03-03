from collections import OrderedDict

from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track.format.TrackFormat import TrackFormat
from gtrackcore.util.CommonConstants import RESERVED_PREFIXES
from gtrackcore.util.pytables.DatabaseQueries import TrackQueries, BrQueries


class TrackViewLoader:
    @staticmethod
    def loadTrackView(trackData, region, borderHandling, allowOverlaps, trackName):
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
                column.offset = (start_index, end_index)

        arg_list = [region] + reserved_columns + [borderHandling, allowOverlaps] + \
                   [OrderedDict(zip(extra_column_names, extra_columns))]

        return TrackView(* arg_list, track_name=trackName)

    @staticmethod
    def _get_start_and_end_indices(region, track_name, allow_overlaps, track_format):
        br_queries = BrQueries(region.genome, track_name, allow_overlaps)
        br_start_index, br_end_index = br_queries.start_and_end_indices(region)
        if track_format.getFormatName() in ['Function', 'Linked function', 'Linked base pairs']:
            return br_start_index, br_end_index
        else:
            track_queries = TrackQueries(region.genome, track_name, allow_overlaps)
            start_index, end_index = track_queries.start_and_end_indices(region, br_start_index,
                                                                         br_end_index, track_format)
            return start_index, end_index
