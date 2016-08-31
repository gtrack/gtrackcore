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
                 end=None, both=None, useFraction=False, useStrands=False,
                 useMissingStrands=True, treatMissingAsNegative=False,
                 updateMissingStrand=False, ignoreNegative=False,
                 ignorePositive=False, keepValuesAndLinks=False,
                 debug=False):

        track = createSimpleTestTrackContent(startList=starts, endList=ends,
                                             valList=values,
                                             strandList=strands,
                                             idList=ids, edgeList=edges,
                                             weightsList=weights,
                                             customChrLength=customChrLength)

        s = Slop(track, both=both, start=start, end=end,
                 useFraction=useFraction, useStrands=useStrands,
                 useMissingStrands=useMissingStrands,
                 treatMissingAsNegative=treatMissingAsNegative,
                 updateMissingStrand=updateMissingStrand,
                 resultAllowOverlap=resultAllowOverlap,
                 ignorePositive=ignorePositive,
                 ignoreNegative=ignoreNegative,
                 keepValuesAndLinks=keepValuesAndLinks, debug=debug)

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

                if debug:
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

        self.assertTrue(resFound)

    # **** Test Points ****
    # Just doing some simple test. When giving Slop a point track we return
    # a segment track. For each point we get a new segment.
    def testPoints(self):
        # Test of start
        self._runTest(starts=[10], expStarts=[5], expEnds=[10],
                      start=5, resultAllowOverlap=True)

        # Test of end
        self._runTest(starts=[10], expStarts=[10], expEnds=[15],
                      end=5, resultAllowOverlap=True)

        # Test of both
        self._runTest(starts=[10], expStarts=[5], expEnds=[15],
                      both=5, resultAllowOverlap=True)

        # test of star and end
        self._runTest(starts=[10], expStarts=[5], expEnds=[15],
                      start=5, end=5, resultAllowOverlap=True)

        # test of star and end. Different values
        self._runTest(starts=[10], expStarts=[6], expEnds=[20],
                      start=4, end=10, resultAllowOverlap=True)

    # **** Test Segments ****
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

    def testSegmentsWithStrands(self):
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

        # Positive, both
        self._runTest(starts=[10], ends=[20], strands=['+'], expStarts=[5],
                      expEnds=[25], expStrands=['+'], both=5, useStrands=True,
                      resultAllowOverlap=True)

        # Positive, start and end
        self._runTest(starts=[10], ends=[20], strands=['+'], expStarts=[5],
                      expEnds=[30], expStrands=['+'], start=5, end=10,
                      useStrands=True, resultAllowOverlap=True)

        # Negative, start
        self._runTest(starts=[10], ends=[20], strands=['-'], expStarts=[10],
                      expEnds=[25], expStrands=['-'], start=5, useStrands=True,
                      resultAllowOverlap=True)

        # Negative, end
        self._runTest(starts=[10], ends=[20], strands=['-'], expStarts=[5],
                      expEnds=[20], expStrands=['-'], end=5, useStrands=True,
                      resultAllowOverlap=True)

        # Negative, both
        self._runTest(starts=[10], ends=[20], strands=['-'], expStarts=[5],
                      expEnds=[25], expStrands=['-'], both=5, useStrands=True,
                      resultAllowOverlap=True)

        # Negative, start and end
        self._runTest(starts=[10], ends=[20], strands=['-'], expStarts=[5],
                      expEnds=[30], expStrands=['-'], start=10, end=5,
                      useStrands=True, resultAllowOverlap=True)

        # Strand missing. As positive, start
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5],
                      expEnds=[20], expStrands=['.'], start=5, useStrands=True,
                      useMissingStrands=True, resultAllowOverlap=True)

        # Strand missing. As positive, end
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[10],
                      expEnds=[25], expStrands=['.'], end=5, useStrands=True,
                      useMissingStrands=True, resultAllowOverlap=True)

        # Strand missing. As positive, both
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5],
                      expEnds=[25], expStrands=['.'], both=5, useStrands=True,
                      useMissingStrands=True, resultAllowOverlap=True)

        # Strand missing. As positive, start and end
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5],
                      expEnds=[30], expStrands=['.'], start=5, end=10,
                      useStrands=True, useMissingStrands=True,
                      resultAllowOverlap=True)

        # Strand missing. As negative, start
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[10],
                      expEnds=[25], expStrands=['.'], start=5, useStrands=True,
                      useMissingStrands=True, treatMissingAsNegative=True,
                      resultAllowOverlap=True)

        # Strand missing. As negative, end
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5],
                      expEnds=[20], expStrands=['.'], end=5, useStrands=True,
                      useMissingStrands=True, treatMissingAsNegative=True,
                      resultAllowOverlap=True)

        # Strand missing. As negative, both
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5],
                      expEnds=[25], expStrands=['.'], both=5, useStrands=True,
                      useMissingStrands=True, treatMissingAsNegative=True,
                      resultAllowOverlap=True)

        # Strand missing. As negative, start and end
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[0],
                      expEnds=[25], expStrands=['.'], start=5, end=10,
                      useStrands=True, useMissingStrands=True,
                      treatMissingAsNegative=True, resultAllowOverlap=True)

        # Strand missing. As positive, start, keeping strand
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5],
                      expEnds=[20], expStrands=['+'], start=5, useStrands=True,
                      useMissingStrands=True, updateMissingStrand=True,
                      resultAllowOverlap=True)

        # Strand missing. As positive, end
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[10],
                      expEnds=[25], expStrands=['+'], end=5, useStrands=True,
                      useMissingStrands=True, updateMissingStrand=True,
                      resultAllowOverlap=True)

        # Strand missing. As positive, both
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5],
                      expEnds=[25], expStrands=['+'], both=5, useStrands=True,
                      useMissingStrands=True, updateMissingStrand=True,
                      resultAllowOverlap=True)

        # Strand missing. As positive, start and end
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5],
                      expEnds=[30], expStrands=['+'], start=5, end=10,
                      useStrands=True, useMissingStrands=True,
                      updateMissingStrand=True, resultAllowOverlap=True)

        # Strand missing. As negative, start
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[10],
                      expEnds=[25], expStrands=['-'], start=5, useStrands=True,
                      useMissingStrands=True, treatMissingAsNegative=True,
                      updateMissingStrand=True, resultAllowOverlap=True)

        # Strand missing. As negative, end
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5],
                      expEnds=[20], expStrands=['-'], end=5, useStrands=True,
                      useMissingStrands=True, treatMissingAsNegative=True,
                      updateMissingStrand=True, resultAllowOverlap=True)

        # Strand missing. As negative, both
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[5],
                      expEnds=[25], expStrands=['-'], both=5, useStrands=True,
                      useMissingStrands=True, treatMissingAsNegative=True,
                      updateMissingStrand=True, resultAllowOverlap=True)

        # Strand missing. As negative, start and end
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[0],
                      expEnds=[25], expStrands=['-'], start=5, end=10,
                      useStrands=True, useMissingStrands=True,
                      treatMissingAsNegative=True, updateMissingStrand=True,
                      resultAllowOverlap=True)

        # Strand missing. Ignoring
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[10],
                      expEnds=[20], expStrands=['.'], start=5, useStrands=True,
                      useMissingStrands=False, resultAllowOverlap=True)

    def testSegmentsOverlap(self):
        """
        Test that we get overlapping segments and that they are merged
        correctly.
        :return: None
        """

        # Test of start, allow overlap in result
        self._runTest(starts=[10,25], ends=[20,30], expStarts=[4,19],
                      expEnds=[20,30], start=6, resultAllowOverlap=True)

        # Test of start, merge overlap in result
        self._runTest(starts=[10,25], ends=[20,30], expStarts=[4],
                      expEnds=[30], start=6, resultAllowOverlap=False)

        # Test of end, allow overlap in result
        self._runTest(starts=[10,24], ends=[20,100], expStarts=[10, 24],
                      expEnds=[25,105], end=5, resultAllowOverlap=True)

        # Test of end, merge overlap in result
        self._runTest(starts=[10,24], ends=[20,100], expStarts=[10],
                      expEnds=[105], end=5, resultAllowOverlap=False)

        # Test of both, allow overlap in result
        self._runTest(starts=[10,22], ends=[20,30], expStarts=[5,17],
                      expEnds=[25,35], both=5, resultAllowOverlap=True)

        # Test of both, merge overlap in result
        self._runTest(starts=[10,22], ends=[20,30], expStarts=[5],
                      expEnds=[35], both=5, resultAllowOverlap=False)

        # test of star and end, allow overlap in result
        self._runTest(starts=[10,22], ends=[20,30], expStarts=[5,17],
                      expEnds=[25,35], start=5, end=5,
                      resultAllowOverlap=True)

        # test of star and end, merge overlap
        self._runTest(starts=[10,22], ends=[20,30], expStarts=[5],
                      expEnds=[35], start=5, end=5, resultAllowOverlap=False)

        # test of star and end. Different values, allow overlap in result
        self._runTest(starts=[10,37], ends=[20,50], expStarts=[6],
                      expEnds=[65], start=4, end=15,
                      resultAllowOverlap=False, debug=True)

        # test of star and end. Different values, merge overlap in result
        self._runTest(starts=[10,37], ends=[20,50], expStarts=[6],
                      expEnds=[65], start=4, end=15,
                      resultAllowOverlap=False, debug=True)

    def testFractions(self):
        # Test of start
        self._runTest(starts=[10], ends=[20], expStarts=[5], expEnds=[20],
                      start=0.5, useFraction=True, resultAllowOverlap=True)

        # Test of end
        self._runTest(starts=[10], ends=[20], expStarts=[10], expEnds=[25],
                      end=0.5, useFraction=True, resultAllowOverlap=True)

        # Test of both
        self._runTest(starts=[10], ends=[20], expStarts=[5], expEnds=[25],
                      both=0.5, useFraction=True, resultAllowOverlap=True)

        # test of star and end
        self._runTest(starts=[10], ends=[20], expStarts=[5], expEnds=[25],
                      start=0.5, end=0.5, useFraction=True,
                      resultAllowOverlap=True,)

        # test of star and end. Different values
        self._runTest(starts=[10], ends=[20], expStarts=[5], expEnds=[30],
                      start=0.5, end=1, useFraction=True,
                      resultAllowOverlap=True)

    def testIgnorePartOfStrand(self):
        """

        :return:
        """

        # Nothing to ignore.
        self._runTest(starts=[10], ends=[20], strands=['+'], expStarts=[5],
                      expEnds=[20], expStrands=['+'], start=5, useStrands=True,
                      ignoreNegative=True, resultAllowOverlap=True)

        self._runTest(starts=[10], ends=[20], strands=['-'], expStarts=[10],
                      expEnds=[25], expStrands=['-'], start=5, useStrands=True,
                      ignorePositive=True, resultAllowOverlap=True)

        # Ignoring positive
        self._runTest(starts=[10], ends=[20], strands=['+'], expStarts=[10],
                      expEnds=[20], expStrands=['+'], start=5, useStrands=True,
                      ignorePositive=True, resultAllowOverlap=True, debug=True)

        # Ignoring negative
        self._runTest(starts=[10], ends=[20], strands=['-'], expStarts=[10],
                      expEnds=[20], expStrands=['-'], start=5, useStrands=True,
                      ignoreNegative=True, resultAllowOverlap=True, debug=True)

        # Treat missing as positive and ignore them..
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[10],
                      expEnds=[20], expStrands=['.'], end=5, useStrands=True,
                      useMissingStrands=True, ignorePositive=True,
                      resultAllowOverlap=True)

        # Treat missing as negative and ignore them..
        self._runTest(starts=[10], ends=[20], strands=['.'], expStarts=[10],
                      expEnds=[20], expStrands=['.'], end=5, useStrands=True,
                      useMissingStrands=True, ignoreNegative=True,
                      treatMissingAsNegative=True,
                      resultAllowOverlap=True)

        # Positive, both
        self._runTest(starts=[10], ends=[20], strands=['+'], expStarts=[5],
                      expEnds=[25], expStrands=['+'], both=5, useStrands=True,
                      resultAllowOverlap=True)

        # Positive, start and end
        self._runTest(starts=[10], ends=[20], strands=['+'], expStarts=[5],
                      expEnds=[30], expStrands=['+'], start=5, end=10,
                      useStrands=True, resultAllowOverlap=True)

        # Negative, start
        self._runTest(starts=[10], ends=[20], strands=['-'], expStarts=[10],
                      expEnds=[25], expStrands=['-'], start=5, useStrands=True,
                      resultAllowOverlap=True)

        # Negative, end
        self._runTest(starts=[10], ends=[20], strands=['-'], expStarts=[5],
                      expEnds=[20], expStrands=['-'], end=5, useStrands=True,
                      resultAllowOverlap=True)

        # Negative, both
        self._runTest(starts=[10], ends=[20], strands=['-'], expStarts=[5],
                      expEnds=[25], expStrands=['-'], both=5, useStrands=True,
                      resultAllowOverlap=True)

        # Negative, start and end
        self._runTest(starts=[10], ends=[20], strands=['-'], expStarts=[5],
                      expEnds=[30], expStrands=['-'], start=10, end=5,
                      useStrands=True, resultAllowOverlap=True)


        # Test ignoring negative, positive, missing positive and missing
        # negative.
        # Test resorting

    def testSegmentsResorting(self):
        """
        In some cases the we loose the ordering of the segments.
        To fix this we need to re-sort them.

        This case can happen when we have a segment track with strand
        information, and we only add to the end or the start

        Start = 6
        Input: starts=[5,10], ends=[8,15]
              a    b
            ---- ++++++

        Result: starts=[5,4], ends=[14,15]
            ----------
           ++++++++++++

        Here segment b has moved in front of segment a.

        Result after sort: starts=[4,5], ends=[15,14]

        :return:
        """

        self._runTest(starts=[5,10], ends=[8,15], strands=['-','+'],
                      ids=['1','2'], edges=['2','1'], start=6,
                      expStarts=[4,5], expEnds=[15,14], expStrands=['+','-'],
                      expIds=['2','1'], expEdges=['1','2'], useStrands=True,
                      keepValuesAndLinks=True, resultAllowOverlap=True,
                      debug=True)

if __name__ == "__main__":
    unittest.main()
