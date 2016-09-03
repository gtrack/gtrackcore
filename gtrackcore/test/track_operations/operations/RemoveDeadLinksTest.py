import unittest
import numpy as np
from collections import OrderedDict

from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.operations.RemoveDeadLinks import \
    RemoveDeadLinks
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.test.track_operations.TestUtils import createTrackView
from gtrackcore.test.track_operations.TestUtils import \
    createSimpleTestTrackContent


class RemoveDeadLinksTest(unittest.TestCase):

    def setUp(self):
        self.chr1 = (GenomeRegion('hg19', 'chr1', 0,
                                  GenomeInfo.GENOMES['hg19']['size']['chr1']))
        self.chromosomes = (GenomeRegion('hg19', c, 0, l)
                            for c, l in
                            GenomeInfo.GENOMES['hg19']['size'].iteritems())

    def _runTest(self, starts=None, ends=None, values=None, strands=None,
                 ids=None, edges=None, weights=None, newId=None,
                 expStarts=None, expEnds=None, expValues=None,
                 expStrands=None, expIds=None, expEdges=None,
                 expWeights=None, customChrLength=None, allowOverlap=True,
                 resultAllowOverlap=False,
                 debug=False):

        track = createSimpleTestTrackContent(startList=starts, endList=ends,
                                             valList=values,
                                             strandList=strands,
                                             idList=ids, edgeList=edges,
                                             weightsList=weights,
                                             customChrLength=customChrLength)

        r = RemoveDeadLinks(track, newId=newId,
                            resultAllowOverlap=resultAllowOverlap,
                            debug=debug)

        result = r.calculate()
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
                    print("newWeights: {}".format(newWeights))
                    print("expWeights: {}".format(expWeights))

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
                    # As weights can contain numpy.nan, we can not use the
                    # normal array_equal method.
                    # (np.nan == np.nan) == False
                    # Using the assert_equal instead which.

                    self.assertTrue(newWeights is not None)
                    try:
                        np.testing.assert_equal(newWeights, expWeights)
                    except AssertionError:
                        self.fail("Weights are not equal")
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

    def testSimple(self):
        """
        Simple test
        :return: None
        """
        self._runTest(starts=[10,20], ids=['3','10'], edges=['8','3'],
                      expStarts=[10,20], expIds=['3','10'], expEdges=['','3'],
                      resultAllowOverlap=True)

    def testMultipleEdges(self):
        """
        Test removing edges when there are multiple edges per id.
        :return: None
        """
        self._runTest(starts=[10,20], ids=['3','10'],
                      edges=[['3','9'],['3','10']],
                      expStarts=[10,20], expIds=['3','10'],
                      expEdges=[['3',''],['3','10']],
                      resultAllowOverlap=True, debug=True)

        # Removed edge, not at the end
        self._runTest(starts=[10,20], ids=['3','10'],
                      edges=[['9','3'],['3','10']],
                      expStarts=[10,20], expIds=['3','10'],
                      expEdges=[['3',''],['3','10']],
                      resultAllowOverlap=True, debug=True)

        self._runTest(starts=[10,20], ids=['3','10'],
                      edges=['9','424'],
                      expStarts=[10,20], expIds=['3','10'],
                      expEdges=['',''],
                      resultAllowOverlap=True, debug=True)

        self._runTest(starts=[10,20], ids=['3','10'],
                      edges=[['9','43'],['43','424']],
                      expStarts=[10,20], expIds=['3','10'],
                      expEdges=['',''],
                      resultAllowOverlap=True, debug=True)

    def testChangingEdgesLength(self):
        """
        All of the edge lists have one empty space. We can remove this and
        make the edges arrays smaller.
        :return: None
        """
        self._runTest(starts=[10,20], ids=['3','10'],
                      edges=[['3','9'],['3','4']],
                      expStarts=[10,20], expIds=['3','10'],
                      expEdges=[['3'],['3']],
                      resultAllowOverlap=True, debug=True)

        self._runTest(starts=[10,20], ids=['3','10'],
                      edges=[['3','9'],['34','4']],
                      expStarts=[10,20], expIds=['3','10'],
                      expEdges=[['3'],['']],
                      resultAllowOverlap=True, debug=True)

    def testWithWeights(self):
        """
        Check that the corresponding weights are removed as well.

        Weights are always floats. np.nan is used for padding.
        :return: None
        """
        self._runTest(starts=[10,20], ids=['3','10'], edges=['8','3'],
                      weights=[[0.33], [3.31]], expStarts=[10,20],
                      expIds=['3','10'], expEdges=['','3'],
                      expWeights=[[np.nan], [3.31]], resultAllowOverlap=True,
                      debug=True)

        self._runTest(starts=[10,20], ids=['3','10'],
                      edges=[['3','9'],['3','10']],
                      weights=[[1.,2.],[3.,4.]],
                      expStarts=[10,20], expIds=['3','10'],
                      expEdges=[['3',''],['3','10']],
                      expWeights=[[1.,np.nan],[3.,4.]],
                      resultAllowOverlap=True, debug=True)

        # Removed edge, not at the end
        self._runTest(starts=[10,20], ids=['3','10'],
                      edges=[['9','3'],['3','10']],
                      weights=[[1.,3.],[4.,10,]],
                      expStarts=[10,20], expIds=['3','10'],
                      expEdges=[['3',''],['3','10']],
                      expWeights=[[3., np.nan],[4.,10.]],
                      resultAllowOverlap=True, debug=True)

        # Change the length
        self._runTest(starts=[10,20], ids=['3','10'],
                      edges=[['3','9'],['3','4']],
                      weights=[[4.,3.3],[98.,13.4]],
                      expStarts=[10,20], expIds=['3','10'],
                      expEdges=[['3'],['3']],
                      expWeights=[[4.],[98.]],
                      resultAllowOverlap=True, debug=True)

        self._runTest(starts=[10,20], ids=['3','10'],
                      edges=[['3','9'],['34','4']],
                      weights=[[32.,4.],[23.,43.4]],
                      expStarts=[10,20], expIds=['3','10'],
                      expEdges=[['3'],['']],
                      expWeights=[[32.],[np.nan]],
                      resultAllowOverlap=True, debug=True)

    def testNewIds(self):
        """
        Test assigning a new id instead of removing the dead edge.
        :return: None
        """
        self._runTest(starts=[10,20], ids=['3','10'], edges=['8','3'],
                      newId="dead",
                      expStarts=[10,20], expIds=['3','10'],
                      expEdges=['dead','3'], debug=True,
                      resultAllowOverlap=True)

        self._runTest(starts=[10,20], ids=['3','10'],
                      edges=[['3','9'],['3','4']], newId='dead',
                      expStarts=[10,20], expIds=['3','10'],
                      expEdges=[['3','dead'],['3','dead']],
                      resultAllowOverlap=True, debug=True)

        self._runTest(starts=[10,20], ids=['3','10'],
                      edges=[['3','9'],['34','4']], newId='dead',
                      expStarts=[10,20], expIds=['3','10'],
                      expEdges=[['3','dead'],['dead','dead']],
                      resultAllowOverlap=True, debug=True)

    def atestGlobalId(self):
        """
        Test using global ids.
        :return: None
        """
        chr2 = (GenomeRegion('hg19', 'chr2', 0,
                             GenomeInfo.GENOMES['hg19']['size']['chr2']))

        t1Starts = np.array([5,15])
        t1Ends = np.array([10,20])
        t1Ids = np.array(['1','2'])
        t1Edges = np.array([])

        t2Starts = np.array([50,230])
        t2Ends = np.array([100,500])
        t2Ids = np.array(['3','4'])
        t2Edges = np.array([])

        tv1 = TrackView(self.chr1, t1Starts, t1Ends, None, None, t1Ids,
                        t1Edges, None, borderHandling='crop',
                        allowOverlaps=False, extraLists=OrderedDict())

        tv2 = TrackView(chr2, t2Starts, t2Ends, None, None, t2Ids, t2Edges,
                        None, borderHandling='crop', allowOverlaps=False,
                        extraLists=OrderedDict())

        d = OrderedDict()
        d[self.chr1] = tv1
        d[chr2] = tv2
        track = TrackContents(self.chromosomes, d)

        r = RemoveDeadLinks(track)

        result = r.calculate()
        self.assertTrue(result is not None)

        """
        self._runTest(starts=[10,20], ids=['3','10'], edges=['8','3'],
                      newId="dead",
                      expStarts=[10,20], expIds=['3','10'],
                      expEdges=['dead','3'], debug=True,
                      resultAllowOverlap=True)
        """

if __name__ == "__main__":
    unittest.main()