
import unittest
import numpy as np
from collections import OrderedDict

from gtrackcore.track_operations.operations.Coverage import Coverage
from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track_operations.TrackContents import TrackContents

# Test utils
from gtrackcore.test.track_operations.TestUtils import createTrackView
from gtrackcore.test.track_operations.TestUtils import createSimpleTestTrackContent


class CoverageTest(unittest.TestCase):
    """
    Tests of the coverage operation

    Test objectives
    * Find correct cover for a non overlapping track
    * Find correct cover for a overlapping track
    """

    def setUp(self):
        self.chr1 = (GenomeRegion('hg19', 'chr1', 0, GenomeInfo.GENOMES['hg19']['size']['chr1']))
        self.chromosomes = (GenomeRegion('hg19', c, 0, l)
                            for c, l in GenomeInfo.GENOMES['hg19']['size'].iteritems())

    def _runCoverageTest(self, starts, ends, expCover):
        """

        :param starts:
        :param ends:
        :param expCover:
        :return:
        """

        track = createSimpleTestTrackContent(startList=starts, endList=ends)
        u = Coverage(track)
        res = u()

        for (k, v) in res.iteritems():
            if cmp(k, self.chr1) == 0:
                self.assertTrue(v, expCover)

    def testSimpleCoverage(self):
        """
        Simple coverage
        :return: None
        """
        self._runCoverageTest(starts=[2], ends=[4], expCover=2)

    def testComplexCoverage(self):
        """
        A more complex coverage
        :return: None
        """
        self._runCoverageTest(starts=[2,10,100], ends=[4,45,150],
                              expCover=2+35+50)

    def testOverlapCoverage(self):
        """
        Coverage of overlapping segments
        :return: None
        """
        self._runCoverageTest(starts=[2,6], ends=[6,8], expCover=6)


if __name__ == "__main__":
    unittest.main()

