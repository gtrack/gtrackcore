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
                 allowOverlap=False, resultAllowOverlap=False,
                 useStands=True, useMissingStrands=True,
                 treatMissingAsPositive=True,
                 mergeValues=True, mergeValuesFunction=None,
                 mergeLinks=True, makeLinksUnique=False,
                 trackALinkTag=None, trackBLinkTag=None):
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

        u = Union(track1, track2, useStands=useStands,
                  useMissingStrands=useMissingStrands,
                  treatMissingAsPositive=treatMissingAsPositive,
                  mergeValues=mergeValues,
                  mergeValuesFunction=mergeValuesFunction,
                  mergeLinks=mergeLinks, makeLinksUnique=makeLinksUnique,
                  trackALinkTag=trackALinkTag, trackBLinkTag=trackBLinkTag,
                  allowOverlap=allowOverlap,
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

                #newVals = v.valsAsNumpyArray()
                #newStrands = v.strandsAsNumpyArray()
                #newIds = v.idsAsNumpyArray()
                #newEdges = v.edgesAsNumpyArray()
                #newWeights = v.weightsAsNumpyArray()
                #newExtras = v.extrasAsNumpyArray()

    # **** Points tests ****
    def testPoints(self):
        """
        Test points tests
        :return: None
        """
        # Points union, no overlap, sorted
        self._runTest(startsA=[1,2,3], startsB=[4,5,6],
                      expStarts=[1,2,3,4,5,6], allowOverlap=False)

        # Points union, A and B overlap. No overlap in result.
        self._runTest(startsA=[14,20], startsB=[14], expStarts=[14,20],
                      resultAllowOverlap=False)

        # Points union, A and B overlap, No overlap in result.
        self._runTest(startsA=[14,463], startsB=[45,463],
                      expStarts=[14,45,463], resultAllowOverlap=False)

        # Points union, A and B overlap, result overlap
        self._runTest(startsA=[14,463], startsB=[45,463],
                      expStarts=[14,45,463,463], resultAllowOverlap=True)

        # Points union, A and B overlap, result overlap merged
        self._runTest(startsA=[14,463], startsB=[45,463],
                      expStarts=[14,45,463], resultAllowOverlap=False)

    def testPointsStrands(self):
        # TODO
        pass

    # **** Valued Points tests ****
    def testValuedPoints(self):
        """
        Valued points union
        :return: None
        """

        # Union, no overlap
        self._runTest(startsA=[1], valsA=[4],
                      startsB=[4], valsB=[1],
                      expStarts=[1,4], expVals=[4,1],

                      resultAllowOverlap=False)

        # Union, no overlap
        self._runTest(startsA=[1,2,3], valsA=[4,5,6],
                      startsB=[4,5,6], valsB=[1,2,3],
                      expStarts=[1,2,3,4,5,6], expVals=[4,5,6,1,2,3],
                      resultAllowOverlap=False)

        # Union, no overlap
        self._runTest(startsA=[1,3], valsA=[6,7], startsB=[2], valsB=[8],
                      expStarts=[1,2,3], expVals=[6,8,7],
                      resultAllowOverlap=False)

        # Simple test. Overlap. Not sorted.
        # Overlap at the end of the track.
        # When overlapping it should return the default from merge witch is
        # the maximum
        self._runTest(startsA=[1,3,10], valsA=[6,7,45],
                      startsB=[2,10], valsB=[8,100],
                      expStarts=[1,2,3,10], expVals=[6,8,7,100],
                      resultAllowOverlap=False)

        # Simple test. Overlap. Not sorted.
        # Overlap at the start of the track.
        # When overlapping it should return the default witch is the maximum
        self._runTest(startsA=[2,3,10], valsA=[6,7,45],
                      startsB=[2,15], valsB=[8,100],
                      expStarts=[2,3,10,15], expVals=[8,7,45,100],
                      resultAllowOverlap=False)

        # Simple test. Overlap. Not sorted.
        # Multiple overlapping points
        # When overlapping it should return the maximum of the values
        self._runTest(startsA=[1,3,6,10,20], valsA=[6,7,45,5,3],
                      startsB=[2,3,8,10,24], valsB=[8,100,42,3,2],
                      expStarts=[1,2,3,6,8,10,20,24],
                      expVals=[6,8,100,45,42,5,3,2])

    # **** Linked points tests ****
    def testLinkedPoints(self):
        """
        Linked points tests
        ids=["1","2"], edges=[["2"], [np.nan]],
        :return: None
        """
        # Linked points union, no overlap, sorted
        self._runTest(startsA=[1,2,3], startsB=[4,5,6], idsA=['1','2','3'],
                      idsB=['4','5','6'], edgesA=['2','3','1'],
                      edgesB=['5','6','4'], expStarts=[1,2,3,4,5,6],
                      expIds=['1','2','3','4','5','6'],
                      expEdges=['2','3','1','5','6','4'],
                      resultAllowOverlap=False)

        # Linked points union, A and B overlap. No overlap in result.
        self._runTest(startsA=[14,20], startsB=[14], idsA=['1','2'],
                      idsB=['4'], edgesA=['2','1'],
                      edgesB=['4'], expStarts=[14,20],
                      expIds=['1','2'], expEdges=['2','1'],
                      resultAllowOverlap=False)

        # Linked points union, A and B overlap. Overlap removed
        self._runTest(startsA=[14,463], startsB=[45,463], idsA=['1','2'],
                      idsB=['3','4'], edgesA=['2','1'],
                      edgesB=['4','3'], expStarts=[14,45,463],
                      expIds=['1','3','2'], expEdges=['2','4','1'],
                      resultAllowOverlap=False)

        # Points union, A and B overlap. Overlap in results
        self._runTest(startsA=[14,463], startsB=[45,463], idsA=["1","2"],
                      idsB=["3","4"], edgesA=[2,1],
                      edgesB=[4,3], expStarts=[14,45,463,463],
                      expIds=["1","3","2","4"],
                      expEdges=[2,4,1,3], resultAllowOverlap=True)


    # **** Linked Valued Points ****
    def testLinkedValuedPoints(self):
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
                      expIds=['1','2','3','4','5','6'],
                      expEdges=['2','1','3','5','6','7'],
                      resultAllowOverlap=False)

        # Simple test. Overlap. Not sorted.
        # Overlap at the end of the track.
        # When overlapping it should return the default value from merge
        # witch is the maximum
        # We do nothing with the links here. Returning the links from track A
        self._runTest(startsA=[1,3,10], valsA=[6,7,45],
                      idsA=['1','2','3'], idsB=['4','5'],
                      edgesA=['2','1','3'], edgesB=['5','4'],
                      startsB=[2,10], valsB=[8,100],
                      expStarts=[1,2,3,10], expVals=[6,8,7,100],
                      expIds=['1','4','2','3'],
                      expEdges=['2','5','1','3'],
                      resultAllowOverlap=False)

    def daf(self):

        # Simple test. Overlap. Not sorted.
        # Overlap at the start of the track.
        # When overlapping it should return the default witch is the maximum
        self._runTest(startsA=[2,3,10], valsA=[6,7,45],
                      startsB=[2,15], valsB=[8,100],
                      expStarts=[2,3,10,15], expVals=[8,7,45,100],
                      resultAllowOverlap=False)

        # Simple test. Overlap. Not sorted.
        # Multiple overlapping points
        # When overlapping it should return the maximum of the values
        self._runTest(startsA=[1,3,6,10,20], valsA=[6,7,45,5,3],
                      startsB=[2,3,8,10,24], valsB=[8,100,42,3,2],
                      expStarts=[1,2,3,6,8,10,20,24],
                      expVals=[6,8,100,45,42,5,3,2])

    # **** Segments tests ****
    def testSegments(self):
        """
        Test union of segment tracks
        :return:
        """

        # Segments union, no overlap.
        # Two non overlapping segments
        self._runTest(startsA=[2], endsA=[4], startsB=[5], endsB=[8],
                      expStarts=[2,5], expEnds=[4,8], allowOverlap=False)

        # Two partially overlapping segments, A before B. Merge overlap
        self._runTest(startsA=[2], endsA=[4], startsB=[3], endsB=[5],
                      expStarts=[2], expEnds=[5], allowOverlap=False,
                      resultAllowOverlap=False)

        # Two partially overlapping segments, B before A. Merge overlap
        self._runTest(startsA=[3], endsA=[5], startsB=[2], endsB=[4],
                      expStarts=[2], expEnds=[5], allowOverlap=False,
                      resultAllowOverlap=False)

        # Two overlapping segments, B totally inside A. Merge overlap
        self._runTest(startsA=[2], endsA=[6], startsB=[3], endsB=[5],
                      expStarts=[2], expEnds=[6], allowOverlap=False,
                      resultAllowOverlap=False)

        # Two overlapping segments, A totally inside B. Merge overlap
        self._runTest(startsA=[3], endsA=[5], startsB=[2], endsB=[6],
                      expStarts=[2], expEnds=[6], allowOverlap=False,
                      resultAllowOverlap=False)

        # Two totally overlapping segments, A == B. Merge overlap
        self._runTest(startsA=[2], endsA=[4], startsB=[2], endsB=[4],
                      expStarts=[2], expEnds=[4], allowOverlap=False,
                      resultAllowOverlap=False)

        # Two overlapping segments, B totally inside A. Merge overlap
        # B.start == A.start
        # len(A) > len(B)
        self._runTest(startsA=[2], endsA=[6], startsB=[2], endsB=[4],
                      expStarts=[2], expEnds=[6], allowOverlap=False,
                      resultAllowOverlap=False)

        # Two overlaping segments, A totally inside B. Merge overlap
        # A.start == B.start
        # len(B) > len (A)
        self._runTest(startsA=[2], endsA=[4], startsB=[2], endsB=[6],
                      expStarts=[2], expEnds=[6], allowOverlap=False,
                      resultAllowOverlap=False)

        # Two overlapping segments, B totally inside A. Merge overlap
        # A.end == B.end
        # len(A) > len (B)
        self._runTest(startsA=[2], endsA=[6], startsB=[4], endsB=[6],
                      expStarts=[2], expEnds=[6], allowOverlap=False,
                      resultAllowOverlap=False)

        # Two overlapping segments, A totally inside B. Merge overlap
        # B.end == A.end
        # len(B) > len (A)
        self._runTest(startsA=[4], endsA=[6], startsB=[2], endsB=[6],
                      expStarts=[2],expEnds=[6], allowOverlap=False,
                      resultAllowOverlap=False)

        # Two none overlapping "touching" segments
        # A.end == B.start
        #
        self._runTest(startsA=[2], endsA=[4], startsB=[4],
                                   endsB=[6], expStarts=[2,4],expEnds=[4,6],
                                   allowOverlap=False,
                                   resultAllowOverlap=False)

        # Two none overlapping "touching" segments
        # A.end == B.start
        self._runTest(startsA=[4], endsA=[6], startsB=[2], endsB=[4],
                      expStarts=[2,4], expEnds=[4,6], allowOverlap=False,
                      resultAllowOverlap=False)

        # B "joins" two segments in A
        self._runTest(startsA=[2, 6], endsA=[4, 8], startsB=[3], endsB=[7],
                      expStarts=[2], expEnds=[8], allowOverlap=False,
                      resultAllowOverlap=False)

        # A "joins" two segments i B
        self._runTest(startsA=[3], endsA=[7], startsB=[2, 6], endsB=[4, 8],
                      expStarts=[2], expEnds=[8], allowOverlap=False,
                      resultAllowOverlap=False)

    # **** Segments tests ****
    def testSegments(self):
        """
        Test union of segment tracks
        :return:
        """

        # Segments union, no overlap.
        # Two non overlapping segments
        self._runTest(startsA=[2], endsA=[4], startsB=[5], endsB=[8],
                      expStarts=[2,5], expEnds=[4,8], allowOverlap=False)

        # Two partially overlapping segments, A before B. Merge overlap
        self._runTest(startsA=[2], endsA=[4], startsB=[3], endsB=[5],
                      expStarts=[2], expEnds=[5], allowOverlap=False,
                      resultAllowOverlap=False)

        # Two partially overlapping segments, B before A. Merge overlap
        self._runTest(startsA=[3], endsA=[5], startsB=[2], endsB=[4],
                      expStarts=[2], expEnds=[5], allowOverlap=False,
                      resultAllowOverlap=False)

        # Two overlapping segments, B totally inside A. Merge overlap
        self._runTest(startsA=[2], endsA=[6], startsB=[3], endsB=[5],
                      expStarts=[2], expEnds=[6], allowOverlap=False,
                      resultAllowOverlap=False)

        # Two overlapping segments, A totally inside B. Merge overlap
        self._runTest(startsA=[3], endsA=[5], startsB=[2], endsB=[6],
                      expStarts=[2], expEnds=[6], allowOverlap=False,
                      resultAllowOverlap=False)

        # Two totally overlapping segments, A == B. Merge overlap
        self._runTest(startsA=[2], endsA=[4], startsB=[2], endsB=[4],
                      expStarts=[2], expEnds=[4], allowOverlap=False,
                      resultAllowOverlap=False)

        # Two overlapping segments, B totally inside A. Merge overlap
        # B.start == A.start
        # len(A) > len(B)
        self._runTest(startsA=[2], endsA=[6], startsB=[2], endsB=[4],
                      expStarts=[2], expEnds=[6], allowOverlap=False,
                      resultAllowOverlap=False)

        # Two overlaping segments, A totally inside B. Merge overlap
        # A.start == B.start
        # len(B) > len (A)
        self._runTest(startsA=[2], endsA=[4], startsB=[2], endsB=[6],
                      expStarts=[2], expEnds=[6], allowOverlap=False,
                      resultAllowOverlap=False)

        # Two overlapping segments, B totally inside A. Merge overlap
        # A.end == B.end
        # len(A) > len (B)
        self._runTest(startsA=[2], endsA=[6], startsB=[4], endsB=[6],
                      expStarts=[2], expEnds=[6], allowOverlap=False,
                      resultAllowOverlap=False)

        # Two overlapping segments, A totally inside B. Merge overlap
        # B.end == A.end
        # len(B) > len (A)
        self._runTest(startsA=[4], endsA=[6], startsB=[2], endsB=[6],
                      expStarts=[2],expEnds=[6], allowOverlap=False,
                      resultAllowOverlap=False)

        # Two none overlapping "touching" segments
        # A.end == B.start
        #
        self._runTest(startsA=[2], endsA=[4], startsB=[4],
                                   endsB=[6], expStarts=[2,4],expEnds=[4,6],
                                   allowOverlap=False,
                                   resultAllowOverlap=False)

        # Two none overlapping "touching" segments
        # A.end == B.start
        self._runTest(startsA=[4], endsA=[6], startsB=[2], endsB=[4],
                      expStarts=[2,4], expEnds=[4,6], allowOverlap=False,
                      resultAllowOverlap=False)

        # B "joins" two segments in A
        self._runTest(startsA=[2, 6], endsA=[4, 8], startsB=[3], endsB=[7],
                      expStarts=[2], expEnds=[8], allowOverlap=False,
                      resultAllowOverlap=False)

        # A "joins" two segments i B
        self._runTest(startsA=[3], endsA=[7], startsB=[2, 6], endsB=[4, 8],
                      expStarts=[2], expEnds=[8], allowOverlap=False,
                      resultAllowOverlap=False)

    # *** Link handling ***
    # Test of how we handle links in the new track
    def testUniqueLinks(self):
        # Test of the makeLinksUnique feature

        # Linked points, no overlap. equal ids. Creating unique ids
        self._runTest(startsA=[14], startsB=[25], idsA=['1'],
                      idsB=['1'], edgesA=['1'],
                      edgesB=['1'], expStarts=[14,25],
                      expIds=['1-track-1','1-track-2'],
                      expEdges=['1-track-1','1-track-2'],
                      makeLinksUnique=True,
                      resultAllowOverlap=False)

        # Linked points, no overlap. equal ids. Creating unique ids
        self._runTest(startsA=[14,40], startsB=[25], idsA=['1','2'],
                      idsB=['1'], edgesA=['2','1'],
                      edgesB=['1'], expStarts=[14,25,40],
                      expIds=['1-track-1','1-track-2','2-track-1'],
                      expEdges=['2-track-1','1-track-2','1-track-1'],
                      makeLinksUnique=True,
                      resultAllowOverlap=False)

    # Merge links from two tracks

    # Remove dead links

    def testPointsAndSegments(self):
        # When combining segments and points, the points are recalculated as
        # segments with a length of 0
        self._runTest(startsA=[2], endsA=[4], startsB=[5],
                      expStarts=[2,5], expEnds=[4,5], allowOverlap=False)
        self._runTest(startsA=[2], startsB=[5], endsB=[10],
                      expStarts=[2,5], expEnds=[2,10], allowOverlap=False)

    def testPointsAndPartition(self):

        # When combining points and partitions, the points becomes new
        # partitions.

        pass


if __name__ == "__main__":
    unittest.main()
