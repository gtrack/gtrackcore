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
                 ids=None, edges=None, weights=None, extras=None,
                 expStarts=None, expEnds=None, expValues=None,
                 expStrands=None, expIds=None, expEdges=None,
                 expWeights=None, expExtras=None, customChrLength=None,
                 resultAllowOverlap=False, upstream=None, downstream=None,
                 both=None, useFraction=False, useStrands=True,
                 treatMissingAsNegative=False, debug=False,
                 expTrackFormatType=None):

        track = createSimpleTestTrackContent(startList=starts, endList=ends,
                                             valList=values,
                                             strandList=strands,
                                             idList=ids, edgeList=edges,
                                             weightsList=weights,
                                             extraLists=extras,
                                             customChrLength=customChrLength)
        if both is not None:
            self.assertTrue((downstream is None and upstream is None))
        else:
            self.assertTrue((downstream is not None or upstream is not None))

        f = Flank(track, both=both, downstream=downstream, upstream=upstream,
                  resultAllowOverlap=resultAllowOverlap,
                  useStrands=useStrands, useFraction=useFraction,
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
                newExtras = v.allExtrasAsDictOfNumpyArrays()

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

                if expExtras is not None:
                    for key in expExtras.keys():
                        self.assertTrue(v.hasExtra(key))

                        expExtra = expExtras[key]
                        newExtra = newExtras[key]
                        self.assertTrue(np.array_equal(newExtra, expExtra))
                else:
                    self.assertTrue(len(newExtras) == 0)

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

    def testSegmentsDownstream(self):
        """t
        Segments, test downstream
        :return: None
        """
        self._runTest(starts=[10], expStarts=[5], expEnds=[10], downstream=5,
                      expTrackFormatType="Segments")

    def testSegmentsUpstream(self):
        """
        Segments, test upstream
        :return: None
        """
        self._runTest(starts=[10], expStarts=[11], expEnds=[16], upstream=5,
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

    def testSegmentDownstreamSimple(self):
        """
        Simple test of downstream, no strand.
        :return: None
        """

        self._runTest(starts=[10], ends=[20], expStarts=[5], expEnds=[10],
                      downstream=5, expTrackFormatType="Segments")

    def testSegmentsDownstreamSimpleFractions(self):
        """
        No strand, start using fractions
        :return: None
        """

        self._runTest(starts=[10], ends=[20], expStarts=[5], expEnds=[10],
                      downstream=.5, useFraction=True,
                      expTrackFormatType="Segments", debug=True)

    def testSegmentUpstreamSimple(self):
        """
        Simple test of end, no strand
        :return: None
        """

        self._runTest(starts=[10], ends=[20], expStarts=[20], expEnds=[25],
                      upstream=5, resultAllowOverlap=True,
                      expTrackFormatType="Segments", debug=True)

    def testSegmentsUpstreamSimpleFraction(self):
        """
        Simple test of end, no strand.
        :return: None
        """

        self._runTest(starts=[10], ends=[20], expStarts=[20], expEnds=[25],
                      upstream=.5, useFraction=True,
                      expTrackFormatType="Segments")

    def testSegmentsDownstreamAndUpstreamSimple(self):
        """
        Simple test of start and end, no strand.
        :return: None
        """

        self._runTest(starts=[10], ends=[20], expStarts=[5,20],
                      expEnds=[10,25], upstream=5, downstream=5,
                      expTrackFormatType="Segments")

    def testSegmentsDownstreamAndUpstreamSimpleFraction(self):
        """
        Simple test of start and end using fractions
        :return: None
        """

        self._runTest(starts=[10], ends=[20], expStarts=[5,20],
                      expEnds=[10,25], upstream=.5, downstream=.5, useFraction=True,
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

    def testSegmentsStrandDownstreamSimple(self):
        """
        Simple test. Segments with strand, using downstream, only positive
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['+'], expStarts=[5],
                      expEnds=[10], expStrands=['+'], downstream=5,
                      expTrackFormatType="Segments")

    def testSegmentStrandStrandNegativeDownstreamSimple(self):
        """
        Simple test. Segments with strand, using downstram, only negative
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['-'], expStarts=[20],
                      expEnds=[25], expStrands=['-'], downstream=5,
                      expTrackFormatType="Segments")

    def testSegmentStrandStrandDownstreamMultiple(self):
        """
        Simple test. Segments with strand, using downstream,
        :return: None
        """
        self._runTest(starts=[10,30], ends=[20,40], strands=['+', '-'],
                      expStarts=[5,40], expEnds=[10,45], expStrands=['+','-'],
                      downstream=5, expTrackFormatType="Segments", debug=True)

    # *** Strand, start, remove overlap ***
    # *** Strand, end ***
    def testSegmentStrandUpstreamSimple(self):
        """
        Segments with strand, using upstream, only positive
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['+'], expStarts=[20],
                      expEnds=[25], expStrands=['+'], upstream=5,
                      expTrackFormatType="Segments")

    def testSegmentsStrandNegativeUpstreamSimple(self):
        """
        Segments with strand, using upstream, only negative
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['-'], expStarts=[5],
                      expEnds=[10], expStrands=['-'], upstream=5,
                      expTrackFormatType="Segments")

    # *** Strand, upstream, fraction ***
    def testSegmentsStrandUpstreamSimpleFraction(self):
        """
        Segments with strand, using upstream as fraction, only positive
        :return:
        """
        self._runTest(starts=[10], ends=[20], strands=['+'], expStarts=[20],
                      expEnds=[25], expStrands=['+'], upstream=.5,
                      useFraction=True, expTrackFormatType="Segments")

    def testSegmentsStrandNegativeUpstreamSimpleFraction(self):
        """
        Segments with strand, using upstream as fraction, only negative
        :return:
        """
        self._runTest(starts=[10], ends=[20], strands=['-'], expStarts=[5],
                      expEnds=[10], expStrands=['-'], upstream=.5,
                      useFraction=True, expTrackFormatType="Segments")

    # *** Strand, upstream, remove overlap ***
    # *** Strand, downstream and upstream ***
    def testSegmentsStrandDownStramAndUpstremSimple(self):
        """
        Segments with strand, using down and upstream, only positive
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['+'], expStarts=[5,20],
                      expEnds=[10,25], expStrands=['+','+'], upstream=5,
                      downstream=5, expTrackFormatType="Segments")

    def testSegmentsStrandNegativeDownstreamAndUpstreamSimple(self):
        """
        Segments with strand, using down- and upstream, only negative
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['-'], expStarts=[5,20],
                      expEnds=[10,25], expStrands=['-','-'], upstream=5,
                      downstream=5, expTrackFormatType="Segments")

    def testSegmentsStrandDownstreamAndUpstreamSimpleFraction(self):
        """
        Segments with strand, using down- and upstream as fraction,
        only positive
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['+'], expStarts=[5,20],
                      expEnds=[10,25], expStrands=['+','+'], upstream=.5,
                      downstream=.5, useFraction=True,
                      expTrackFormatType="Segments")

    def testSegmentsStrandNegativeDownstreamAndUpstreamSimpleFraction(self):
        """
        Segments with strand, using down- and upstream as fraction,
        only negative
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['-'], expStarts=[5,20],
                      expEnds=[10,25], expStrands=['-','-'], upstream=.5,
                      downstream=.5, useFraction=True,
                      expTrackFormatType="Segments")

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
                      expEnds=[10,25], expStrands=['.','.'], both=5,
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
                      expEnds=[10,25], expStrands=['.','.'], both=.5,
                      useFraction=True, expTrackFormatType="Segments", debug=True)

    # *** Strand, both, missing positive, remove overlap ***
    # TODO

    # *** Strand, both, missing negative ***
    def testSegmentsStrandBothMissingNegative(self):
        """
        Strand info missing. Test that we can treat is as negative.
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5,20],
                      expEnds=[10,25], expStrands=['.','.'], both=5,
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
                      expEnds=[10,25], expStrands=['.','.'], both=.5,
                      treatMissingAsNegative=True, useFraction=True,
                      expTrackFormatType="Segments")

    # *** Strand, both, missing negative, remove overlap ***
    # TODO
    # TODO pos and negative

    def testSegmentsStrandDownstreamMissingDefault(self):
        """
        Strand info missing. Test that the default works.
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5],
                      expEnds=[10], expStrands=['.'], downstream=5,
                      expTrackFormatType="Segments")

    def testSegmentsStrandDownstreamMissingDefaultFraction(self):
        """
        Strand info missing. Test that the default works.
        Using fractions.
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5],
                      expEnds=[10], expStrands=['.'], downstream=.5,
                      useFraction=True, expTrackFormatType="Segments")

    # *** Strand, start, missing positive, remove overlap ***
    # TODO, neg and pos

    def testSegmentsStrandDownstreamMissingNegative(self):
        """
        Strand info missing. Test that we can treat is as negative.
        Using fractions.
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[20],
                      expEnds=[25], expStrands=['.'], downstream=5,
                      treatMissingAsNegative=True,
                      expTrackFormatType="Segments")

    def testSegmentsStrandDownstreamMissingNegativeFraction(self):
        """
        Strand info missing. Test that we can treat is as negative.
        Using fractions.
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[20],
                      expEnds=[25], expStrands=['.'], downstream=.5,
                      treatMissingAsNegative=True, useFraction=True,
                      expTrackFormatType="Segments")

    # *** Strand, start, missing negative, remove overlap ***
    # *** Strand, end, missing positive ***
    # TODO

    def testSegmentsStrandUpstreamMissingPositiveDefault(self):
        """
        Strand info missing. Test that the default works.
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[20],
                      expEnds=[25], expStrands=['.'], upstream=5,
                      expTrackFormatType="Segments")

    # *** Strand, upstream, missing positive, fraction ***
    def testSegmentsStrandUpstreamMissingDefaultFraction(self):
        """
        Strand info missing. Test that the default works.
        Using fractions.
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[20],
                      expEnds=[25], expStrands=['.'], upstream=.5,
                      useFraction=True, expTrackFormatType="Segments")

    # *** Strand, upstream, missing positive, remove overlap ***
    # TODO

    def testSegmentsStrandUpstreamMissingNegative(self):
        """
        Strand info missing. Test that we can treat them as negative.
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5],
                      expEnds=[10], expStrands=['.'], upstream=5,
                      treatMissingAsNegative=True)

    def testSegmentsStrandUpstreamMissingNegativeFraction(self):
        """
        Strand info missing. Test that we can treat them as negative.
        Using fractions.
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5],
                      expEnds=[10], expStrands=['.'], upstream=.5,
                      treatMissingAsNegative=True, useFraction=True,
                      expTrackFormatType="Segments")

    # *** Strand, upstream, missing negative, remove overlap ***
    # TODO neg and pos

    def testSegmentsStrandDownstreamAndUpstreamMissingDefault(self):
        """
        Strand info missing. Test that the default works.
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['.'],expStarts=[5,20],
                      expEnds=[10,25], expStrands=['.','.'], upstream=5,
                      downstream=5, expTrackFormatType="Segments")

    # *** Strand, downstream and upstream, missing positive, fraction ***
    def testSegmentsStrandDownstreamAndUpstreamMissingDefaultFraction(self):
        """
        Strand info missing. Test that the default works.
        Using fractions.
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5,20],
                      expEnds=[10,25], expStrands=['.','.'], upstream=.5,
                      downstream=.5, useFraction=True,
                      expTrackFormatType="Segments")

    # *** Strand, start and end, missing positive, remove overlap ***
    # TODO

    def testSegmentsStrandDownstreamAndUpstreamMissingNegative(self):
        """
        Strand info missing. Test that we can treat them as negative.
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5,20],
                      expEnds=[10,25], expStrands=['.','.'], upstream=5,
                      downstream=5, treatMissingAsNegative=True,
                      expTrackFormatType="Segments")

    def testSegmentsStrandDownstreamAndUpstreamMissingNegativeFractions(self):
        """
        Strand info missing. Test that we can treat them as negative.
        Using fractions.
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5,20],
                      expEnds=[10,25], expStrands=['.','.'], upstream=.5,
                      downstream=.5, treatMissingAsNegative=True,
                      useFraction=True, expTrackFormatType="Segments")

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
