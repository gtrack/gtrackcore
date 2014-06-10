import itertools
from gtrackcore_compressed.input.core.ToolGenomeElementSource import ToolGenomeElementSource
from gtrackcore_compressed.input.core.GenomeElement import GenomeElement
from gtrackcore_compressed.track.core.Track import Track
from gtrackcore_compressed.track.format.TrackFormat import TrackFormatReq


class UnionToolGenomeElementSource(ToolGenomeElementSource):
    _VERSION = '1.0'
    TOOL_NAME = 'union'

    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)

    def __init__(self, *args, **kwArgs):
        ToolGenomeElementSource.__init__(self, *args, **kwArgs)
        assert 'track1' in self._tool_input and 'track2' in self._tool_input \
            and 'genome_regions' in self._tool_input

        self._track1 = Track(self._tool_input['track1']['name'])
        self._track1.addFormatReq(TrackFormatReq(allowOverlaps=self._tool_input['track1']['allow_overlaps']))
        self._track2 = Track(self._tool_input['track2']['name'])
        self._track2.addFormatReq(TrackFormatReq(allowOverlaps=self._tool_input['track2']['allow_overlaps']))
        self._genome_regions = self._tool_input['genome_regions']

    def getPrefixList(self):
        return ['chr', 'start', 'end']

    def hasNoOverlappingElements(self):
        return False

    def __iter__(self):
        self._ge_generator = self._union_generator()
        return self
        
    def next(self):
        return self._ge_generator.next()

    def _union_generator(self):
        for genome_region in self._genome_regions:
            track_view_1 = self._track1.getTrackView(genome_region)
            track_view_2 = self._track2.getTrackView(genome_region)

            for track_el in itertools.chain(track_view_1, track_view_2):
                yield GenomeElement(self._genome, genome_region.chr, track_el.start(), track_el.end())
