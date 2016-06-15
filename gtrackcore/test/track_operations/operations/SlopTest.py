import unittest
import numpy as np
from collections import OrderedDict

from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.operations.Slop import Slop
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.test.track_operations.TestUtils import createTrackView
from gtrackcore.test.track_operations.TestUtils import \
    createSimpleTestTrackContent


class SlopTest(unittest.TestCase):

    def setUp(self):
        self.chr1 = (GenomeRegion('hg19', 'chr1', 0,
                                  GenomeInfo.GENOMES['hg19']['size']['chr1']))
        self.chromosomes = (GenomeRegion('hg19', c, 0, l)
                            for c, l in
                            GenomeInfo.GENOMES['hg19']['size'].iteritems())

    def _runSlopSegmentsTest(self, starts, ends, expStarts, expEnds,
                             strands=None, expStrands=None, start=None,
                             end=None, both=None, ignoreStrand=False,
                             allowOverlap=False, resultAllowOverlap=False,
                             debug=False):

        track = createSimpleTestTrackContent(startList=starts, endList=ends,
                                             strandList=strands)

        if both is not None:
            self.assertTrue((start is None and end is None))
        else:
            self.assertTrue((starts is not None or end is not None))

        u = Slop(track, start=start, end=end, both=both,
                 ignoreStrand=ignoreStrand, allowOverlap=allowOverlap,
                 resultAllowOverlap=resultAllowOverlap, debug=debug)

        self.assertTrue((u is not None))

        tc = u()

        resFound = False

        for (k, v) in tc.getTrackViews().items():
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

    def testSlopSegmentsStartSimple(self):
        """
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10], ends=[20], expStarts=[5],
                                  expEnds=[20], start=5, allowOverlap=False,
                                  resultAllowOverlap=True, ignoreStrand=True)

    def testSlopSegmentsEndSimple(self):
        """
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10], ends=[20], expStarts=[10],
                                  expEnds=[25], end=5, allowOverlap=False,
                                  resultAllowOverlap=True, ignoreStrand=True)

    def testSlopSegmentsBothSimple(self):
        """
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10], ends=[20], expStarts=[5],
                                  expEnds=[25], both=5, allowOverlap=False,
                                  resultAllowOverlap=True, ignoreStrand=True)

    def testSlopSegmentsStartAndEndSameValue(self):
        """
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10], ends=[20], expStarts=[5],
                                  expEnds=[25], start=5, end=5,
                                  allowOverlap=False,
                                  resultAllowOverlap=True, ignoreStrand=True)

    def testSlopSegmentsStartAndEndDifferentValue(self):
        """
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10], ends=[20], expStarts=[6],
                                  expEnds=[35], start=4, end=15,
                                  allowOverlap=False,
                                  resultAllowOverlap=True, ignoreStrand=True)

    def testSlopSegmentsNewStartAtZero(self):
        """
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10], ends=[20], expStarts=[0],
                                  expEnds=[20], start=10, allowOverlap=False,
                                  resultAllowOverlap=True, ignoreStrand=True)

    def testSlopSegmentsUnderflow(self):
        """
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10], ends=[20], expStarts=[0],
                                  expEnds=[20], start=100, allowOverlap=False,
                                  resultAllowOverlap=True, ignoreStrand=True)

    def testSlopSegmentsEndAtRegionSize(self):
        """
        Test if creating a slop with an end equal to the size of the region
        :return: None
        """
        self._runSlopSegmentsTest(starts=[4000000], ends=[len(self.chr1)-20],
                                  expStarts=[4000000],
                                  expEnds=[len(self.chr1)], end=20,
                                  allowOverlap=False,
                                  resultAllowOverlap=True, ignoreStrand=True)

    def testSlopSegmentsOverflow(self):
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

    def testSlopSegmentsMultipleNoOverlapStart(self):
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

    def testSlopSegmentsMultipleNoOverlapEnd(self):
        """
        Test if the slop i cut to prevent the segment from overflowing the
        regions size.
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10,40], ends=[20, 70],
                                  expStarts=[10,40], expEnds=[25,75], end=5,
                                  allowOverlap=False, resultAllowOverlap=True,
                                  ignoreStrand=True)

    def testSlopSegmentsMultipleOverlappingResAllowOverlap(self):
        """
        Test if the slop i cut to prevent the segment from overflowing the
        regions size.
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10,20], ends=[15, 40],
                                  expStarts=[4,14], expEnds=[15,40], start=6,
                                  allowOverlap=False, resultAllowOverlap=True,
                                  ignoreStrand=True)

    def testSlopSegmentsMultipleOverlappingMergeOverlap(self):
        """
        Test if the slop i cut to prevent the segment from overflowing the
        regions size.
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10,20], ends=[15, 40],
                                  expStarts=[4], expEnds=[40], start=6,
                                  allowOverlap=False, resultAllowOverlap=False,
                                  ignoreStrand=True)

    def testSlopSegmentsStartStrandSimple(self):
        """
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10], ends=[20], strands=['+'],
                                  expStarts=[5], expEnds=[20], start=5,
                                  allowOverlap=False, debug=False,
                                  resultAllowOverlap=False, ignoreStrand=False)

    def testSlopSegmentsEndStrandSimple(self):
        """
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10], ends=[20], strands=['+'],
                                  expStarts=[10], expEnds=[25], end=5,
                                  allowOverlap=False, debug=False,
                                  resultAllowOverlap=False, ignoreStrand=False)

    def testSlopSegmentsStartNegStrandSimple(self):
        """
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10], ends=[20], strands=['-'],
                                  expStarts=[10], expEnds=[25], start=5,
                                  allowOverlap=False, debug=False,
                                  resultAllowOverlap=False, ignoreStrand=False)

    def testSlopSegmentsEndNegStrandSimple(self):
        """
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10], ends=[20], strands=["-"],
                                  expStarts=[5], expEnds=[20], end=5,
                                  allowOverlap=False, debug=False,
                                  resultAllowOverlap=False, ignoreStrand=False)

    def testSlopSegmentsStarStrandNotDefinedSimple(self):
        """
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10], ends=[20], strands=['.'],
                                  expStarts=[5], expEnds=[20], start=5,
                                  allowOverlap=False, debug=False,
                                  resultAllowOverlap=False, ignoreStrand=False)

    def testSlopSegmentsEndStrandNotDefinedSimple(self):
        """
        :return: None
        """
        self._runSlopSegmentsTest(starts=[10], ends=[20], strands=["."],
                                  expStarts=[10], expEnds=[25], end=5,
                                  allowOverlap=False, debug=False,
                                  resultAllowOverlap=False, ignoreStrand=False)


if __name__ == "__main__":
    unittest.main()
