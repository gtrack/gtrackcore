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

    def _runTest(self, starts=None, ends=None, values=None, strands=None,
                 ids=None, edges=None, weights=None, expStarts=None,
                 expEnds=None, expValues=None, expStrands=None, expIds=None,
                 expEdges=None, expWeights=None, customChrLength=None,
                 allowOverlap=True, resultAllowOverlap=False, start=None,
                 end=None, both=None, useStrands=False,
                 useMissingStrands=True, treatMissingAsPositive=True,
                 debug=False):

        track = createSimpleTestTrackContent(startList=starts, endList=ends,
                                             valList=values,
                                             strandList=strands,
                                             idList=ids, edgeList=edges,
                                             weightsList=weights,
                                             customChrLength=customChrLength)

        s = Slop(track, both=both, start=start, end=end,
                 useStrands=useStrands, useMissingStrands=useMissingStrands,
                 treatMissingAsPositive=treatMissingAsPositive,
                 resultAllowOverlap=resultAllowOverlap, debug=debug)

        result = s.calculate()
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

                if expStarts is not None:
                    print("newStarts: {}".format(newStarts))
                    print("expStarts: {}".format(expStarts))
                    self.assertTrue(newStarts is not None)
                    self.assertTrue(np.array_equal(newStarts, expStarts))
                else:
                    self.assertTrue(newStarts is None)

                if expEnds is not None:
                    print("newEnds: {}".format(newEnds))
                    print("expEnds: {}".format(expEnds))
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
                    print("newIds: {}".format(newIds))
                    print("expIds: {}".format(expIds))
                    self.assertTrue(newIds is not None)
                    self.assertTrue(np.array_equal(newIds, expIds))
                else:
                    self.assertTrue(newIds is None)

                if expEdges is not None:
                    print("newEdges: {}".format(newEdges))
                    print("expEdges: {}".format(expEdges))
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

        self.assertTrue(resFound)



    # **** Segments tests ****

    def testSegmentSimple(self):
        """
        :return: None
        """
        # Test of start
        self._runTest(starts=[10], ends=[20], expStarts=[5], expEnds=[20],
                      start=5, resultAllowOverlap=True)

        # Test of end
        self._runTest(starts=[10], ends=[20], expStarts=[10], expEnds=[25],
                      end=5, resultAllowOverlap=True)

        # Test of bofh
        self._runTest(starts=[10], ends=[20], expStarts=[5], expEnds=[25],
                      both=5, resultAllowOverlap=True)

        # test of star and end
        self._runTest(starts=[10], ends=[20], expStarts=[5], expEnds=[25],
                      start=5, end=5, resultAllowOverlap=True,)

        # test of star and end. Different values
        self._runTest(starts=[10], ends=[20], expStarts=[6], expEnds=[35],
                      start=4, end=15, resultAllowOverlap=True)

    def testSegmentsOverAndUnderflow(self):
        """
        :return: None
        """
        # Underflow.
        # New start at 0
        self._runTest(starts=[10], ends=[20], expStarts=[0], expEnds=[20],
                      start=10, resultAllowOverlap=True)

        # Cutting underflow
        self._runTest(starts=[10], ends=[20], expStarts=[0], expEnds=[20],
                      start=100, resultAllowOverlap=True)

        # Start at 0
        self._runTest(starts=[0], ends=[20], expStarts=[0], expEnds=[20],
                      start=10, resultAllowOverlap=True)

        # Overflow
        # New end at len(region)
        self._runTest(starts=[400000], ends=[len(self.chr1)-20],
                      expStarts=[400000], expEnds=[len(self.chr1)], end=20,
                      resultAllowOverlap=True)

        # Cuting overflow to region size
        self._runTest(starts=[400000], ends=[len(self.chr1)-20],
                      expStarts=[400000], expEnds=[len(self.chr1)], end=300,
                      resultAllowOverlap=True)

    def testSegmentsMultiple(self):
        """
        Tests slop on multiple tracks. Some overlap. Test merge of the overlap
        :return: None
        """
        # Start, multiple, no overlap.
        self._runTest(starts=[10,40], ends=[20, 70], expStarts=[5,35],
                      expEnds=[20,70], start=5, resultAllowOverlap=True)

        # End, multiple, no overlap.
        self._runTest(starts=[10,40], ends=[20, 70], expStarts=[10,40],
                      expEnds=[25,75], end=5, resultAllowOverlap=True)

        # Start, multiple, overlap, allow overlap in result.
        self._runTest(starts=[10,20], ends=[15, 40], expStarts=[4,14],
                      expEnds=[15,40], start=6, resultAllowOverlap=True)

        # Start, multiple, overlap, merge overlap in result.
        self._runTest(starts=[10,20], ends=[15, 40], expStarts=[4],
                      expEnds=[40], start=6, resultAllowOverlap=False)

    # test overlap in input

    def atestSegmentsWithStrands(self):
        """
        :return: None
        """

        # Positive, start
        self._runTest(starts=[10], ends=[20], strands=['+'], expStarts=[5],
                      expEnds=[20], expStrands=['+'], start=5, useStrands=True,
                      resultAllowOverlap=True)

        # Positive, end
        self._runTest(starts=[10], ends=[20], strands=['+'], expStarts=[10],
                      expEnds=[25], expStrands=['+'], end=5, useStrands=True,
                      resultAllowOverlap=True)

    def testSegmentsWithStrands(self):
        # Negative, start
        self._runTest(starts=[10], ends=[20], strands=['-'], expStarts=[10],
                      expEnds=[25], expStrands=['-'], start=5, useStrands=True,
                      resultAllowOverlap=True)

        # Negative, end
        self._runTest(starts=[10], ends=[20], strands=['-'], expStarts=[5],
                      expEnds=[20], expStrands=['-'], end=5, useStrands=True,
                      resultAllowOverlap=False)

        # Strand missing, Using
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5],
                      expEnds=[20], expStrands=['.'], start=5, useStrands=True,
                      useMissingStrands=True, treatMissingAsPositive=True,
                      resultAllowOverlap=True)

    def atestSlopSegmentsEndStrandNotDefinedSimple(self):
        """
        :return: None
        """
        self._runTest(starts=[10], ends=[20], strands=["."],
                                  expStarts=[10], expEnds=[25], end=5,
                                  allowOverlap=False, debug=False,
                                  resultAllowOverlap=False, ignoreStrand=False)


if __name__ == "__main__":
    unittest.main()
