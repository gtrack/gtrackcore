import unittest
import numpy as np
from collections import OrderedDict

from gtrackcore.track_operations.operations.Union import Union
from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.test.track_operations.TestUtils import createTrackView


class NestedOperatorTest(unittest.TestCase):
    """
    Tests if nesting of operator classes work
    """

    def setUp(self):
        self.chr1 = (GenomeRegion('hg19', 'chr1', 0, GenomeInfo.GENOMES['hg19']['size']['chr1']))
        self.chromosomes = (GenomeRegion('hg19', c, 0, l)
                            for c, l in GenomeInfo.GENOMES['hg19']['size'].iteritems())

    def _runNestedTest(self, operationObject, expStarts, expEnds):
        """
        Runs a test one a operator object.

        The test expects there to only to be segments in chr1,
        All other chromosomes need to be of size zero.
        :return:
        """

        tc = operationObject()

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

    def testUnionAndTrack(self):
        """
        Test if a union between another union and a track works.
        :return: None
        """
        track1 = self._createTrackContent([2], [4])
        track2 = self._createTrackContent([6], [8])
        track3 = self._createTrackContent([10], [12])

        u1 = Union(track1, track2)
        u2 = Union(u1, track3)

        self._runNestedTest(u2, [2, 6, 10], [4, 8, 12])

    def testUnionAndUnion(self):
        """
        Test if a union between another union and a track works.
        :return: None
        """
        track1 = self._createTrackContent([2], [4])
        track2 = self._createTrackContent([6], [8])
        track3 = self._createTrackContent([10], [12])
        track4 = self._createTrackContent([14], [16])

        u1 = Union(track1, track2)
        u2 = Union(track3, track4)
        u3 = Union(u1, u2)

        self._runNestedTest(u3, [2, 6, 10, 14], [4, 8, 12, 16])

if __name__ == "__main__":
    unittest.main()
