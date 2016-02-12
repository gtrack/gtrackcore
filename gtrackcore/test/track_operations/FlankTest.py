import unittest
import numpy as np
from collections import OrderedDict

from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.operations.Flank import Flank
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.test.track_operations.OperationTest import createTrackView


class FlankTest(unittest.TestCase):

    def setUp(self):
        self.chr1 = (GenomeRegion('hg19', 'chr1', 0,
                                  GenomeInfo.GENOMES['hg19']['size']['chr1']))
        self.chromosomes = (GenomeRegion('hg19', c, 0, l)
                            for c, l in
                            GenomeInfo.GENOMES['hg19']['size'].iteritems())

    def _runFlankSegmentsTest(self, starts, ends, expStarts, expEnds,
                              nrBP, after=True, before=True):
        """
        Run a test on the creation of a Flank track from a segmented track.
        The test expects there to only to be segments in chr1,
        All other chromosomes need to be of size zero.
        :param startsA: Arrays of starts in track.
        :param endsA: Array of ends in track.
        :param expStarts: Expected starts of flanks.
        :param expEnds: Expected ends of flanks.
        :parap nrBP: INT. Size of flank i base pairs.
        :param after: Boolean. Flanks from the starts.
        :param before: Boolean. Flanks form the ends.
        :return:
        """
        track = self._createTrackContent(starts, ends)

        f = Flank(track)
        # Result track type is Segments as default
        f.setFlankSize(nrBP)
        f.setAfter(after)
        f.setBefore(before)

        tc = f()

        for (k, v) in tc.getTrackViews().items():

            print expStarts
            print v.startsAsNumpyArray()

            print expEnds
            print v.endsAsNumpyArray()

            if cmp(k, self.chr1) == 0:
                # All test tracks are in chr1
                self.assertTrue(np.array_equal(v.startsAsNumpyArray(),
                                               expStarts))
                self.assertTrue(np.array_equal(v.endsAsNumpyArray(), expEnds))
            else:
                # Tests if all tracks no in chr1 have a size of 0.
                self.assertEqual(v.startsAsNumpyArray().size, 0)
                self.assertEqual(v.endsAsNumpyArray().size, 0)


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

    # **** Points tests ****

    # **** Segments tests ****

    def testFlankSimpleBefore(self):
        """
        Simple single segment before.
        :return: None
        """
        self._runFlankSegmentsTest(starts=[100], ends=[150], expStarts=[50],
                                   expEnds=[100], nrBP=50, after=False,
                                   before=True)

    def testFlankSimpleAfter(self):
        """
        Simple single segment after.
        :return: None
        """
        self._runFlankSegmentsTest(starts=[100], ends=[150], expStarts=[150],
                                   expEnds=[200], nrBP=50, after=True,
                                   before=False)


if __name__ == "__main__":
    unittest.main()
