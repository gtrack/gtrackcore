import unittest
import numpy as np
from collections import OrderedDict

from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.operations.Subtract import Subtract
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.test.track_operations.TestUtils import createTrackView
from gtrackcore.test.track_operations.TestUtils import \
    createSimpleTestTrackContent


class SubtractTest(unittest.TestCase):

    def setUp(self):
        self.chr1 = (GenomeRegion('hg19', 'chr1', 0,
                                  GenomeInfo.GENOMES['hg19']['size']['chr1']))
        self.chromosomes = (GenomeRegion('hg19', c, 0, l)
                            for c, l in
                            GenomeInfo.GENOMES['hg19']['size'].iteritems())

    def _runTest(self, startsA=None, startsB=None, endsA=None, endsB=None,
                 strandsA=None, strandsB=None, valsA=None, valsB=None,
                 idsA=None, idsB=None, edgesA=None, edgesB=None,
                 weightsA=None, weightsB=None, extrasA=None, extrasB=None,
                 expStarts=None, expEnds=None, expStrands=None, expVals=None,
                 expIds=None, expEdges=None, expWeights=None, expExtras=None,
                 expNoResult=False, allowOverlap=False,
                 resultAllowOverlap=False, debug=False):
        """
        Run a union test
        :param startsA:
        :param startsB:
        :param endsA:
        :param endsB:
        :param strandsA:
        :param strandsB:
        :param valsA:
        :param valsB:
        :param idsA:
        :param idsB:
        :param edgesA:
        :param edgesB:
        :param weightsA:
        :param weightsB:
        :param extrasA:
        :param extrasB:
        :param expStarts:
        :param expEnds:
        :param expStrands:
        :param expVals:
        :param expIds:
        :param expEdges:
        :param expWeights:
        :param expExtras:
        :param allowOverlap:
        :param resultAllowOverlap:
        :return:
        """

        track1 = createSimpleTestTrackContent(startList=startsA,
                                              endList=endsA, valList=valsA,
                                              strandList=strandsA,
                                              idList=idsA, edgeList=edgesA,
                                              weightsList=weightsA,
                                              extraLists=extrasA)
        track2 = createSimpleTestTrackContent(startList=startsB,
                                              endList=endsB, valList=valsB,
                                              strandList=strandsB,
                                              idList=idsB, edgeList=edgesB,
                                              weightsList=weightsB,
                                              extraLists=extrasB)

        o = Subtract(track1, track2, allowOverlap=allowOverlap,
                     resultAllowOverlap=resultAllowOverlap)

        tc = o.calculate()

        resFound = False

        for (k, v) in tc.getTrackViews().items():
            if cmp(k, self.chr1) == 0:
                # All test tracks are in chr1
                newStarts = v.startsAsNumpyArray()
                newEnds = v.endsAsNumpyArray()
                newVals = v.valsAsNumpyArray()
                newStrands = v.strandsAsNumpyArray()
                newIds = v.idsAsNumpyArray()
                newEdges = v.edgesAsNumpyArray()
                newWeights = v.weightsAsNumpyArray()
                #newExtras = v.extrasAsNumpyArray()

                resFound = True

                if debug:
                    print("**********************")
                    print("DEBUG: Subtract result")
                    print("newStarts: {}".format(newStarts))
                    print("newEnds: {}".format(newEnds))
                    print("newStrands: {}".format(newStrands))
                    print("newVals:: {}".format(newVals))
                    print("newIds: {}".format(newIds))
                    print("newEdges: {}".format(newEdges))
                    print("newWeights: {}".format(newWeights))
                    print("**********************")

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

                if expVals is not None:
                    self.assertTrue(newVals is not None)
                    self.assertTrue(np.array_equal(newVals, expVals))
                else:
                    self.assertTrue(newVals is None)

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
                self.assertEqual(v.startsAsNumpyArray().size, 0)
                self.assertEqual(v.endsAsNumpyArray().size, 0)

        if expNoResult:
            self.assertFalse(resFound)
        else:
            self.assertTrue(resFound)

    # **** Points tests ****

    def testPointsSimple(self):
        """
        Simple points subtract
        :return: None
        """
        self._runTest(startsA=[1,2,3], startsB=[3], expStarts=[1,2])

        self._runTest(startsA=[1,4], startsB=[14], expStarts=[1,4])

        self._runTest(startsA=[14,463], startsB=[45,463],
                      expStarts=[14])

        # "Overlap" in the middle.
        self._runTest(startsA=[14,36,65], startsB=[24,36,463],
                      expStarts=[14,65])

    # **** Valued Points tests ****
    def testValuedPoints(self):
        """
        Valued points subtract
        :return: None
        """
        self._runTest(startsA=[1,2,3], valsA=[3,4,5], startsB=[3,5],
                      valsB=[1,2], expStarts=[1,2], expVals=[3,4])

        # No subtract
        self._runTest(startsA=[1,3], valsA=[6,7], startsB=[2], valsB=[8],
                      expStarts=[1,3], expVals=[6,7])

        # In the middle
        self._runTest(startsA=[1,10,78], valsA=[6,34,45], startsB=[2,10],
                      valsB=[8,100], expStarts=[1,78], expVals=[6,45])

        # Multiple
        self._runTest(startsA=[1,3,6,10,20], valsA=[6,7,45,5,3],
                      startsB=[2,3,8,10,24], valsB=[8,100,42,3,2],
                      expStarts=[1,6,20], expVals=[6,45,3])

    # **** Segments tests ****
    def testSegmentsSimple(self):
        """
        Segments intersect, simple.
        Two non overlapping segments
        :return: None
        """
        self._runTest(startsA=[2], endsA=[6], startsB=[4], endsB=[8],
                      expStarts=[2], expEnds=[4], debug=True)

    def testSegmentsNoOverlap(self):
        """
        Segment intersect, no overlap
        :return: None
        """
        self._runTest(startsA=[2], endsA=[4], startsB=[6], endsB=[8],
                      expStarts=[2], expEnds=[4])

    def testSegmentsOverlapABeforeB(self):
        """
        Two partially overlapping segments, A before B
        :return: None
        """
        self._runTest(startsA=[2], endsA=[4], startsB=[3], endsB=[5],
                      expStarts=[2], expEnds=[3])

    def testSegmentsOverlapBBeforeA(self):
        """
        Two partially overlapping segments, B before A
        :return: None
        """
        self._runTest(startsA=[3], endsA=[5], startsB=[2], endsB=[4],
                      expStarts=[4], expEnds=[5])

    def testSegmentsOverlapBInsideA(self):
        """
        Two overlapping segments, B totally inside A
        :return: None
        """
        self._runTest(startsA=[2], endsA=[6], startsB=[3], endsB=[5],
                      expStarts=[2,5], expEnds=[3,6])

    def testSegmentsOverlapAInsideB(self):
        """
        Two overlapping segments, A totally inside B
        :return: None
        """
        self._runTest(startsA=[3], endsA=[5], startsB=[2], endsB=[6],
                      expNoResult=True)

    def testSegmentsTotalOverlap(self):
        """
        Two totally overlapping segments, A == B
        :return: None
        """
        self._runTest(startsA=[2], endsA=[4], startsB=[2], endsB=[4],
                      expNoResult=True, debug=True)

    def testSegmentsOverlapBAtStartOfA(self):
        """
        Two overlapping segments, B totally inside A
        B.start == A.start
        len(A) > len(B)
        :return: None
        """
        self._runTest(startsA=[2], endsA=[6], startsB=[2], endsB=[4],
                      expStarts=[4], expEnds=[6], debug=True)

    def testSegmentsOverlapAAtStartOfB(self):
        """
        Two overlaping segments, A totally inside B
        A.start == B.start
        len(B) > len (A)
        :return: None
        """
        self._runTest(startsA=[2], endsA=[4], startsB=[2], endsB=[6],
                      expNoResult=True)

    def testSegmentsOverlapBAtEndOfA(self):
        """
        Two overlapping segments, B totally inside A
        A.end == B.end
        len(A) > len (B)
        :return: None
        """
        self._runTest(startsA=[2], endsA=[6], startsB=[4], endsB=[6],
                      expStarts=[2], expEnds=[4])

    def testSegmentsOverlapAAtEndOfB(self):
        """
        Two overlapping segments, A totally inside B
        B.end == A.end
        len(B) > len (A)
        :return: None
        """
        self._runTest(startsA=[4], endsA=[6], startsB=[2], endsB=[6],
                      expNoResult=True)

    def testSegmentsTouchingABeforeB(self):
        """
        Two none overlapping "touching" segments
        A.end == B.start

        :return: None
        """
        self._runTest(startsA=[2], endsA=[4], startsB=[4], endsB=[6],
                      expStarts=[2],expEnds=[4])

    def testSegmentsTouchingBBeforeA(self):
        """
        Two none overlapping "touching" segments
        A.end == B.start

        :return: None
        """
        self._runTest(startsA=[4], endsA=[6], startsB=[2], endsB=[4],
                      expStarts=[4], expEnds=[6])

    def testSegmentsBCoversMultipleSegments(self):
        """
        B covers multiple segments in A
        :return: None
        """
        self._runTest(startsA=[2, 6], endsA=[4, 8], startsB=[3], endsB=[7],
                      expStarts=[2,7], expEnds=[3, 8])

    def testUnionSegmentsAJoinsTwoBs(self):
        """
        A covers multiple segments in B
        :return: None
        """
        self._runTest(startsA=[2], endsA=[15], startsB=[3,7], endsB=[5,10],
                      expStarts=[2,5,10], expEnds=[3,7,15])

    # **** Points - Segments ****
    def testPointsAndSegments(self):
        self._runTest(startsA=[1,2,3,4], startsB=[3], endsB=[10],
                      expStarts=[1,2], debug=True)

    def testPointsAndSegmentsTotal(self):
        self._runTest(startsA=[3,4,8], startsB=[3], endsB=[10],
                      expNoResult=True, debug=True)


if __name__ == "__main__":
    unittest.main()
