from collections import OrderedDict

from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track.format.TrackFormat import TrackFormat
from gtrackcore.track.pytables.database.Queries import TrackQueries
from gtrackcore.util.CommonConstants import RESERVED_PREFIXES


class TrackViewLoader:

    @staticmethod
    def loadTrackView(trackData, region, borderHandling, allowOverlaps, trackName):
        extra_column_names = [column_name for column_name in trackData if column_name not in RESERVED_PREFIXES.keys()]
        reserved_columns = [trackData[column_name] if column_name in trackData else None
                            for column_name in RESERVED_PREFIXES]
        extra_columns = [trackData[column_name] if column_name in trackData else None
                         for column_name in extra_column_names]

        track_format = TrackFormat(*(reserved_columns + [OrderedDict(zip(extra_column_names, extra_columns))]))

        queries = TrackQueries(region.genome, trackName, allowOverlaps)
        start_index, end_index = queries.start_and_end_indices(region, track_format)

        for column in reserved_columns + extra_columns:
            if column is not None:
                column.offset = (start_index, end_index)

        arg_list = [region] + reserved_columns + [borderHandling, allowOverlaps] + \
                   [OrderedDict(zip(extra_column_names, extra_columns))]

        return TrackView(* arg_list, track_name=trackName, start_index=start_index, end_index=end_index)
