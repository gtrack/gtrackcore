import unittest
import numpy as np
from collections import OrderedDict

from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track.format.TrackFormat import TrackFormat
from gtrackcore.track.format.TrackFormat import TrackFormatReq

from gtrackcore.track_operations.operations.Merge import Merge
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.test.track_operations.TestUtils import createTrackView
from gtrackcore.test.track_operations.TestUtils import \
    createSimpleTestTrackContent


class MergeTest(unittest.TestCase):

    def setUp(self):
        self.chr1 = (GenomeRegion('hg19', 'chr1', 0,
                                  GenomeInfo.GENOMES['hg19']['size']['chr1']))
        self.chromosomes = (GenomeRegion('hg19', c, 0, l)
                            for c, l in
                            GenomeInfo.GENOMES['hg19']['size'].iteritems())

    def _runTest(self, starts=None, ends=None, strands=None, values=None,
                 ids=None, edges=None, weights=None, extras=None,
                 expStarts=None, expEnds=None,expValues=None,
                 expStrands=None, expIds=None, expEdges=None,
                 expWeights=None, expExtras=None, expTrackFormatType=None,
                 useStrands=False, treatMissingAsNegative=False,
                 mergeValuesFunction=None, debug=False):

        track = createSimpleTestTrackContent(startList=starts, endList=ends,
                                             strandList=strands,
                                             valList=values, idList=ids,
                                             edgeList=edges,
                                             weightsList=weights)

        m = Merge(track, useStrands=useStrands,
                  treatMissingAsNegative=treatMissingAsNegative,
                  mergeValuesFunction=mergeValuesFunction, debug=debug)

        self.assertTrue((m is not None))

        result = m.calculate()

        resFound = False

        for (k, v) in result.getTrackViews().items():

            newStarts = v.startsAsNumpyArray()
            newEnds = v.endsAsNumpyArray()
            newVals = v.valsAsNumpyArray()
            newStrands = v.strandsAsNumpyArray()
            newIds = v.idsAsNumpyArray()
            newEdges = v.edgesAsNumpyArray()
            newWeights = v.weightsAsNumpyArray()
            #newExtras = v.extrasAsNumpyArray()

            if cmp(k, self.chr1) == 0:

                if expTrackFormatType is not None:
                    points = ['Points', 'Valued points', 'Linked points',
                              'Linked valued points']

                    # Todo fix for segments and partitions
                    if expTrackFormatType in points:
                        # Point type track, we create the expected "virtual"
                        # ends.
                        self.assertTrue(v.trackFormat.getFormatName() == \
                               expTrackFormatType)
                        self.assertTrue(expEnds is None)
                        expEnds = np.array(expStarts) + 1

                # All test tracks are in chr1
                if debug:
                    print("**************************************")
                    print("Result and expected results:")
                    print("expStarts: {}".format(expStarts))
                    print("newStarts: {}".format(newStarts))
                    print("expEnds: {}".format(expEnds))
                    print("newEnds: {}".format(newStarts))
                    print("expStrands: {}".format(expStrands))
                    print("newStrands: {}".format(newStrands))
                    print("expValues: {}".format(expValues))
                    print("newValues: {}".format(newVals))
                    print("expIds: {}".format(expIds))
                    print("newIds: {}".format(newIds))
                    print("expEdges: {}".format(expEdges))
                    print("newEdges: {}".format(newEdges))
                    print("expWeights: {}".format(expWeights))
                    print("newWeights: {}".format(newWeights))
                    print("**************************************")

                resFound = True

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
                    self.assertTrue(newVals is not None)
                    self.assertTrue(np.array_equal(newVals, expValues))
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
                if newStarts is not None:
                    self.assertEqual(newStarts, 0)
                if newEnds is not None:
                    self.assertEqual(newEnds, 0)
                if newStrands is not None:
                    self.assertEqual(newStrands, 0)
                if newVals is not None:
                    self.assertEqual(newVals, 0)
                if newIds is not None:
                    self.assertEqual(newIds, 0)
                if newEdges is not None:
                    self.assertEqual(newEdges, 0)
                if newWeights is not None:
                    self.assertEqual(newWeights, 0)
                #if newExtras is not None:
                #    self.assertEqual(newExtras, 0)

        self.assertTrue(resFound)

    # **** Use strands ****
    # **** Stranded points, following strands ****
    # Here we use the strand information and only merge points with ewual
    # strand
    def testUseStrandsPositive(self):
        """
        Positive strands
        :return:
        """
        self._runTest(starts=[10,10], strands=['+','+'],
                      expStarts=[10],
                      expStrands=['+'], useStrands=True,
                      expTrackFormatType="Points")

    def testUseStrandsNegative(self):
        """
        Negative strands
        :return:
        """
        self._runTest(starts=[10,10], strands=['-','-'], expStarts=[10],
                      expStrands=['-'], useStrands=True,
                      expTrackFormatType="Points")

    def testUseStrandsPositiveComplex(self):
        """
        More complex track
        :return:
        """
        self._runTest(starts=[1,5,5,10], strands=['-','+','+','+'],
                      expStarts=[1,5,10], expStrands=['-','+','+'],
                      useStrands=True, expTrackFormatType="Points")

    def testUseStrandsMultiple(self):
        """
        More complex track
        :return:
        """
        self._runTest(starts=[1,5,5,10,10,20],
                      strands=['-','+','+','-','-','+'],
                      expStarts=[1,5,10,20], expStrands=['-','+','-','+'],
                      useStrands=True, expTrackFormatType="Points")

    def testUseStrandMix(self):
        """
        Multiple overlap with mixed strands. Test that we merge the positive
        points and that the negative one is unaltered.
        :return:
        """
        self._runTest(starts=[1,1,1,4], strands=['+','+','-','+'],
                      values=[2,4,10,14], expStarts=[1,1,4],
                      expStrands=['+','-','+'], expValues=[4,10,14],
                      useStrands=True, expTrackFormatType="Valued points")

    def testUseStrandsCrossingLinks(self):
        """
        Test that links from a positive segment to a negative segment are
        updated to the new merge-ids
        :return: None
        """
        self._runTest(starts=[10,15,30], ends=[20,25,40],
                      strands=['+','+','-'], ids=['1','2','3'],
                      edges=['2','3','1'],
                      expStarts=[10,30], expEnds=[25,40], expStrands=['+','-'],
                      expIds=['merge-1','3'],
                      expEdges=[['merge-1','3'],['merge-1', '']],
                      expTrackFormatType="Linked segments")

    # **** Points ****
    def testPointsOverlap(self):
        """
        Test simple overlap of two points
        :return:
        """
        self._runTest(starts=[10,10], expStarts=[10],
                      expTrackFormatType="Points")

    def testPointsOverlapMultiple(self):
        """
        Test overlap of multiple points
        :return:
        """
        self._runTest(starts=[1,5,5,10,32,32,43,64],
                      expStarts=[1,5,10,32,43,64],
                      expTrackFormatType="Points")

    def testPointsOverlapAtRegionEnd(self):
        """
        Overlap at the region end.
        The points is from end-1 -> end
        :return: None
        """
        self._runTest(starts=[1,5,5,10,32,32,40,len(self.chr1)-1],
                      expStarts=[1,5,10,32,40,len(self.chr1)-1],
                      expTrackFormatType="Points")

    def testPointsOverlapAtRegionEndMultiple(self):
        """
        Multiple overlapping points at the region end
        :return: None
        """
        self._runTest(starts=[1,5,5,10,32,32,43,len(self.chr1)-1,
                              len(self.chr1)-1],
                      expStarts=[1,5,10,32,43,len(self.chr1)-1],
                      expTrackFormatType="Points", debug=True)

    # **** Points with strands ****
    # Here we are not using the stand information in the merg. We just test
    # that the strand information is merged

    def testPointsWithStrandsPositive(self):
        """
        Positive strands
        :return:
        """
        self._runTest(starts=[10,10], strands=['+','+'], expStarts=[10],
                      expStrands=['+'], expTrackFormatType="Points")

    def testPointsWithStrandsNegative(self):
        """
        Negative strands
        :return:
        """
        self._runTest(starts=[10,10], strands=['-','-'], expStarts=[10],
                      expStrands=['-'], expTrackFormatType="Points")

    def testPointsWithStrandsPositiveComplex(self):
        """
        More complex track
        :return:
        """
        self._runTest(starts=[1,5,5,10], strands=['+','+','+','+'],
                      expStarts=[1,5,10], expStrands=['+','+','+'],
                      expTrackFormatType="Points")

    def testPointsWithStrandsBoth(self):
        """
        Using both '+' and '-'
        :return:
        """
        self._runTest(starts=[1,5,5,10], strands=['+','-','-','+'],
                      expStarts=[1,5,10], expStrands=['+','-','+'],
                      expTrackFormatType="Points")

    def testPointsWithStrandsMissingAsResult(self):
        """
        When merging '+' and '-' we expect to get '.' as result
        :return:
        """
        self._runTest(starts=[1,5,5,10], strands=['+','-','+','+'],
                      expStarts=[1,5,10], expStrands=['+','.','+'],
                      expTrackFormatType="Points")


    # **** Valued Points ****
    def testValuedPointsDefault(self):
        """
        Test the default merge function. np.max(overlapping)
        :return:
        """
        self._runTest(starts=[10,10], values=[2,4], expStarts=[10],
                      expValues=[4], expTrackFormatType="Valued points")

    def testValuedPointsDefaultComplex(self):
        """
        A more complex test.
        :return:
        """
        self._runTest(starts=[3,10,10,25], values=[10,2,4,90],
                      expStarts=[3,10,25], expValues=[10,4,90],
                      mergeValuesFunction=np.maximum,
                      expTrackFormatType="Valued points")

    def testValuedPointsCustomMerge(self):
        """
        Test using a custom mergeValueFunction
        :return:
        """
        self._runTest(starts=[10,10], values=[2,4], expStarts=[10],
                      expValues=[2], mergeValuesFunction=np.minimum,
                      expTrackFormatType="Valued points")

    def testValuedPointsCustomMergeComplex(self):
        self._runTest(starts=[3,10,10,25], values=[10,2,4,90],
                      expStarts=[3,10,25], expValues=[10,2,90],
                      mergeValuesFunction=np.minimum,
                      expTrackFormatType="Valued points")

    def testValuedPointsMultipleOverlap(self):
        """
        Test merge of multiple overlapping valued points
        :return:
        """
        self._runTest(starts=[1,1,1], values=[2,4,10], expStarts=[1],
                      expValues=[10], expTrackFormatType="Valued points")

    def testValuedPointsMultipleOverlapMultiple(self):
        """
        Test multiple merge of multiple overlapping valued points.
        :return:
        """
        self._runTest(starts=[5,10,10,10,10,14,15,15,15,15],
                      values=[8,2,2,2,4,100,6,6,6,8],
                      expStarts=[5,10,14,15], expValues=[8,4,100,8],
                      expTrackFormatType="Valued points")

    def testValuedPointsMultipleOverlapMultiple2(self):
        """
        Second multiple test
        :return:
        """
        self._runTest(starts=[10,10,10,20,20,20], values=[2,4,2,4,4,6],
                      expStarts=[10,20], expValues=[4,6],
                      expTrackFormatType="Valued points")

    def testValuedPointsWithStrand(self):
        """
        Test merge of multiple overlapping valued points, with stands
        :return:
        """
        self._runTest(starts=[1,1,1,4], strands=['+','+','-','+'],
                      values=[2,4,10,14], expStarts=[1,4],
                      expStrands=['.','+'], expValues=[10,14],
                      expTrackFormatType="Valued points")

    # **** Linked points ****
    def testLinkedPointsOverlap(self):
        """
        Merge of two overlapping linked points
        :return: None
        """
        self._runTest(starts=[10,10], ids=['1','2'], edges=['2','1'],
                      expStarts=[10], expIds=['merge-1'],
                      expEdges=[['merge-1','merge-1']],
                      expTrackFormatType="Linked points")

    def testLinkedPointsNonSortedIds(self):
        """
        Simple test. Ids not in sorted order.
        :return: None
        """
        self._runTest(starts=[10,10], ids=['2','1'], edges=['2','1'],
                      expStarts=[10], expIds=['merge-1'],
                      expEdges=[['merge-1','merge-1']],
                      expTrackFormatType="Linked points")

    def testLinkedPointsOverlapPadding(self):
        """
        Test that none overlapping points are left alone and that the edge
        is padded correctly.
        :return: None
        """
        self._runTest(starts=[10,10,20], ids=['1','2','3'],
                      edges=['2','1','3'],
                      expStarts=[10,20], expIds=['merge-1','3'],
                      expEdges=[['merge-1','merge-1'],['3','']],
                      expTrackFormatType="Linked points")

    def testLinkedPointsOverlapMultiple(self):
        """
        Test that overlap on multiple points works.
        :return: None
        """
        self._runTest(starts=[10,10,15,15], ids=['1','2','3','4'],
                      edges=['2','1','4','3'],
                      expStarts=[10,15], expIds=['merge-1', 'merge-2'],
                      expEdges=[['merge-1','merge-1'],
                                ['merge-2','merge-2']],
                      expTrackFormatType="Linked points")

    def testLinkedPointsMultipleOverlap(self):
        """
        Test that overlap on more then two points work.
        Testing that all of the edges are saved.
        :return: None
        """
        self._runTest(starts=[10,10,10], ids=['1','2','3'],
                      edges=['2','3','1'],
                      expStarts=[10], expIds=['merge-2'],
                      expEdges=[['merge-2','merge-2','merge-2']],
                      expTrackFormatType="Linked points")

    def testLinkedPointsMultipleOverlap2(self):
        """
        Test that overlap on more then two points work.
        :return: None
        """
        self._runTest(starts=[10,10,10,10], ids=['1','2','3','4'],
                      edges=['2','3','4','1'],
                      expStarts=[10], expIds=['merge-3'],
                      expEdges=[['merge-3','merge-3','merge-3','merge-3']],
                      expTrackFormatType="Linked points")

    def testLinkedPointsMultipleOverlapMultiple(self):
        """
        Test that multiple points overlapping multiple times works as expected.
        :return:
        """
        self._runTest(starts=[10,10,10,10,20,20,20,20],
                      ids=['1','2','3','4','5','6','7','8'],
                      edges=['2','3','4','1','6','7','8','5'],
                      expStarts=[10,20], expIds=['merge-5','merge-6'],
                      expEdges=[['merge-5','merge-5','merge-5','merge-5'],
                                ['merge-6','merge-6','merge-6','merge-6']],
                      expTrackFormatType="Linked points")

    # **** Linked valued points ****
    def testLinkedValuedPointsSimple(self):
        """
        Simple test on overlap of two points
        :return:
        """
        self._runTest(starts=[10,10], ids=['1','2'], edges=['2','1'],
                      values=[10,5], expValues=[10],
                      expStarts=[10], expIds=['merge-1'],
                      expEdges=[['merge-1','merge-1']],
                      debug=True, expTrackFormatType="Linked valued points")

    def testLinkedValuedPointsComplex(self):
        """
        Test overlap on more then one point
        :return:
        """
        self._runTest(starts=[10,10,20], ids=['1','2','3'],
                      edges=['2','1','3'], values=[10,5,20], expValues=[10,20],
                      expStarts=[10,20], expIds=['merge-1','3'],
                      expEdges=[['merge-1','merge-1'],['3','']],
                      expTrackFormatType="Linked valued points")

    def testLinkedValuedPointsMany(self):
        """
        Test overlap on multiple overlapping points.
        :return:
        """
        self._runTest(starts=[10,10,15,15], ids=['1','2','3','4'],
                      edges=['2','1','4','3'], values=[10,5,20,15],
                      expValues=[10,20], expStarts=[10,15],
                      expIds=['merge-1', 'merge-2'],
                      expEdges=[['merge-1','merge-1'],
                                ['merge-2','merge-2']],
                      expTrackFormatType="Linked valued points")

    def testLinkedValuedPointsMultiple(self):
        """
        Test multiple overlapping points. Test that the links and values are
        merged correctly
        :return:
        """
        self._runTest(starts=[10,10,10], ids=['1','2','3'],
                      edges=['2','3','1'], values=[10,5,20], expValues=[20],
                      expStarts=[10], expIds=['merge-2'],
                      expEdges=[['merge-2','merge-2','merge-2']],
                      expTrackFormatType="Linked valued points")

    def testLinkedValuedPointsMultiple2(self):
        """
        Test multiple overlapping points. Test that the links and values are
        merged correctly
        :return:
        """
        self._runTest(starts=[10,10,10,10], ids=['1','2','3','4'],
                      edges=['2','3','4','1'],
                      values=[10,5,20,4], expValues=[20],
                      expStarts=[10], expIds=['merge-3'],
                      expEdges=[['merge-3','merge-3','merge-3','merge-3']],
                      expTrackFormatType="Linked valued points",)

    def testLinkedValuedPointsManyMultiple2(self):
        """
        Test a track with many, multiple overlapping points. Test that the
        links and values aremerged correctly
        :return:
        """
        self._runTest(starts=[10,10,10,10,20,20,20,20],
                      ids=['1','2','3','4','5','6','7','8'],
                      edges=['2','3','4','1','6','7','8','5'],
                      values=[10,5,20,4,10,15,16,4], expValues=[20,16],
                      expStarts=[10,20], expIds=['merge-5','merge-6'],
                      expEdges=[['merge-5','merge-5','merge-5','merge-5'],
                                ['merge-6','merge-6','merge-6','merge-6']],
                      expTrackFormatType="Linked valued points",
                      debug=True)

    # **** Segments ****
    def testSegmentsPartialOverlap(self):
        """
        Test that two partial overlapping segments are merged correctly
        :return:
        """
        self._runTest(starts=[10,20], ends=[30,25], expStarts=[10],
                      expEnds=[30], expTrackFormatType="Segments")

    def testSegmentsOverlapEqual(self):
        """
        Test that two equal segments are merged correctly.
        :return:
        """
        self._runTest(starts=[10,10], ends=[30,30], expStarts=[10],
                      expEnds=[30], expTrackFormatType="Segments")

    def testSegmentsMultipleOverlapEqual(self):
        """
        Test overlap of multiple equal segments.
        :return:
        """
        self._runTest(starts=[10,10,10,10], ends=[30,30,30,30],
                      expStarts=[10], expEnds=[30],
                      expTrackFormatType="Segments")

    def testSegmentsMultipleOverlap(self):
        """
        Test overlap when there are multiple segments inside a segment.
        :return:
        """
        self._runTest(starts=[10,20,40], ends=[50,25,45], expStarts=[10],
                      expEnds=[50], expTrackFormatType="Segments")

    def testSegmentsNoOverlap(self):
        """
        Test that we do nothing when we have no overlap
        :return:
        """
        self._runTest(starts=[10], ends=[50], expStarts=[10], expEnds=[50],
                      expTrackFormatType="Segments")

    def testSegmentsNoOverlapMultiple(self):
        """
        Test that we do nothing when we have no overlap
        :return:
        """
        self._runTest(starts=[10,100], ends=[50,300], expStarts=[10,100],
                      expEnds=[50,300], expTrackFormatType="Segments")

    def testSegmentsPartial(self):
        """
        Test that two partially overlapping segments are merge
        :return:
        """
        self._runTest(starts=[10,20], ends=[25, 40], expStarts=[10],
                      expEnds=[40], expTrackFormatType="Segments")

    def testSegmentsCombinesMultiple(self):
        """
        Segment A combines two other segments  B and C creating one new
        segment.
        :return: None
        """
        self._runTest(starts=[10,20,35], ends=[25,40,100],
                      expStarts=[10], expEnds=[100], debug=True,
                      expTrackFormatType="Segments")

    # **** Valued Segments ****
    def testValuedSegmentsNoOverlap(self):
        """
        No overlapp in track
        :return:
        """
        self._runTest(starts=[10,20], ends=[15,25], values=[1,2],
                      expStarts=[10,20], expEnds=[15,25], expValues=[1,2],
                      expTrackFormatType="Valued segments")

    def testValuedSegmentsTotalOverlap(self):
        """
        Segment B is totally inside A.
        :return:
        """
        self._runTest(starts=[10,20], ends=[30, 25], values=[10,20],
                      expStarts=[10], expEnds=[30], expValues=[20],
                      expTrackFormatType="Valued segments")

    def testValuedSegmentsCustomMerge(self):
        """
        Test using a custom mergeValuesFunction
        :return:
        """
        self._runTest(starts=[10,20], ends=[30, 25], values=[10,20],
                      expStarts=[10], expEnds=[30], expValues=[10],
                      mergeValuesFunction=np.minimum,
                      expTrackFormatType="Valued segments")

    def testValuedSegmentsPartial(self):
        """
        Test of partial overlap
        :return:
        """
        self._runTest(starts=[10,20,35], ends=[25,40,100], values=[50,40,30],
                      expStarts=[10], expEnds=[100], expValues=[50],
                      expTrackFormatType="Valued segments")

    def testValuedSegmentsPartialCustomMerge(self):
        """
        Partial overlap using a custom mergeValuesFunction
        :return:
        """
        self._runTest(starts=[10,20,35], ends=[25,40,100], values=[10,20,30],
                      expStarts=[10], expEnds=[100], expValues=[10],
                      mergeValuesFunction=np.minimum,
                      expTrackFormatType="Valued segments")

    # **** LinkedSegments ****
    def testLinkedSegmentsNoOverlap(self):
        """
        No overlap
        :return:
        """
        self._runTest(starts=[10,20], ends=[15, 25],
                      ids=['1','2'], edges=['2','1'],
                      expIds=['1','2'], expEdges=['2','1'],
                      expStarts=[10,20], expEnds=[15,25],
                      expTrackFormatType="Linked segments")

    def testLinkedSegmentsTotalOverlap(self):
        """
        B inside A
        :return:
        """
        self._runTest(starts=[10,20], ends=[30, 25],
                      ids=['1','2'], edges=['2','1'],
                      expIds=['merge-1'], expEdges=[['merge-1','merge-1']],
                      expStarts=[10], expEnds=[30],
                      expTrackFormatType="Linked segments")

    def testLinkedSegmentsEqualOverlap(self):
        """
        A == B
        :return:
        """
        self._runTest(starts=[10,10], ends=[30, 30],
                      ids=['1','2'], edges=['2','1'],
                      expIds=['merge-1'], expEdges=[['merge-1','merge-1']],
                      expStarts=[10], expEnds=[30],
                      expTrackFormatType="Linked segments")

    def testLinkedSegmentsMultipleTotalOverlap(self):
        """
        B and C inside A
        :return:
        """
        self._runTest(starts=[10,20,40], ends=[50,25,45],
                      ids=['1','2','3'], edges=['2','3','1'],
                      expIds=['merge-2'],
                      expEdges=[['merge-2','merge-2','merge-2']],
                      expStarts=[10], expEnds=[50],
                      expTrackFormatType="Linked segments")

    def testLinkedSegmentsOneSegment(self):
        # No overlap
        self._runTest(starts=[10], ends=[50],
                      ids=['1'], edges=['1'],
                      expIds=['1'], expEdges=['1'],
                      expStarts=[10], expEnds=[50],
                      expTrackFormatType="Linked segments")

    def testLinkedSegmentsMultiplePartialOverlap(self):
        """
        B joins A and C
        :return:
        """
        self._runTest(starts=[10,20,30], ends=[25,35,50],
                      ids=['1','2','3'], edges=['2','3','1'],
                      expIds=['merge-2'],
                      expEdges=[['merge-2','merge-2','merge-2']],
                      expStarts=[10], expEnds=[50],
                      expTrackFormatType="Linked segments")

    # **** weights ****
    def testWeightedLinksNoOverlap(self):
        """
        Weighted links, no overlap
        :return:
        """
        self._runTest(starts=[10,20], ends=[15, 25],
                      ids=['1','2'], edges=['2','1'], weights=[[1.],[2.]],
                      expIds=['1','2'], expEdges=['2','1'],
                      expWeights=[[1.],[2.]],
                      expStarts=[10,20], expEnds=[15,25], debug=True,
                      expTrackFormatType="Linked segments")

    def testWeightedLinkedTotalOverlap(self):
        """
        B inside A
        :return:
        """
        self._runTest(starts=[10,20], ends=[30, 25],
                      ids=['1','2'], edges=['2','1'], weights=[[1.],[2.]],
                      expIds=['merge-1'], expEdges=[['merge-1','merge-1']],
                      expWeights=[[1., 2.]], expStarts=[10], expEnds=[30],
                      expTrackFormatType="Linked segments")

    def testWeightedLinksEqualOverlap(self):
        """
        A == B
        :return:
        """
        self._runTest(starts=[10,10], ends=[30, 30],
                      ids=['1','2'], edges=['2','1'], weights=[[1.],[2.]],
                      expIds=['merge-1'], expEdges=[['merge-1','merge-1']],
                      expStarts=[10], expEnds=[30], expWeights=[[1.,2.]],
                      expTrackFormatType="Linked segments")

    def testWeightedLinksMultipleTotalOverlap(self):
        """
        B and C inside A
        :return:
        """
        self._runTest(starts=[10,20,40], ends=[50,25,45],
                      ids=['1','2','3'], edges=['2','3','1'],
                      weights=[[1.],[2.],[3.]], expIds=['merge-2'],
                      expEdges=[['merge-2','merge-2','merge-2']],
                      expWeights=[[1.,2.,3.]], expStarts=[10], expEnds=[50],
                      expTrackFormatType="Linked segments")

    def testWeightedLinksOneSegment(self):
        # No overlap
        self._runTest(starts=[10], ends=[50],
                      ids=['1'], edges=['1'], weights=[[1.]],
                      expIds=['1'], expEdges=['1'],
                      expStarts=[10], expEnds=[50], expWeights=[[1.]],
                      expTrackFormatType="Linked segments")

    def testWeightedLinksMultiplePartialOverlap(self):
        """
        B joins A and C
        The way we merge multiple overlap from the end, the order of the
        resulting weights is not intuitive, but the weight is attached to
        the correct edge.
        :return:
        """
        self._runTest(starts=[10,20,30], ends=[25,35,50],
                      ids=['1','2','3'], edges=['2','3','1'],
                      weights=[[1.],[2.],[3.]], expIds=['merge-2'],
                      expEdges=[['merge-2','merge-2','merge-2']],
                      expStarts=[10], expEnds=[50], expWeights=[[1.,3.,2.]],
                      expTrackFormatType="Linked segments")

if __name__ == "__main__":
    unittest.main()
