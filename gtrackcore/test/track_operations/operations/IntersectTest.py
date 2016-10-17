
import unittest
import numpy as np
from collections import OrderedDict

from gtrackcore.track_operations.operations.Intersect import Intersect
from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.test.track_operations.TestUtils import createTrackView
from gtrackcore.test.track_operations.TestUtils import \
    createSimpleTestTrackContent

class IntersectTest(unittest.TestCase):
    """
    Template class for creating track_operations tests.
    """

    def setUp(self):
        self.chr1 = (GenomeRegion('hg19', 'chr1', 0, GenomeInfo.GENOMES['hg19']['size']['chr1']))
        self.chromosomes = (GenomeRegion('hg19', c, 0, l)
                            for c, l in GenomeInfo.GENOMES['hg19']['size'].iteritems())

    def _runTest(self, t1Starts=None, t2Starts=None, t1Ends=None, t2Ends=None,
                 t1Strands=None, t2Strands=None, t1Vals=None, t2Vals=None,
                 t1Ids=None, t2Ids=None, t1Edges=None, t2Edges=None,
                 t1Weights=None, t2Weights=None, expStarts=None, expEnds=None,
                 expValues=None, expStrands=None, expIds=None, expEdges=None,
                 expWeights=None, expNoResult=False, customChrLength=None,
                 resultAllowOverlap=True,
                 debug=False, expTrackFormatType=None):

        t1 = createSimpleTestTrackContent(startList=t1Starts, endList=t1Ends,
                                          valList=t1Vals, strandList=t1Strands,
                                          idList=t1Ids, edgeList=t1Edges,
                                          weightsList=t1Weights,
                                          customChrLength=customChrLength)

        t2 = createSimpleTestTrackContent(startList=t2Starts, endList=t2Ends,
                                          valList=t2Vals, strandList=t2Strands,
                                          idList=t2Ids, edgeList=t2Edges,
                                          weightsList=t2Weights,
                                          customChrLength=customChrLength)

        i = Intersect(t1, t2, resultAllowOverlap=resultAllowOverlap,
                      debug=debug)

        result = i.calculate()
        self.assertTrue(result is not None)

        print(result.trackViews)

        resFound = False

        for (k, v) in result.trackViews.iteritems():
            if cmp(k, self.chr1) == 0 or cmp(k, self.chr1Small) == 0:
                # All test tracks are in chr1
                resFound = True

                newStarts = v.startsAsNumpyArray()
                newEnds = v.endsAsNumpyArray()
                newValues = v.valsAsNumpyArray()
                newStrands = v.strandsAsNumpyArray()
                newIds = v.idsAsNumpyArray()
                newEdges = v.edgesAsNumpyArray()
                newWeights = v.weightsAsNumpyArray()
                #newExtras = v.extrasAsNumpyArray()

                if debug:
                    print("expFormatName: {}".format(expTrackFormatType))
                    print("newFormatName: {}".format(v.trackFormat.getFormatName()))
                    print("newStarts: {}".format(newStarts))
                    print("expStarts: {}".format(expStarts))
                    print("newEnds: {}".format(newEnds))
                    print("expEnds: {}".format(expEnds))
                    print("newStrands: {}".format(newStrands))
                    print("expStrands: {}".format(expStrands))
                    print("newIds: {}".format(newIds))
                    print("expIds: {}".format(expIds))
                    print("newEdges: {}".format(newEdges))
                    print("expEdges: {}".format(expEdges))

                if expTrackFormatType is not None:
                    # Check that the track is of the expected type.
                    self.assertTrue(v.trackFormat.getFormatName() ==
                                    expTrackFormatType)

                if expEnds is None:
                    # Assuming a point type track. Creating the expected ends.
                    expEnds = np.array(expStarts) + 1

                if expStarts is not None:
                    self.assertTrue(newStarts is not None)
                    self.assertTrue(np.array_equal(newStarts, expStarts))
                else:
                    self.assertTrue(newStarts is None)

                if expEnds is not None:
                    self.assertTrue(newEnds is not None)
                    self.assertTrue(np.array_equal(newEnds, expEnds))
                else:
                    self.assertTrue(newEnds is None)

                if expValues is not None:
                    self.assertTrue(newValues is not None)
                    self.assertTrue(np.array_equal(newValues, expValues))
                else:
                    self.assertTrue(newValues is None)

                if expStrands is not None:
                    self.assertTrue(newStrands is not None)
                    self.assertTrue(np.array_equal(newStrands, expStrands))
                else:
                    self.assertTrue(newStrands is None)

                if expIds is not None:
                    print("newIds: {}".format(newIds))
                    print("expIds: {}".format(expIds))
                    self.assertTrue(newIds is not None)
                    self.assertTrue(np.array_equal(newIds, expIds))
                else:
                    self.assertTrue(newIds is None)

                if expEdges is not None:
                    print("newEdges: {}".format(newEdges))
                    print("expEdges: {}".format(expEdges))
                    self.assertTrue(newEdges is not None)
                    self.assertTrue(np.array_equal(newEdges, expEdges))
                else:
                    self.assertTrue(newEdges is None)

                if expWeights is not None:
                    self.assertTrue(newWeights is not None)
                    self.assertTrue(np.array_equal(newWeights, expWeights))
                else:
                    self.assertTrue(newWeights is None)

                #if expExtras is not None:
                #    self.assertTrue(newExtras is not None)
                #    self.assertTrue(np.array_equal(newExtras, expExtras))
                #else:
                #    self.assertTrue(newExtras is None)

            else:
                # Tests if all tracks no in chr1 have a size of 0.
                self.assertEqual(v.size, 0)

        if expNoResult:
            self.assertFalse(resFound)
        else:
            self.assertTrue(resFound)

    def testPointsNoOverlap(self):
        """
        Intersect of two point tracks, no overlap
        :return:
        """
        # No overlap
        self._runTest(t1Starts=[1,2,3], t2Starts=[4,5,6], expNoResult=True)

    def testPointsTotalOverlap(self):
        """
        Points, total overlap of A and B
        :return:
        """
        # Total overlap
        self._runTest(t1Starts=[2,6], t2Starts=[2,6], expStarts=[2,6],
                      expTrackFormatType="Points")

    def testPointsSomeOverlap(self):
        """
        Points, some overlap.
        :return:
        """
        self._runTest(t1Starts=[2,6,8,15], t2Starts=[2,8], expStarts=[2,8],
                      expTrackFormatType="Points")

    # **** Segments ****
    def testNoIntersect(self):
        """
        No intersect between A and B
        :return:
        """
        self._runTest(t1Starts=[2], t1Ends=[4], t2Starts=[5], t2Ends=[8],
                      expNoResult=True, expTrackFormatType="Segments")

    def testTotalIntersect(self):
        """
        A == b
        :return:
        """
        self._runTest(t1Starts=[2,6], t1Ends=[4,8], t2Starts=[2,6],
                      t2Ends=[4,8], expStarts=[2,6], expEnds=[4,8],
                      expTrackFormatType="Segments")

    def testABeforeBIntersect(self):
        """
        A intersects B at the end of A
        :return:
        """
        self._runTest(t1Starts=[2], t1Ends=[6], t2Starts=[4], t2Ends=[8],
                      expStarts=[4], expEnds=[6],
                      expTrackFormatType="Segments")

    def testBBeforeAIntersect(self):
        """
        B intersects A at the end of B
        :return:
        """
        self._runTest(t1Starts=[4], t1Ends=[8], t2Starts=[2], t2Ends=[6],
                      expStarts=[4], expEnds=[6],
                      expTrackFormatType="Segments")

    def testAInsideBIntersect(self):
        """
        A is totally inside B
        :return:
        """
        self._runTest(t1Starts=[4], t1Ends=[6], t2Starts=[2], t2Ends=[8],
                      expStarts=[4], expEnds=[6],
                      expTrackFormatType="Segments")

    def testBInsideAIntersect(self):
        """
        B is totally inside A
        :return:
        """
        self._runTest(t1Starts=[2], t1Ends=[8], t2Starts=[4], t2Ends=[6],
                      expStarts=[4], expEnds=[6],
                      expTrackFormatType="Segments")

    def testAInsideBStartIntersect(self):
        """
        A is totally inside B, Start of A equals start of B
        :return:
        """
        self._runTest(t1Starts=[2], t1Ends=[4], t2Starts=[2], t2Ends=[8],
                      expStarts=[2], expEnds=[4],
                      expTrackFormatType="Segments")

    def testBInsideAStartIntersect(self):
        """
        B is totally inside A, Start of A equals start of B
        :return:
        """
        self._runTest(t1Starts=[2], t1Ends=[8], t2Starts=[2], t2Ends=[4],
                      expStarts=[2], expEnds=[4],
                      expTrackFormatType="Segments")

    def testAInsideBEndIntersect(self):
        """
        A is totally inside B, End of A equals start of B
        :return:
        """
        self._runTest(t1Starts=[6], t1Ends=[8], t2Starts=[2], t2Ends=[8],
                      expStarts=[6], expEnds=[8],
                      expTrackFormatType="Segments")

    def testBInsideAEndIntersect(self):
        """
        B is totally inside A, End of A equals start of B
        :return:
        """
        self._runTest(t1Starts=[2], t1Ends=[8], t2Starts=[6], t2Ends=[8],
                      expStarts=[6], expEnds=[8],
                      expTrackFormatType="Segments")

    def testMultipleIntersect(self):
        """
        B overlaps multiple segments in A
        :return:
        """
        self._runTest(t1Starts=[2,6], t1Ends=[4, 10], t2Starts=[3],
                      t2Ends=[8],  expStarts=[3, 6], expEnds=[4,8],
                      expTrackFormatType="Segments")

    # **** Values/Links ****

    def testValues(self):
        """
        TODO! Who do
        :return:
        """
        pass

    # **** Mixed tracks types ****

    def testSegmentsAndPointsNoOverlap(self):
        """
        Tests where the input tracks are a mix of points and segments
        :return:
        """
        # No overlap, segment + points
        self._runTest(t1Starts=[5], t1Ends=[10], t2Starts=[2],
                      expNoResult=True)

    def testSegmentsAndPointsOverlap(self):
        """
        Segments and points.
        :return:
        """
        self._runTest(t1Starts=[5], t1Ends=[10], t2Starts=[8],
                      expStarts=[8], expTrackFormatType="Points")

    def testPointsAndSegmentsOverlap(self):
        """
        Points and segments
        :return:
        """
        self._runTest(t1Starts=[8], t2Starts=[5], t2Ends=[10],
                      expStarts=[8], expTrackFormatType="Points")

    def testPointsAndSegmentsMultiple(self):
        """
        Points and segments
        Multiple overlap in the same segment
        :return:
        """
        self._runTest(t1Starts=[5], t1Ends=[10], t2Starts=[6,8,9],
                      expStarts=[6,8,9], expTrackFormatType="Points", debug=True)

if __name__ == "__main__":
    unittest.main()

