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

    def _runSubtractPointsTest(self, startsA, endsA, startsB, endsB, expStarts,
                            expEnds, allowOverlap=False,
                            resultAllowOverlap=False):
        """
        Run a union test over two points tracks.
        The test expects there to only to be segments in chr1,
        All other chromosomes need to be of size zero.
        :param startsA: Arrays of starts in track A
        :param endsA: Array of ends in track A
        :param startsB: Array of starts in track B
        :param endsB: Array of ends in track B
        :param expStarts: Expected startss after union
        :param expEnds: Expected ends after union
        :return:
        """
        track1 = createSimpleTestTrackContent(startList=startsA, endList=endsA)
        track2 = createSimpleTestTrackContent(startList=startsB, endList=endsB)

        u = Subtract(track1, track2, allowOverlap=allowOverlap,
                  resultAllowOverlap=resultAllowOverlap)

        tc = u()

        if len(expStarts) != 0:
            resFound = False
        else:
            # No result is expected
            resFound = True

        for (k, v) in tc.getTrackViews().items():
            if cmp(k, self.chr1) == 0:
                # All test tracks are in chr1
                resFound = True
                print("in red check!")
                print(v.startsAsNumpyArray())
                print(v.endsAsNumpyArray())
                self.assertTrue(np.array_equal(v.startsAsNumpyArray(),
                                               expStarts))
                self.assertTrue(np.array_equal(v.endsAsNumpyArray(), expEnds))
                self.assertTrue(np.array_equal(v.startsAsNumpyArray(),
                                               v.endsAsNumpyArray()))
            else:
                # Tests if all tracks no in chr1 have a size of 0.
                self.assertEqual(v.startsAsNumpyArray().size, 0)
                self.assertEqual(v.endsAsNumpyArray().size, 0)
                self.assertTrue(np.array_equal(v.startsAsNumpyArray(),
                                               v.endsAsNumpyArray()))

        self.assertTrue(resFound)

    def _runSubtractValuedPointsTest(self, startsA, endsA, valsA, startsB,
                                    endsB,
                                valsB, expStarts, expEnds, expVals,
                                  allowOverlap=False,
                                  resultAllowOverlap=False):
        """
        Run a union test over two Valued points tracks.
        The test expects there to only to be segments in chr1,
        All other chromosomes need to be of size zero.
        :param startsA: Arrays of starts in track A
        :param endsA: Array of ends in track A
        :param valsA: Array of values in track A
        :param startsB: Array of starts in track B
        :param endsB: Array of ends in track B
        :param valsB: Array of values in track B
        :param expStarts: Array of expected starts after union
        :param expEnds: Array of expected ends after union
        :param expVals: Array of expected values after union
        :return:
        """
        track1 = createSimpleTestTrackContent(startList=startsA,
                                              endList=endsA, valList=valsA)
        track2 = createSimpleTestTrackContent(startList=startsB,
                                              endList=endsB, valList=valsB)

        u = Subtract(track1, track2, allowOverlap=allowOverlap,
                  resultAllowOverlap=resultAllowOverlap)

        tc = u()

        for (k, v) in tc.getTrackViews().items():
            if cmp(k, self.chr1) == 0:
                # All test tracks are in chr1
                self.assertTrue(np.array_equal(v.startsAsNumpyArray(),
                                               expStarts))
                self.assertTrue(np.array_equal(v.endsAsNumpyArray(), expEnds))
                self.assertTrue(np.array_equal(v.startsAsNumpyArray(),
                                               v.endsAsNumpyArray()))
                self.assertTrue(np.array_equal(v.valsAsNumpyArray(), expVals))
            else:
                # Tests if all tracks no in chr1 have a size of 0.
                self.assertEqual(v.startsAsNumpyArray().size, 0)
                self.assertEqual(v.endsAsNumpyArray().size, 0)
                self.assertEqual(v.valsAsNumpyArray().size, 0)
                self.assertTrue(np.array_equal(v.startsAsNumpyArray(),
                                               v.endsAsNumpyArray()))

    def _runSubtractLinkedPointsTest(self, startsA, endsA, edgesA, startsB,
                                   endsB,
                                  edgesB, expStarts, expEnds, expEdges):
        """
        Run a union test over two Linked points tracks.
        The test expects there to only to be segments in chr1,
        All other chromosomes need to be of size zero.
        :param startsA: Arrays of starts in track A
        :param endsA: Array of ends in track A
        :param edgesA: Array of edges in track A
        :param startsB: Array of starts in track B
        :param endsB: Array of ends in track B
        :param edgesB: Array of edges in track B
        :param expStarts: Array of expected starts after union
        :param expEnds: Array of expected ends after union
        :param expEdges: Array of expected edges after union
        :return:
        """
        track1 = createSimpleTestTrackContent(startList=startsA,
                                              endList=endsA, edgeList=edgesA)
        track2 = createSimpleTestTrackContent(startList=startsB,
                                              endList=endsB, edgeList=edgesB)

        u = Subtract(track1, track2)

        tc = u()

        for (k, v) in tc.getTrackViews().items():
            if cmp(k, self.chr1) == 0:
                # All test tracks are in chr1
                self.assertTrue(np.array_equal(v.startsAsNumpyArray(),
                                               expStarts))
                self.assertTrue(np.array_equal(v.endsAsNumpyArray(), expEnds))
                self.assertTrue(np.array_equal(v.startsAsNumpyArray(),
                                               v.endsAsNumpyArray()))
                self.assertTrue(np.array_equal(v.edgesAsNumpyArray(),
                                               expEdges))
            else:
                # Tests if all tracks no in chr1 have a size of 0.
                self.assertEqual(v.startsAsNumpyArray().size, 0)
                self.assertEqual(v.endsAsNumpyArray().size, 0)
                self.assertEqual(v.edgesAsNumpyArray().size, 0)
                self.assertTrue(np.array_equal(v.startsAsNumpyArray(),
                                               v.endsAsNumpyArray()))

    def _runSubtractLinkedValuedPointsTest(self, startsA, endsA, valsA, edgesA,
                                        startsB, endsB, valsB, edgesB,
                                        expStarts, expEnds, expVals, expEdges):
        """
        Run a union test over two Linke Valued points tracks.
        The test expects there to only to be segments in chr1,
        All other chromosomes need to be of size zero.
        :param startsA: Arrays of starts in track A
        :param endsA: Array of ends in track A
        :param valsA: Array of values in track A
        :param edgesA: Array of edges in track A
        :param startsB: Array of starts in track B
        :param endsB: Array of ends in track B
        :param valsB: Array of values in track B
        :param edgesB: Array of edges in track A
        :param expStarts: Array of expected starts after union
        :param expEnds: Array of expected ends after union
        :param expVals: Array of expected values after union
        :param expEdges: Array of expected edges after union
        :return:
        """
        track1 = createSimpleTestTrackContent(startList=startsA,
                                              endList=endsA, valList=valsA,
                                              edgeList=edgesA)
        track2 = createSimpleTestTrackContent(startList=startsB,
                                              endList=endsB, valList=valsB,
                                              edgeList=edgesB)

        u = Subtract(track1, track2)

        # Set result track type to Linked Valued Points
        # TODO weights?
        resReq = TrackFormat([], None, [], None, None, [], None, None)
        u.setResultTrackRequirements(resReq)

        tc = u()

        for (k, v) in tc.getTrackViews().items():
            if cmp(k, self.chr1) == 0:
                # All test tracks are in chr1
                self.assertTrue(np.array_equal(v.startsAsNumpyArray(),
                                               expStarts))
                self.assertTrue(np.array_equal(v.endsAsNumpyArray(), expEnds))
                self.assertTrue(np.array_equal(v.startsAsNumpyArray(),
                                               v.endsAsNumpyArray()))
                self.assertTrue(np.array_equal(v.valsAsNumpyArray(), expVals))
                self.assertTrue(np.array_equal(v.edgesAsNumpyArray(),
                                               expEdges))
            else:
                # Tests if all tracks no in chr1 have a size of 0.
                self.assertEqual(v.startsAsNumpyArray().size, 0)
                self.assertEqual(v.endsAsNumpyArray().size, 0)
                self.assertEqual(v.valsAsNumpyArray().size, 0)
                self.assertEqual(v.edgesAsNumpyArray().size, 0)
                self.assertTrue(np.array_equal(v.startsAsNumpyArray(),
                                               v.endsAsNumpyArray()))

    def _runSubtractSegmentsTest(self, startsA, endsA, startsB, endsB,
                              expStarts, expEnds, allowOverlap=False,
                              resultAllowOverlap=False):
        """
        Run a union test over two segmented tracks.
        The test expects there to only to be segments in chr1,
        All other chromosomes need to be of size zero.
        :param startsA: Arrays of starts in track A
        :param endsA: Array of ends in track B
        :param startsB: Array of starts in track B
        :param endsB: Array of ends in track B
        :param expStarts: Array of expected starts after union
        :param expEnds: Array of expected ends after union
        :return: None
        """
        track1 = createSimpleTestTrackContent(startList=startsA, endList=endsA)
        track2 = createSimpleTestTrackContent(startList=startsB, endList=endsB)

        u = Subtract(track1, track2, allowOverlap=allowOverlap,
                  resultAllowOverlap=resultAllowOverlap)

        tc = u.calculate()

        foundRes = False

        for (k, v) in tc.getTrackViews().items():
            if cmp(k, self.chr1) == 0:
                foundRes = True
                # All test tracks are in chr1
                print("---RUN-TEST---")
                print("starts: {}".format(v.startsAsNumpyArray()))
                print("expStarts: {}".format(expStarts))
                print("ends: {}".format(v.endsAsNumpyArray()))
                print("expEnds: {}".format(expEnds))
                print("---RUN-TEST---")

                self.assertTrue(np.array_equal(v.startsAsNumpyArray(),
                                               expStarts))
                self.assertTrue(np.array_equal(v.endsAsNumpyArray(), expEnds))
            else:
                # Tests if all tracks no in chr1 have a size of 0.
                self.assertEqual(v.startsAsNumpyArray().size, 0)
                self.assertEqual(v.endsAsNumpyArray().size, 0)

        if len(expStarts) == 0:
            self.assertFalse(foundRes)
        else:
            self.assertTrue(foundRes)

    # **** Points tests ****

    def atestSubtractSimple(self):
        """
        Simple points subtract
        :return: None
        """
        self._runSubtractPointsTest(startsA=[1,2,3], endsA=[1,2,3],
                                    startsB=[3], endsB=[3], expStarts=[1,2],
                                    expEnds=[1,2])

    def atestSubtractPointsNoOverlap(self):
        """
        Points subtract, no overlapping points
        :return: None
        """
        self._runSubtractPointsTest(startsA=[1,4], endsA=[2,6], startsB=[14],
                                    endsB=[16], expStarts=[1,4], expEnds=[1,4])

    def ftestUnionPointsOverlap(self):
        """
        Points union, A and B overlap, No overlap in result.
        :return: None
        """
        self._runUnionPointsTest(startsA=[14,463], endsA=[14,463],
                                 startsB=[45,463], endsB=[45,463],
                                 expStarts=[14,45,463],
                                 expEnds=[14,45,463],
                                 resultAllowOverlap=False)

    def ftestUnionPointsOverlapAllowed(self):
        """
        Points union, A and B overlap, result overlap
        :return: None
        """
        self._runUnionPointsTest(startsA=[14,463], endsA=[14,463],
                                 startsB=[45,463], endsB=[45,463],
                                 expStarts=[14,45,463, 463],
                                 expEnds=[14,45,463, 463],
                                 resultAllowOverlap=True)

    # **** Valued Points tests ****

    def ftestUnionValuedPointsSorted(self):
        """
        Valued points union, no overlap
        :return: None
        """
        self._runUnionValuedPointsTest(startsA=[1,2,3], endsA=[1,2,3],
                                       valsA=[4,5,6], startsB=[4,5,6],
                                       endsB=[4,5,6], valsB=[1,2,3],
                                       expStarts=[1,2,3,4,5,6],
                                       expEnds=[1,2,3,4,5,6],
                                       expVals=[4,5,6,1,2,3],
                                       allowOverlap=False)

    def ftestUnionValuedPointsNotSorted(self):
        """
        Valued points union, no overlap
        :return: None
        """
        self._runUnionValuedPointsTest(startsA=[1,3],
                                       endsA=[1,3], valsA=[6,7],
                                       startsB=[2],
                                       endsB=[2], valsB=[8],
                                       expStarts=[1,2,3],
                                       expEnds=[1,2,3],
                                       expVals=[6,8,7],
                                       allowOverlap=False)

    def fptestUnionValuedPointsOverlapEnd(self):
        """
        Simple test. Overlap. Not sorted.
        Overlap at the end of the track.
        When overlapping it should return the value from track A not B
        :return: None
        """
        self._runUnionValuedPointsTest(startsA=[1,3,10],
                                       endsA=[1,3,10], valsA=[6,7,45],
                                       startsB=[2,10],
                                       endsB=[2,10], valsB=[8,100],
                                       expStarts=[1,2,3,10],
                                       expEnds=[1,2,3,10],
                                       expVals=[6,8,7,45],
                                       allowOverlap=False)

    def ptestUnionValuedPointsOverlapStart(self):
        """
        Simple test. Overlap. Not sorted.
        Overlap at the start of the track.
        When overlapping it should return the value from track A not B
        :return: None
        """
        self._runUnionValuedPointsTest(startsA=[2,3,10],
                                       endsA=[2,3,10], valsA=[6,7,45],
                                       startsB=[2,15],
                                       endsB=[2,15], valsB=[8,100],
                                       expStarts=[2,3,10,15],
                                       expEnds=[2,3,10,15],
                                       expVals=[6,7,45,100])

    def ptestUnionValuedPointsOverlapMultiple(self):
        """
        Simple test. Overlap. Not sorted.
        Multiple overlapping points
        When overlapping it should return the value from track A not B
        :return: None
        """
        self._runUnionValuedPointsTest(startsA=[1,3,6,10,20],
                                       endsA=[1,3,6,10,20],
                                       valsA=[6,7,45,5,3],
                                       startsB=[2,3,8,10,24],
                                       endsB=[2,3,8,10,24],
                                       valsB=[8,100,42,3,2],
                                       expStarts=[1,2,3,6,8,10,20,24],
                                       expEnds=[1,2,3,6,8,10,20,24],
                                       expVals=[6,8,7,45,42,5,3,2])

    # **** Segments tests ****

    def atestSubtractSegmentsSimple(self):
        """
        Segments intersect, simple.
        Two non overlapping segments
        :return: None
        """
        self._runSubtractSegmentsTest(startsA=[2], endsA=[6], startsB=[4],
                                   endsB=[8], expStarts=[2], expEnds=[4],
                                   allowOverlap=False)

    def atestSubtractSegmentsNoOverlap(self):
        """
        Segment intersect, no overlap
        :return: None
        """
        self._runSubtractSegmentsTest(startsA=[2], endsA=[4], startsB=[6],
                                      endsB=[8], expStarts=[2], expEnds=[4],
                                      allowOverlap=False)

    def atestSubtractSegmentsOverlapABeforeB(self):
        """
        Two partially overlapping segments, A before B
        :return: None
        """
        self._runSubtractSegmentsTest(startsA=[2], endsA=[4], startsB=[3],
                                      endsB=[5], expStarts=[2], expEnds=[3],
                                      allowOverlap=False)

    def atestSubtractSegmentsOverlapBBeforeA(self):
        """
        Two partially overlapping segments, B before A
        :return: None
        """
        self._runSubtractSegmentsTest(startsA=[3], endsA=[5], startsB=[2],
                                   endsB=[4], expStarts=[4], expEnds=[5],
                                   allowOverlap=False)

    def atestSubtractSegmentsOverlapBInsideA(self):
        """
        Two overlapping segments, B totally inside A
        :return: None
        """
        self._runSubtractSegmentsTest(startsA=[2], endsA=[6], startsB=[3],
                                      endsB=[5], expStarts=[2,5],
                                      expEnds=[3,6], allowOverlap=False)

    def atestSubtractSegmentsOverlapAInsideB(self):
        """
        Two overlapping segments, A totally inside B
        :return: None
        """
        self._runSubtractSegmentsTest(startsA=[3], endsA=[5], startsB=[2],
                                      endsB=[6], expStarts=[], expEnds=[],
                                      allowOverlap=False,)

    def atestSubtractSegmentsTotalOverlap(self):
        """
        Two totally overlapping segments, A == B
        :return: None
        """
        self._runSubtractSegmentsTest(startsA=[2], endsA=[4], startsB=[2],
                                      endsB=[4], expStarts=[], expEnds=[],
                                      allowOverlap=False)

    def testSubtractSegmentsOverlapBAtStartOfA(self):
        """
        Two overlapping segments, B totally inside A
        B.start == A.start
        len(A) > len(B)
        :return: None
        """
        self._runSubtractSegmentsTest(startsA=[2], endsA=[6], startsB=[2],
                                      endsB=[4], expStarts=[4], expEnds=[6],
                                      allowOverlap=False)

    def atestSubtractSegmentsOverlapAAtStartOfB(self):
        """
        Two overlaping segments, A totally inside B
        A.start == B.start
        len(B) > len (A)
        :return: None
        """
        self._runSubtractSegmentsTest(startsA=[2], endsA=[4], startsB=[2],
                                      endsB=[6], expStarts=[], expEnds=[],
                                      allowOverlap=False)

    def atestSubtractSegmentsOverlapBAtEndOfA(self):
        """
        Two overlapping segments, B totally inside A
        A.end == B.end
        len(A) > len (B)
        :return: None
        """
        self._runSubtractSegmentsTest(startsA=[2], endsA=[6], startsB=[4],
                                      endsB=[6], expStarts=[2], expEnds=[4],
                                      allowOverlap=False)

    def ftestUnionSegmentsOverlapAAtEndOfB(self):
        """
        Two overlapping segments, A totally inside B
        B.end == A.end
        len(B) > len (A)
        :return: None
        """
        self._runUnionSegmentsTest(startsA=[4], endsA=[6], startsB=[2],
                                   endsB=[6], expStarts=[2],expEnds=[6],
                                   allowOverlap=False,
                                   resultAllowOverlap=False)

    def ftestUnionSegmentsTouchingABeforeB(self):
        """
        Two none overlapping "touching" segments
        A.end == B.start

        We do not combine these at the moment.
        :return: None
        """
        self._runUnionSegmentsTest(startsA=[2], endsA=[4], startsB=[4],
                                   endsB=[6], expStarts=[2,4],expEnds=[4,6],
                                   allowOverlap=False,
                                   resultAllowOverlap=False)

    def ftestUnionSegmentsTouchingBBeforeA(self):
        """
        Two none overlapping "touching" segments
        A.end == B.start

        We do not combine these at the moment.
        :return: None
        """
        self._runUnionSegmentsTest(startsA=[4], endsA=[6], startsB=[2],
                                   endsB=[4], expStarts=[2,4], expEnds=[4,6],
                                   allowOverlap=False,
                                   resultAllowOverlap=False)

    def ftestUnionSegmentsBJoinsTwoAs(self):
        """
        B "joins" two segments in A
        :return: None
        """
        self._runUnionSegmentsTest(startsA=[2, 6], endsA=[4, 8], startsB=[3],
                                   endsB=[7], expStarts=[2], expEnds=[8],
                                   allowOverlap=False,
                                   resultAllowOverlap=False)

    def ftestUnionSegmentsAJoinsTwoBs(self):
        """
        A "joins" two segments i B
        :return: None
        """
        self._runUnionSegmentsTest(startsA=[3], endsA=[7], startsB=[2, 6],
                                   endsB=[4, 8], expStarts=[2], expEnds=[8],
                                   allowOverlap=False,
                                   resultAllowOverlap=False)

if __name__ == "__main__":
    unittest.main()
