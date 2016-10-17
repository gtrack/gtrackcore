import unittest
import numpy as np
from collections import OrderedDict

from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.operations.Union import Union
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.test.track_operations.TestUtils import createTrackView
from gtrackcore.test.track_operations.TestUtils import \
    createSimpleTestTrackContent


class UnionTest(unittest.TestCase):

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
                 resultAllowOverlap=False, useStrands=True,
                 treatMissingAsNegative=True,
                 expTrackFormatType=None, debug=False):

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

        u = Union(track1, track2, useStrands=useStrands,
                  treatMissingAsNegative=treatMissingAsNegative,
                  resultAllowOverlap=resultAllowOverlap)

        tc = u.calculate()

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

                if expTrackFormatType is not None:
                    points = ['Points', 'Valued points', 'Linked points',
                              'Linked valued points']

                    print(v.trackFormat.getFormatName())
                    assert v.trackFormat.getFormatName() == \
                           expTrackFormatType
                     # Todo fix for segments and partitions

                    if expTrackFormatType in points:
                        print("In points!")
                        # Create the expected ends for a point type track.
                        assert expEnds is None
                        expEnds = np.array(expStarts) + 1

                if debug:
                    print("**************************************")
                    print("Result and expected results:")
                    print("TrackFormat: {}".format(v.trackFormat.getFormatName()))
                    print("expStarts: {}".format(expStarts))
                    print("newStarts: {}".format(v.startsAsNumpyArray()))
                    print("expEnds: {}".format(expEnds))
                    print("newEnds: {}".format(v.endsAsNumpyArray()))
                    print("expStrands: {}".format(expStrands))
                    print("newStrands: {}".format(v.strandsAsNumpyArray()))
                    print("expValues: {}".format(expVals))
                    print("newValues: {}".format(v.valsAsNumpyArray()))
                    print("expIds: {}".format(expIds))
                    print("newIds: {}".format(v.idsAsNumpyArray()))
                    print("expEdges: {}".format(expEdges))
                    print("newEdges: {}".format(v.edgesAsNumpyArray()))
                    print("**************************************")
                # All test tracks are in chr1

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
                    self.assertTrue(newIds is not None)
                    self.assertTrue(np.array_equal(newIds, expIds))
                else:
                    self.assertTrue(newIds is None)

                if expEdges is not None:
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

    # **** Points tests ****
    def testPointsNoOverlap(self):
        """
        Two points track, no overlap
        :return:
        """
        # Points union, no overlap, sorted
        self._runTest(startsA=[1,2,3], startsB=[4,5,6],
                      expStarts=[1,2,3,4,5,6],
                      expTrackFormatType="Points")

    def testPointsOverlapMergeSimple(self):
        """
        Points union, A and B overlap. No overlap in result.
        :return:
        """
        self._runTest(startsA=[14,20], startsB=[14], expStarts=[14,20],
                      resultAllowOverlap=False, expTrackFormatType="Points")

    def testPointsOverlapNoMergeSimple(self):
        """
        Points union, A and B overlap. No overlap in result.
        :return:
        """
        self._runTest(startsA=[14,20], startsB=[14], expStarts=[14,14,20],
                      resultAllowOverlap=True, expTrackFormatType="Points")

    def testPointsOverlapMergeMultiple(self):
        """
        Points union, A and B overlap, No overlap in result.
        :return:
        """
        self._runTest(startsA=[14,463], startsB=[14,45,463],
                      expStarts=[14,45,463], resultAllowOverlap=False,
                      expTrackFormatType="Points", debug=True)

    def testPointsOverlapNoMergeMultiple(self):
        """
        Points union, A and B overlap, result overlap
        :return:
        """

        self._runTest(startsA=[14,463], startsB=[45,463],
                      expStarts=[14,45,463,463], resultAllowOverlap=True,
                      expTrackFormatType="Points")

    def testPointsStrands(self):
        # TODO
        pass

    # **** Valued Points tests ****
    def testValuedPointsNoOverlapSimple(self):
        """
        Valued points, no overlapp
        :return: None
        """
        # Union, no overlap
        self._runTest(startsA=[1], valsA=[4], startsB=[4], valsB=[1],
                      expStarts=[1,4], expVals=[4,1],
                      expTrackFormatType="Valued points",
                      resultAllowOverlap=False)

    def testValuedPointsNoOverlapComplex(self):
        # Union, no overlap
        self._runTest(startsA=[1,2,3], valsA=[4,5,6],
                      startsB=[4,5,6], valsB=[1,2,3],
                      expStarts=[1,2,3,4,5,6], expVals=[4,5,6,1,2,3],
                      resultAllowOverlap=False,
                      expTrackFormatType="Valued points")

    def testValuedPointsMergeOverlapEnd(self):
        """
        Simple test. Overlap. Not sorted.
        Overlap at the end of the track.
        When overlapping it should return the default from merge witch is
        the maximum
        :return:
        """
        self._runTest(startsA=[1,3,10], valsA=[6,7,45],
                      startsB=[2,10], valsB=[8,100],
                      expStarts=[1,2,3,10], expVals=[6,8,7,100],
                      resultAllowOverlap=False,
                      expTrackFormatType="Valued points")

    def testValuedPointsMergeOverlapStart(self):
        """
        Simple test. Overlap. Not sorted.
        Overlap at the start of the track.
        When overlapping it should return the default witch is the maximum
        :return:
        """
        self._runTest(startsA=[2,3,10], valsA=[6,7,45],
                      startsB=[2,15], valsB=[8,100],
                      expStarts=[2,3,10,15], expVals=[8,7,45,100],
                      resultAllowOverlap=False,
                      expTrackFormatType="Valued points")

    def testValuedPointsMergeOverlapMultiple(self):
        """
        Simple test. Overlap. Not sorted.
        Multiple overlapping points
        When overlapping it should return the maximum of the values
        :return:
        """
        self._runTest(startsA=[1,3,6,10,20], valsA=[6,7,45,5,3],
                      startsB=[2,3,8,10,24], valsB=[8,100,42,3,2],
                      expStarts=[1,2,3,6,8,10,20,24],
                      expVals=[6,8,100,45,42,5,3,2],
                      resultAllowOverlap=False,
                      expTrackFormatType="Valued points")

    def testValuedPointsNoMergeOverlapEnd(self):
        """
        Simple test. Overlap. Not sorted.
        Overlap at the end of the track.
        No merge of overlap
        :return:
        """
        self._runTest(startsA=[1,3,10], valsA=[6,7,45],
                      startsB=[2,10], valsB=[8,100],
                      expStarts=[1,2,3,10,10], expVals=[6,8,7,45,100],
                      resultAllowOverlap=True,
                      expTrackFormatType="Valued points")

    def testValuedPointsNoMergeOverlapStart(self):
        """
        Simple test. Overlap. Not sorted.
        Overlap at the start of the track.
        No merge of overlap
        :return:
        """
        self._runTest(startsA=[2,3,10], valsA=[6,7,45],
                      startsB=[2,15], valsB=[8,100],
                      expStarts=[2,2,3,10,15], expVals=[6,8,7,45,100],
                      resultAllowOverlap=True,
                      expTrackFormatType="Valued points")

    def testValuedPointsNoMergeOverlapMultiple(self):
        """
        Simple test. Overlap. Not sorted.
        Multiple overlapping points
        When overlapping it should return the maximum of the values
        No merge of overlap.
        :return:
        """
        self._runTest(startsA=[1,3,6,10,20], valsA=[6,7,45,5,3],
                      startsB=[2,3,8,10,24], valsB=[8,100,42,3,2],
                      expStarts=[1,2,3,3,6,8,10,10,20,24],
                      expVals=[6,8,7,100,45,42,5,3,3,2],
                      resultAllowOverlap=True,
                      debug=True,
                      expTrackFormatType="Valued points")

    # **** Linked points tests ****
    def testLinkedPointsNoOverlap(self):
        """
        Linked points union, no overlap, sorted
        """
        self._runTest(startsA=[1,2,3], startsB=[4,5,6], idsA=['1','2','3'],
                      idsB=['4','5','6'], edgesA=['2','3','1'],
                      edgesB=['5','6','4'], expStarts=[1,2,3,4,5,6],
                      expIds=['1-track-1','2-track-1','3-track-1',
                              '4-track-2','5-track-2','6-track-2'],
                      expEdges=['2-track-1','3-track-1','1-track-1',
                                '5-track-2','6-track-2','4-track-2'],
                      resultAllowOverlap=False, debug=True,
                      expTrackFormatType="Linked points")

    def testLinkedPointsOverlapSimple(self):
        """
        Linked points union, A and B overlap. No overlap in result.
        :return:
        """
        self._runTest(startsA=[14,20], startsB=[14], idsA=['1','2'],
                      idsB=['4'], edgesA=['2','1'],
                      edgesB=['4'], expStarts=[14,20],
                      expIds=['merge-1','2-track-1'],
                      expEdges=[['2-track-1','merge-1'],['merge-1', '']],
                      resultAllowOverlap=False,
                      expTrackFormatType="Linked points")

    def testLinkedPointsMergeOverlapComplex(self):
        """
        Linked points union, A and B overlap. No overlap in result.
        :return:
        """
        self._runTest(startsA=[14,463], startsB=[45,463], idsA=['1','2'],
                      idsB=['3','4'], edgesA=['2','1'],
                      edgesB=['4','3'], expStarts=[14,45,463],
                      expIds=['1-track-1','3-track-2','merge-1'],
                      expEdges=[['merge-1',''],
                                ['merge-1',''],
                                ['1-track-1','3-track-2']],
                      resultAllowOverlap=False,
                      debug=True,
                      expTrackFormatType="Linked points")

    def testLinkedPointsNoMergeOverlapComplex(self):
        # Points union, A and B overlap. Overlap in results
        self._runTest(startsA=[14,463], startsB=[45,463], idsA=["1","2"],
                      idsB=["3","4"], edgesA=[2,1],
                      edgesB=[4,3], expStarts=[14,45,463,463],
                      expIds=["1-track-1","3-track-2","2-track-1","4-track-2"],
                      expEdges=["2-track-1","4-track-2","1-track-1",
                                "3-track-2"], resultAllowOverlap=True,
                      expTrackFormatType="Linked points")

    # **** Linked Valued Points ****
    def testLinkedValuedPointsNoOverlap(self):
        """
        TODO
        Linked valued points union
        :return: None
        """
        # Union, no overlap
        self._runTest(startsA=[1,2,3], valsA=[4,5,6],
                      idsA=['1','2','3'], idsB=['4','5','6'],
                      edgesA=['2','1','3'], edgesB=['5','6','7'],
                      startsB=[4,5,6], valsB=[1,2,3],
                      expStarts=[1,2,3,4,5,6], expVals=[4,5,6,1,2,3],
                      expIds=['1-track-1','2-track-1','3-track-1','4-track-2',
                              '5-track-2','6-track-2'],
                      expEdges=['2-track-1','1-track-1','3-track-1',
                                '5-track-2','6-track-2','7-track-2'],
                      resultAllowOverlap=False, debug=True,
                      expTrackFormatType="Linked valued points")

    def testLinkedValuedPointsMergeOverlapEnd(self):
        """
        Simple test. Overlap. Not sorted.
        Overlap at the end of the track.
        When overlapping it should return the default value from merge
        witch is the maximum
        :return:
        """

        self._runTest(startsA=[1,3,10], valsA=[6,7,45],
                      idsA=['1','2','3'], edgesA=['2','1','3'],
                      startsB=[2,10], valsB=[8,100],
                      idsB=['4','5'], edgesB=['5','4'],
                      expStarts=[1,2,3,10], expVals=[6,8,7,100],
                      expIds=['1-track-1','4-track-2','2-track-1','merge-1'],
                      expEdges=[['2-track-1',''],
                                ['merge-1',''],
                                ['1-track-1',''],
                                ['merge-1','4-track-2']],
                      resultAllowOverlap=False,
                      expTrackFormatType="Linked valued points")

    def testLinkedValuedPointsNoMergeOverlap(self):
        """
        Simple test. Overlap. Not sorted.
        Overlap at the end of the track.
        No merge of overlap
        :return:
        """

        self._runTest(startsA=[1,3,10], valsA=[6,7,45],
                      idsA=['1','2','3'], edgesA=['2','1','3'],
                      startsB=[2,10], valsB=[8,100],
                      idsB=['4','5'], edgesB=['5','4'],
                      expStarts=[1,2,3,10,10], expVals=[6,8,7,45,100],
                      expIds=['1-track-1','4-track-2','2-track-1','3-track-1',
                              '5-track-2'],
                      expEdges=['2-track-1','5-track-2','1-track-1',
                                '3-track-1','4-track-2'],
                      resultAllowOverlap=True,
                      debug=True,
                      expTrackFormatType="Linked valued points")

    def testLinkedValuedPointsMergeOverlapStart(self):
        # Simple test. Overlap. Not sorted.
        # Overlap at the start of the track.
        # When overlapping it should return the default witch is the maximum
        self._runTest(startsA=[2,3,10], valsA=[6,7,45],
                      idsA=['1','2','3'], edgesA=['2','3','1'],
                      startsB=[2,15], valsB=[8,100],
                      idsB=['4','5'], edgesB=['5','4'],
                      expStarts=[2,3,10,15], expVals=[8,7,45,100],
                      expIds=['merge-1','2-track-1','3-track-1','5-track-2'],
                      expEdges=[['2-track-1','5-track-2'],
                                ['3-track-1',''],
                                ['merge-1',''],
                                ['merge-1','']],
                      resultAllowOverlap=False,
                      expTrackFormatType="Linked valued points")

    def testLinkedValuedPointsOverlapMultiple(self):
        # Simple test. Overlap. Not sorted.
        # Multiple overlapping points
        # When overlapping it should return the maximum of the values
        self._runTest(startsA=[1,3,6,10,20], valsA=[6,7,45,5,3],
                      idsA=['1','2','3','4','5'],
                      edgesA=['2','3','4','5','1'],
                      startsB=[2,3,8,10,24], valsB=[8,100,42,3,2],
                      idsB=['6','7','8','9','10'],
                      edgesB=['7','8','9','10','6'],
                      expStarts=[1,2,3,6,8,10,20,24],
                      expVals=[6,8,100,45,42,5,3,2],
                      expIds=['1-track-1','6-track-2','merge-1','3-track-1',
                              '8-track-2','merge-2','5-track-1','10-track-2'],
                      expEdges=[['merge-1',''],
                                ['merge-1',''],
                                ['3-track-1','8-track-2'],
                                ['merge-2',''],
                                ['merge-2',''],
                                ['5-track-1','10-track-2'],
                                ['1-track-1',''],
                                ['6-track-2','']],
                      resultAllowOverlap=False,
                      expTrackFormatType="Linked valued points")

    # **** Segments tests ****
    def testSegmentsNoOverlap(self):
        """
        Segments union, no overlap.
        Two non overlapping segments
        :return:
        """
        self._runTest(startsA=[2], endsA=[4], startsB=[5], endsB=[8],
                      expStarts=[2,5], expEnds=[4,8],
                      resultAllowOverlap=False, expTrackFormatType="Segments")

    def testSegmentsPartialOverlapMergeAB(self):
        """
        Two partially overlapping segments, A before B. Merge overlap
        :return:
        """
        self._runTest(startsA=[2], endsA=[4], startsB=[3], endsB=[5],
                      expStarts=[2], expEnds=[5],
                      resultAllowOverlap=False, expTrackFormatType="Segments")

    def testSegmentsPartialOverlapMergeBA(self):
        """
        Two partially overlapping segments, B before A. Merge overlap
        :return:
        """
        self._runTest(startsA=[3], endsA=[5], startsB=[2], endsB=[4],
                      expStarts=[2], expEnds=[5],
                      resultAllowOverlap=False, expTrackFormatType="Segments")

    def testSegmentsTotalOverlapMergeBInsideA(self):
        """
        Two overlapping segments, B totally inside A. Merge overlap
        :return:
        """
        self._runTest(startsA=[2], endsA=[6], startsB=[3], endsB=[5],
                      expStarts=[2], expEnds=[6],
                      resultAllowOverlap=False, expTrackFormatType="Segments")

    def testSegmentsTotalOverlapMergeAInsideB(self):
        """
        Two overlapping segments, A totally inside B. Merge overlap
        :return:
        """
        self._runTest(startsA=[3], endsA=[5], startsB=[2], endsB=[6],
                      expStarts=[2], expEnds=[6],
                      resultAllowOverlap=False, expTrackFormatType="Segments")

    def testSegmentsTotalOverlapMergeAEqualB(self):
        """
        Two totally overlapping segments, A == B. Merge overlap
        :return:
        """
        self._runTest(startsA=[2], endsA=[4], startsB=[2], endsB=[4],
                      expStarts=[2], expEnds=[4],
                      resultAllowOverlap=False, expTrackFormatType="Segments")

    def testSegmentsTotalOverlapMergeBInsideAStart(self):
        """
        Two overlapping segments, B totally inside A. Merge overlap
        B.start == A.start
        len(A) > len(B)
        :return:
        """
        self._runTest(startsA=[2], endsA=[6], startsB=[2], endsB=[4],
                      expStarts=[2], expEnds=[6],
                      resultAllowOverlap=False, expTrackFormatType="Segments")

    def testSegmentsTotalOverlapMergeAInsideBStart(self):
        """
        Two overlapping segments, A totally inside B. Merge overlap
        A.start == B.start
        len(B) > len (A)
        :return:
        """
        self._runTest(startsA=[2], endsA=[4], startsB=[2], endsB=[6],
                      expStarts=[2], expEnds=[6],
                      resultAllowOverlap=False, expTrackFormatType="Segments")

    def testSegmentsTotalOverlapMergeBInsideAEnd(self):
        """
        Two overlapping segments, B totally inside A. Merge overlap
        A.end == B.end
        len(A) > len (B)
        :return:
        """
        self._runTest(startsA=[2], endsA=[6], startsB=[4], endsB=[6],
                      expStarts=[2], expEnds=[6], resultAllowOverlap=False,
                      expTrackFormatType="Segments")

    def testSegmentsTotalOverlapMergeAInsideBEnd(self):
        """
        Two overlapping segments, A totally inside B. Merge overlap
        B.end == A.end
        len(B) > len (A)
        :return:
        """
        self._runTest(startsA=[4], endsA=[6], startsB=[2], endsB=[6],
                      expStarts=[2],expEnds=[6], resultAllowOverlap=False,
                      expTrackFormatType="Segments")

    def testSegmentsNoMergeOfTouchingSegmentsAStart(self):
        """
        Two none overlapping "touching" segments
        A.end == B.start
        :return:
        """
        self._runTest(startsA=[2], endsA=[4], startsB=[4], endsB=[6],
                      expStarts=[2,4], expEnds=[4,6],
                      resultAllowOverlap=False, expTrackFormatType="Segments")

    def testSegmentsNoMergeOfTouchingSegmentsAEnd(self):
        """
        Two none overlapping "touching" segments
        A.end == B.start
        :return:
        """
        self._runTest(startsA=[4], endsA=[6], startsB=[2], endsB=[4],
                      expStarts=[2,4], expEnds=[4,6],
                      resultAllowOverlap=False, expTrackFormatType="Segments")

    def testSegmentsBJoinsA(self):
        """
        B "joins" two segments in A
        :return:
        """
        self._runTest(startsA=[2, 6], endsA=[4, 8], startsB=[3], endsB=[7],
                      expStarts=[2], expEnds=[8], resultAllowOverlap=False,
                      expTrackFormatType="Segments")

    def testSegmentsAJoinsB(self):
        """
        A "joins" two segments i B
        :return:
        """
        self._runTest(startsA=[3], endsA=[7], startsB=[2,6], endsB=[4,8],
                      expStarts=[2], expEnds=[8], resultAllowOverlap=False,
                      expTrackFormatType="Segments")

    # **** Valued segments tests ****
    # Most of the operation function is already covered by the segments
    # tests. Here we only do some simple tests and check that we get the
    # expected trackFormat on the resulting tracks.
    def testValuedSegmentsSimple(self):
        """
        Test valued segment tracks
        # Segments union, no overlap.
        # Two non overlapping segments
        :return:
        """

        self._runTest(startsA=[2], endsA=[4], valsA=[10], startsB=[5],
                      endsB=[8], valsB=[20], expStarts=[2,5], expEnds=[4,8],
                      expVals=[10,20], resultAllowOverlap=False,
                      expTrackFormatType="Valued segments")

    def testValuedSegmentsPartialOverlapABeforeB(self):
        """
        Two partially overlapping segments, A before B. Merge overlap
        :return:
        """
        self._runTest(startsA=[2], endsA=[4], valsA=[10], startsB=[3],
                      endsB=[5], valsB=[100], expStarts=[2], expEnds=[5],
                      expVals=[100], resultAllowOverlap=False,
                      expTrackFormatType="Valued segments")

    def testValuedSegmentsPartialOverlapBBeforeA(self):
        """
        Two partially overlapping segments, B before A. Merge overlap
        :return:
        """
        self._runTest(startsA=[3], endsA=[5], valsA=[10], startsB=[2],
                      endsB=[4], valsB=[100], expStarts=[2], expEnds=[5],
                      expVals=[100], resultAllowOverlap=False,
                      expTrackFormatType="Valued segments")

    def testValuedSegmentsOverlapBInsideA(self):
        """
        Two overlapping segments, B totally inside A. Merge overlap
        :return:
        """
        self._runTest(startsA=[2], endsA=[6], valsA=[10], startsB=[3],
                      endsB=[5], valsB=[100], expStarts=[2], expEnds=[6],
                      expVals=[100], resultAllowOverlap=False,
                      expTrackFormatType="Valued segments")

    def testValuedSegmentsOverlapAInsideB(self):
        """
        Two overlapping segments, A totally inside B. Merge overlap
        :return:
        """
        self._runTest(startsA=[3], endsA=[5], valsA=[10], startsB=[2],
                      endsB=[6], valsB=[100], expStarts=[2], expEnds=[6],
                      expVals=[100], resultAllowOverlap=False,
                      expTrackFormatType="Valued segments")

    def testValuedSegmentsOverlapAEqualB(self):
        """
        Two totally overlapping segments, A == B. Merge overlap
        :return:
        """
        self._runTest(startsA=[2], endsA=[4], valsA=[10], startsB=[2],
                      endsB=[4], valsB=[100], expStarts=[2], expEnds=[4],
                      expVals=[100], resultAllowOverlap=False,
                      expTrackFormatType="Valued segments")

    # *** Link handling ***
    # Test that we uniquefy ids
    def testUniqueLinksSimple(self):
        # Test of the makeLinksUnique feature
        # Linked points, no overlap. equal ids. Creating unique ids
        self._runTest(startsA=[14], startsB=[25], idsA=['1'],
                      idsB=['1'], edgesA=['1'],
                      edgesB=['1'], expStarts=[14,25],
                      expIds=['1-track-1','1-track-2'],
                      expEdges=['1-track-1','1-track-2'],
                      resultAllowOverlap=False,
                      expTrackFormatType="Linked points")

    def testUniqueLinksComplex(self):
        # Linked points, no overlap. equal ids. Creating unique ids
        self._runTest(startsA=[14,40], startsB=[25], idsA=['1','2'],
                      idsB=['1'], edgesA=['2','1'],
                      edgesB=['1'], expStarts=[14,25,40],
                      debug=True,
                      expIds=['1-track-1','1-track-2','2-track-1'],
                      expEdges=['2-track-1','1-track-2','1-track-1'],
                      resultAllowOverlap=False,
                      expTrackFormatType="Linked points")

    # Points and segments
    def atestPointsAndSegmentsNoOverlap(self):
        # When combining segments and points, t
        self._runTest(startsA=[2], endsA=[4], startsB=[5],
                      expStarts=[2,5], expEnds=[4,6],
                      resultAllowOverlap=False,
                      debug=True,
                      expTrackFormatType="Segments")

    def atestPointsAndSegmentsNoOverlap2(self):
        # When combining segments and points, the points are recalculated as
        self._runTest(startsA=[2], startsB=[5], endsB=[10],
                      expStarts=[2,5], expEnds=[3,10],
                      debug=True,
                      resultAllowOverlap=False, expTrackFormatType="Segments")

    # strandend and non stranded?
    # valued and not valued? default values?

if __name__ == "__main__":
    unittest.main()
