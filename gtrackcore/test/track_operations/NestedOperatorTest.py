import unittest
import numpy as np
from collections import OrderedDict

from gtrackcore.track_operations.operations.Union import Union
from gtrackcore.track_operations.operations.Flank import Flank
from gtrackcore.track_operations.operations.Expand import Expand
from gtrackcore.track_operations.operations.ValueSelect import ValueSelect


from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.test.track_operations.TestUtils import createTrackView

from gtrackcore.test.track_operations.TestUtils import \
    createSimpleTestTrackContent



class NestedOperatorTest(unittest.TestCase):
    """
    Tests if nesting of operator classes work
    """

    def setUp(self):
        self.chr1 = (GenomeRegion('hg19', 'chr1', 0, GenomeInfo.GENOMES['hg19']['size']['chr1']))
        self.chromosomes = (GenomeRegion('hg19', c, 0, l)
                            for c, l in GenomeInfo.GENOMES['hg19']['size'].iteritems())

    def _runNestedTest(self, operationObject, expStarts=None, expEnds=None,
                       expStrands=None, expValues=None, expIds=None,
                       expEdges=None, expWeights=None):
        """
        Runs a test one a operator object.

        The test expects there to only to be segments in chr1,
        All other chromosomes need to be of size zero.
        :return:
        """

        result = operationObject.calculate()

        for (k, v) in result.getTrackViews().items():
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

    def testUnionAndTrack(self):
        """
        Test if a union between another union and a track works.
        :return: None
        """
        track1 = createSimpleTestTrackContent(startList=[2], endList=[4])
        track2 = createSimpleTestTrackContent(startList=[6], endList=[8])
        track3 = createSimpleTestTrackContent(startList=[10], endList=[12])

        u1 = Union(track1, track2)
        u2 = Union(u1, track3)

        self._runNestedTest(u2, expStarts=[2, 6, 10], expEnds=[4, 8, 12])

    def testUnionAndUnion(self):
        """
        Test if a union between another union and a track works.
        :return: None
        """
        track1 = createSimpleTestTrackContent(startList=[2], endList=[4])
        track2 = createSimpleTestTrackContent(startList=[6], endList=[8])
        track3 = createSimpleTestTrackContent(startList=[10], endList=[12])
        track4 = createSimpleTestTrackContent(startList=[14], endList=[16])

        u1 = Union(track1, track2)
        u2 = Union(track3, track4)
        u3 = Union(u1, u2)

        self._runNestedTest(u3, expStarts=[2, 6, 10, 14],
                            expEnds=[4, 8, 12, 16])

    def testExpandAndUnion(self):

        track1 = createSimpleTestTrackContent(startList=[10], endList=[15])

        track2 = createSimpleTestTrackContent(startList=[18], endList=[30])

        s = Expand(track1, downstream=5, useStrands=False, debug=True)

        u = Union(s, track2, debug=True)

        self._runNestedTest(u, expStarts=[5,18], expEnds=[10,30])



if __name__ == "__main__":
    unittest.main()
