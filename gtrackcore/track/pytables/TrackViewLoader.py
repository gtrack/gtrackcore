from collections import OrderedDict

from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track.format.TrackFormat import TrackFormat
from gtrackcore.track.memmap.BoundingRegionShelve import BoundingRegionShelve
from gtrackcore.util.CompBinManager import CompBinManager
from gtrackcore.util.CommonConstants import RESERVED_PREFIXES
from gtrackcore.track.pytables.DatabaseHandler import TrackTableReader


class TrackViewLoader:

    @staticmethod
    def loadTrackView(trackData, region, borderHandling, allowOverlaps, trackName=[]):
        """
        trackData : see TrackSource.getTrackData {'id' : smartmemmap}
        region : see GenomeRegion
        """

        extra_column_names = [column_name for column_name in trackData if column_name not in RESERVED_PREFIXES.keys()]
        reserved_columns = [trackData[column_name] for column_name in RESERVED_PREFIXES]
        extra_columns = [trackData[column_name] for column_name in extra_column_names]

        sliced_reserved_columns = [(column[region.start:region.end] if column is not None else None)
                                   for column in reserved_columns]
        sliced_extra_columns = [(column[region.start:region.end] if column is not None else None)
                                for column in extra_columns]

        arg_list = [region] + sliced_reserved_columns + [borderHandling, allowOverlaps] + \
                   [OrderedDict(zip(extra_column_names, sliced_extra_columns))]
        track_view = TrackView( *(arg_list) )

        return track_view
