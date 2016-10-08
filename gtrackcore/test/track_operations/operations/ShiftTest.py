import unittest
import numpy as np

from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion

from gtrackcore.track_operations.operations.Shift import Shift
from gtrackcore.test.track_operations.TestUtils import \
    createSimpleTestTrackContent


class ShiftTest(unittest.TestCase):

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
                 allowOverlaps=True, resultAllowOverlaps=False,
                 shiftLength=None, useFraction=False, useStrands=False,
                 treatMissingAsNegative=False, debug=False,
                 expTrackFormatType=None, expNoResult=False):

        track = createSimpleTestTrackContent(startList=starts, endList=ends,
                                             valList=values,
                                             strandList=strands,
                                             idList=ids, edgeList=edges,
                                             weightsList=weights,
                                             customChrLength=customChrLength)

        self.assertTrue(shiftLength is not None)

        f = Shift(track, shiftLength=shiftLength, useFraction=useFraction,
                  useStrands=useStrands,
                  treatMissingAsNegative=treatMissingAsNegative,
                  allowOverlaps=allowOverlaps,
                  resultAllowOverlaps=resultAllowOverlaps, debug=debug)

        self.assertTrue((f is not None))
        result = f.calculate()
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
                #newExtras = v.extrasAsNumpyArray()

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

        if expNoResult:
            self.assertFalse(resFound)
        else:
            self.assertTrue(resFound)

    # **** Segments tests ****

    def testSegmentsSimple(self):
        """
        Simple shift test
        :return: None
        """
        self._runTest(starts=[5], ends=[10], expStarts=[10], expEnds=[15],
                      shiftLength=5, expTrackFormatType="Segments")

    def testSegmentsNegativeSimple(self):
        """
        Simple shift test where the shift is negative.
        :return: None
        """
        self._runTest(starts=[5], ends=[10], expStarts=[0], expEnds=[5],
                      shiftLength=-5, expTrackFormatType="Segments")

    def testSegmentsSimpleStartUnderflow(self):
        """
        Simple shift test. Start underflow.
        :return: None
        """
        self._runTest(starts=[5], ends=[10], expStarts=[0], expEnds=[4],
                      shiftLength=-6, expTrackFormatType="Segments")

    def testSegmentsSimpleEndUnderflow(self):
        """
        Simple shift test. End underflow.
        :return: None
        """
        self._runTest(starts=[5], ends=[10], shiftLength=-11, expNoResult=True)

    def testSegmentsSimpleEndOverflow(self):
        """
        Test overflow
        :return: None
        """
        self._runTest(starts=[50000], ends=[len(self.chr1)-9],
                      expStarts=[50010], expEnds=[len(self.chr1)], shiftLength=10,
                      expTrackFormatType="Segments")

    def testSegmentsSimpleEndAtRegionSize(self):
        """
        Test when new end is at the region size
        :return: None
        """
        self._runTest(starts=[50000], ends=[len(self.chr1)-10],
                      expStarts=[50010],expEnds=[len(self.chr1)], shiftLength=10,
                      expTrackFormatType="Segments")

    def testSegmentsSimpleStartOverflow(self):
        """
        Test if we get a empty track if the whole segment is shifted paste
        the region size
        :return: None
        """
        self._runTest(starts=[len(self.chr1)-10], ends=[len(self.chr1)-5],
                      shiftLength=11, expNoResult=True)

    def testSegmentsSimpleStartAtRegionSize(self):
        """
        Start at region size
        :return: None
        """
        self._runTest(starts=[len(self.chr1)-10], ends=[len(self.chr1)-5],
                      expNoResult=True, shiftLength=10)

    def testSegmentsComplex(self):
        """
        A more complex test with more then on segment
        :return: None
        """
        self._runTest(starts=[5,30,56,2332], ends=[10,34,90,4323],
                      expStarts=[105,130,156,2432], expEnds=[110,134,190,4423],
                      shiftLength=100, expTrackFormatType="Segments")

    def testSegmentsOverlappingAllow(self):
        """
        Overlapping input, allow overlap in result
        :return: None
        """
        self._runTest(starts=[5,30],ends=[35,140], expStarts=[105,130],
                      expEnds=[135,240], shiftLength=100, allowOverlaps=True,
                      resultAllowOverlaps=True, expTrackFormatType="Segments")

    def testSegmentsOverlappingMerge(self):
        """
        Overlapping input, No overlap in result
        :return: None
        """
        self._runTest(starts=[5,30],ends=[35,140], expStarts=[105],
                      expEnds=[240], shiftLength=100, allowOverlaps=True,
                      resultAllowOverlaps=False, expTrackFormatType="Segments")

    # **** Segments with strands tests ****

    def testKeepingPositiveStrands(self):
        """
        Ignoring the strand. Keeping the values
        :return: None
        """
        self._runTest(starts=[5], ends=[10], strands=['+'], expStarts=[10],
                      expEnds=[15], expStrands=['+'], shiftLength=5,
                      useStrands=False, expTrackFormatType="Segments")

    def testKeepingNegativeStrand(self):
        """
        Ignoring the strand. Keeping the values
        :return: None
        """
        self._runTest(starts=[5], ends=[10], strands=['-'], expStarts=[10],
                      expEnds=[15], expStrands=['-'], shiftLength=5,
                      useStrands=False, expTrackFormatType="Segments")

    def testKeepingMissingMissing(self):
        """
        Ignoring the strand. Keeping the values
        :return: None
        """
        self._runTest(starts=[5], ends=[10], strands=['.'], expStarts=[10],
                      expEnds=[15], expStrands=['.'], shiftLength=5,
                      useStrands=False, expTrackFormatType="Segments")

    def testKeepingMissingMissingAsNeg(self):
        """
        Ignoring the strand. Keeping the values
        :return: None
        """
        self._runTest(starts=[5], ends=[10], strands=['.'], expStarts=[10],
                      expEnds=[15], expStrands=['.'], shiftLength=5,
                      useStrands=False, expTrackFormatType="Segments",
                      treatMissingAsNegative=True)

    # **** Using strands ****
    def testUsingStrandsPositive(self):
        """
        Following the strand
        :return: None
        """
        self._runTest(starts=[5], ends=[10], strands=['+'], expStarts=[10],
                      expEnds=[15], expStrands=['+'], shiftLength=5,
                      useStrands=True, expTrackFormatType="Segments")

    def testUsingStrandsNegative(self):
        """
        Following the strand
        :return: None
        """
        self._runTest(starts=[5], ends=[10], strands=['-'], expStarts=[0],
                      expEnds=[5], expStrands=['-'], shiftLength=5,
                      useStrands=True, expTrackFormatType="Segments")

    def testUsingStrandsMissing(self):
        """
        Following the strand
        Missing as positive
        :return: None
        """
        self._runTest(starts=[5], ends=[10], strands=['.'], expStarts=[10],
                      expEnds=[15], expStrands=['.'], shiftLength=5,
                      useStrands=True, expTrackFormatType="Segments")

    def testUsingStrandsAsNeg(self):
        """
        Following the strand
        Missing as negative
        :return: None
        """
        self._runTest(starts=[5], ends=[10], strands=['.'], expStarts=[0],
                      expEnds=[5], expStrands=['.'], shiftLength=5,
                      useStrands=True, expTrackFormatType="Segments",
                      treatMissingAsNegative=True)

    def testUsingStrandsComplexAllPositive(self):
        """
        Using strands, complex. All Positive
        :return:
        """
        self._runTest(starts=[5,30,450,2340], ends=[25,150,560,3000],
                      strands=['+','+','+','+'], expStarts=[10,35,455,2345],
                      expEnds=[30,155,565,3005], expStrands=['+','+','+','+'],
                      useStrands=True, shiftLength=5, expTrackFormatType="Segments")

    def testUsingStrandsComplexAllNegative(self):
        """
        Using strands, complex. all negative
        :return:
        """
        self._runTest(starts=[5,30,450,2340], ends=[25,150,560,3000],
                      strands=['-','-','-','-'], expStarts=[0,25,445,2335],
                      expEnds=[20,145,555,2995], expStrands=['-','-','-','-'],
                      useStrands=True, shiftLength=5, expTrackFormatType="Segments")

    def testUsingStrandsComplexMix(self):
        """
        Using strands, complex. mix
        :return:
        """
        self._runTest(starts=[5,30,450,2340], ends=[25,150,560,3000],
                      strands=['+','-','+','-'], expStarts=[10,25,455,2335],
                      expEnds=[30,145,565,2995], expStrands=['+','-','+','-'],
                      shiftLength=5, useStrands=True, expTrackFormatType="Segments")

    def testUsingStrandsComplexMixMissing(self):
        """
        Using strands, complex. mix with missing
        Default, treat as positive
        :return:
        """
        self._runTest(starts=[5,30,450,2340], ends=[25,150,560,3000],
                      strands=['+','.','.','-'], expStarts=[10,35,455,2335],
                      expEnds=[30,155,565,2995], expStrands=['+','.','.','-'],
                      shiftLength=5, useStrands=True, expTrackFormatType="Segments")

    def testUsingStrandsComplexMixMissingNegative(self):
        """
        Using strands, complex. mix with missing
        Treat as negative
        :return:
        """
        self._runTest(starts=[5,30,450,2340], ends=[25,150,560,3000],
                      strands=['+','.','.','-'], expStarts=[10,25,445,2335],
                      expEnds=[30,145,555,2995], expStrands=['+','.','.','-'],
                      shiftLength=5, useStrands=True, treatMissingAsNegative=True,
                      expTrackFormatType="Segments")

    # **** Using fractions ****
    def testFractionSegments(self):
        """
        Fraction shift test
        :return: None
        """
        self._runTest(starts=[10], ends=[20], expStarts=[15], expEnds=[25],
                      shiftLength=0.5, useFraction=True,
                      expTrackFormatType="Segments")

    def testFractionNegativeS(self):
        """
        Fraction shift test where the shift is negative.
        :return: None
        """
        self._runTest(starts=[10], ends=[20], expStarts=[5], expEnds=[15],
                      shiftLength=-0.5, useFraction=True,
                      expTrackFormatType="Segments")

    def testFractionStartUnderflow(self):
        """
        Fraction shift test. Start underflow.
        :return: None
        """
        self._runTest(starts=[3], ends=[13], expStarts=[0], expEnds=[8],
                      shiftLength=-0.5, useFraction=True,
                      expTrackFormatType="Segments")

    def testFractionEndUnderflow(self):
        """
        Fraction shift test. End underflow.
        :return: None
        """
        self._runTest(starts=[5], ends=[10], shiftLength=-2.5,
                      useFraction=True, expNoResult=True)

    def testFractionEndOverflow(self):
        """
        Fraction. end overflow
        :return: None
        """
        self._runTest(starts=[len(self.chr1)-12], ends=[len(self.chr1)-2],
                      expStarts=[len(self.chr1)-7], expEnds=[len(self.chr1)],
                      shiftLength=0.5, useFraction=True,
                      expTrackFormatType="Segments")

    def testFractionStartOverflow(self):
        """
        Test if we get a empty track if the whole segment is shifted paste
        the region size
        :return: None
        """
        self._runTest(starts=[len(self.chr1)-10], ends=[len(self.chr1)-5],
                      shiftLength=2.5, useFraction=True, expNoResult=True)

    # **** Using strands and fractions ****
    def testUsingStrandsAndFractionPositive(self):
        """
        Following the strand
        :return: None
        """
        self._runTest(starts=[5], ends=[15], strands=['+'], expStarts=[10],
                      expEnds=[20], expStrands=['+'], shiftLength=0.5,
                      useStrands=True, useFraction=True,
                      expTrackFormatType="Segments")

    def testUsingStrandsAndFractionNegative(self):
        """
        Following the strand
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['-'], expStarts=[5],
                      expEnds=[15], expStrands=['-'], shiftLength=0.5,
                      useStrands=True, useFraction=True,
                      expTrackFormatType="Segments")

    def testUsingStrandsAndFractionMissing(self):
        """
        Following the strand
        Missing as positive
        :return: None
        """
        self._runTest(starts=[5], ends=[15], strands=['.'], expStarts=[10],
                      expEnds=[20], expStrands=['.'], shiftLength=0.5,
                      useStrands=True, useFraction=True,
                      expTrackFormatType="Segments")

    def testUsingStrandsAndFractionAsNeg(self):
        """
        Following the strand
        Missing as negative
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5],
                      expEnds=[15], expStrands=['.'], shiftLength=0.5,
                      useStrands=True, treatMissingAsNegative=True,
                      useFraction=True, expTrackFormatType="Segments")


    def testUsingStrandsAndFractionMix(self):
        """
        Using strands, complex. mix
        :return:
        """
        self._runTest(starts=[20,55,450,2500], ends=[40,65,560,3000],
                      strands=['+','-','+','-'],
                      expStarts=[30,50,505,2250],
                      expEnds=[50,60,615,2750],
                      expStrands=['+','-','+','-'],
                      shiftLength=0.5, useStrands=True, useFraction=True,
                      expTrackFormatType="Segments")

    # **** Other inputs ****

    def testInputPoints(self):
        """
        Valued points track as input
        :return:
        """
        self._runTest(starts=[10], expStarts=[15], shiftLength=5,
                      expTrackFormatType="Points", debug=True)

    def testInputValuedPoints(self):
        """
        Valued points track as input
        :return:
        """
        self._runTest(starts=[10], values=[20], expStarts=[15],
                      expValues=[20], shiftLength=5,
                      expTrackFormatType="Valued points")

    def testInputLinkedPoints(self):
        """
        Linked points track as input
        :return:d
        """
        self._runTest(starts=[10], ids=['1'], edges=['1'],
                      expStarts=[15], expIds=['1'], expEdges=['1'],
                      shiftLength=5, expTrackFormatType="Linked points")

    def testInputLinkedValuedPoints(self):
        """
        Linked valued points track as input
        :return:
        """
        self._runTest(starts=[10], values=[20], ids=['1'], edges=['1'],
                      expStarts=[15], expValues=[20], expIds=['1'],
                      expEdges=['1'], shiftLength=5,
                      expTrackFormatType="Linked valued points")

    def testInputValuedSegments(self):
        """
        Valued segments track as input
        :return:
        """
        self._runTest(starts=[10], ends=[15], values=[20], expStarts=[15],
                      expEnds=[20], expValues=[20], shiftLength=5,
                      expTrackFormatType="Valued segments")

    def testInputLinkedSegments(self):
        """
        Linked segments track as input
        :return:
        """
        self._runTest(starts=[10], ends=[15], ids=['1'], edges=['1'],
                      expStarts=[15], expEnds=[20], expIds=['1'],
                      expEdges=['1'], shiftLength=5,
                      expTrackFormatType="Linked segments")

    def testInputLinkedValuedSegments(self):
        """
        Linked valued segments track as input
        :return:
        """
        self._runTest(starts=[10], ends=[15], values=[20], ids=['1'],
                      edges=['1'], expStarts=[15], expEnds=[20],
                      expValues=[20],  expIds=['1'], expEdges=['1'],
                      shiftLength=5,
                      expTrackFormatType="Linked valued segments")

if __name__ == "__main__":
    unittest.main()
