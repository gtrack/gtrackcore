import unittest
import numpy as np

from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion

from gtrackcore.track_operations.operations.CountElements import CountElements
from gtrackcore.test.track_operations.TestUtils import \
    createSimpleTestTrackContent


class CountElementsTest(unittest.TestCase):

    def setUp(self):
        self.chr1 = (GenomeRegion('hg19', 'chr1', 0,
                                  GenomeInfo.GENOMES['hg19']['size']['chr1']))
        self.chr1Small = (GenomeRegion('hg19', 'chr1', 0, 3))
        self.chromosomes = (GenomeRegion('hg19', c, 0, l)
                            for c, l in
                            GenomeInfo.GENOMES['hg19']['size'].iteritems())

    def _runTest(self, starts=None, ends=None, strands=None, values=None,
                 ids=None, edges=None, weights=None, expCount=None,
                 customChrLength=None, allowOverlap=True, debug=False):

        track = createSimpleTestTrackContent(startList=starts, endList=ends,
                                             valList=values,
                                             strandList=strands,
                                             idList=ids, edgeList=edges,
                                             weightsList=weights,
                                             customChrLength=customChrLength)

        c = CountElements(track, debug=debug)

        self.assertTrue((c is not None))
        result = c.calculate()
        self.assertTrue(result is not None)

        resFound = False

        for (k, v) in result.iteritems():
            if cmp(k, self.chr1) == 0 or cmp(k, self.chr1Small) == 0:
                # All test tracks are in chr1
                if debug:
                    print("count: {}".format(v))
                    print("expCount: {}".format(expCount))
                self.assertTrue(v == expCount)
                resFound = True

            else:
                # Tests if all tracks no in chr1 have a size of 0.
                self.assertEqual(v.size, 0)

        self.assertTrue(resFound)

    def testPointsSimple(self):
        """
        Test with one point
        :return:
        """
        self._runTest(starts=[1], expCount=1)

    def testPointsMultiple(self):
        """
        Test using multiple points
        :return:
        """
        self._runTest(starts=[1,3,4,5,6,7,10,34534,54352], expCount=9)

    def testPointsMultipleOverlapping(self):
        """
        Test with overlapping points. Expect to count all
        :return:
        """
        self._runTest(starts=[1,2,3,3,3,3,4,5,9,9], expCount=10)

    def testSegmentsOne(self):
        """
        Test using one segment
        :return:
        """
        self._runTest(starts=[1], ends=[10], expCount=1)

    def testSegmentsMultiple(self):
        """
        Test using multiple segments.
        :return:
        """
        self._runTest(starts=[0,20], ends=[10,30], expCount=2)

    # **** Test different track types as input ****
    # The test below do not test the function of the operation,
    # only that the operation accepts the supported track types as input.

    def testPointsStrands(self):
        """
        Test that the operation accepts a points track with strands as
        input.
        :return:
        """
        self._runTest(starts=[1,2,3], strands=['+','-','.'], expCount=3)

    def testValuedPoints(self):
        """
        Test that the operation accepts a valued points track as input.
        :return:
        """
        self._runTest(starts=[1,2,3], strands=['+','-','.'], values=[1,2,3],
                      expCount=3)

    def testLinkedPoints(self):
        """
        Test that the operation accepts a linked points track as input.
        :return:
        """
        self._runTest(starts=[1,2,3], strands=['+','-','.'], ids=[1,2,3],
                      edges=[2,3,1], weights=[[1],[1],[1]], expCount=3)

    def testLinkedValuedPoints(self):
        """
        Test that the operation accepts a linked valued points track as input.
        :return:
        """
        self._runTest(starts=[1,2,3], strands=['+','-','.'], values=[1,2,3],
                      ids=[1,2,3], edges=[2,3,1], weights=[[1],[1],[1]],
                      expCount=3)

    def testValuedSegments(self):
        """
        Test that the operation accepts a valued segments track with
        strand as input.
        :return:
        """
        self._runTest(starts=[0,20], ends=[10,30], strands=['+','-'],
                      values=[1,2], expCount=2)

    def testLinkedSegments(self):
        """
        Test that the operation accepts a linked segments track as input.
        :return:
        """
        self._runTest(starts=[0,20], ends=[10,30], strands=['+','-'],
                      ids=[1,2], edges=[2,1], weights=[[1],[1]], expCount=2)

    def testLinkedValuedSegments(self):
        """
        Test that the operation accepts a linked valued segments track as
        input.
        :return:
        """
        self._runTest(starts=[0,20], ends=[10,30], strands=['+','-'],
                      values=[1,2], ids=[1,2], edges=[2,1],
                      weights=[[1],[1]], expCount=2)

if __name__ == "__main__":
    unittest.main()
