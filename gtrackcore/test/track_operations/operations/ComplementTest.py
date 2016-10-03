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

    def _runTest(self, starts=None, ends=None, strands=None, values=None,
                 ids=None, edges=None, weights=None, expStarts=None,
                 expEnds=None, expNoResult=False, expTrackFormatType=None,
                 customChrLength=None, debug=False):

        track = createSimpleTestTrackContent(startList=starts, endList=ends,
                                             valList=values,
                                             strandList=strands, idList=ids,
                                             edgeList=edges,
                                             weightsList=weights,
                                             customChrLength=customChrLength)

        c = Complement(track, debug=debug)

        self.assertTrue((c is not None))

        result = c.calculate()

        resFound = False
        for (k, v) in result.trackViews.iteritems():
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

                if expTrackFormatType is not None:
                    self.assertTrue(v.trackFormat.getFormatName() ==
                                    expTrackFormatType)

                if expEnds is None:
                    # Assuming a point type track. Creating the expected ends.
                    expEnds = np.array(expStarts) + 1

                self.assertTrue(newStarts is not None)
                self.assertTrue(np.array_equal(newStarts, expStarts))

                self.assertTrue(newEnds is not None)
                self.assertTrue(np.array_equal(newEnds, expEnds))

                # Complement removes all other information.
                # Test that none of it is left
                self.assertTrue(newValues is None)
                self.assertTrue(newStrands is None)
                self.assertTrue(newIds is None)
                self.assertTrue(newEdges is None)
                self.assertTrue(newWeights is None)
                #self.assertTrue(newExtras is None)

            else:
                # Tests if all tracks no in chr1 have a size of 0.
                self.assertEqual(v.size, 0)

        if expNoResult:
            self.assertFalse(resFound)
        else:
            self.assertTrue(resFound)

    # **** Points ****
    def testInputPointsSimple(self):
        """
        Test that we get no values or strand in return
        :return:
        """
        self._runTest(starts=[5], expStarts=[0,6], expEnds=[5,len(self.chr1)],
                      expTrackFormatType="Segments")

    def testInputPointsComplex(self):
        """
        Test that we get no values or strand in return
        :return:
        """
        self._runTest(starts=[5,10,40], expStarts=[0,6,11,41],
                      expEnds=[5,10,40,len(self.chr1)],
                      expTrackFormatType="Segments")

    def testInputPointsAtStart(self):
        """
        Test that we get no values or strand in return
        :return:
        """
        self._runTest(starts=[0,10], expStarts=[1,11],
                      expEnds=[10,len(self.chr1)],
                      expTrackFormatType="Segments")

    def testInputPointsAtRegionEnd(self):
        """
        Test that we get no values or strand in return
        :return:
        """
        self._runTest(starts=[5,len(self.chr1)-1], expStarts=[0,6],
                      expEnds=[5, len(self.chr1)-1],
                      expTrackFormatType="Segments", debug=True)

    # **** Segments ****
    # Start at 0, end at GenomeSize, both, strand do missing
    def testSegmentsSimple(self):
        """
        Simple test
        :return:
        """
        self._runTest(starts=[10], ends=[20], expStarts=[0,20],
                      expEnds=[10, len(self.chr1)],
                      expTrackFormatType="Segments")

    def testSegmentsStartAtZero(self):
        """
        Segment start at 0
        :return:
        """
        self._runTest(starts=[0], ends=[20], expStarts=[20], expEnds=[len(
            self.chr1)], expTrackFormatType="Segments")

    def testSegmentsEndAtRegionSize(self):
        """
        Segment end at regionSize
        :return:
        """
        self._runTest(starts=[50], ends=[len(self.chr1)], expStarts=[0],
                      expEnds=[50], expTrackFormatType="Segments")

    def testSegmentsEndAndStart(self):
        """
        Segment start at 0, end at regionSize
        :return:
        """
        self._runTest(starts=[0, 500], ends=[200, len(self.chr1)],
                      expStarts=[200], expEnds=[500],
                      expTrackFormatType="Segments")

    def testEmptyInput(self):
        """
        Test if an empty input gives us one large segment with start at 0,
        end at regionSize
        :return:
        """
        self._runTest(starts=[], ends=[], expStarts=[0],
                      expEnds=[len(self.chr1)], expTrackFormatType="Segments")

    def testSegmentsComplex(self):
        """
        Segment start at 0, end at regionSize
        :return:
        """
        self._runTest(starts=[50,500,1000,45000], ends=[65,950,5400,69000],
                      expStarts=[0,65,950,5400,69000],
                      expEnds=[50,500,1000,45000,len(self.chr1)],
                      expTrackFormatType="Segments")

    def testSegmentsOfSizeZero(self):
        """
        Test that two ajasoned segments do not create a new segment of size 0
        :return:
        """
        self._runTest(starts=[10,20], ends=[20,30], expStarts=[0, 30],
                      expEnds=[10,len(self.chr1)],
                      expTrackFormatType="Segments", debug=True)

    def testSegmentsPointsOutput(self):
        """
        Special case where there are only points in the complement.
        The result is a segment track as the calculation would we
        unnecessary in most cases.
        :return:
        """
        self._runTest(starts=[1], ends=[len(self.chr1)], expStarts=[0],
                      expEnds=[1], expTrackFormatType="Segments")

    # *** Other tracks as input ***
    # These tests check that the information from the other valid track types
    # are removed.
    def testInputValuedPoints(self):
        """
        Test that we get no values or strand in return
        :return:
        """
        self._runTest(starts=[5], strands=['+'], values=[1],
                      expStarts=[0,6], expEnds=[5,len(self.chr1)],
                      expTrackFormatType="Segments")

    def testInputLinkedPoints(self):
        """
        Test that the operation accepts a linked points track as input.
        :return:
        """
        self._runTest(starts=[5,10], strands=['+','-'], ids=[1,2],
                      edges=[2,1], weights=[[1],[1]], expStarts=[0,6,11],
                      expEnds=[5,10,len(self.chr1)],
                      expTrackFormatType="Segments")

    def testInputLinkedValuedPoints(self):
        """
        Test that the operation accepts a linked valued points track as input.
        :return:
        """
        self._runTest(starts=[5,10], strands=['+','-'], values=[1,3],
                      ids=[1,2], edges=[2,1], weights=[[1],[1]],
                      expStarts=[0,6,11], expEnds=[5,10,len(self.chr1)],
                      expTrackFormatType="Segments")

    def testInputValuedSegments(self):
        """
        Test that the operation accepts a valued segments track with
        strand as input.
        :return:
        """
        self._runTest(starts=[0,20], ends=[10,30], strands=['+','-'],
                      values=[1,2],
                      expStarts=[10,30],
                      expEnds=[20,len(self.chr1)],
                      expTrackFormatType="Segments")

    def testInputLinkedSegments(self):
        """
        Test that the operation accepts a linked segments track as input.
        :return:
        """
        self._runTest(starts=[0,20], ends=[10,30], strands=['+','-'],
                      ids=[1,2], edges=[2,1], weights=[[1],[1]],
                      expStarts=[10,30], expEnds=[20,len(self.chr1)],
                      expTrackFormatType="Segments")

    def testInputLinkedValuedSegments(self):
        """
        Test that the operation accepts a linked valued segments track as
        input.
        :return:
        """
        self._runTest(starts=[0,20], ends=[10,30], strands=['+','-'],
                      values=[1,2], ids=[1,2], edges=[2,1],
                      weights=[[1],[1]], expStarts=[10,30],
                      expEnds=[20,len(self.chr1)],
                      expTrackFormatType="Segments")

if __name__ == "__main__":
    unittest.main()
