import unittest
import numpy as np
from collections import OrderedDict

from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.operations.Union import Union
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.test.track_operations.OperationTest import createTrackView


class UnionTest(unittest.TestCase):

    def setUp(self):
        self.chr1 = (GenomeRegion('hg19', 'chr1', 0,
                                  GenomeInfo.GENOMES['hg19']['size']['chr1']))
        self.chromosomes = (GenomeRegion('hg19', c, 0, l)
                            for c, l in
                            GenomeInfo.GENOMES['hg19']['size'].iteritems())

    def _runUnionPointsTest(self, startsA, endsA, startsB, endsB, expStarts,
                            expEnds):
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
        track1 = self._createTrackContent(startsA, endsA)
        track2 = self._createTrackContent(startsB, endsB)

        u = Union(track1, track2)

        tc = u()

        for (k, v) in tc.getTrackViews().items():
            if cmp(k, self.chr1) == 0:
                # All test tracks are in chr1
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

    def _runUnionValuedPointsTest(self, startsA, endsA, valsA, startsB, endsB,
                                valsB, expStarts, expEnds, expVals):
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
        :param expStarts: Expected startss after union
        :param expEnds: Expected ends after union
        :param expVals: Expected values after union
        :
        :return:
        """
        track1 = self._createTrackContent(startsA, endsA, valsA)
        track2 = self._createTrackContent(startsB, endsB, valsB)

        u = Union(track1, track2)

        # Set result track type to Valued Points
        resReq = TrackFormat([], None, [], None, None, None, None, None)
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
            else:
                # Tests if all tracks no in chr1 have a size of 0.
                self.assertEqual(v.startsAsNumpyArray().size, 0)
                self.assertEqual(v.endsAsNumpyArray().size, 0)
                self.assertEqual(v.valsAsNumpyArrat().size, 0)
                self.assertTrue(np.array_equal(v.startsAsNumpyArray(),
                                               v.endsAsNumpyArray()))

    def _runUnionSegmentsTest(self, startsA, endsA, startsB, endsB,
                              expStarts, expEnds):
        """
        Run a union test over two segmented tracks.
        The test expects there to only to be segments in chr1,
        All other chromosomes need to be of size zero.
        :param startsA: Arrays of starts in track A
        :param endsA: Array of ends in track B
        :param startsB: Array of starts in track B
        :param endsB: Array of ends in track B
        :param expStarts: Expected startss after union
        :param expEnds: Expected ends after union
        :return:
        """
        track1 = self._createTrackContent(startsA, endsA)
        track2 = self._createTrackContent(startsB, endsB)

        u = Union(track1, track2)

        # Set result track type to Segments
        resReq = TrackFormat([], [], None, None, None, None, None, None)
        u.setResultTrackRequirements(resReq)

        tc = u()

        for (k, v) in tc.getTrackViews().items():

            if cmp(k, self.chr1) == 0:
                # All test tracks are in chr1
                self.assertTrue(np.array_equal(v.startsAsNumpyArray(),
                                               expStarts))
                self.assertTrue(np.array_equal(v.endsAsNumpyArray(), expEnds))
            else:
                # Tests if all tracks no in chr1 have a size of 0.
                self.assertEqual(v.startsAsNumpyArray().size, 0)
                self.assertEqual(v.endsAsNumpyArray().size, 0)

    def _createTrackContent(self, starts, ends, vals=None):
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
        if vals is not None:
            vals = np.array(vals)

        tv = createTrackView(region=self.chr1, startList=starts, endList=ends,
                             allow_overlap=False, valList=vals)

        d = OrderedDict()
        d[self.chr1] = tv
        return TrackContents('hg19', d)

    # **** Points tests ****

    def testUnionPointsNoOverlap(self):
        self._runUnionPointsTest(startsA=[1,2,3], endsA=[1,2,3],
                                   startsB=[4,5,6], endsB=[4,5,6],
                                   expStarts=[1,2,3,4,5,6],
                                   expEnds=[1,2,3,4,5,6])

    def testUnionPointsOverlap(self):
        self._runUnionPointsTest(startsA=[14,463], endsA=[14,463],
                                   startsB=[45,463], endsB=[45,463],
                                   expStarts=[14,45,463],
                                   expEnds=[14,45,463])

    # **** Valued Points tests ****

    def ttestUnionValuedPointsSorted(self):
        """
        Simple test. No overlap. Pre sorted. Values not sorted.
        :return: None
        """
        self._runUnionValuedPointsTest(startsA=[1,2,3], endsA=[1,2,3],
                                       valsA=[4,5,6], startsB=[4,5,6],
                                       endsB=[4,5,6], valsB=[1,2,3],
                                       expStarts=[1,2,3,4,5,6],
                                       expEnds=[1,2,3,4,5,6],
                                       expVals=[4,5,6,1,2,3])

    def testUnionValuedPointsNotSorted(self):
        """
        Simple test. No overlap. Not sorted. Values not sorted.
        :return: None
        """
        self._runUnionValuedPointsTest(startsA=[1,3],
                                       endsA=[1,3], valsA=[6,7],
                                       startsB=[2],
                                       endsB=[2], valsB=[8],
                                       expStarts=[1,2,3],
                                       expEnds=[1,2,3],
                                       expVals=[6,8,7])

    def testUnionValuedPointsOverlapEnd(self):
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
                                       expVals=[6,8,7,45])

    def testUnionValuedPointsOverlapStart(self):
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

    def testUnionValuedPointsOverlapMultiple(self):
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

    def testUnionSegmentsNoOverlap(self):
        """
        Two non overlapping segments
        :return: None
        """
        self._runUnionSegmentsTest(startsA=[2], endsA=[4], startsB=[5],
                                   endsB=[8], expStarts=[2,5], expEnds=[4,8])

    def testUnionSegmentsOverlapABeforeB(self):
        """
        Two partially overlapping segments, A before B
        :return: None
        """
        self._runUnionSegmentsTest(startsA=[2], endsA=[4], startsB=[3],
                                   endsB=[5], expStarts=[2], expEnds=[5])

    def testUnionSegmentsOverlapBBeforeA(self):
        """
        Two partially overlapping segments, B before A
        :return: None
        """
        self._runUnionSegmentsTest(startsA=[3], endsA=[5], startsB=[2],
                                   endsB=[4], expStarts=[2], expEnds=[5])

    def testUnionSegmentsOverlapBInsideA(self):
        """
        Two overlapping segments, B totally inside A
        :return: None
        """
        self._runUnionSegmentsTest(startsA=[2], endsA=[6], startsB=[3],
                                   endsB=[5], expStarts=[2], expEnds=[6])

    def testUnionSegmentsOverlapAInsideB(self):
        """
        Two overlapping segments, A totally inside B
        :return: None
        """
        self._runUnionSegmentsTest(startsA=[3], endsA=[5], startsB=[2],
                                   endsB=[6], expStarts=[2], expEnds=[6])

    def testUnionSegmentsTotalOverlap(self):
        """
        Two totally overlapping segments, A == B
        :return: None
        """
        self._runUnionSegmentsTest(startsA=[2], endsA=[4], startsB=[2],
                                   endsB=[4], expStarts=[2], expEnds=[4])

    def testUnionSegmentsOverlapBAtStartOfA(self):
        """
        Two overlapping segments, B totally inside A
        B.start == A.start
        len(A) > len(B)
        :return: None
        """
        self._runUnionSegmentsTest(startsA=[2], endsA=[6], startsB=[2],
                                   endsB=[4], expStarts=[2], expEnds=[6])

    def testUnionSegmentsOverlapAAtStartOfB(self):
        """
        Two overlaping segments, A totally inside B
        A.start == B.start
        len(B) > len (A)
        :return: None
        """
        self._runUnionSegmentsTest(startsA=[2], endsA=[4], startsB=[2],
                                   endsB=[6], expStarts=[2], expEnds=[6])

    def testUnionSegmentsOverlapBAtEndOfA(self):
        """
        Two overlapping segments, B totally inside A
        A.end == B.end
        len(A) > len (B)
        :return: None
        """
        self._runUnionSegmentsTest(startsA=[2], endsA=[6], startsB=[4],
                                   endsB=[6], expStarts=[2], expEnds=[6])

    def testUnionSegmentsOverlapAAtEndOfB(self):
        """
        Two overlapping segments, A totally inside B
        B.end == A.end
        len(B) > len (A)
        :return: None
        """
        self._runUnionSegmentsTest(startsA=[4], endsA=[6], startsB=[2],
                                   endsB=[6], expStarts=[2],expEnds=[6])

    def testUnionSegmentsTouchingABeforeB(self):
        """
        Two none overlapping "touching" segments
        A.end == B.start
        :return: None
        """
        self._runUnionSegmentsTest(startsA=[2], endsA=[4], startsB=[4],
                                   endsB=[6], expStarts=[2],expEnds=[6])

    def testUnionSegmentsTouchingBBeforeA(self):
        """
        Two none overlapping "touching" segments
        A.end == B.start
        :return: None
        """
        self._runUnionSegmentsTest(startsA=[4], endsA=[6], startsB=[2],
                                   endsB=[4], expStarts=[2], expEnds=[6])

    def testUnionSegmentsBJoinsTwoAs(self):
        """
        B "joins" two segments in A
        :return: None
        """
        self._runUnionSegmentsTest(startsA=[2, 6], endsA=[4, 8], startsB=[3],
                                   endsB=[7], expStarts=[2], expEnds=[8])

    def testUnionSegmentsAJoinsTwoBs(self):
        """
        A "joins" two segments i B
        :return: None
        """
        self._runUnionSegmentsTest(startsA=[3], endsA=[7], startsB=[2, 6],
                                   endsB=[4, 8], expStarts=[2], expEnds=[8])

if __name__ == "__main__":
    unittest.main()
