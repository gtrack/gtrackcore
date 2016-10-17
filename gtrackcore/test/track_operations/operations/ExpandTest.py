import unittest
import numpy as np
from collections import OrderedDict

from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.operations.Expand import Expand
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.test.track_operations.TestUtils import createTrackView
from gtrackcore.test.track_operations.TestUtils import \
    createSimpleTestTrackContent


class ExpandTest(unittest.TestCase):

    def setUp(self):
        self.chr1 = (GenomeRegion('hg19', 'chr1', 0,
                                  GenomeInfo.GENOMES['hg19']['size']['chr1']))
        self.chromosomes = (GenomeRegion('hg19', c, 0, l)
                            for c, l in
                            GenomeInfo.GENOMES['hg19']['size'].iteritems())

    def _runTest(self, starts=None, ends=None, values=None, strands=None,
                 ids=None, edges=None, weights=None, expStarts=None,
                 expEnds=None, expValues=None, expStrands=None, expIds=None,
                 expEdges=None, expWeights=None, expExtras=None,
                 customChrLength=None, allowOverlap=True,
                 resultAllowOverlap=False, downstream=None, upstream=None, both=None,
                 useFraction=False, useStrands=False,
                 treatMissingAsNegative=False, debug=False,
                 expTrackFormatType=None):

        track = createSimpleTestTrackContent(startList=starts, endList=ends,
                                             valList=values,
                                             strandList=strands,
                                             idList=ids, edgeList=edges,
                                             weightsList=weights,
                                             customChrLength=customChrLength)

        s = Expand(track, both=both, downstream=downstream, upstream=upstream,
                   useFraction=useFraction, useStrands=useStrands,
                   treatMissingAsNegative=treatMissingAsNegative,
                   resultAllowOverlap=resultAllowOverlap, debug=debug)

        result = s.calculate()
        self.assertTrue(result is not None)

        resFound = False

        for (k, v) in result.getTrackViews().iteritems():
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
                newExtras = v.allExtrasAsDictOfNumpyArrays()

                if debug:
                    print("expTrackFormat: {}".format(expTrackFormatType))
                    print("newTrackFormat: {}".format(v.trackFormat.getFormatName()))
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
                self.assertEqual(v.size, 0)

        self.assertTrue(resFound)

    # **** Test Points ****
    # Just doing some simple test. When giving Slop a point track we return
    # a segment track. For each point we get a new segment.
    def testPointsStart(self):
        """
        Expand at the start of a point
        :return:
        """
        self._runTest(starts=[10], expStarts=[5], expEnds=[11],
                      downstream=5, expTrackFormatType="Segments")

    def testPointsEnd(self):
        """
        Expand at the end of a point
        :return:
        """
        self._runTest(starts=[10], expStarts=[10], expEnds=[16],
                      upstream=5, expTrackFormatType="Segments")

    def testPointsBoth(self):
        """
        Expand a point at both sides
        :return:
        """
        self._runTest(starts=[10], expStarts=[5], expEnds=[16],
                      both=5, expTrackFormatType="Segments")

    def testPointsStartAndEnd(self):
        """
        Expand point a start and end
        :return:
        """
        self._runTest(starts=[10], expStarts=[5], expEnds=[16],
                      downstream=5, upstream=5, expTrackFormatType="Segments")

    def testPointsStartAndEndDiff(self):
        """
        Expand point a start and end using different values
        :return:
        """
        self._runTest(starts=[10], expStarts=[6], expEnds=[21],
                      downstream=4, upstream=10, expTrackFormatType="Segments")

    # **** Test Segments ****
    def testSegmentSimpleStart(self):
        """
        Test expanding at the start of a segment
        :return: None
        """
        self._runTest(starts=[10], ends=[20], expStarts=[5], expEnds=[20],
                      downstream=5, expTrackFormatType="Segments")

    def testSegmentSimpleEnd(self):
        """
        Test expanding at the end of a segment
        :return:
        """
        self._runTest(starts=[10], ends=[20], expStarts=[10], expEnds=[25],
                      upstream=5, expTrackFormatType="Segments")

    def testSegmentSimpleBoth(self):
        """
        Test expanding a segment at both ends
        :return:
        """
        self._runTest(starts=[10], ends=[20], expStarts=[5], expEnds=[25],
                      both=5, expTrackFormatType="Segments")

    def testSegmentSimpleStartAndEnd(self):
        """
        Test expanding a segment at the start and end
        :return:
        """
        self._runTest(starts=[10], ends=[20], expStarts=[5], expEnds=[25],
                      downstream=5, upstream=5, expTrackFormatType="Segments")

    def testSegmentSimpleStartAndEndDiff(self):
        """
        Test expanding a segment at the start and end using different values
        :return:
        """
        self._runTest(starts=[10], ends=[20], expStarts=[6], expEnds=[35],
                      downstream=4, upstream=15, expTrackFormatType="Segments")

    def testUnderflowAtStart(self):
        """
        Test that a new segment can start at 0
        :return: None
        """
        self._runTest(starts=[10], ends=[20], expStarts=[0], expEnds=[20],
                      downstream=10, expTrackFormatType="Segments")

    def testUnderflowCut(self):
        """
        Test that a segment bellow 0 is cut
        :return:
        """
        self._runTest(starts=[10], ends=[20], expStarts=[0], expEnds=[20],
                      downstream=100, expTrackFormatType="Segments")

    def testUnderflowFromStart(self):
        """
        Test that the underflow is cut when the start is at 0
        :return:
        """
        self._runTest(starts=[0], ends=[20], expStarts=[0], expEnds=[20],
                      downstream=10, expTrackFormatType="Segments", debug=True)

    def testOverflowAtEnd(self):
        """
        Test that a new end can be at the len(region)
        :return:
        """
        self._runTest(starts=[400000], ends=[len(self.chr1)-20],
                      expStarts=[400000], expEnds=[len(self.chr1)], upstream=20,
                      expTrackFormatType="Segments")

    def testOverflowCut(self):
        """
        Test that a segments over the region size are cut down to the region
        size.
        :return:
        """
        self._runTest(starts=[400000], ends=[len(self.chr1)-20],
                      expStarts=[400000], expEnds=[len(self.chr1)], upstream=300,
                      expTrackFormatType="Segments")

    def testSegmentsMultipleStartNoOverlap(self):
        """
        Using start
        Test expand on multiple segments. No overlap
        :return: None
        """
        self._runTest(starts=[10,40], ends=[20,70], expStarts=[5,35],
                      expEnds=[20,70], downstream=5, expTrackFormatType="Segments")

    def testSegmentsMultipleEndNoOverlap(self):
        """
        Using end
        Test expand on multiple segments. No overlap
        :return: None
        """
        self._runTest(starts=[10,40], ends=[20, 70], expStarts=[10,40],
                      expEnds=[25,75], upstream=5, expTrackFormatType="Segments")

    def testSegmentsMultipleStartOverlapAllow(self):
        """
        Using start
        Test expand on multiple segments. Overlap, allow
        :return: None
        """
        self._runTest(starts=[10,20], ends=[15, 40], expStarts=[4,14],
                      expEnds=[15,40], downstream=6, resultAllowOverlap=True,
                      expTrackFormatType="Segments")

    def testSegmentsMultipleStartOverlapMerge(self):
        """
        Using start
        Test expand on multiple segments. Overlap, merge
        :return: None
        """
        self._runTest(starts=[10,20], ends=[15, 40], expStarts=[4],
                      expEnds=[40], downstream=6, resultAllowOverlap=False,
                      expTrackFormatType="Segments")

    def testStrandsPositiveStart(self):
        """
        Using strand, positive at the start.
        :return: None
        """
        # Positive, start
        self._runTest(starts=[10], ends=[20], strands=['+'], expStarts=[5],
                      expEnds=[20], expStrands=['+'], downstream=5, useStrands=True,
                      expTrackFormatType="Segments")

    def testStrandsPositiveEnd(self):
        """
        Using strand, positive at the end.
        :return:
        """
        self._runTest(starts=[10], ends=[20], strands=['+'], expStarts=[10],
                      expEnds=[25], expStrands=['+'], upstream=5, useStrands=True,
                      expTrackFormatType="Segments")

    def testStrandsPositiveBoth(self):
        """
        Using strand, positive at both ends
        :return:
        """
        self._runTest(starts=[10], ends=[20], strands=['+'], expStarts=[5],
                      expEnds=[25], expStrands=['+'], both=5, useStrands=True,
                      expTrackFormatType="Segments")

    def testStrandsPositiveStartAndEnd(self):
        """
        Using strand, positive at start and end
        :return:
        """
        self._runTest(starts=[10], ends=[20], strands=['+'], expStarts=[5],
                      expEnds=[30], expStrands=['+'], downstream=5, upstream=10,
                      useStrands=True, expTrackFormatType="Segments")

    def testStrandsNegativeStart(self):
        """
        Using strand, negative at start
        :return:
        """
        self._runTest(starts=[10], ends=[20], strands=['-'], expStarts=[10],
                      expEnds=[25], expStrands=['-'], downstream=5, useStrands=True,
                      expTrackFormatType="Segments")

    def testStrandsNegativeEnd(self):
        """
        Using strand, negative at end
        :return:
        """
        self._runTest(starts=[10], ends=[20], strands=['-'], expStarts=[5],
                      expEnds=[20], expStrands=['-'], upstream=5, useStrands=True,
                      expTrackFormatType="Segments")

    def testStrandsNegativeBoth(self):
        """
        Using strand, negative at both ends
        :return:
        """
        self._runTest(starts=[10], ends=[20], strands=['-'], expStarts=[5],
                      expEnds=[25], expStrands=['-'], both=5, useStrands=True,
                      expTrackFormatType="Segments")

    def testStrandsNegativeStartAndEndDifferent(self):
        """
        Using strand, negative at start and end, different values
        :return:
        """
        self._runTest(starts=[10], ends=[20], strands=['-'], expStarts=[5],
                      expEnds=[30], expStrands=['-'], downstream=10,
                      upstream=5, useStrands=True,
                      expTrackFormatType="Segments")

    def testStrandsMissingStart(self):
        """
        Using strand, at start. Strand info missing. Treating as positive.
        :return:
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5],
                      expEnds=[20], expStrands=['.'], downstream=5,
                      useStrands=True, expTrackFormatType="Segments")

    def testStrandsMissingEnd(self):
        """
        Using strand, at end. Strand info missing. Treating as positive.
        :return:
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[10],
                      expEnds=[25], expStrands=['.'], upstream=5,
                      useStrands=True, expTrackFormatType="Segments")

    def testStrandsMissingBoth(self):
        """
        Using strand, at both ends. Strand info missing. Treating as positive.
        :return:
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5],
                      expEnds=[25], expStrands=['.'], both=5, useStrands=True,
                      expTrackFormatType="Segments")

    def testStrandsMissingStartAndEnds(self):
        """
        Using strand, at start and ends. Strand info missing. Treating as
        positive.
        :return:
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5],
                      expEnds=[30], expStrands=['.'], downstream=5,
                      upstream=10, useStrands=True,
                      expTrackFormatType="Segments")

    def testStrandsMissingAsNegativeStart(self):
        """
        Using strand, at start. Strand info missing. Treating as
        negative.
        :return:
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[10],
                      expEnds=[25], expStrands=['.'], downstream=5,
                      useStrands=True, treatMissingAsNegative=True,
                      expTrackFormatType="Segments")

    def testStrandsMissingAsNegativeEnd(self):
        """
        Using strand, at end. Strand info missing. Treating as
        negative.
        :return:
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5],
                      expEnds=[20], expStrands=['.'], upstream=5,
                      useStrands=True, treatMissingAsNegative=True,
                      expTrackFormatType="Segments")

    def testStrandsMissingAsNegativeBoth(self):
        """
        Using strand, at both. Strand info missing. Treating as
        negative.
        :return:
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5],
                      expEnds=[25], expStrands=['.'], both=5, useStrands=True,
                      treatMissingAsNegative=True,
                      expTrackFormatType="Segments")

    def testStrandsMissingAsNegativeStartAndEnd(self):
        """
        Using strand, at both. Strand info missing. Treating as
        negative.
        :return:
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[0],
                      expEnds=[25], expStrands=['.'], downstream=5,
                      upstream=10, useStrands=True,
                      treatMissingAsNegative=True,
                      expTrackFormatType="Segments")

    def testOverlapStartAllow(self):
        """
        Using start
        Overlapping segments after expand. We allow overlap in the result.
        Check that we get the correct segment.
        :return: None
        """
        self._runTest(starts=[10,25], ends=[20,30], expStarts=[4,19],
                      expEnds=[20,30], downstream=6, resultAllowOverlap=True,
                      expTrackFormatType="Segments")

    def testOverlapStartMerge(self):
        """
        Using start
        Overlapping segments after expand. Check that they are merge
        correctly if we do not allow overlap.
        :return:
        """
        self._runTest(starts=[10,25], ends=[20,30], expStarts=[4],
                      expEnds=[30], downstream=6, resultAllowOverlap=False,
                      expTrackFormatType="Segments")

    def testOverlapEndAllow(self):
        """
        Using end
        Overlapping segments after expand. We allow overlap in the result.
        Check that we get the correct segment.
        :return: None
        """
        self._runTest(starts=[10,24], ends=[20,100], expStarts=[10, 24],
                      expEnds=[25,105], upstream=5, resultAllowOverlap=True,
                      expTrackFormatType="Segments")

    def testOverlapEndMerge(self):
        """
        Using end
        Overlapping segments after expand. Check that they are merge
        correctly if we do not allow overlap.
        :return:
        """
        self._runTest(starts=[10,24], ends=[20,100], expStarts=[10],
                      expEnds=[105], upstream=5, resultAllowOverlap=False,
                      expTrackFormatType="Segments")

    def testOverlapBothAllow(self):
        """
        Using both
        Overlapping segments after expand. We allow overlap in the result.
        Check that we get the correct segment.
        :return: None
        """
        self._runTest(starts=[10,22], ends=[20,30], expStarts=[5,17],
                      expEnds=[25,35], both=5, resultAllowOverlap=True,
                      expTrackFormatType="Segments")

    def testOverlapBothMerge(self):
        """
        Using both
        Overlapping segments after expand. Check that they are merge
        correctly if we do not allow overlap.
        :return:
        """
        self._runTest(starts=[10,22], ends=[20,30], expStarts=[5],
                      expEnds=[35], both=5, resultAllowOverlap=False,
                      expTrackFormatType="Segments")

    def testOverlapStartAndEndAllow(self):
        """
        Using start and end
        Overlapping segments after expand. We allow overlap in the result.
        Check that we get the correct segment.
        :return: None
        """
        self._runTest(starts=[10,22], ends=[20,30], expStarts=[5,17],
                      expEnds=[25,35], downstream=5, upstream=5,
                      resultAllowOverlap=True, expTrackFormatType="Segments")

    def testOverlapStartAndEndMerge(self):
        """
        Using start and end
        Overlapping segments after expand. Check that they are merge
        correctly if we do not allow overlap.
        :return:
        """
        self._runTest(starts=[10,22], ends=[20,30], expStarts=[5],
                      expEnds=[35], downstream=5, upstream=5, resultAllowOverlap=False,
                      expTrackFormatType="Segments")

    def testOverlapStartAndEndAllowDiff(self):
        """
        Using start and end, different values
        Overlapping segments after expand. We allow overlap in the result.
        Check that we get the correct segment.
        :return: None
        """
        self._runTest(starts=[10,37], ends=[20,50], expStarts=[6],
                      expEnds=[65], downstream=4, upstream=15,
                      resultAllowOverlap=False, expTrackFormatType="Segments")

    def testOverlapStartAndEndMergeDiff(self):
        """
        Using start and end, different values
        Overlapping segments after expand. Check that they are merge
        correctly if we do not allow overlap.
        :return:
        """
        self._runTest(starts=[10,37], ends=[20,50], expStarts=[6],
                      expEnds=[65], downstream=4, upstream=15,
                      resultAllowOverlap=False, expTrackFormatType="Segments")

    def testFractionsStart(self):
        """
        Using start
        Test expanding using a fraction of the segments length
        :return:
        """
        self._runTest(starts=[10], ends=[20], expStarts=[5], expEnds=[20],
                      downstream=0.5, useFraction=True, resultAllowOverlap=True,
                      expTrackFormatType="Segments")

    def testFractionsEnd(self):
        """
        Using end
        Test expanding using a fraction of the segments length
        :return:
        """
        self._runTest(starts=[10], ends=[20], expStarts=[10], expEnds=[25],
                      upstream=0.5, useFraction=True, resultAllowOverlap=True,
                      expTrackFormatType="Segments", debug=True)

    def testFractionsBoth(self):
        """
        Using both
        Test expanding using a fraction of the segments length
        :return:
        """
        self._runTest(starts=[10], ends=[20], expStarts=[5], expEnds=[25],
                      both=0.5, useFraction=True, resultAllowOverlap=True,
                      expTrackFormatType="Segments")

    def testFractionsStartAndEnd(self):
        """
        Using start and end
        Test expanding using a fraction of the segments length
        :return:
        """
        self._runTest(starts=[10], ends=[20], expStarts=[5], expEnds=[25],
                      downstream=0.5, upstream=0.5, useFraction=True,
                      resultAllowOverlap=True, expTrackFormatType="Segments")

    def testFractionsStartAndEndDiff(self):
        """
        Using start and end, different values
        Test expanding using a fraction of the segments length
        :return:
        """
        self._runTest(starts=[10], ends=[20], expStarts=[5], expEnds=[30],
                      downstream=0.5, upstream=1, useFraction=True,
                      resultAllowOverlap=True, expTrackFormatType="Segments")

    def testSegmentsResorting(self):
        """
        In some cases the we loose the ordering of the segments.
        To fix this we need to re-sort them.

        This case can happen when we have a segment track with strand
        information, and we only add to the end or the start

        Start = 6
        Input: starts=[5,10], ends=[8,15]
              a    b
            ---- ++++++

        Result: starts=[5,4], ends=[14,15]
            ----------
           ++++++++++++

        Here segment b has moved in front of segment a.

        Result after sort: starts=[4,5], ends=[15,14]

        :return:
        """

        self._runTest(starts=[5,10], ends=[8,15], strands=['-','+'],
                      downstream=6, expStarts=[4,5], expEnds=[15,14],
                      expStrands=['+','-'], useStrands=True,
                      resultAllowOverlap=True, expTrackFormatType="Segments")

    # *** Test track input ***
    # Test that the different information is saved into the new track
    def testInputValuedPoints(self):
        """
        Test that the values are kept.
        :return:
        """
        self._runTest(starts=[10], values=[100], upstream=10, expStarts=[10],
                      expEnds=[21], expValues=[100],
                      expTrackFormatType="Valued segments",
                      debug=True)

    def testInputLinkedPoints(self):
        """
        Test linked points as input
        :return:
        """
        self._runTest(starts=[10], ids=['1'], edges=['1'], upstream=10,
                      expStarts=[10], expEnds=[21], expIds=['1'],
                      expEdges=['1'], expTrackFormatType="Linked segments")

    def testInputLinkedValuedPoints(self):
        """
        Test linked valued points as input
        :return:
        """
        self._runTest(starts=[10], values=[100], ids=['1'], edges=['1'],
                      upstream=10, expStarts=[10], expEnds=[21], expValues=[100],
                      expIds=['1'], expEdges=['1'],
                      expTrackFormatType="Linked valued segments",)

    def testInputValuedSegments(self):
        """
        Test Valued segments as input
        :return:
        """
        self._runTest(starts=[10], ends=[20], values=[100], upstream=10,
                      expStarts=[10], expEnds=[30], expValues=[100],
                      expTrackFormatType="Valued segments",)

    def testInputLinkedSegments(self):
        """
        Test Linked segments as input
        :return:
        """
        self._runTest(starts=[10], ends=[20], ids=['1'], edges=['1'],
                      upstream=10, expStarts=[10], expEnds=[30], expIds=['1'],
                      expEdges=['1'], expTrackFormatType="Linked segments",)

    def testInputLinkedValuedSegments(self):
        """
        Test Linked valued segments as inpout
        :return:
        """
        self._runTest(starts=[10], ends=[20], values=[100], ids=['1'],
                      edges=['1'], upstream=10, expStarts=[10], expEnds=[30],
                      expValues=[100], expIds=['1'], expEdges=['1'],
                      expTrackFormatType="Linked valued segments",)

if __name__ == "__main__":
    unittest.main()
