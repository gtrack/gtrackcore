import unittest
import numpy as np
from collections import OrderedDict

from gtrackcore.track_operations.operations.Union import Union
from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.test.track_operations.OperationTest import createTrackView


class TemplateTest(unittest.TestCase):
    """
    Template class for creating track_operations tests.
    """

    def setUp(self):
        self.chr1 = (GenomeRegion('hg19', 'chr1', 0, GenomeInfo.GENOMES['hg19']['size']['chr1']))
        self.chromosomes = (GenomeRegion('hg19', c, 0, l)
                            for c, l in GenomeInfo.GENOMES['hg19']['size'].iteritems())

    def _runTemplateTest(self, startsA, endsA, startsB, endsB, expStarts, expEnds):
        """
        Runs a test over one or more tracks. The number of tracks need to correspond
        to the operation being tested.

        The expected result need to reflect the operation as well.

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
        track1 = self._createTrackContent(startsA, endsA)
        track2 = self._createTrackContent(startsB, endsB)

        u = Union(track1, track2)
        tc = u()

        for (k, v) in tc.getTrackViews().items():

            if cmp(k, self.chr1) == 0:
                # All test tracks are in chr1
                self.assertTrue(np.array_equal(v.startsAsNumpyArray(), expStarts))
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



    def testCase1(self):
        """
        Test for case 1
        :return: None
        """
        self._runUnionTest(startsA=[2], endsA=[4], startsB=[5], endsB=[8], expStarts=[2, 5],
                           expEnds=[4, 8])

    def testEdgecase1(self):
        """
        Test for a edge case.
        :return: None
        """
        self._runTemplateTest(startsA=[2], endsA=[4], startsB=[3], endsB=[5], expStarts=[2],
                           expEnds=[5])


if __name__ == "__main__":
    unittest.main()
