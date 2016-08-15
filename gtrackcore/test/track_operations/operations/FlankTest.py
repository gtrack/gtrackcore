import unittest
import numpy as np
from collections import OrderedDict

from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.operations.Flank import Flank
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.test.track_operations.TestUtils import createTrackView
from gtrackcore.test.track_operations.TestUtils import \
    createSimpleTestTrackContent


class FlankTest(unittest.TestCase):

    def setUp(self):
        self.chr1 = (GenomeRegion('hg19', 'chr1', 0,
                                  GenomeInfo.GENOMES['hg19']['size']['chr1']))
        self.chromosomes = (GenomeRegion('hg19', c, 0, l)
                            for c, l in
                            GenomeInfo.GENOMES['hg19']['size'].iteritems())

    def _runFlankSegmentsTest(self, starts, ends, expStarts, expEnds,
                              strands=None, expStrands=None, start=None,
                              end=None, both=None, ignoreStrand=False,
                              useFraction=False, useMissingStrands=False,
                              treatMissingAsPositive=True,
                              allowOverlap=True, debug=False):

        track = createSimpleTestTrackContent(startList=starts, endList=ends,
                                             strandList=strands)

        if both is not None:
            self.assertTrue((start is None and end is None))
        else:
            self.assertTrue((starts is not None or end is not None))

        f = Flank(track, both=both, start=start, end=end,
                  ignoreStrand=ignoreStrand, useFraction=useFraction,
                  useMissingStrands=useMissingStrands,
                  treatMissingAsPositive=treatMissingAsPositive,
                  allowOverlap=allowOverlap, debug=debug)

        self.assertTrue((f is not None))

        result = f.calculate()

        resFound = False

        # TODO check expStrands
        for (k, v) in result.getTrackViews().items():
            if cmp(k, self.chr1) == 0:
                # All test tracks are in chr1
                if debug:
                    print(v.startsAsNumpyArray())
                    print(v.endsAsNumpyArray())
                    print(expStarts)
                    print(expEnds)

                if strands is not None:
                    self.assertTrue(np.array_equal(v.strandsAsNumpyArray(),
                                                   expStrands))

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
    # *** No strand, both ***
    def testFlankNoStrandBothSimple(self):
        """
        :return: None
        """

        self._runFlankSegmentsTest(starts=[10], ends=[20], expStarts=[5,20],
                                   expEnds=[10,25], both=5,
                                   debug=True)

    def testFlankNoStrandBothComplex(self):
        """
        :return: None
        """

        self._runFlankSegmentsTest(starts=[10,50], ends=[20,100],
                                   expStarts=[5,20,45,100],
                                   expEnds=[10,25,50,105], both=5,
                                   debug=True)

    def testFlankNoStrandBothOverlap(self):
        """
        Two of the resulting flanks overlap. Overlap allowed
        :return: None
        """

        self._runFlankSegmentsTest(starts=[10,18], ends=[15,21],
                                   expStarts=[5,13,15,21],
                                   expEnds=[10,18,20,26], both=5,
                                   debug=True)

    def testFlankNoStrandBothUnderflow(self):
        """
        Test of underflow. Segment cut to 0
        :return: None
        """
        self._runFlankSegmentsTest(starts=[5], ends=[10], expStarts=[0,10],
                                   expEnds=[5,20], both=10,
                                   debug=True)

    def testFlankNoStrandBothOverflow(self):
        """
        Test of overflow. Segment cut to region size
        :return: None
        """
        self._runFlankSegmentsTest(starts=[len(self.chr1)-10],
                                   ends=[len(self.chr1)-5],
                                   expStarts=[len(self.chr1)-20,
                                              len(self.chr1)-5],
                                   expEnds=[len(self.chr1)-10,
                                            len(self.chr1)],
                                   both=10, debug=True)

    # *** No strand, both, fractions ***
    def testFlankNoStrandBothSimpleFractions(self):
        """
        :return: None
        """

        self._runFlankSegmentsTest(starts=[10], ends=[20], expStarts=[5,20],
                                   expEnds=[10,25], both=.5,
                                   useFraction=True,
                                   debug=True)

    # *** No strand, both, remove overlap ***

    # *** No strand, start ***
    def testFlankNoStrandStartSimple(self):
        """
        Simple test of start, no strand, overlap allowed.
        :return: None
        """

        self._runFlankSegmentsTest(starts=[10], ends=[20], expStarts=[5],
                                   expEnds=[10], start=5, debug=True)

    # *** No strand, start, fractions ***
    def testFlankNoStrandStartSimpleFractions(self):
        """
        :return: None
        """

        self._runFlankSegmentsTest(starts=[10], ends=[20], expStarts=[5],
                                   expEnds=[10], start=.5,
                                   useFraction=True,
                                   debug=True)

    # *** No strand, start, remove overlap ***

    # *** No strand, end ***
    def testFlankNoStrandEndSimple(self):
        """
        Simple test of end, no strand, overlap allowed.
        :return: None
        """

        self._runFlankSegmentsTest(starts=[10], ends=[20], expStarts=[20],
                                   expEnds=[25], end=5, debug=True)

    # *** No strand, end, fraction  ***
    def testFlankNoStrandEndSimpleFraction(self):
        """
        Simple test of end, no strand, overlap allowed.
        :return: None
        """

        self._runFlankSegmentsTest(starts=[10], ends=[20], expStarts=[20],
                                   expEnds=[25], end=.5,
                                   useFraction=True, debug=True)

    # *** No strand, end, remove overlap  ***
    # *** No strand, start and end ***
    def testFlankNoStrandStartAndEndSimple(self):
        """
        Simple test of start and end, no strand, overlap allowed.
        :return: None
        """

        self._runFlankSegmentsTest(starts=[10], ends=[20], expStarts=[5,20],
                                   expEnds=[10,25], start=5, end=5,
                                   debug=True)

    # *** No strand, start and end, fraction ***
    def testFlankNoStrandStartAndEndSimpleFraction(self):
        """
        Simple test of start and end, no strand, overlap allowed. Fraction
        :return: None
        """

        self._runFlankSegmentsTest(starts=[10], ends=[20], expStarts=[5,20],
                                   expEnds=[10,25], start=.5, end=.5,
                                   useFraction=True,
                                   debug=True)

    # *** No strand, start and end, remove overlap ***
    # *** Strand, both ***
    def testFlankStrandBothSimple(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['+'],
                                   expStarts=[5,20], expEnds=[10,25],
                                   expStrands=['+','+'], both=5,
                                   debug=True)

    def testFlankStrandNegativeBothSimple(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['-'],
                                   expStarts=[5,20], expEnds=[10,25],
                                   expStrands=['-','-'], both=5,
                                   debug=True)

    # *** Strand, both, fractions ***
    def testFlankStrandBothSimpleFraction(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['+'],
                                   expStarts=[5,20], expEnds=[10,25],
                                   expStrands=['+','+'], both=.5,
                                   useFraction=True,
                                   debug=True)

    def testFlankStrandNegativeBothSimpleFraction(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['-'],
                                   expStarts=[5,20], expEnds=[10,25],
                                   expStrands=['-','-'], both=.5,
                                   useFraction=True,
                                   debug=True)

    # *** Strand, both, remove overlap ***

    # *** Strand, start ***
    def testFlankStrandStartSimple(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['+'],
                                   expStarts=[5], expEnds=[10],
                                   expStrands=['+'], start=5,
                                   debug=True)

    def testFlankStrandNegativeStartSimple(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['-'],
                                   expStarts=[20], expEnds=[25],
                                   expStrands=['-'], start=5,
                                   debug=True)

    # *** Strand, start, remove overlap ***
    # *** Strand, end ***
    def testFlankStrandEndSimple(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['+'],
                                   expStarts=[20], expEnds=[25],
                                   expStrands=['+'], end=5,
                                   debug=True)

    def testFlankStrandNegativeEndSimple(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['-'],
                                   expStarts=[5], expEnds=[10],
                                   expStrands=['-'], end=5,
                                   debug=True)

    # *** Strand, end, fraction ***
    def testFlankStrandEndSimpleFraction(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['+'],
                                   expStarts=[20], expEnds=[25],
                                   expStrands=['+'], end=.5,
                                   useFraction=True,
                                   debug=True)

    def testFlankStrandNegativeEndSimpleFraction(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['-'],
                                   expStarts=[5], expEnds=[10],
                                   expStrands=['-'], end=.5,
                                   useFraction=True,
                                   debug=True)

    # *** Strand, end, remove overlap ***
    # *** Strand, start and end ***
    def testFlankStrandStartAndEndSimple(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['+'],
                                   expStarts=[5,20], expEnds=[10,25],
                                   expStrands=['+','+'], start=5, end=5,
                                   debug=True)

    def testFlankStrandNegativeStartAndEndSimple(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['-'],
                                   expStarts=[5,20], expEnds=[10,25],
                                   expStrands=['-','-'], start=5, end=5,
                                   debug=True)

    # *** Strand, start and end, fraction ***
    def testFlankStrandStartAndEndSimpleFraction(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['+'],
                                   expStarts=[5,20], expEnds=[10,25],
                                   expStrands=['+','+'], start=.5, end=.5,
                                   useFraction=True,
                                   debug=True)

    def testFlankStrandNegativeStartAndEndSimpleFraction(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['-'],
                                   expStarts=[5,20], expEnds=[10,25],
                                   expStrands=['-','-'], start=.5, end=.5,
                                   useFraction=True,
                                   debug=True)

    # *** Strand, start and end, remove overlap ***
    # *** Strand, both, missing positive ***
    def testFlankStrandBothMissingPositiveSimple(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['.'],
                                   expStarts=[5,20], expEnds=[10,25],
                                   expStrands=['+','+'], both=5,
                                   useMissingStrands=True,
                                   debug=True)

    # *** Strand, both, missing positive, fraction ***
    def testFlankStrandBothMissingPositiveSimpleFraction(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['.'],
                                   expStarts=[5,20], expEnds=[10,25],
                                   expStrands=['+','+'], both=.5,
                                   useMissingStrands=True,
                                   useFraction=True,
                                   debug=True)

    # *** Strand, both, missing positive, remove overlap ***

    # *** Strand, both, missing negative ***
    def testFlankStrandBothMissingNegativeSimple(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['.'],
                                   expStarts=[5,20], expEnds=[10,25],
                                   expStrands=['-','-'], both=5,
                                   useMissingStrands=True,
                                   treatMissingAsPositive=False,
                                   debug=True)

    # *** Strand, both, missing negative, fraction ***
    def testFlankStrandBothMissingNegativeSimpleFraction(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['.'],
                                   expStarts=[5,20], expEnds=[10,25],
                                   expStrands=['-','-'], both=.5,
                                   useMissingStrands=True,
                                   treatMissingAsPositive=False,
                                   useFraction=True,
                                   debug=True)

    # *** Strand, both, missing negative, remove overlap ***
    # *** Strand, start, missing positive ***
    def testFlankStrandStartMissingPositiveSimple(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['.'],
                                   expStarts=[5], expEnds=[10],
                                   expStrands=['+'], start=5,
                                   useMissingStrands=True,
                                   debug=True)

    # *** Strand, start, missing positive, fraction ***
    def testFlankStrandStartMissingPositiveSimpleFraction(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['.'],
                                   expStarts=[5], expEnds=[10],
                                   expStrands=['+'], start=.5,
                                   useMissingStrands=True,
                                   useFraction=True,
                                   debug=True)

    # *** Strand, start, missing positive, remove overlap ***
    # *** Strand, start, missing negative ***
    def testFlankStrandStartMissingNegativeSimple(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['.'],
                                   expStarts=[20], expEnds=[25],
                                   expStrands=['-'], start=5,
                                   useMissingStrands=True,
                                   treatMissingAsPositive=False,
                                   debug=True)

    # *** Strand, start, missing negative, fraction ***
    def testFlankStrandStartMissingNegativeSimpleFraction(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['.'],
                                   expStarts=[20], expEnds=[25],
                                   expStrands=['-'], start=.5,
                                   useMissingStrands=True,
                                   treatMissingAsPositive=False,
                                   useFraction=True,
                                   debug=True)

    # *** Strand, start, missing negative, remove overlap ***
    # *** Strand, end, missing positive ***
    def testFlankStrandEndMissingPositiveSimple(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['.'],
                                   expStarts=[20], expEnds=[25],
                                   expStrands=['+'], end=5,
                                   useMissingStrands=True,
                                   debug=True)

    # *** Strand, end, missing positive, fraction ***
    def testFlankStrandEndMissingPositiveSimpleFraction(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['.'],
                                   expStarts=[20], expEnds=[25],
                                   expStrands=['+'], end=.5,
                                   useMissingStrands=True,
                                   useFraction=True,
                                   debug=True)

    # *** Strand, end, missing positive, remove overlap ***
    # *** Strand, end, missing negative ***
    def testFlankStrandEndMissingNegativeSimple(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['.'],
                                   expStarts=[5], expEnds=[10],
                                   expStrands=['-'], end=5,
                                   useMissingStrands=True,
                                   treatMissingAsPositive=False,
                                   debug=True)

    # *** Strand, end, missing negative, fraction ***
    def testFlankStrandEndMissingNegativeSimpleFraction(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['.'],
                                   expStarts=[5], expEnds=[10],
                                   expStrands=['-'], end=.5,
                                   useMissingStrands=True,
                                   treatMissingAsPositive=False,
                                   useFraction=True,
                                   debug=True)

    # *** Strand, end, missing negative, remove overlap ***
    # *** Strand, start and end, missing positive ***
    def testFlankStrandStartAndEndMissingPositiveSimple(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['.'],
                                   expStarts=[5,20], expEnds=[10,25],
                                   expStrands=['+','+'], start=5, end=5,
                                   useMissingStrands=True,
                                   debug=True)

    # *** Strand, start and end, missing positive, fraction ***
    def testFlankStrandStartAndEndMissingPositiveSimpleFraction(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['.'],
                                   expStarts=[5,20], expEnds=[10,25],
                                   expStrands=['+','+'], start=.5, end=.5,
                                   useMissingStrands=True,
                                   useFraction=True,
                                   debug=True)

    # *** Strand, start and end, missing positive, remove overlap ***
    # *** Strand, start and end, missing negative ***
    def testFlankStrandStartAndEndMissingNegativeSimple(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['.'],
                                   expStarts=[5,20], expEnds=[10,25],
                                   expStrands=['-','-'], start=5, end=5,
                                   useMissingStrands=True,
                                   treatMissingAsPositive=False,
                                   debug=True)

    # *** Strand, start and end, missing negative, fractions ***
    def testFlankStrandStartAndEndMissingNegativeSimpleFractions(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['.'],
                                   expStarts=[5,20], expEnds=[10,25],
                                   expStrands=['-','-'], start=.5, end=.5,
                                   useMissingStrands=True,
                                   treatMissingAsPositive=False,
                                   useFraction=True,
                                   debug=True)

if __name__ == "__main__":
    unittest.main()
