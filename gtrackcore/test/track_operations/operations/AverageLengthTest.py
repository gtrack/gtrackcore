import unittest
import numpy as np

from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion

from gtrackcore.track_operations.operations.AverageLength import AverageLength
from gtrackcore.test.track_operations.TestUtils import \
    createSimpleTestTrackContent


class AverageLengthTest(unittest.TestCase):

    def setUp(self):
        self.chr1 = (GenomeRegion('hg19', 'chr1', 0,
                                  GenomeInfo.GENOMES['hg19']['size']['chr1']))
        self.chr1Small = (GenomeRegion('hg19', 'chr1', 0, 3))
        self.chromosomes = (GenomeRegion('hg19', c, 0, l)
                            for c, l in
                            GenomeInfo.GENOMES['hg19']['size'].iteritems())

    def _runTest(self, starts=None, ends=None, strands=None, values=None,
                 ids=None, edges=None, weights=None, expAverage=None,
                 customAverageFunction=None, customChrLength=None,
                 allowOverlap=True, debug=False):

        track = createSimpleTestTrackContent(startList=starts, endList=ends,
                                             valList=values,
                                             strandList=strands,
                                             idList=ids, edgeList=edges,
                                             weightsList=weights,
                                             customChrLength=customChrLength)

        a = AverageLength(track, customAverageFunction=customAverageFunction,
                          debug=debug)

        self.assertTrue((a is not None))
        result = a.calculate()
        self.assertTrue(result is not None)

        resFound = False

        for (k, v) in result.iteritems():
            if cmp(k, self.chr1) == 0 or cmp(k, self.chr1Small) == 0:
                # All test tracks are in chr1
                self.assertTrue(v == expAverage)
                resFound = True

            else:
                # Tests if all tracks no in chr1 have a size of 0.
                self.assertEqual(v.size, 0)

        self.assertTrue(resFound)

    def testPointsOne(self):
        """
        Test the average length of one point
        :return:
        """
        self._runTest(starts=[1], expAverage=1)

    def testPointsMultiple(self):
        """
        Test the average length of multiple points
        :return:
        """
        self._runTest(starts=[1,3,4,5,6,7,10,34534,54352], expAverage=1)

    def testPointsMultipleOverlapping(self):
        """
        Test the average length of multiple points
        :return:
        """
        self._runTest(starts=[1,2,3,3,3,3,4,5,9,9], expAverage=1)

    def testSegmentsOne(self):
        """
        Test the average length of one segment
        :return:
        """

        self._runTest(starts=[1], ends=[10], expAverage=9)

    def testSegmentsMultiple(self):
        """
        Test the average length of multiple segment
        :return:
        """

        self._runTest(starts=[0,20], ends=[10,30], expAverage=10)

    def testSegmentsFloat(self):
        """
        Check that that we return a float when the average is not an integer.
        :return:
        """

        self._runTest(starts=[0,20], ends=[10,25], expAverage=7.5)

    def atestCustomAverageFunction(self):
        """
        Test that the use of a custom average function works
        :return:
        """
        pass

    # **** Test different track types as input ****
    # The test below do not test the function of the operation,
    # only that the operation accepts the supported track types as input.

    def testPointsStrands(self):
        """
        Test that the operation accepts a points track with strands as
        input.
        :return:
        """
        self._runTest(starts=[1,2,3], strands=['+','-','.'], expAverage=1)

    def testValuedPoints(self):
        """
        Test that the operation accepts a valued points track as input.
        :return:
        """
        self._runTest(starts=[1,2,3], strands=['+','-','.'], values=[1,2,3],
                      expAverage=1)

    def testLinkedPoints(self):
        """
        Test that the operation accepts a linked points track as input.
        :return:
        """
        self._runTest(starts=[1,2,3], strands=['+','-','.'], ids=[1,2,3],
                      edges=[2,3,1], weights=[[1],[1],[1]], expAverage=1)

    def testLinkedValuedPoints(self):
        """
        Test that the operation accepts a linked valued points track as input.
        :return:
        """
        self._runTest(starts=[1,2,3], strands=['+','-','.'], values=[1,2,3],
                      ids=[1,2,3], edges=[2,3,1], weights=[[1],[1],[1]],
                      expAverage=1)

    def testValuedSegments(self):
        """
        Test that the operation accepts a valued segments track with
        strand as input.
        :return:
        """
        self._runTest(starts=[0,20], ends=[10,30], strands=['+','-'],
                      values=[1,2], expAverage=10)

    def testLinkedSegments(self):
        """
        Test that the operation accepts a linked segments track as input.
        :return:
        """
        self._runTest(starts=[0,20], ends=[10,30], strands=['+','-'],
                      ids=[1,2], edges=[2,1], weights=[[1],[1]], expAverage=10)

    def testLinkedValuedSegments(self):
        """
        Test that the operation accepts a linked valued segments track as
        input.
        :return:
        """
        self._runTest(starts=[0,20], ends=[10,30], strands=['+','-'],
                      values=[1,2], ids=[1,2], edges=[2,1],
                      weights=[[1],[1]], expAverage=10)

if __name__ == "__main__":
    unittest.main()
