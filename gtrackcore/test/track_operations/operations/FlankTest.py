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
    # *** No strand, both, overlap ***
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

    # *** No strand, both, no overlap ***

    # *** No strand, both, overlap, fractions ***


    # *** No strand, start, overlap ***
    def testFlankNoStrandStartSimple(self):
        """
        Simple test of start, no strand, overlap allowed.
        :return: None
        """

        self._runFlankSegmentsTest(starts=[10], ends=[20], expStarts=[5],
                                   expEnds=[10], start=5, debug=True)

    # *** No strand, start, no overlap ***

    # *** No strand, end, overlap  ***
    def testFlankNoStrandEndSimple(self):
        """
        Simple test of end, no strand, overlap allowed.
        :return: None
        """

        self._runFlankSegmentsTest(starts=[10], ends=[20], expStarts=[20],
                                   expEnds=[25], end=5, debug=True)

    # *** No strand, end, no overlap  ***
    # *** No strand, start and end, overlap ***
    def testFlankNoStrandStartAndEndSimple(self):
        """
        Simple test of start and end, no strand, overlap allowed.
        :return: None
        """

        self._runFlankSegmentsTest(starts=[10], ends=[20], expStarts=[5,20],
                                   expEnds=[10,25], start=5, end=5,
                                   debug=True)

    # *** No strand, start and end, no overlap ***
    # *** Strand, both, overlap ***
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

    # *** Strand, both, no overlap ***
    # *** Strand, start, overlap ***
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

    # *** Strand, start, no overlap ***
    # *** Strand, end, overlap ***
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


    # *** Strand, end, no overlap ***
    # *** Strand, start and end, overlap ***
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

    # *** Strand, start and end, no overlap ***
    # *** Strand, both, missing positive, overlap ***
    def testFlankStrandBothMissingPositiveSimple(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['.'],
                                   expStarts=[5,20], expEnds=[10,25],
                                   expStrands=['+','+'], both=5,
                                   useMissingStrands=True,
                                   debug=True)

    # *** Strand, both, missing positive, no overlap ***
    # *** Strand, both, missing negative, overlap ***
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

    # *** Strand, both, missing negative, no overlap ***
    # *** Strand, start, missing positive, overlap ***
    def testFlankStrandStartMissingPositiveSimple(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['.'],
                                   expStarts=[5], expEnds=[10],
                                   expStrands=['+'], start=5,
                                   useMissingStrands=True,
                                   debug=True)

    # *** Strand, start, missing positive, no overlap ***
    # *** Strand, start, missing negative, overlap ***
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

    # *** Strand, start, missing negative, no overlap ***
    # *** Strand, end, missing positive, overlap ***
    def testFlankStrandEndMissingPositiveSimple(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['.'],
                                   expStarts=[20], expEnds=[25],
                                   expStrands=['+'], end=5,
                                   useMissingStrands=True,
                                   debug=True)

    # *** Strand, end, missing positive, no overlap ***
    # *** Strand, end, missing negative, overlap ***
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

    # *** Strand, end, missing negative, no overlap ***
    # *** Strand, start and end, missing positive, overlap ***
    def testFlankStrandStartAndEndMissingPositiveSimple(self):
        """
        :return: None
        """
        self._runFlankSegmentsTest(starts=[10], ends=[20], strands=['.'],
                                   expStarts=[5,20], expEnds=[10,25],
                                   expStrands=['+','+'], start=5, end=5,
                                   useMissingStrands=True,
                                   debug=True)

    # *** Strand, start and end, missing positive, no overlap ***
    # *** Strand, start and end, missing negative, overlap ***
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

if __name__ == "__main__":
    unittest.main()
