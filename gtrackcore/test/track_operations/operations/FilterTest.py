import unittest
import numpy as np

from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion

from gtrackcore.track_operations.operations.Filter import Filter
from gtrackcore.test.track_operations.TestUtils import \
    createSimpleTestTrackContent


class FilterTest(unittest.TestCase):

    def setUp(self):
        self.chr1 = (GenomeRegion('hg19', 'chr1', 0,
                                  GenomeInfo.GENOMES['hg19']['size']['chr1']))
        self.chr1Small = (GenomeRegion('hg19', 'chr1', 0, 10))
        self.chromosomes = (GenomeRegion('hg19', c, 0, l)
                            for c, l in
                            GenomeInfo.GENOMES['hg19']['size'].iteritems())

    def _runTest(self, starts=None, ends=None, values=None, strands=None,
                 ids=None, edges=None, weights=None, expStarts=None,
                 expEnds=None, expValues=None, expStrands=None, expIds=None,
                 expEdges=None, expWeights=None, customChrLength=None,
                 removeStrands=False, removeValues=False, removeIds=False,
                 removeEdges=False, removeWeights=False, removeExtras=False,
                 debug=False, expTrackFormatType=None):

        track = createSimpleTestTrackContent(startList=starts, endList=ends,
                                             valList=values,
                                             strandList=strands,
                                             idList=ids, edgeList=edges,
                                             weightsList=weights,
                                             customChrLength=customChrLength)

        f = Filter(track, removeStrands=removeStrands,
                   removeValues=removeValues, removeIds=removeIds,
                   removeEdges=removeEdges, removeWeights=removeWeights,
                   removeExtras=removeExtras, debug=debug)

        result = f.calculate()
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

                if expTrackFormatType is not None:
                    # Check that the track is of the expected type.
                    print(expTrackFormatType)
                    print(v.trackFormat.getFormatName())
                    self.assertTrue(v.trackFormat.getFormatName() ==
                                    expTrackFormatType)

                if expEnds is None:
                    # Assuming a point type track. Creating the expected ends.
                    expEnds = np.array(expStarts) + 1


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

    def testValuedPointsToPoints(self):
        """
        Test removing values from valued points
        :return:
        """
        self._runTest(starts=[1,2], values=[3,4], removeValues=True,
                      expStarts=[1,2], expTrackFormatType="Points")

    def testLinkedPointsToPoints(self):
        """
        Removing all links by removing the ids
        :return:
        """
        self._runTest(starts=[1,2], ids=['1','2'], edges=['2','1'],
                      removeIds=True, expStarts=[1,2],
                      expTrackFormatType="Points")

    def testLinkedPointsRemoveEdges(self):
        """
        Removing all edges.
        :return:
        """
        self._runTest(starts=[1,2], ids=['1','2'], edges=['2','1'],
                      removeEdges=True, expStarts=[1,2], expIds=['1','2'],
                      expTrackFormatType="Points")

    def testLinkedValuedPointsToValuedPoints(self):
        """
        Removing both links keeping values
        :return:
        """
        self._runTest(starts=[1,2], ids=['1','2'], edges=['2','1'],
                      values=[3,4], removeIds=True,
                      expStarts=[1,2], expValues=[3,4],
                      expTrackFormatType="Valued points")

    def testLinkedValuedPointsToPoints(self):
        """
        Removing both links and values
        :return:
        """
        self._runTest(starts=[1,2], ids=['1','2'], edges=['2','1'],
                      values=[3,4], removeIds=True, removeValues=True,
                      expStarts=[1,2], expTrackFormatType="Points")

    def testRemovingWeightsFromLinkedPoints(self):
        """
        Removing both links and values
        :return:
        """
        self._runTest(starts=[1,2], ids=['1','2'], edges=['2','1'],
                      weights=[[4],[5]], removeWeights=True, expStarts=[1,2],
                      expIds=['1','2'], expEdges=['2','1'],
                      expTrackFormatType="Linked points")

    def testRemovingStrandsFromPoints(self):
        """
        Remove strands
        :return:
        """
        self._runTest(starts=[1,2], strands=['+','.'], removeStrands=True,
                      expStarts=[1,2], expTrackFormatType="Points")

    def testRemoveValuesMissing(self):
        """
        Try to remove values from a track without values. Expect to get the
        same track in return
        :return:
        """
        self._runTest(starts=[1,2], removeValues=True,
                      expStarts=[1,2], expTrackFormatType="Points")

    def testRemoveStrandsMissing(self):
        """
        Try to remove strands from a track without strands. Expect to get the
        same track in return
        :return:
        """
        self._runTest(starts=[1,2], removeValues=True,
                      expStarts=[1,2], expTrackFormatType="Points")

    def testRemoveIdsMissing(self):
        """
        Try to remove ids from a track without ids. Expect to get the
        same track in return
        :return:
        """
        self._runTest(starts=[1,2], removeIds=True,
                      expStarts=[1,2], expTrackFormatType="Points")

    def testRemoveEdgesMissing(self):
        """
        Try to remove edges from a track without edges. Expect to get the
        same track in return
        :return:
        """
        self._runTest(starts=[1,2], removeEdges=True,
                      expStarts=[1,2], expTrackFormatType="Points")

    def testRemoveWeightsMissing(self):
        """
        Try to remove weights from a track without weights. Expect to get the
        same track in return
        :return:
        """
        self._runTest(starts=[1,2], removeWeights=True,
                      expStarts=[1,2], expTrackFormatType="Points")

    # **** Segments ****
    def testValuedSegmentsToSegments(self):
        """
        Test removing values from valued segments
        :return:
        """
        self._runTest(starts=[1,10], ends=[5,15], values=[3,4],
                      removeValues=True, expStarts=[1,10], expEnds=[5,15],
                      expTrackFormatType="Segments")

    def testLinkedSegmentsToSegments(self):
        """
        Removing all links by removing the ids
        :return:
        """
        self._runTest(starts=[1,10], ends=[5,15], ids=['1','2'],
                      edges=['2','1'], removeIds=True, expStarts=[1,10],
                      expEnds=[5,15], expTrackFormatType="Segments")

    def testLinkedValuedSegmentsToValuedSegments(self):
        """
        Removing both links keeping values
        :return:
        """
        self._runTest(starts=[1,10], ends=[5,15], ids=['1','2'],
                      edges=['2','1'], values=[3,4], removeIds=True,
                      expStarts=[1,10], expEnds=[5,15], expValues=[3,4],
                      expTrackFormatType="Valued segments")

    def testLinkedValuedSegmentToSegments(self):
        """
        Removing both links and values
        :return:
        """
        self._runTest(starts=[1,10], ends=[5,15], ids=['1','2'],
                      edges=['2','1'], values=[3,4], removeIds=True,
                      removeValues=True, expStarts=[1,10], expEnds=[5,15],
                      expTrackFormatType="Segments")

if __name__ == "__main__":
    unittest.main()
