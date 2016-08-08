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
        self._runFlankSegmentsTest(starts=[5], ends=[10], expStarts=[0,10],
                                   expEnds=[5,20], both=10,
                                   debug=True)

    # *** No strand, both, no overlap ***

    # *** No strand, start, overlap ***
    # *** No strand, start, no overlap ***
    # *** No strand, end, overlap  ***
    # *** No strand, end, no overlap  ***
    # *** No strand, start and end, overlap ***
    # *** No strand, start and end, no overlap ***
    # *** Strand, both, overlap ***
    # *** Strand, both, no overlap ***
    # *** Strand, start, overlap ***
    # *** Strand, start, no overlap ***
    # *** Strand, end, overlap ***
    # *** Strand, end, no overlap ***
    # *** Strand, start and end, overlap ***
    # *** Strand, start and end, no overlap ***
    # *** Strand, both, missing positive, overlap ***
    # *** Strand, both, missing positive, no overlap ***
    # *** Strand, both, missing negative, overlap ***
    # *** Strand, both, missing negative, no overlap ***
    # *** Strand, start, missing positive, overlap ***
    # *** Strand, start, missing positive, no overlap ***
    # *** Strand, start, missing negative, overlap ***
    # *** Strand, start, missing negative, no overlap ***
    # *** Strand, end, missing positive, overlap ***
    # *** Strand, end, missing positive, no overlap ***
    # *** Strand, end, missing negative, overlap ***
    # *** Strand, end, missing negative, no overlap ***
    # *** Strand, start and end, missing positive, overlap ***
    # *** Strand, start and end, missing positive, no overlap ***
    # *** Strand, start and end, missing negative, overlap ***
    # *** Strand, start and end, missing negative, no overlap ***

    def atestFlankSegmentsStartSimple(self):
        """
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10], ends=[20], expStarts=[5],
                                  expEnds=[10], start=5, allowOverlap=False,
                                  resultAllowOverlap=True, ignoreStrand=True)

    def atestSlopSegmentsEndSimple(self):
        """
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10], ends=[20], expStarts=[10],
                                  expEnds=[25], end=5, allowOverlap=False,
                                  resultAllowOverlap=True, ignoreStrand=True)

    def atestSlopSegmentsBothSimple(self):
        """
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10], ends=[20], expStarts=[5],
                                  expEnds=[25], both=5, allowOverlap=False,
                                  resultAllowOverlap=True, ignoreStrand=True)

    def atestSlopSegmentsStartAndEndSameValue(self):
        """
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10], ends=[20], expStarts=[5],
                                  expEnds=[25], start=5, end=5,
                                  allowOverlap=False,
                                  resultAllowOverlap=True, ignoreStrand=True)

    def atestSlopSegmentsStartAndEndDifferentValue(self):
        """
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10], ends=[20], expStarts=[6],
                                  expEnds=[35], start=4, end=15,
                                  allowOverlap=False,
                                  resultAllowOverlap=True, ignoreStrand=True)

    def atestSlopSegmentsNewStartAtZero(self):
        """
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10], ends=[20], expStarts=[0],
                                  expEnds=[20], start=10, allowOverlap=False,
                                  resultAllowOverlap=True, ignoreStrand=True)

    def atestSlopSegmentsUnderflow(self):
        """
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10], ends=[20], expStarts=[0],
                                  expEnds=[20], start=100, allowOverlap=False,
                                  resultAllowOverlap=True, ignoreStrand=True)

    def atestSlopSegmentsEndAtRegionSize(self):
        """
        Test if creating a slop with an end equal to the size of the region
        :return: None
        """
        self._runSlopSegmentsTest(starts=[4000000], ends=[len(self.chr1)-20],
                                  expStarts=[4000000],
                                  expEnds=[len(self.chr1)], end=20,
                                  allowOverlap=False,
                                  resultAllowOverlap=True, ignoreStrand=True)

    def atestSlopSegmentsOverflow(self):
        """
        Test if the slop i cut to prevent the segment from overflowing the
        regions size.
        :return: None
        """
        self._runSlopSegmentsTest(starts=[4000000], ends=[len(self.chr1)-20],
                                  expStarts=[4000000],
                                  expEnds=[len(self.chr1)], end=300,
                                  allowOverlap=False,
                                  resultAllowOverlap=True, ignoreStrand=True)

    def atestSlopSegmentsMultipleNoOverlapStart(self):
        """
        Test if the slop i cut to prevent the segment from overflowing the
        regions size.
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10,40], ends=[20, 70],
                                  expStarts=[5,35],
                                  expEnds=[20,70], start=5,
                                  allowOverlap=False,
                                  resultAllowOverlap=True, ignoreStrand=True)

    def atestSlopSegmentsMultipleNoOverlapEnd(self):
        """
        Test if the slop i cut to prevent the segment from overflowing the
        regions size.
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10,40], ends=[20, 70],
                                  expStarts=[10,40], expEnds=[25,75], end=5,
                                  allowOverlap=False, resultAllowOverlap=True,
                                  ignoreStrand=True)

    def atestSlopSegmentsMultipleOverlappingResAllowOverlap(self):
        """
        Test if the slop i cut to prevent the segment from overflowing the
        regions size.
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10,20], ends=[15, 40],
                                  expStarts=[4,14], expEnds=[15,40], start=6,
                                  allowOverlap=False, resultAllowOverlap=True,
                                  ignoreStrand=True)

    def atestSlopSegmentsMultipleOverlappingMergeOverlap(self):
        """
        Test if the slop i cut to prevent the segment from overflowing the
        regions size.
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10,20], ends=[15, 40],
                                  expStarts=[4], expEnds=[40], start=6,
                                  allowOverlap=False, resultAllowOverlap=False,
                                  ignoreStrand=True)

    def atestSlopSegmentsStartStrandSimple(self):
        """
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10], ends=[20], strands=['+'],
                                  expStarts=[5], expEnds=[20], start=5,
                                  allowOverlap=False, debug=False,
                                  resultAllowOverlap=False, ignoreStrand=False)

    def atestSlopSegmentsEndStrandSimple(self):
        """
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10], ends=[20], strands=['+'],
                                  expStarts=[10], expEnds=[25], end=5,
                                  allowOverlap=False, debug=False,
                                  resultAllowOverlap=False, ignoreStrand=False)

    def atestSlopSegmentsStartNegStrandSimple(self):
        """
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10], ends=[20], strands=['-'],
                                  expStarts=[10], expEnds=[25], start=5,
                                  allowOverlap=False, debug=False,
                                  resultAllowOverlap=False, ignoreStrand=False)

    def atestSlopSegmentsEndNegStrandSimple(self):
        """
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10], ends=[20], strands=["-"],
                                  expStarts=[5], expEnds=[20], end=5,
                                  allowOverlap=False, debug=False,
                                  resultAllowOverlap=False, ignoreStrand=False)

    def atestSlopSegmentsStarStrandNotDefinedSimple(self):
        """
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10], ends=[20], strands=['.'],
                                  expStarts=[5], expEnds=[20], start=5,
                                  allowOverlap=False, debug=False,
                                  resultAllowOverlap=False, ignoreStrand=False)

    def atestSlopSegmentsEndStrandNotDefinedSimple(self):
        """
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10], ends=[20], strands=["."],
                                  expStarts=[10], expEnds=[25], end=5,
                                  allowOverlap=False, debug=False,
                                  resultAllowOverlap=False, ignoreStrand=False)


if __name__ == "__main__":
    unittest.main()
