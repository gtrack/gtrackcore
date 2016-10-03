
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

    def _runTest(self, starts=None, ends=None, strands=None, values=None,
                 ids=None, edges=None, weights=None, expCoverage=None,
                 customAverageFunction=None, customChrLength=None,
                 allowOverlap=True, debug=False):

        track = createSimpleTestTrackContent(startList=starts, endList=ends,
                                             valList=values,
                                             strandList=strands,
                                             idList=ids, edgeList=edges,
                                             weightsList=weights,
                                             customChrLength=customChrLength)

        c = Coverage(track, debug=debug)

        self.assertTrue((c is not None))
        result = c.calculate()
        self.assertTrue(result is not None)

        resFound = False

        for (k, v) in result.iteritems():
            if cmp(k, self.chr1) == 0 or cmp(k, self.chr1Small) == 0:
                # All test tracks are in chr1
                self.assertTrue(v == expCoverage)
                resFound = True

            else:
                # Tests if all tracks no in chr1 have a size of 0.
                self.assertEqual(v.size, 0)

        self.assertTrue(resFound)

    def testPointsSimple(self):
        """
        Test coverage of simple points track
        :return:
        """

        self._runTest(starts=[4,10], expCoverage=2)

    def testPointsComplex(self):
        """
        Test coverage of more complex points track
        :return:
        """
        starts = [4,10,50,73,123,21441,4124]

        self._runTest(starts=starts, expCoverage=len(starts))

    def testSegmentsSimple(self):
        """
        Test coverage of simple segment track
        :return: None
        """
        self._runTest(starts=[2], ends=[4], expCoverage=2)

    def testSegmentsComplex(self):
        """
        A more complex coverage
        :return: None
        """
        self._runTest(starts=[2,10,100], ends=[4,45,150],
                              expCoverage=2+35+50)

    def testSegmentsOverlapping(self):
        """
        Coverage of overlapping segments
        :return: None
        """
        self._runTest(starts=[2,6], ends=[6,8], expCoverage=6)

if __name__ == "__main__":
    unittest.main()

