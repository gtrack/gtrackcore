import unittest
import numpy as np
from collections import OrderedDict

from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.operations.Complement import Complement
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.test.track_operations.TestUtils import createTrackView
from gtrackcore.test.track_operations.TestUtils import \
    createSimpleTestTrackContent


class ComplementTest(unittest.TestCase):

    def setUp(self):
        self.chr1 = (GenomeRegion('hg19', 'chr1', 0,
                                  GenomeInfo.GENOMES['hg19']['size']['chr1']))
        self.chromosomes = (GenomeRegion('hg19', c, 0, l)
                            for c, l in
                            GenomeInfo.GENOMES['hg19']['size'].iteritems())

    def _runComplementSegmentsTest(self, starts, ends, expStarts, expEnds,
                                   strands=None, expStrands=None, debug=False,
                                   allowOverlap=False):

        track = createSimpleTestTrackContent(startList=starts, endList=ends,
                                             strandList=strands)

        assert starts is not None
        assert ends is not None

        expStarts = np.array(expStarts)
        expEnds = np.array(expEnds)

        c = Complement(track, allowOverlap=allowOverlap)

        self.assertTrue((c is not None))

        result = c.calculate()

        resFound = False

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

    # Start at 0, end at GenomeSize, both, strand do missing

    def testComplementSegmentsSimple(self):
        """
        Simple test
        :return:
        """
        self._runComplementSegmentsTest(starts=[10], ends=[20],
                                        expStarts=[0,20],
                                        expEnds=[10, len(self.chr1)],
                                        debug=True)

    def testComplementSegmentsStartAtZero(self):
        """
        Segment start at 0
        :return:
        """
        self._runComplementSegmentsTest(starts=[0], ends=[20],
                                        expStarts=[20],
                                        expEnds=[len(self.chr1)],
                                        debug=True)

    def testComplementSegmentsEndAtRegionSize(self):
        """
        Segment end at regionSize
        :return:
        """
        self._runComplementSegmentsTest(starts=[50], ends=[len(self.chr1)],
                                        expStarts=[0],
                                        expEnds=[50],
                                        debug=True)

    def testComplementSegmentsEndAndStat(self):
        """
        Segment start at 0, end at regionSize
        :return:
        """
        self._runComplementSegmentsTest(starts=[0, 500],
                                        ends=[200, len(self.chr1)],
                                        expStarts=[200],
                                        expEnds=[500],
                                        debug=True)

    def testComplementEmptyInput(self):
        """
        Segment start at 0, end at regionSize
        :return:
        """
        self._runComplementSegmentsTest(starts=[],
                                        ends=[],
                                        expStarts=[0],
                                        expEnds=[len(self.chr1)],
                                        debug=True)

    def testComplementSegmentsComplex(self):
        """
        Segment start at 0, end at regionSize
        :return:
        """
        self._runComplementSegmentsTest(starts=[50,500,1000,45000],
                                        ends=[65,950,5400,69000],
                                        expStarts=[0,65,950,5400,69000],
                                        expEnds=[50,500,1000,45000,
                                                 len(self.chr1)],
                                        debug=True)

if __name__ == "__main__":
    unittest.main()
