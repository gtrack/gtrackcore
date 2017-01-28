import unittest
import numpy as np

from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.test.track_operations.TestUtils import \
    createSimpleTestTrackContent

# Import the appropriate Operation
from gtrackcore.track_operations.operations.SomeOperation import SomeOperation

class TemplateTest(unittest.TestCase):

    def setUp(self):
        # Define some chromosomes to use

        # A small one makes it easier to test partitions ect
        self.chr1Small = (GenomeRegion('hg19', 'chr1', 0, 3))

        # Here we do most of the test on chr1
        self.chr1 = (GenomeRegion('hg19', 'chr1', 0,
                                  GenomeInfo.GENOMES['hg19']['size']['chr1']))
        self.chromosomes = (GenomeRegion('hg19', c, 0, l)
                            for c, l in
                            GenomeInfo.GENOMES['hg19']['size'].iteritems())

    def _runTest(self, starts=None, ends=None, values=None, strands=None,
                 ids=None, edges=None, weights=None, extras=None,
                 expStarts=None,expEnds=None, expValues=None, expStrands=None,
                 expIds=None, expEdges=None, expWeights=None, expExtras=None,
                 expNoResult=False, customChrLength=None, allowOverlap=True,
                 resultAllowOverlap=False,
                 someOperationOption=None, someOtherOption=None,
                 debug=False, expTrackFormatType=None):

        # gtrackcore.test.track_operations.TestUtils contains a useful methods.
        # We use one to create a simple test TrackContent
        track = createSimpleTestTrackContent(startList=starts, endList=ends,
                                             valList=values,
                                             strandList=strands,
                                             idList=ids, edgeList=edges,
                                             weightsList=weights,
                                             extraLists=extras,
                                             customChrLength=customChrLength)

        # Create the operation

        s = SomeOperation(track, someOperationOption=someOperationOption,
                          someOtherOption=someOtherOption, debug=debug)

        # Run the calculation
        self.assertTrue((s is not None))
        result = s.calculate()

        resFound = False

        for (k, v) in result.getTrackViews().items():
            if cmp(k, self.chr1) == 0 or cmp(k, self.chr1Small) == 0:
                # All test tracks are in chr1
                resFound = True

                # Get all the arrays
                newStarts = v.startsAsNumpyArray()
                newEnds = v.endsAsNumpyArray()
                newValues = v.valsAsNumpyArray()
                newStrands = v.strandsAsNumpyArray()
                newIds = v.idsAsNumpyArray()
                newEdges = v.edgesAsNumpyArray()
                newWeights = v.weightsAsNumpyArray()
                newExtras = v.allExtrasAsDictOfNumpyArrays()

                if debug:
                    # A debug print is useful to have
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
                    self.assertTrue(v.trackFormat.getFormatName() ==
                                    expTrackFormatType)

                if expEnds is None and expStarts is not None:
                    # Assuming a point type track. Creating the expected ends.
                    # We need to do this as gtrackcore create a ends array for
                    # a points track
                    expEnds = np.array(expStarts) + 1

                # Check that the different arrays are correct or empty
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

        if expNoResult:
            self.assertFalse(resFound)
        else:
            self.assertTrue(resFound)

    # We the create a test method for each thing we want to test
    def testSegments(self):
        """
        Segments, test
        :return: None
        """
        self._runTest(starts=[10], ends=[32], expStarts=[5,11],
                      expEnds=[10,16], someOtherOption=123,
                      expTrackFormatType="Segments")

    def testLinkedBasePairs(self):
        """
        LBP example, note the use of customChrLength
        :return:
        """
        self._runTest(ids=['1','2','3'], edges=['2','3','1'],
                      weights=[[1],[1],[1]], someOperationOption=True,
                      expIds=['1','2','3'], expEdges=['2', '3', 'run'],
                      customChrLength=3,
                      expTrackFormatType="Linked base pairs")

if __name__ == "__main__":
    unittest.main()
