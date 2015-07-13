import unittest
import numpy as np
import os

from gtrackcore.track_operations.operations.Union import Union
from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.core.Api import importFile
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.track.core.TrackView import TrackView

#from OperationTest import createTrackView
#import gtrackcore.track_operations.tests.OperationTest.createTrackView


from collections import OrderedDict
from gtrackcore.track_operations.tests.OperationTest import createTrackView

class UnionTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Loads the testdata
        :return:
        """
        #os.environ['GTRACKCORE_DIR'] = "/Users/skh/gtrack-data"
        #tracks = TrackOperations.get_available_tracks()
        #path = './testdata/'

        #for fn in os.listdir(path):
        #    track_name = os.path.splitext(fn)[0]

        #    if not any(track_name in t for t in tracks):
        #        importFile(path+fn, 'hg19', track_name)

    def setUp(self):
        #os.environ['GTRACKCORE_DIR'] = "/Users/skh/gtrack-data"
        self.chr1 = (GenomeRegion('hg19', 'chr1', 0, GenomeInfo.GENOMES['hg19']['size']['chr1']))
        self.cromosomes = (GenomeRegion('hg19', chr, 0, len)
                    for chr, len in GenomeInfo.GENOMES['hg19']['size'].iteritems())


    def _run_union_test(self, track1, track2, expected_starts, expected_ends):
        """
        Run a union test over two tracks.
        The test expects there to only to be segments in chr1,
        All other chromosomes need to be of size zero.

        :param track1: Name in GTrackCore of track A
        :param track2: Name in GTrackCore of track B
        :param expected_starts: Expected starts of the union
        :param expected_ends: Expected ends of the union
        :return: None
        """

        print "testtype: %s " % type(track2).__name__
        u = Union(track1, track2)
        tvList = u()

        print tvList

        #for i in tvList:
        #    if cmp(i[0], self.chr1) == 0:
        #        # All test tracks are in chr1
        #        self.assertTrue(np.array_equal(i[1], expected_starts))
        #        self.assertTrue(np.array_equal(i[2], expected_ends))
        #    else:
        #        # Tests if all tracks no in chr1 have a size of 0.
        #        self.assertEqual(i[1].size, 0)
        #        self.assertEqual(i[2].size, 0)

    def _createTrackContent(self, start, end):
        """
        Create a track view a start, end list pair.
        Help method used in testing. This method will create a hg19 tracks with
        data in chromosome 1 only.
        :param start: List of track start positions
        :param end: List of track end positions
        :return: A TrackContent object
        """

        print "In createTrackContent!!"

        startA = np.array(start)
        endA = np.array(end)

        tv = createTrackView(region=self.chr1, startList=start, endList=end,
                               allow_overlap=False)

        d = OrderedDict()
        d[self.chr1] = tv
        return TrackContents('hg19', d)


    def test_union_no_overlap(self):
        """
        Two non overlapping segments
        :return: None
        """
        startA = [2]
        endA = [4]
        startB = [5]
        endB = [8]

        expected_starts = [2, 5]
        expected_ends = [4, 8]
        track1 = self._createTrackContent(startA, endA)
        track2 = self._createTrackContent(startB, endB)

        self._run_union_test(track1, track2, expected_starts, expected_ends)


if __name__ == "__main__":
    unittest.main()
