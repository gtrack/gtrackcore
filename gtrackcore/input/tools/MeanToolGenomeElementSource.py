from gtrackcore.input.core.ToolGenomeElementSource import ToolGenomeElementSource
from gtrackcore.input.core.GenomeElement import GenomeElement
from gtrackcore.track.core.Track import Track
from gtrackcore.track.format.TrackFormat import TrackFormatReq


class MeanToolGenomeElementSource(ToolGenomeElementSource):
    _VERSION = '1.0'
    TOOL_NAME = 'mean'

    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)

    def __init__(self, *args, **kwArgs):
        ToolGenomeElementSource.__init__(self, *args, **kwArgs)
        assert 'segment_track' in self._tool_input and 'function_track' in self._tool_input \
            and 'genome_regions' in self._tool_input

        self._segment_track = Track(self._tool_input['segment_track']['name'])
        self._segment_track.addFormatReq(TrackFormatReq(allowOverlaps=self._tool_input['segment_track']['allow_overlaps']))
        self._function_track = Track(self._tool_input['function_track']['name'])
        self._function_track.addFormatReq(TrackFormatReq(allowOverlaps=self._tool_input['function_track']['allow_overlaps']))
        self._genome_regions = self._tool_input['genome_regions']

    def getPrefixList(self):
        return ['chr', 'start', 'end', 'val']

    def getValDataType(self):
        return 'float64'  # TODO: fix to be dynamic

    def getValDim(self):
        return 1  # TODO: fix to be dynamic

    def __iter__(self):
        self._ge_generator = self._mean_generator()
        return self
        
    def next(self):
        return self._ge_generator.next()

    def _mean_generator(self):
        for genome_region in self._genome_regions:
            segment_track_view = self._segment_track.getTrackView(genome_region)
            function_track_view = self._function_track.getTrackView(genome_region)
            values = function_track_view.valsAsNumpyArray()
            try:
                for segment in segment_track_view:
                    start, end = segment.start(), segment.end()

                    values_within_segment = values[start:end]
                    mean = sum(values_within_segment) / len(values_within_segment)

                    yield GenomeElement(self._genome, genome_region.chr, start, end, val=mean)
            except StopIteration:
                pass
