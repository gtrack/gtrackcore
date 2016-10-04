import unittest
import numpy as np

from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track_operations.operations.Flank import Flank
from gtrackcore.test.track_operations.TestUtils import \
    createSimpleTestTrackContent


class FlankTest(unittest.TestCase):

    def setUp(self):
        self.chr1 = (GenomeRegion('hg19', 'chr1', 0,
                                  GenomeInfo.GENOMES['hg19']['size']['chr1']))
        self.chromosomes = (GenomeRegion('hg19', c, 0, l)
                            for c, l in
                            GenomeInfo.GENOMES['hg19']['size'].iteritems())

    def _runTest(self, starts=None, ends=None, values=None, strands=None,
                 ids=None, edges=None, weights=None, expStarts=None,
                 expEnds=None, expValues=None, expStrands=None, expIds=None,
                 expEdges=None, expWeights=None, customChrLength=None,
                 allowOverlap=True, resultAllowOverlap=False, start=None,
                 end=None, both=None, useFraction=False, useStrands=False,
                 treatMissingAsNegative=False, debug=False,
                 expTrackFormatType=None):

        track = createSimpleTestTrackContent(startList=starts, endList=ends,
                                             valList=values,
                                             strandList=strands,
                                             idList=ids, edgeList=edges,
                                             weightsList=weights,
                                             customChrLength=customChrLength)
        if both is not None:
            self.assertTrue((start is None and end is None))
        else:
            self.assertTrue((starts is not None or end is not None))

        f = Flank(track, both=both, start=start, end=end,
                  allowOverlap=allowOverlap,
                  resultAllowOverlap=resultAllowOverlap,
                  useStrand=useStrands, useFraction=useFraction,
                  treatMissingAsNegative=treatMissingAsNegative,
                  debug=debug)

        self.assertTrue((f is not None))

        result = f.calculate()

        resFound = False

        for (k, v) in result.getTrackViews().items():
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

    # **** Points tests ****
    # Some simple tests using a track as input. We do not need to test
    # everything as its will be equal to segments
    def testSegmentsBoth(self):
        """
        Segments, test both
        :return: None
        """

        self._runTest(starts=[10], expStarts=[5,11], expEnds=[10,16],
                      both=5, expTrackFormatType="Segments")

    def testSegmentsStart(self):
        """t
        Segments, test start
        :return: None
        """
        self._runTest(starts=[10], expStarts=[5], expEnds=[10], start=5,
                      expTrackFormatType="Segments")

    def testSegmentsEnd(self):
        """
        Segments, test end
        :return: None
        """
        self._runTest(starts=[10], expStarts=[11], expEnds=[16], end=5,
                      expTrackFormatType="Segments")

    # **** Segments tests ****
    def testSegmentsBothSimple(self):
        """
        Segments, test both, simple
        :return: None
        """

        self._runTest(starts=[10], ends=[20], expStarts=[5,20],
                      expEnds=[10,25], both=5, expTrackFormatType="Segments")

    def testSegmentsBothComplex(self):
        """
        Segments, test both, complex
        :return: None
        """
        self._runTest(starts=[10,50], ends=[20,100],expStarts=[5,20,45,100],
                      expEnds=[10,25,50,105], both=5,
                      expTrackFormatType="Segments")

    def testSegmentsBothOverlapAllow(self):
        """
        Two of the resulting flanks overlap. Overlap allowed
        :return: None
        """
        self._runTest(starts=[10,18], ends=[15,21],expStarts=[5,13,15,21],
                      expEnds=[10,18,20,26], both=5, resultAllowOverlap=True,
                      expTrackFormatType="Segments")

    def testUnderflow(self):
        """
        Test of underflow. Segment cut to 0
        :return: None
        """
        self._runTest(starts=[5], ends=[10], expStarts=[0,10], expEnds=[5,20],
                      both=10, expTrackFormatType="Segments")

    def testOverflow(self):
        """
        Test of overflow. Segment cut to region size
        :return: None
        """
        self._runTest(starts=[len(self.chr1)-10], ends=[len(self.chr1)-5],
                      expStarts=[len(self.chr1)-20, len(self.chr1)-5],
                      expEnds=[len(self.chr1)-10, len(self.chr1)], both=10,
                      expTrackFormatType="Segments")

    def testSegmentsBothSimpleFractions(self):
        """
        Simple test of lengths as fraction
        :return: None
        """
        self._runTest(starts=[10], ends=[20], expStarts=[5,20],
                      expEnds=[10,25], both=.5, useFraction=True,
                      expTrackFormatType="Segments")

    def testSegmentsBothOverlapMerge(self):
        """
        Test that overlapping segments are merged.
        :return:
        """
        self._runTest(starts=[10,20], ends=[15,30], expStarts=[5,15,30],
                      expEnds=[10,20,35], resultAllowOverlap=False,
                      both=5, expTrackFormatType="Segments")

    def testSegmentStartSimple(self):
        """
        Simple test of start, no strand.
        :return: None
        """

        self._runTest(starts=[10], ends=[20], expStarts=[5], expEnds=[10],
                      start=5, expTrackFormatType="Segments")

    def testSegmentsStartSimpleFractions(self):
        """
        No strand, start using fractions
        :return: None
        """

        self._runTest(starts=[10], ends=[20], expStarts=[5], expEnds=[10],
                      start=.5, useFraction=True,
                      expTrackFormatType="Segments")

    def testSegmentEndSimple(self):
        """
        Simple test of end, no strand
        :return: None
        """

        self._runTest(starts=[10], ends=[20], expStarts=[20], expEnds=[25],
                      end=5, resultAllowOverlap=True,
                      expTrackFormatType="Segments")

    def testSegmentsEndSimpleFraction(self):
        """
        Simple test of end, no strand.
        :return: None
        """

        self._runTest(starts=[10], ends=[20], expStarts=[20], expEnds=[25],
                      end=.5, useFraction=True, expTrackFormatType="Segments")

    def testSegmentsStartAndEndSimple(self):
        """
        Simple test of start and end, no strand.
        :return: None
        """

        self._runTest(starts=[10], ends=[20], expStarts=[5,20],
                      expEnds=[10,25], start=5, end=5,
                      expTrackFormatType="Segments")

    def testSegmentsStartAndEndSimpleFraction(self):
        """
        Simple test of start and end using fractions
        :return: None
        """

        self._runTest(starts=[10], ends=[20], expStarts=[5,20],
                      expEnds=[10,25], start=.5, end=.5, useFraction=True,
                      expTrackFormatType="Segments")

    def testSegmentsStrandPositiveBothSimple(self):
        """
        Test if positive strands are set correctly.
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['+'],
                      expStarts=[5,20], expEnds=[10,25], expStrands=['+','+'],
                      both=5, expTrackFormatType="Segments")

    def testSegmentsStrandNegativeBothSimple(self):
        """
        Test if negative strands are set correctly.
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['-'], expStarts=[5, 20],
                      expEnds=[10,25], expStrands=['-','-'], both=5,
                      expTrackFormatType="Segments")

    def testSegmentStrandStrandBothMultiple(self):
        """
        Simple test. Segments with strand, using start, only negative
        :return: None
        """
        self._runTest(starts=[10,30], ends=[20,40], strands=['+', '-'],
                      expStarts=[5,20,25,40], expEnds=[10,25,30,45],
                      expStrands=['+','+','-','-'], both=5,
                      resultAllowOverlap=True,
                      expTrackFormatType="Segments")

    def testSegmentsStrandBothSimpleFraction(self):
        """
        Test if positive strands are set correctly when using fractions
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['+'], expStarts=[5,20],
                      expEnds=[10,25], expStrands=['+','+'], both=.5,
                      useFraction=True, expTrackFormatType="Segments")

    def testSegmentsStrandNegativeBothSimpleFraction(self):
        """
        Test if positive strands are set correctly when using fractions
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['-'], expStarts=[5,20],
                      expEnds=[10,25], expStrands=['-','-'], both=.5,
                      useFraction=True, expTrackFormatType="Segments")

    def testSegmentsStrandStartSimple(self):
        """
        Simple test. Segments with strand, using start, only positive
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['+'], expStarts=[5],
                      expEnds=[10], expStrands=['+'], start=5,
                      expTrackFormatType="Segments")

    def testSegmentStrandStrandNegativeStartSimple(self):
        """
        Simple test. Segments with strand, using start, only negative
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['-'], expStarts=[20],
                      expEnds=[25], expStrands=['-'], start=5,
                      expTrackFormatType="Segments")

    def testSegmentStrandStrandStartMultiple(self):
        """
        Simple test. Segments with strand, using start, only negative
        :return: None
        """
        self._runTest(starts=[10,30], ends=[20,40], strands=['+', '-'],
                      expStarts=[5,40], expEnds=[10,45], expStrands=['+','-'],
                      start=5, expTrackFormatType="Segments")

    # *** Strand, start, remove overlap ***
    # *** Strand, end ***
    def testSegmentStrandEndSimple(self):
        """
        Segments with strand, using end, only positive
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['+'], expStarts=[20],
                      expEnds=[25], expStrands=['+'], end=5,
                      expTrackFormatType="Segments")

    def testSegmentsStrandNegativeEndSimple(self):
        """
        Segments with strand, using end, only negative
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['-'], expStarts=[5],
                      expEnds=[10], expStrands=['-'], end=5,
                      expTrackFormatType="Segments")

    # *** Strand, end, fraction ***
    def testSegmentsStrandEndSimpleFraction(self):
        """
        Segments with strand, using end as fraction, only positive
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['+'], expStarts=[20],
                      expEnds=[25], expStrands=['+'], end=.5, useFraction=True,
                      expTrackFormatType="Segments")

    def testSegmentsStrandNegativeEndSimpleFraction(self):
        """
        Segments with strand, using end as fraction, only negative
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['-'], expStarts=[5],
                      expEnds=[10], expStrands=['-'], end=.5,useFraction=True,
                      expTrackFormatType="Segments")

    # TODO test pos and neg

    # *** Strand, end, remove overlap ***
    # *** Strand, start and end ***
    def testSegmentsStrandStartAndEndSimple(self):
        """
        Segments with strand, using start and end, only positive
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['+'], expStarts=[5,20],
                      expEnds=[10,25], expStrands=['+','+'], start=5, end=5,
                      expTrackFormatType="Segments")

    def testSegmentsStrandNegativeStartAndEndSimple(self):
        """
        Segments with strand, using start and end, only negative
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['-'], expStarts=[5,20],
                      expEnds=[10,25], expStrands=['-','-'], start=5, end=5,
                      expTrackFormatType="Segments")

    def testSegmentsStrandStartAndEndSimpleFraction(self):
        """
        Segments with strand, using start and end as fraction, only positive
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['+'], expStarts=[5,20],
                      expEnds=[10,25], expStrands=['+','+'], start=.5, end=.5,
                      useFraction=True, expTrackFormatType="Segments")

    def testSegmentsStrandNegativeStartAndEndSimpleFraction(self):
        """
        Segments with strand, using start and end as fraction, only negative
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['-'], expStarts=[5,20],
                      expEnds=[10,25], expStrands=['-','-'], start=.5, end=.5,
                      useFraction=True, expTrackFormatType="Segments")

    # *** Strand, start and end, remove overlap ***
    # TODO pos and neg

    # *** Strand, both, missing positive ***
    def testSegmentsStrandBothMissingDefault(self):
        """
        Strand info missing. Test that it does the default which is to treat
        it as a positive segment.
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5,20],
                      expEnds=[10,25], expStrands=['+','+'], both=5,
                      expTrackFormatType="Segments")

    # *** Strand, both, missing positive, fraction ***
    def testSegmentStrandBothMissingDefaultFraction(self):
        """
        Strand info missing. Test that it does the default which is to treat
        it as a positive segment.
        Using fractions.
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5,20],
                      expEnds=[10,25], expStrands=['+','+'], both=.5,
                      useFraction=True, expTrackFormatType="Segments")

    # *** Strand, both, missing positive, remove overlap ***
    # TODO

    # *** Strand, both, missing negative ***
    def testSegmentsStrandBothMissingNegative(self):
        """
        Strand info missing. Test that we can treat is as negative.
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5,20],
                      expEnds=[10,25], expStrands=['-','-'], both=5,
                      treatMissingAsNegative=True,
                      expTrackFormatType="Segments")

    # *** Strand, both, missing negative, fraction ***
    def testSegmentsStrandBothMissingNegativeSimpleFraction(self):
        """
        Strand info missing. Test that we can treat is as negative.
        Using fractions.
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5,20],
                      expEnds=[10,25], expStrands=['-','-'], both=.5,
                      treatMissingAsNegative=True, useFraction=True,
                      expTrackFormatType="Segments")

    # *** Strand, both, missing negative, remove overlap ***
    # TODO
    # TODO pos and negative

    def testSegmentsStrandStartMissingDefault(self):
        """
        Strand info missing. Test that the default works.
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5],
                      expEnds=[10], expStrands=['+'], start=5,
                      expTrackFormatType="Segments")

    def testSegmentsStrandStartMissingDefaultFraction(self):
        """
        Strand info missing. Test that the default works.
        Using fractions.
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5],
                      expEnds=[10], expStrands=['+'], start=.5,
                      useFraction=True, expTrackFormatType="Segments")

    # *** Strand, start, missing positive, remove overlap ***
    # TODO, neg and pos

    def testSegmentsStrandStartMissingNegative(self):
        """
        Strand info missing. Test that we can treat is as negative.
        Using fractions.
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[20],
                      expEnds=[25], expStrands=['-'], start=5,
                      treatMissingAsNegative=True,
                      expTrackFormatType="Segments")

    def testSegmentsStrandStartMissingNegativeFraction(self):
        """
        Strand info missing. Test that we can treat is as negative.
        Using fractions.
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[20],
                      expEnds=[25], expStrands=['-'], start=.5,
                      treatMissingAsNegative=True, useFraction=True,
                      expTrackFormatType="Segments")

    # *** Strand, start, missing negative, remove overlap ***
    # *** Strand, end, missing positive ***
    # TODO

    def testSegmentsStrandEndMissingPositiveDefault(self):
        """
        Strand info missing. Test that the default works.
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[20],
                      expEnds=[25], expStrands=['+'], end=5,
                      expTrackFormatType="Segments")

    # *** Strand, end, missing positive, fraction ***
    def testSegmentsStrandEndMissingDefaultFraction(self):
        """
        Strand info missing. Test that the default works.
        Using fractions.
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[20],
                      expEnds=[25], expStrands=['+'], end=.5, useFraction=True,
                      expTrackFormatType="Segments")

    # *** Strand, end, missing positive, remove overlap ***
    # TODO

    def testSegmentsStrandEndMissingNegative(self):
        """
        Strand info missing. Test that we can treat them as negative.
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5],
                      expEnds=[10], expStrands=['-'], end=5,
                      treatMissingAsNegative=True)

    def testSegmentsStrandEndMissingNegativeFraction(self):
        """
        Strand info missing. Test that we can treat them as negative.
        Using fractions.
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5],
                      expEnds=[10], expStrands=['-'], end=.5,
                      treatMissingAsNegative=True, useFraction=True,
                      expTrackFormatType="Segments")

    # *** Strand, end, missing negative, remove overlap ***
    # TODO neg and pos

    def testSegmentsStrandStartAndEndMissingDefault(self):
        """
        Strand info missing. Test that the default works.
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['.'],expStarts=[5,20],
                      expEnds=[10,25], expStrands=['+','+'], start=5, end=5,
                      expTrackFormatType="Segments")

    # *** Strand, start and end, missing positive, fraction ***
    def testSegmentsStrandStartAndEndMissingDefaultFraction(self):
        """
        Strand info missing. Test that the default works.
        Using fractions.
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5,20],
                      expEnds=[10,25], expStrands=['+','+'], start=.5, end=.5,
                      useFraction=True, expTrackFormatType="Segments")

    # *** Strand, start and end, missing positive, remove overlap ***
    # TODO

    def testSegmentsStrandStartAndEndMissingNegative(self):
        """
        Strand info missing. Test that we can treat them as negative.
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5,20],
                      expEnds=[10,25], expStrands=['-','-'], start=5, end=5,
                      treatMissingAsNegative=True,
                      expTrackFormatType="Segments")

    def testSegmentsStrandStartAndEndMissingNegativeFractions(self):
        """
        Strand info missing. Test that we can treat them as negative.
        Using fractions.
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5,20],
                      expEnds=[10,25], expStrands=['-','-'], start=.5, end=.5,
                      treatMissingAsNegative=True, useFraction=True,
                      expTrackFormatType="Segments")

    # *** Test inputs ***
    # Test that the operations accepts the different supported track types.
    # Here we expect all extra data to be removed. The result track will
    # always be a segment type track.

    def testInputValuedPoints(self):
        """
        Valued points track as input
        :return:
        """
        self._runTest(starts=[10], values=[20], expStarts=[5,11],
                      expEnds=[10,16], both=5, expTrackFormatType="Segments")

    def testInputLinkedPoints(self):
        """
        Linked points track as input
        :return:d
        """
        self._runTest(starts=[10], ids=['1'], edges=['1'],
                      expStarts=[5,11], expEnds=[10,16], both=5,
                      expTrackFormatType="Segments")

    def testInputLinkedValuedPoints(self):
        """
        Linked valued points track as input
        :return:
        """
        self._runTest(starts=[10], values=[20], ids=['1'], edges=['1'],
                      expStarts=[5,11], expEnds=[10,16], both=5,
                      expTrackFormatType="Segments")

    def testInputValuedSegments(self):
        """
        Valued segments track as input
        :return:
        """
        self._runTest(starts=[10], ends=[15], values=[20], expStarts=[5,15],
                      expEnds=[10,20], both=5, expTrackFormatType="Segments")

    def testInputLinkedSegments(self):
        """
        Linked segments track as input
        :return:
        """
        self._runTest(starts=[10], ends=[15], ids=['1'], edges=['1'],
                      expStarts=[5,15], expEnds=[10,20], both=5,
                      expTrackFormatType="Segments")

    def testInputLinkedValuedSegments(self):
        """
        Linked valued segments track as input
        :return:
        """
        self._runTest(starts=[10], ends=[15], values=[20], ids=['1'],
                      edges=['1'], expStarts=[5,15], expEnds=[10,20], both=5,
                      expTrackFormatType="Segments")

if __name__ == "__main__":
    unittest.main()
