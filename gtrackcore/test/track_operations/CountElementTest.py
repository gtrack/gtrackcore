import unittest
import numpy as np
from collections import OrderedDict

from gtrackcore.track_operations.operations.CountElements import CountElements
from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.test.track_operations.OperationTest import createTrackView


class CountElementTest(unittest.TestCase):

    def setUp(self):
        self.chr1 = (GenomeRegion('hg19', 'chr1', 0, GenomeInfo.GENOMES['hg19']['size']['chr1']))
        self.chromosomes = (GenomeRegion('hg19', c, 0, l)
                            for c, l in GenomeInfo.GENOMES['hg19']['size'].iteritems())

    def _runCountElementTest(self, starts, ends, expRes):
        """
        Run a union test over two tracks.
        The test expects there to only to be segments in chr1,
        All other chromosomes need to be of size zero.
        :param startsA: Arrays of starts in track A
        :param endsA: Array of ends in track B
        :param startsB: Array of starts in track B
        :param endsB: Array of ends in track B
        :param expStarts: Expected startss after union
        :param expEnds: Expected ends after union
        :return:
        """
        track = self._createTrackContent(starts, ends)

        c = CountElements(track)
        res = c()

        for (k, v) in res.iteritems():

            if cmp(k, self.chr1) == 0:
                # All test tracks are in chr1
                self.assertEqual(v,expRes)
            else:
                pass

    def _createTrackContent(self, starts, ends):
        """
        Create a track view a start, end list pair.
        Help method used in testing. This method will create a hg19 tracks with
        data in chromosome 1 only.
        :param starts: List of track start positions
        :param ends: List of track end positions
        :return: A TrackContent object
        """
        starts = np.array(starts)
        ends = np.array(ends)
        tv = createTrackView(region=self.chr1, startList=starts, endList=ends,
                             allow_overlap=False)
        d = OrderedDict()
        d[self.chr1] = tv
        return TrackContents('hg19', d)

    def testCountOne(self):
        """
        Two non overlapping segments
        :return: None
        """
        self._runCountElementTest(starts=[2], ends=[4], expRes=1)

    def testCountTwo(self):
        self._runCountElementTest(starts=[2, 6], ends=[4, 8], expRes=2)

if __name__ == "__main__":
    unittest.main()
