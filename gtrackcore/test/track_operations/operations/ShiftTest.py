import unittest
import numpy as np
from collections import OrderedDict

from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.operations.Shift import Shift
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.test.track_operations.TestUtils import createTrackView
from gtrackcore.test.track_operations.TestUtils import \
    createSimpleTestTrackContent


class ShiftTest(unittest.TestCase):

    def setUp(self):
        self.chr1 = (GenomeRegion('hg19', 'chr1', 0,
                                  GenomeInfo.GENOMES['hg19']['size']['chr1']))
        self.chromosomes = (GenomeRegion('hg19', c, 0, l)
                            for c, l in
                            GenomeInfo.GENOMES['hg19']['size'].iteritems())

    def _runShiftSegmentsTest(self, starts, ends, expStarts, expEnds,
                              strands=None, expStrands=None, shift=None,
                              positive=None, negative=None, fraction=False,
                              useMissingStrand=True,
                              treatMissingAsPositive=True,
                              allowOverlap=False, debug=False):

        track = createSimpleTestTrackContent(startList=starts, endList=ends,
                                             strandList=strands)

        if shift is not None:
            self.assertTrue((positive is None and negative is None))
        else:
            self.assertTrue((positive is not None or negative is not None))

        f = Shift(track, shift=shift, positive=positive, negative=negative,
                  fraction=fraction, useMissingStrand=useMissingStrand,
                  treatMissingAsPositive=treatMissingAsPositive,
                  allowOverlap=allowOverlap)

        self.assertTrue((f is not None))
        result = f.calculate()

        resFound = False
        if len(expStarts) == 0:
            resFound = True

        for (k, v) in result.getTrackViews().items():
            if cmp(k, self.chr1) == 0:
                # All test tracks are in chr1
                if debug:
                    print(v.startsAsNumpyArray())
                    print(v.endsAsNumpyArray())
                    print(expStarts)
                    print(expEnds)

                self.assertTrue(np.array_equal(v.startsAsNumpyArray(),
                                               expStarts))
                self.assertTrue(np.array_equal(v.endsAsNumpyArray(), expEnds))
                resFound = True
                if strands is not None:
                    pass
            else:
                # Tests if all tracks no in chr1 have a size of 0.
                self.assertEqual(v.startsAsNumpyArray().size, 0)
                self.assertEqual(v.endsAsNumpyArray().size, 0)

        self.assertTrue(resFound)

    # **** Segments tests ****

    def testShiftSegmentsShiftSimple(self):
        """
        Simple shift test
        :return: None
        """
        self._runShiftSegmentsTest(starts=[5], ends=[10], expStarts=[10],
                                   expEnds=[15], shift=5, allowOverlap=True,
                                   debug=True)

    def testShiftSegmentsShiftNegativeSimple(self):
        """
        Simple shift test where the shift is negative.
        :return: None
        """
        self._runShiftSegmentsTest(starts=[5], ends=[10], expStarts=[0],
                                   expEnds=[5], shift=-5, allowOverlap=True,
                                   debug=True)

    def testShiftSegmentsShiftSimpleStartUnderflow(self):
        """
        Simple shift test. Start underflow.
        :return: None
        """
        self._runShiftSegmentsTest(starts=[5], ends=[10], expStarts=[0],
                                   expEnds=[4], shift=-6, allowOverlap=True,
                                   debug=True)

    def testShiftSegmentsShiftSimpleEndUnderflow(self):
        """
        Simple shift test. End underflow.
        :return: None
        """
        self._runShiftSegmentsTest(starts=[5], ends=[10], expStarts=[],
                                   expEnds=[], shift=-11, allowOverlap=True,
                                   debug=True)

    def testShiftSegmentsShiftSimpleStartUnderflowToPoint(self):
        """
        GTrackCore represents points as a segment with length 0.

        Why do we get a empty track and not a point (0,0) when we create the
        trackview? Is it the borderHandling='crop'?

        :return: None
        """
        self._runShiftSegmentsTest(starts=[5], ends=[10], expStarts=[],
                                   expEnds=[], shift=-10, allowOverlap=True,
                                   debug=True)

    def testShiftSegmentsShiftSimpleEndOverflow(self):
        """
        :return: None
        """
        self._runShiftSegmentsTest(starts=[50000], ends=[len(self.chr1)-9],
                                   expStarts=[50010],
                                   expEnds=[len(self.chr1)], shift=10,
                                   allowOverlap=True, debug=True)

    def testShiftSegmentsShiftSimpleEndAtRegionSize(self):
        """
        :return: None
        """
        self._runShiftSegmentsTest(starts=[50000], ends=[len(self.chr1)-10],
                                   expStarts=[50010],
                                   expEnds=[len(self.chr1)], shift=10,
                                   allowOverlap=True, debug=True)

    def testShiftSegmentsShiftSimpleStartOverflow(self):
        """
        :return: None
        """
        self._runShiftSegmentsTest(starts=[len(self.chr1)-10],
                                   ends=[len(self.chr1)-5], expStarts=[],
                                   expEnds=[], shift=11,
                                   allowOverlap=True, debug=True)

    def testShiftSegmentsShiftSimpleStartAtRegionSize(self):
        """
        :return: None
        """
        self._runShiftSegmentsTest(starts=[len(self.chr1)-10],
                                   ends=[len(self.chr1)-5],
                                   expStarts=[len(self.chr1)],
                                   expEnds=[len(self.chr1)], shift=10,
                                   allowOverlap=True, debug=True)

    def testShiftSegmentsShiftComplex(self):
        """
        A more complex test with more then on segment
        :return: None
        """
        self._runShiftSegmentsTest(starts=[5,30,56,2332],
                                   ends=[10,34,90,4323],
                                   expStarts=[105,130,156,2432],
                                   expEnds=[110,134,190,4423], shift=100,
                                   allowOverlap=True,
                                   debug=True)

    def testShiftSegmentsShiftOverlappingInput(self):
        """
        Overlapping input, allow overlap in result
        :return: None
        """
        self._runShiftSegmentsTest(starts=[5,30],
                                   ends=[35,140],
                                   expStarts=[105,130],
                                   expEnds=[135,240], shift=100,
                                   allowOverlap=True,
                                   debug=True)

    # **** Segments with strands tests ****

    def testShiftSegmentsShiftSimpleStrandPositive(self):
        """
        Simple shift test with strand
        :return: None
        """
        self._runShiftSegmentsTest(starts=[5], ends=[10], expStarts=[10],
                                   expEnds=[15], shift=5, strands=['+'],
                                   allowOverlap=True, debug=True)

    def testShiftSegmentsShiftSimpleStrandNegative(self):
        """
        Simple shift test with strand
        :return: None
        """
        self._runShiftSegmentsTest(starts=[5], ends=[10], expStarts=[0],
                                   expEnds=[5], shift=5, strands=['-'],
                                   allowOverlap=True, debug=True)

    def testShiftSegmentsShiftSimpleStrandMissing(self):
        """
        Simple shift test with strand
        :return: None
        """
        self._runShiftSegmentsTest(starts=[5], ends=[10], expStarts=[10],
                                   expEnds=[15], shift=5, strands=['.'],
                                   allowOverlap=True, debug=True)

    def testShiftSegmentsShiftSimpleStrandMissingAsNegative(self):
        """
        Simple shift test with strand
        :return: None
        """
        self._runShiftSegmentsTest(starts=[5], ends=[10], expStarts=[0],
                                   expEnds=[5], shift=5, strands=['.'],
                                   treatMissingAsPositive=False,
                                   allowOverlap=True, debug=True)

    def testShiftSegmentsShiftComplexPositive(self):
        """
        Simple shift test with strand
        :return: None
        """
        self._runShiftSegmentsTest(starts=[5,30,450,2340],
                                   ends=[25,150,560,3000],
                                   expStarts=[10,35,455,2345],
                                   expEnds=[30,155,565,3005],
                                   shift=5, strands=['+','+','+','+'],
                                   allowOverlap=True, debug=True)

    def testShiftSegmentsShiftComplexNegative(self):
        """
        Simple shift test with strand
        :return: None
        """
        self._runShiftSegmentsTest(starts=[5,30,450,2340],
                                   ends=[25,150,560,3000],
                                   expStarts=[0,25,445,2335],
                                   expEnds=[20,145,555,2995],
                                   shift=5, strands=['-','-','-','-'],
                                   allowOverlap=True, debug=True)

    def testShiftSegmentsShiftComplexMix(self):
        """
        Simple shift test with strand
        :return: None
        """
        self._runShiftSegmentsTest(starts=[5,30,450,2340],
                                   ends=[25,150,560,3000],
                                   expStarts=[10,25,455,2335],
                                   expEnds=[30,145,565,2995],
                                   shift=5, strands=['+','-','+','-'],
                                   allowOverlap=True, debug=True)

    def testShiftSegmentsShiftComplexMixMissing(self):
        """
        Simple shift test with strand
        :return: None
        """
        self._runShiftSegmentsTest(starts=[5,30,450,2340],
                                   ends=[25,150,560,3000],
                                   expStarts=[10,35,455,2335],
                                   expEnds=[30,155,565,2995],
                                   shift=5, strands=['+','.','.','-'],
                                   allowOverlap=True, debug=True)

    def testShiftSegmentsShiftComplexMixMissingNegative(self):
        """
        Simple shift test with strand
        :return: None
        """
        self._runShiftSegmentsTest(starts=[5,30,450,2340],
                                   ends=[25,150,560,3000],
                                   expStarts=[10,25,445,2335],
                                   expEnds=[30,145,555,2995],
                                   shift=5, strands=['+','.','.','-'],
                                   treatMissingAsPositive=False,
                                   allowOverlap=True, debug=True)

    def testShiftSegmentsPositiveSimple(self):
        """
        Simple shift test of positive strand
        :return: None
        """
        self._runShiftSegmentsTest(starts=[5], ends=[10], expStarts=[10],
                                   expEnds=[15], positive=5, strands=['+'],
                                   allowOverlap=True, debug=True)

    def testShiftSegmentsPositiveSimpleNegative(self):
        """
        Simple shift test of positive strand. Negative value
        :return: None
        """
        self._runShiftSegmentsTest(starts=[5], ends=[10], expStarts=[0],
                                   expEnds=[5], positive=-5, strands=['+'],
                                   allowOverlap=True, debug=True)

    def testShiftSegmentsPositiveSimpleNoPositive(self):
        """
        Simple shift test of positive strand. Only negative segments
        :return: None
        """
        self._runShiftSegmentsTest(starts=[5], ends=[10], expStarts=[5],
                                   expEnds=[10], positive=5, strands=['-'],
                                   allowOverlap=True, debug=True)

    def testShiftSegmentsPositiveSimpleMissing(self):
        """
        Simple shift test of positive strand, strand not given
        :return: None
        """
        self._runShiftSegmentsTest(starts=[5], ends=[10], expStarts=[10],
                                   expEnds=[15], positive=5, strands=['.'],
                                   allowOverlap=True, debug=True)

    def testShiftSegmentsPositiveSimpleMissingNegative(self):
        """
        Simple shift test of positive strand, strand not given
        :return: None
        """
        self._runShiftSegmentsTest(starts=[5], ends=[10], expStarts=[5],
                                   expEnds=[10], positive=5, strands=['.'],
                                   treatMissingAsPositive=False,
                                   allowOverlap=True, debug=True)

    def testShiftSegmentsNegativeSimple(self):
        """
        Simple shift test of negative strand
        :return: None
        """
        self._runShiftSegmentsTest(starts=[5], ends=[10], expStarts=[0],
                                   expEnds=[5], negative=5, strands=['-'],
                                   allowOverlap=True, debug=True)

    def testShiftSegmentsNegativeSimpleNegative(self):
        """
        Simple shift test of negative strand, negative value
        :return: None
        """
        self._runShiftSegmentsTest(starts=[5], ends=[10], expStarts=[10],
                                   expEnds=[15], negative=-5, strands=['-'],
                                   allowOverlap=True, debug=True)

    def testShiftSegmentsNegativeSimpleNoNegative(self):
        """
        Simple shift test of negatie shift. Only positive segments
        :return: None
        """
        self._runShiftSegmentsTest(starts=[5], ends=[10], expStarts=[5],
                                   expEnds=[10], negative=5, strands=['+'],
                                   allowOverlap=True, debug=True)

    def testShiftSegmentsPositiveMixedStrand(self):
        """
        Simple shift test of mixed strands. Positive strand, positive value
        :return: None
        """
        self._runShiftSegmentsTest(starts=[5,20,50], ends=[10,30,100],
                                   expStarts=[10,20,55],
                                   expEnds=[15,30,105], positive=5,
                                   strands=['+','-','+'],
                                   allowOverlap=True, debug=True)

    def testShiftSegmentsPositiveMixedStrandNegative(self):
        """
        Simple shift test of mixed strands. Positive strand, negative value
        :return: None
        """
        self._runShiftSegmentsTest(starts=[5,20,50], ends=[10,30,100],
                                   expStarts=[0,20,45],
                                   expEnds=[5,30,95], positive=-5,
                                   strands=['+','-','+'],
                                   allowOverlap=True, debug=True)

    def testShiftSegmentsPositiveMissingStrand(self):
        """
        Simple shift test of negative strand. Only positive segments
        Treat missing as positive.
        :return: None
        """
        self._runShiftSegmentsTest(starts=[5,20,50], ends=[10,30,100],
                                   expStarts=[10,25,55],
                                   expEnds=[15,35,105], positive=5,
                                   strands=['+','.','+'],
                                   allowOverlap=True, debug=True)

    def testShiftSegmentsPositiveMissingStrandNegative(self):
        """
        Simple shift test of negative strand. Only positive segments.
        Treat missing as negative
        :return: None
        """
        self._runShiftSegmentsTest(starts=[5,20,50], ends=[10,30,100],
                                   expStarts=[10,20,55],
                                   expEnds=[15,30,105], positive=5,
                                   treatMissingAsPositive=False,
                                   strands=['+','.','+'],
                                   allowOverlap=True, debug=True)

    def testShiftSegmentsMixSimple(self):
        """
        Simple shift test, negative and positive strand
        :return: None
        """
        self._runShiftSegmentsTest(starts=[5,40], ends=[10,50],
                                   expStarts=[10,35], expEnds=[15,45],
                                   negative=5, positive=5,
                                   strands=['+', '-'],
                                   allowOverlap=True, debug=True)

    def testShiftSegmentsMixSimpleOverlap(self):
        """
        Simple shift test, negative and positive strand. Results overlap.
        :return: None
        """
        self._runShiftSegmentsTest(starts=[5,40], ends=[35,50],
                                   expStarts=[10,35], expEnds=[40,45],
                                   negative=5, positive=5,
                                   strands=['+', '-'],
                                   allowOverlap=True, debug=True)

    # **** Segments fractions ****

if __name__ == "__main__":
    unittest.main()
