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
                print("res:")
                print(v)
                self.assertTrue(v == expAverage)
                resFound = True

            else:
                # Tests if all tracks no in chr1 have a size of 0.
                self.assertEqual(v.size, 0)

        self.assertTrue(resFound)

    def testLinkedPoints(self):

        # Value is scalar
        self._runTest(ids=[1], edges=[2], weights=[[1]],
                      starts=[1], expAverage=1, debug=True)
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1],[3]],
                      starts=[1,2], expAverage=2)

        # Value is a pair of scalars
        self._runTest(ids=[1,2], edges=[[2],[1]], weights=[[1,1],[1,1]],
                      starts=[1,5], expAverage=1)
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1],[2,2]],
                      starts=[1,5], expAverage=1.5)

        # Value is a vector of scalars
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1,1],[1,1,1]],
                      starts=[1,5], expAverage=1)
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1,1],[2,2,2]],
                      starts=[1,5], expAverage=1.5)

        # Value is a list of scalars
        # It looks like this is not supported directly i Gtrack. Only when
        # parsing from file.
        # If we give GTrack a object array with shape = (n,) the
        # inferValType method i TrackFormat fails.
        # When parsing the arrays are padded with np.nan so we get an ndarray
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1,1,],[1,1,np.nan]],
                      starts=[1,5], expAverage=1)
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1,1],[2,2,np.nan]],
                      starts=[1,5], expAverage=1.5)

        # Values is boolean
        self._runTest(ids=[1,2], edges=[2,1], weights=[[True],[True]],
                      starts=[1,2], expAverage=True)
        self._runTest(ids=[1,2], edges=[2,1], weights=[[False],[True]],
                      starts=[1,2], expAverage=False)
        self._runTest(ids=[1,2], edges=[2,1], weights=[[False],[False]],
                      starts=[1,2], expAverage=False)

        # Values is boolean pairs
        self._runTest(ids=[1,2], edges=[2,1],
                      weights=[[True,True],[True,True]],
                      starts=[1,2], expAverage=True)
        self._runTest(ids=[1,2], edges=[2,1],
                      weights=[[True,False],[True,True]],
                      starts=[1,2], expAverage=False)
        self._runTest(ids=[1,2], edges=[2,1],
                      weights=[[False,False],[False,False]],
                      starts=[1,2], expAverage=False)

        # Values is boolean vectors
        self._runTest(ids=[1,2], edges=[2,1],
                      weights=[[True,True,True],[True,True,True]],
                      starts=[1,2], expAverage=True)
        self._runTest(ids=[1,2], edges=[2,1],
                      weights=[[True,False,True],[True,True,True]],
                      starts=[1,2], expAverage=False)
        self._runTest(ids=[1,2], edges=[2,1],
                      weights=[[False,False,False],[False,False,False]],
                      starts=[1,2], expAverage=False)

        # Values is boolean lists
        self._runTest(ids=[1,2], edges=[2,1],
                      weights=[[True,True,True],[True,True,np.nan]],
                      starts=[1,2], expAverage=True)
        self._runTest(ids=[1,2], edges=[2,1],
                      weights=[[False,False,False],[False,False,np.nan]],
                      starts=[1,2], expAverage=False)
        #self._runTest(ids=[1,2], edges=[2,1],
        #              weights=[[True,False,True],[True,True,np.nan]],
        #              starts=[1,2], expAverage=False)

    def testLinkedValuedPoints(self):
        """
        Most of this is tested i the LP test. Mostly checking that adding
        columns does not change anything.
        :return:
        """
        # Value is a vector of scalars
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1,1],[1,1,1]],
                      starts=[1,5], values=[1,2], expAverage=1)
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1,1],[2,2,2]],
                      starts=[1,5], values=[1,2], expAverage=1.5)

        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1,1,],[1,1,np.nan]],
                      starts=[1,5], values=[1,2], expAverage=1)
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1,1],[2,2,np.nan]],
                      starts=[1,5], values=[1,2], expAverage=1.5)

    def testLinkedSegments(self):
        """
        Most of this is tested i the LP test. Mostly checking that adding
        columns does not change anything.
        :return:
        """
        # Value is a vector of scalars
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1,1],[1,1,1]],
                      starts=[1,5], ends=[3,10], expAverage=1)
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1,1],[2,2,2]],
                      starts=[1,5], ends=[3,10], expAverage=1.5)

        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1,1,],[1,1,np.nan]],
                      starts=[1,5], ends=[3,10], expAverage=1)
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1,1],[2,2,np.nan]],
                      starts=[1,5], ends=[3,10], expAverage=1.5)

    def testLinkedValuedSegments(self):
        """
        Most of this is tested i the LP test. Mostly checking that adding
        columns does not change anything.
        :return:
        """
        # Value is a vector of scalars
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1,1],[1,1,1]],
                      starts=[1,5], ends=[3,10], values=[1,2], expAverage=1)
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1,1],[2,2,2]],
                      starts=[1,5], ends=[3,10], values=[1,2], expAverage=1.5)

        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1,1,],[1,1,np.nan]],
                      starts=[1,5], ends=[3,10], values=[1,2], expAverage=1)
        self._runTest(ids=[1,2], edges=[2,1], weights=[[1,1,1],[2,2,np.nan]],
                      starts=[1,5], ends=[3,10], values=[1,2], expAverage=1.5)

    def testLinkedGenomePartitioning(self):
        """
        Most of this is tested i the LP test. Mostly checking that adding
        columns does not change anything.
        :return:
        """
        self._runTest(ids=[1,2,3], edges=[2,1,3],
                      weights=[[1,1,1],[1,1,1],[1,1,1]],
                      ends=[1,2,3], expAverage=1,
                      customChrLength=3)

        self._runTest(ids=[1,2], edges=[2,1],
                      weights=[[1,1,1,],[1,1,np.nan]],
                      ends=[1,3], expAverage=1,
                      customChrLength=3)


    def testLinkedStepFunction(self):
        """
        Most of this is tested i the LP test. Mostly checking that adding
        columns does not change anything.
        :return:
        """
        self._runTest(ids=[1,2,3], edges=[2,1,3],
                      weights=[[1,1,1],[1,1,1],[1,1,1]],
                      ends=[1,2,3], values=[1,2,3], expAverage=1,
                      customChrLength=3)

        self._runTest(ids=[1,2], edges=[2,1],
                      weights=[[1,1,1,],[1,1,np.nan]],
                      ends=[1,3], values=[1,2], expAverage=1,
                      customChrLength=3)

    def testLinkedFunction(self):
        """
        Most of this is tested i the LP test. Mostly checking that adding
        columns does not change anything.
        :return:
        """
        self._runTest(ids=[1,2,3], edges=[2,1,3],
                      weights=[[1,1,1],[1,1,1],[1,1,1]],
                      values=[1,2,3], expAverage=1,
                      customChrLength=3)

        self._runTest(ids=[1,2,3], edges=[2,1,3],
                      weights=[[1,1,1],[1,1,1],[1,1,np.nan]],
                      values=[1,2,3], expAverage=1,
                      customChrLength=3)

    def testLinkedBasePairs(self):
        """
        Most of this is tested i the LP test. Mostly checking that adding
        columns does not change anything.
        :return:
        """
        self._runTest(ids=[1,2,3], edges=[2,1,3],
                      weights=[[1,1,1],[1,1,1],[1,1,1]],
                      expAverage=1, customChrLength=3)

        self._runTest(ids=[1,2,3], edges=[2,1,3],
                      weights=[[1,1,1],[1,1,1],[1,1,np.nan]],
                      expAverage=1, customChrLength=3)

if __name__ == "__main__":
    unittest.main()
