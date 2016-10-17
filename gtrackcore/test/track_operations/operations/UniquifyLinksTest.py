import unittest
import numpy as np

from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion

from gtrackcore.track_operations.operations.UniquifyLinks import UniquifyLinks
from gtrackcore.test.track_operations.TestUtils import \
    createSimpleTestTrackContent


class UniquifyLinksTest(unittest.TestCase):

    def setUp(self):
        self.chr1 = (GenomeRegion('hg19', 'chr1', 0,
                                  GenomeInfo.GENOMES['hg19']['size']['chr1']))
        self.chr1Small = (GenomeRegion('hg19', 'chr1', 0, 3))
        self.chromosomes = (GenomeRegion('hg19', c, 0, l)
                            for c, l in
                            GenomeInfo.GENOMES['hg19']['size'].iteritems())

    def _runTest(self, ids, edges, expIds, expEdges, starts=None,
                 ends=None, values=None, strands=None, weights=None,
                 expStarts=None, expEnds=None, expValues=None, expStrands=None,
                 expWeights=None, expExtras=None, expTrackFormatType=None,
                 trackIdentifier=None, customChrLength=None, debug=False):

        track = createSimpleTestTrackContent(startList=starts, endList=ends,
                                             valList=values,
                                             strandList=strands,
                                             idList=ids, edgeList=edges,
                                             weightsList=weights,
                                             customChrLength=customChrLength)

        u = UniquifyLinks(track, identifier=trackIdentifier, debug=debug)

        result = u.calculate()
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
                newExtras = v.allExtrasAsDictOfNumpyArrays()

                if debug:
                    print("newTrackFormatType: {}".format(v.trackFormat))
                    print("expTrackFormatType: {}".format(expTrackFormatType))
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

                if expTrackFormatType is not None:
                    self.assertTrue(v.trackFormat.getFormatName() ==
                                    expTrackFormatType)

                if expEnds is None and expStarts is not None:
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

                if expExtras is not None:
                    for key in expExtras.keys():
                        self.assertTrue(v.hasExtra(key))

                        expExtra = expExtras[key]
                        newExtra = newExtras[key]
                        self.assertTrue(np.array_equal(newExtra, expExtra))
                else:
                    self.assertTrue(len(newExtras) == 0)

            else:
                # Tests if all tracks no in chr1 have a size of 0.
                self.assertEqual(v.size, 0)

        self.assertTrue(resFound)

    def testLinkedPointsSimple(self):
        self._runTest(ids=['1'], edges=['1'], weights=[[1]],
                      starts=[1], trackIdentifier='runID42',
                      expIds=['1-runID42'], expEdges=['1-runID42'],
                      expWeights=[[1]], expStarts=[1],
                      expTrackFormatType="Linked points")

    def testLinkedPointsComplex(self):
        self._runTest(ids=['1','2'], edges=['2','1'], weights=[[1],[1]],
                      starts=[1,2], trackIdentifier='runID42',
                      expIds=['1-runID42','2-runID42'],
                      expEdges=['2-runID42', '1-runID42'],
                      expWeights=[[1],[1]], expStarts=[1,2],
                      expTrackFormatType="Linked points")

    def testLinkedPointsMultipleEdges(self):
        self._runTest(ids=['1'], edges=[['1','1']], weights=[[1,1]],
                      starts=[1], trackIdentifier='runID42',
                      expIds=['1-runID42'],
                      expEdges=[['1-runID42','1-runID42']],
                      expWeights=[[1,1]], expStarts=[1],
                      expTrackFormatType="Linked points")

    def testLinkedPointsMultipleEdgesList(self):
        self._runTest(ids=['1','2'], edges=[['2',''],['1','1']],
                      weights=[[1,1],[1,1]],
                      starts=[1,2], trackIdentifier='tag',
                      expIds=['1-tag','2-tag'],
                      expEdges=[['2-tag', ''],['1-tag','1-tag']],
                      expWeights=[[1,1],[1,1]], expStarts=[1,2],
                      expTrackFormatType="Linked points")

    def testLinkedValuedPoints(self):
        """
        Most of this is tested i the LP test. Mostly checking that adding
        columns does not change anything.
        :return:
        """
        self._runTest(ids=['1','2'], edges=['2',''], weights=[[1],[1]],
                      starts=[1,2], trackIdentifier='runID42',
                      values=[1,2], expValues=[1,2],
                      expIds=['1-runID42','2-runID42'],
                      expEdges=['2-runID42', ''],
                      expWeights=[[1],[1]], expStarts=[1,2],
                      expTrackFormatType="Linked valued points")

    def testLinkedSegments(self):
        """
        Most of this is tested i the LP test. Mostly checking that adding
        columns does not change anything.
        :return:
        """
        self._runTest(ids=['1','2'], edges=['2',''], weights=[[1],[1]],
                      starts=[1,5], ends=[3,10], trackIdentifier='runID42',
                      expEnds=[3,10],expIds=['1-runID42','2-runID42'],
                      expEdges=['2-runID42', ''],
                      expWeights=[[1],[1]], expStarts=[1,5],
                      expTrackFormatType="Linked segments")

    def testLinkedValuedSegments(self):
        """
        Most of this is tested i the LP test. Mostly checking that adding
        columns does not change anything.
        :return:
        """
        self._runTest(ids=['1','2'], edges=['2',''], weights=[[1],[1]],
                      starts=[1,5], ends=[3,10], trackIdentifier='runID42',
                      values=[1,2], expValues=[1,2], expEnds=[3,10],
                      expIds=['1-runID42','2-runID42'],
                      expEdges=['2-runID42', ''],
                      expWeights=[[1],[1]], expStarts=[1,5],
                      expTrackFormatType="Linked valued segments")

    def atestLinkedGenomePartitioning(self):
        """
        Most of this is tested i the LP test. Mostly checking that adding
        columns does not change anything.
        :return:
        """
        self._runTest(ids=['1','2'], edges=['2',''], weights=[[1],[1]],
                      ends=[1,3], trackIdentifier='runID42',
                      expEnds=[1,3], expIds=['1-runID42','2-runID42'],
                      expEdges=['2-runID42', ''], expWeights=[[1],[1]],
                      customChrLength=3, debug=True)

    def atestLinkedStepFunction(self):
        """
        Most of this is tested i the LP test. Mostly checking that adding
        columns does not change anything.
        :return:
        """
        self._runTest(ids=['1','2'], edges=['2',''], weights=[[1],[1]],
                      ends=[1,3], trackIdentifier='runID42',
                      values=[1,2], expValues=[1,2], expEnds=[1,3],
                      expIds=['1-runID42','2-runID42'],
                      expEdges=['2-runID42', ''],
                      expWeights=[[1],[1]], customChrLength=3, debug=True)

    def testLinkedFunction(self):
        """
        Most of this is tested i the LP test. Mostly checking that adding
        columns does not change anything.
        :return:
        """
        self._runTest(ids=['1','2','3'], edges=['2','',''],
                      weights=[[1],[1],[1]], trackIdentifier='runID42',
                      values=[1,2,3], expValues=[1,2,3],
                      expIds=['1-runID42','2-runID42','3-runID42'],
                      expEdges=['2-runID42', '', ''],
                      expWeights=[[1],[1],[1]], customChrLength=3,
                      expTrackFormatType="Linked function")

    def testLinkedBasePairs(self):
        """
        Most of this is tested i the LP test. Mostly checking that adding
        columns does not change anything.
        :return:
        """
        self._runTest(ids=['1','2','3'], edges=['2','3','1'],
                      weights=[[1],[1],[1]], trackIdentifier='runID42',
                      expIds=['1-runID42','2-runID42','3-runID42'],
                      expEdges=['2-runID42', '3-runID42', '1-runID42'],
                      expWeights=[[1],[1],[1]], customChrLength=3,
                      expTrackFormatType="Linked base pairs")

if __name__ == "__main__":
    unittest.main()
