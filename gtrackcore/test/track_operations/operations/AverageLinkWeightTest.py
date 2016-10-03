import unittest
import numpy as np

from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion

from gtrackcore.track_operations.operations.AverageLinkWeight import \
    AverageLinkWeight
from gtrackcore.test.track_operations.TestUtils import \
    createSimpleTestTrackContent


class AverageLinkWeightTest(unittest.TestCase):

    def setUp(self):
        self.chr1 = (GenomeRegion('hg19', 'chr1', 0,
                                  GenomeInfo.GENOMES['hg19']['size']['chr1']))
        self.chr1Small = (GenomeRegion('hg19', 'chr1', 0, 3))
        self.chromosomes = (GenomeRegion('hg19', c, 0, l)
                            for c, l in
                            GenomeInfo.GENOMES['hg19']['size'].iteritems())

    def _runTest(self, ids, edges, weights, expAverage, starts=None,
                 ends=None, values=None, strands=None,
                 customAverageFunction=None, customChrLength=None,
                 allowOverlap=True, debug=False):

        track = createSimpleTestTrackContent(startList=starts, endList=ends,
                                             valList=values,
                                             strandList=strands,
                                             idList=ids, edgeList=edges,
                                             weightsList=weights,
                                             customChrLength=customChrLength)

        a = AverageLinkWeight(track,
                              customAverageFunction=customAverageFunction,
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

    def testLinkedPointsScalarOne(self):
        """
        Simple test, only one edge
        :return:
        """
        self._runTest(ids=[1], edges=[2], weights=[[1]],
                      starts=[1], expAverage=1, debug=True)

    def testLinkedPointsScalarMultiple(self):
        """
        Test with one node per edge
        :return:
        """
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1],[3]],
                      starts=[1,2], expAverage=2)

    def testLinkedPointsPairOfEdges(self):
        """
        Test using two edges per node
        :return:
        """
        self._runTest(ids=[1,2], edges=[[2],[1]], weights=[[1,1],[1,1]],
                      starts=[1,5], expAverage=1)

    def testLinkedPointsPairEdgesFloatResult(self):
        """
        Test if a float is returned and not integer
        :return:
        """
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1],[2,2]],
                      starts=[1,5], expAverage=1.5)

    def testLinkedPointsVectorOfEdges(self):
        """
        Weights is a vector
        :return:
        """
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1,1],[1,1,1]],
                      starts=[1,5], expAverage=1)

    def testLinkedPointsVectorOfEdgesFloat(self):
        """
        Test vector, float as result
        :return:
        """
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1,1],[2,2,2]],
                      starts=[1,5], expAverage=1.5)

    def testLinkedPointsScalarOfEdges(self):
        """
        Test with a mixed number of edges per node. The others are padded.
        :return:
        """
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1,1],[1,1,np.nan]],
                      starts=[1,5], expAverage=1)

    def testLinkedPointsScalarOfEdgesFloat(self):
        """
        Test with a mixed number of edges per node. The others are padded.
        Float as result
        :return:
        """
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1,1],[2,2,np.nan]],
                      starts=[1,5], expAverage=1.5)

    def testLinkedPointsBooleanTrue(self):
        """
        Test using boolean as weights. All True
        :return:
        """
        self._runTest(ids=[1,2], edges=[2,1], weights=[[True],[True]],
                      starts=[1,2], expAverage=True)

    def testLinkedPointsBooleanMixed(self):
        """
        Test using boolean as weights. Mixed
        :return:
        """
        self._runTest(ids=[1,2], edges=[2,1], weights=[[False],[True]],
                      starts=[1,2], expAverage=False)

    def testLinkedPointsBooleanFalse(self):
        """
        Test using boolean as weights. All False
        :return:
        """
        self._runTest(ids=[1,2], edges=[2,1], weights=[[False],[False]],
                      starts=[1,2], expAverage=False)

    def testLinkedPointsPairBooleanTrue(self):
        """
        Test using pairs of booleans. All True
        :return:
        """
        self._runTest(ids=[1,2], edges=[2,1],
                      weights=[[True,True],[True,True]],
                      starts=[1,2], expAverage=True)

    def testLinkedPointsPairBooleanMixed(self):
        """
        Test using pairs of booleans. Mixed
        :return:
        """
        self._runTest(ids=[1,2], edges=[2,1],
                      weights=[[True,False],[True,True]],
                      starts=[1,2], expAverage=False)

    def testLinkedPointsPairBooleanFalse(self):
        """
        Test using pairs of booleans. All False
        :return:
        """
        self._runTest(ids=[1,2], edges=[2,1],
                      weights=[[False,False],[False,False]],
                      starts=[1,2], expAverage=False)

    def testLinkedPointsVectorBooleanTrue(self):
        """
        Test using vectors of booleans. All true
        :return:
        """
        self._runTest(ids=[1,2], edges=[2,1],
                      weights=[[True,True,True],[True,True,True]],
                      starts=[1,2], expAverage=True)

    def testLinkedPointsVectorBooleanMixed(self):
        """
        Test using vectors of booleans. Mixed
        :return:
        """
        self._runTest(ids=[1,2], edges=[2,1],
                      weights=[[True,False,True],[True,True,True]],
                      starts=[1,2], expAverage=False)

    def testLinkedPointsVectorBooleanFalse(self):
        """
        Test using vectors of booleans. All False
        :return:
        """
        self._runTest(ids=[1,2], edges=[2,1],
                      weights=[[False,False,False],[False,False,False]],
                      starts=[1,2], expAverage=False)

    def testLinkedPointsListBooleanTrue(self):
        """
        Test using list of booleans, padded with np.nan.
        All True
        :return:
        """
        self._runTest(ids=[1,2], edges=[2,1],
                      weights=[[True,True,True],[True,True,np.nan]],
                      starts=[1,2], expAverage=True)

    def testLinkedPointsListBooleanFalse(self):
        """
        Test using list of booleans, padded with np.nan.
        All False
        :return:
        """
        self._runTest(ids=[1,2], edges=[2,1],
                      weights=[[False,False,False],[False,False,np.nan]],
                      starts=[1,2], expAverage=False)

    def testLinkedPointsListBooleanMixed(self):
        """
        Test using list of booleans, padded with np.nan.
        Mixed

        This does not work, as when we use nan as padding, the array is
        converted to ints. We can't distinguish between whats a boolean int
        array and an normal int array.
        :return:
        """
        #self._runTest(ids=[1,2], edges=[2,1],
        #              weights=[[True,False,True],[True,True,np.nan]],
        #              starts=[1,2], expAverage=False)

    # Most of the testing is done in the LP test. Here we mostly check that
    # adding columns does not change anything.
    def testLinkedValuedPoints(self):
        """
        Simple test of LVP
        :return:
        """
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1,1],[1,1,1]],
                      starts=[1,5], values=[1,2], expAverage=1)

    def testLinkedValuedPointsFloat(self):
        """
        Test of LVP, float as result
        :return:
        """
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1,1],[2,2,2]],
                      starts=[1,5], values=[1,2], expAverage=1.5)

    def testLinkedValuedPointsList(self):
        """
        List of weights
        :return:
        """
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1,1,],[1,1,np.nan]],
                      starts=[1,5], values=[1,2], expAverage=1)

    def testLinkedValuedPointsListFloat(self):
        """
        List of weights, float as result
        :return:
        """
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1,1],[2,2,np.nan]],
                      starts=[1,5], values=[1,2], expAverage=1.5)

    def testLinkedSegments(self):
        """
        Simple test of LS
        :return:
        """
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1,1],[1,1,1]],
                      starts=[1,5], ends=[3,10], expAverage=1)

    def testLinkedSegmentsFloat(self):
        """
        Float as result
        :return:
        """
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1,1],[2,2,2]],
                      starts=[1,5], ends=[3,10], expAverage=1.5)

    def testLinkedSegmentsList(self):
        """
        Test using list with padding.
        :return:
        """
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1,1,],[1,1,np.nan]],
                      starts=[1,5], ends=[3,10], expAverage=1)

    def testLinkedSegmentsListFloat(self):
        """
        Test using list with padding.
        Float as result.
        :return:
        """
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1,1],[2,2,np.nan]],
                      starts=[1,5], ends=[3,10], expAverage=1.5)

    def testLinkedValuedSegments(self):
        """
        Test of LVS
        :return:
        """
        # Value is a vector of scalars
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1,1],[1,1,1]],
                      starts=[1,5], ends=[3,10], values=[1,2], expAverage=1)

    def testLinkedValuedSegmentsFloat(self):
        """
        Float as result
        :return:
        """
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1,1],[2,2,2]],
                      starts=[1,5], ends=[3,10], values=[1,2], expAverage=1.5)

    def testLinkedValuedSegmentsLists(self):
        """
        Test using list with padding
        :return:
        """
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1,1,],[1,1,np.nan]],
                      starts=[1,5], ends=[3,10], values=[1,2], expAverage=1)

    def testLinkedValuedSegmentsListsFloat(self):
        """
        Test using list with padding
        Float as result
        :return:
        """
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1,1],[2,2,np.nan]],
                      starts=[1,5], ends=[3,10], values=[1,2], expAverage=1.5)

    def testLinkedGenomePartitioning(self):
        """
        Simple test of LGP
        :return:
        """
        self._runTest(ids=[1,2,3], edges=[2,1,3],
                      weights=[[1,1,1],[1,1,1],[1,1,1]],
                      ends=[1,2,3], expAverage=1,
                      customChrLength=3)

    def testLinkedGenomePartitioningList(self):
        """
        List with paddin
        :return:
        """
        self._runTest(ids=[1,2], edges=[2,1],
                      weights=[[1,1,1,],[1,1,np.nan]],
                      ends=[1,3], expAverage=1,
                      customChrLength=3)

    def testLinkedStepFunction(self):
        """
        Simple test of LSF
        :return:
        """
        self._runTest(ids=[1,2,3], edges=[2,1,3],
                      weights=[[1,1,1],[1,1,1],[1,1,1]],
                      ends=[1,2,3], values=[1,2,3], expAverage=1,
                      customChrLength=3)

    def testLinkedStepFunctionList(self):
        """
        Test using list with padding
        :return:
        """
        self._runTest(ids=[1,2], edges=[2,1],
                      weights=[[1,1,1,],[1,1,np.nan]],
                      ends=[1,3], values=[1,2], expAverage=1,
                      customChrLength=3)

    def testLinkedFunction(self):
        """
        Simple test of LF
        :return:
        """
        self._runTest(ids=[1,2,3], edges=[2,1,3],
                      weights=[[1,1,1],[1,1,1],[1,1,1]],
                      values=[1,2,3], expAverage=1,
                      customChrLength=3)

    def testLinkedFunctionLists(self):
        """
        Test using list with padding
        :return:
        """
        self._runTest(ids=[1,2,3], edges=[2,1,3],
                      weights=[[1,1,1],[1,1,1],[1,1,np.nan]],
                      values=[1,2,3], expAverage=1,
                      customChrLength=3)

    def testLinkedBasePairs(self):
        """
        Simmple test of LBP
        :return:
        """
        self._runTest(ids=[1,2,3], edges=[2,1,3],
                      weights=[[1,1,1],[1,1,1],[1,1,1]],
                      expAverage=1, customChrLength=3)

    def testLinkedBasePairsLists(self):
        """
        Test using lists with padding
        :return:
        """
        self._runTest(ids=[1,2,3], edges=[2,1,3],
                      weights=[[1,1,1],[1,1,1],[1,1,np.nan]],
                      expAverage=1, customChrLength=3)

if __name__ == "__main__":
    unittest.main()
