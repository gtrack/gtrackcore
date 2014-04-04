from gtrackcore.input.core.ToolGenomeElementSource import ToolGenomeElementSource
from gtrackcore.input.core.GenomeElement import GenomeElement
from gtrackcore.track.core.Track import Track
from gtrackcore.track.format.TrackFormat import TrackFormatReq


class OverlapToolGenomeElementSource(ToolGenomeElementSource):
    _VERSION = '1.0'
    TOOL_NAME = 'overlap'

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

    def __iter__(self):
        self._ge_generator = self._overlap_generator()
        return self
        
    def next(self):
        return self._ge_generator.next()

    def _overlap_generator(self):
        for genome_region in self._genome_regions:
            track_view_1 = self._track1.getTrackView(genome_region)
            track_view_2 = self._track2.getTrackView(genome_region)

            track_element_iterator1 = iter(track_view_1)
            track_element_iterator2 = iter(track_view_2)
            try:
                track_el1 = track_element_iterator1.next()
                track_el2 = track_element_iterator2.next()
                while True:
                    start, end = max(track_el1.start(), track_el2.start()), min(track_el1.end(), track_el2.end())

                    if end - start > 0:
                        yield GenomeElement(self._genome, genome_region.chr, start, end)

                    if track_el1.end() < track_el2.end():
                        track_el1 = track_element_iterator1.next()
                    elif track_el1.end() > track_el2.end():
                        track_el2 = track_element_iterator2.next()
                    else:
                        track_el1 = track_element_iterator1.next()
                        track_el2 = track_element_iterator2.next()
            except StopIteration:
                pass
