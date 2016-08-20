import unittest
import sys
import numpy as np
from collections import OrderedDict

from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.operations.ValueSelect import ValueSelect
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.test.track_operations.TestUtils import createTrackView
from gtrackcore.test.track_operations.TestUtils import \
    createSimpleTestTrackContent


class ValueSelectTest(unittest.TestCase):

    def setUp(self):
        self.chr1 = (GenomeRegion('hg19', 'chr1', 0,
                                  GenomeInfo.GENOMES['hg19']['size']['chr1']))
        self.chr1Small = (GenomeRegion('hg19', 'chr1', 0, 3))
        self.chromosomes = (GenomeRegion('hg19', c, 0, l)
                            for c, l in
                            GenomeInfo.GENOMES['hg19']['size'].iteritems())

    def _runTest(self, values, expValues, limit, starts=None, ends=None,
                 expStarts=None, expEnds=None, strands=None, ids=None,
                 edges=None, expStrands=None, expIds=None, expEdges=None,
                 compareFunction=None, customChrLength=None,
                 allowOverlap=True, debug=False):

        track = createSimpleTestTrackContent(startList=starts, endList=ends,
                                             valList=values, idList=ids,
                                             edgeList=edges,
                                             customChrLength=customChrLength)

        vs = ValueSelect(track, limit=limit, compareFunction=compareFunction,
                         allowOverlap=allowOverlap, debug=debug)

        self.assertTrue((vs is not None))
        result = vs.calculate()
        self.assertTrue(result is not None)

        resFound = False

        if len(expValues) == 0:
            resFound = True

        for (k, v) in result.getTrackViews().items():
            if cmp(k, self.chr1) == 0 or cmp(k, self.chr1Small) == 0:
                # All test tracks are in chr1
                newStarts = v.startsAsNumpyArray()
                newEnds = v.endsAsNumpyArray()
                newVals = v.valsAsNumpyArray()
                newStrands = v.strandsAsNumpyArray()
                newIds = v.idsAsNumpyArray()
                newEdges = v.edgesAsNumpyArray()

                if debug:
                    print(newStarts)
                    print(newEnds)
                    print(newVals)
                    print(expStarts)
                    print(expEnds)
                    print(expValues)
                if newStarts is not None and starts is not None:
                    self.assertTrue(np.array_equal(newStarts, expStarts))
                if newEnds is not None and ends is not None:
                    self.assertTrue(np.array_equal(newEnds, expEnds))
                if newVals is not None:
                    self.assertTrue(np.array_equal(newVals, expValues))
                else:
                    self.assertTrue(expValues is None)
                if strands is not None:
                    self.assertTrue(np.array_equal(newStrands, expStrands))
                if newIds is not None:
                    self.assertTrue(np.array_equal(newIds, expIds))
                else:
                    self.assertTrue(expIds is None)
                if newEdges is not None:
                    self.assertTrue(np.array_equal(newEdges, expEdges))
                else:
                    self.assertTrue(expEdges is None)

                resFound = True

            else:
                # Tests if all tracks no in chr1 have a size of 0.
                self.assertEqual(v.startsAsNumpyArray().size, 0)
                self.assertEqual(v.endsAsNumpyArray().size, 0)
                self.assertEqual(v.vasAsNumpyArray().size, 0)
                self.assertEqual(v.idsAsNumpyArray().size, 0)
                self.assertEqual(v.edgesAsNumpyArray().size, 0)

        self.assertTrue(resFound)

    # **** Valued points tests ****
    def testValuedPointsSimple(self):
        """
        Simple tests on valued points. Interger values
        :return: None
        """

        self._runTest(starts=[10], ends=[10], values=[10], expStarts=[10],
                      expEnds=[10], expValues=[10], limit=5, debug=True)
        self._runTest(starts=[10], ends=[10], values=[10], expStarts=[10],
                      expEnds=[10], expValues=[10], limit=10, debug=True)
        self._runTest(starts=[10], ends=[10], values=[10], expStarts=[],
                      expEnds=[], expValues=[], limit=11, debug=True)

    def testValuedPointsComplex(self):
        """
        More complex test on valued points. Integer values
        :return: None
        """

        self._runTest(starts=[10,20,30], ends=[10,20,30], values=[10,0,50],
                      expStarts=[10,30], expEnds=[10,30], expValues=[10,50],
                      limit=5, debug=True)
        self._runTest(starts=[10,20,30], ends=[10,20,30], values=[10,0,50],
                      expStarts=[10,20,30], expEnds=[10,20,30],
                      expValues=[10,0,50], limit=0, debug=True)
        self._runTest(starts=[10,20,30], ends=[10,20,30], values=[10,0,50],
                      expStarts=[], expEnds=[], expValues=[], limit=100,
                      debug=True)

    def testValuedPointsBoolean(self):
        """
        Test of valued points, with boolean values
        :return: None
        """

        self._runTest(starts=[10], ends=[10], values=[True], expStarts=[10],
                      expEnds=[10], expValues=[True], limit=True, debug=True)
        self._runTest(starts=[10], ends=[10], values=[False], expStarts=[10],
                      expEnds=[10], expValues=[False], limit=False, debug=True)
        self._runTest(starts=[10], ends=[10], values=[True], expStarts=[],
                      expEnds=[], expValues=[], limit=False, debug=True)
        self._runTest(starts=[10], ends=[10], values=[False], expStarts=[],
                      expEnds=[], expValues=[], limit=True, debug=True)
        self._runTest(starts=[10,20,50], ends=[10,20,50],
                      values=[True,False,True], expStarts=[10,50],
                      expEnds=[10,50], expValues=[True,True], limit=True,
                      debug=True)
        self._runTest(starts=[10,20,50], ends=[10,20,50],
                      values=[True,False,True], expStarts=[20], expEnds=[20],
                      expValues=[False], limit=False, debug=True)

    # **** Linked valued points tests ****
    def testLinkedValuedPoints(self):
        """
        Simple test on linked valued points.
        :return: None
        """

        self._runTest(starts=[10], ends=[10], values=[10], ids=["1"],
                      edges=[["1"]], expStarts=[10], expEnds=[10],
                      expValues=[10], expIds=["1"],
                      expEdges=[["1"]], limit=5, debug=True)

        # Test with a node with no edges
        self._runTest(starts=[10,20], ends=[10,20], values=[10,20],
                      ids=["1","2"], edges=[["2"], [np.nan]],
                      expStarts=[10,20],
                      expEnds=[10,20],
                      expValues=[10,20], expIds=["1","2"],
                      expEdges=[["2"],[np.nan]], limit=5, debug=True)

        # Remove point. This creates a dangling link...
        self._runTest(starts=[10,20], ends=[10,20], values=[10,2],
                      ids=["1","2"], edges=[["2"], ["1"]],
                      expStarts=[10], expEnds=[10], expValues=[10],
                      expIds=["1"], expEdges=[["2"]], limit=5, debug=True)

    # **** Valued segments tests ****
    def testValuedSegmentsSimple(self):
        """
        Simple test on valued segments. Integer values
        :return: None
        """

        self._runTest(starts=[10], ends=[20], values=[10], expStarts=[10],
                      expEnds=[20], expValues=[10], limit=5, debug=True)
        self._runTest(starts=[10], ends=[20], values=[10], expStarts=[10],
                      expEnds=[20], expValues=[10], limit=10, debug=True)
        self._runTest(starts=[10], ends=[20], values=[10], expStarts=[],
                      expEnds=[], expValues=[], limit=11, debug=True)

    def testValuedSegmentsComplex(self):
        """
        More complex tests on valued segments. Integer values
        :return: None
        """

        self._runTest(starts=[10,20,30], ends=[15,25,35], values=[10,0,50],
                      expStarts=[10,30], expEnds=[15,35], expValues=[10,50],
                      limit=5, debug=True)
        self._runTest(starts=[10,20,30], ends=[15,25,35], values=[10,0,50],
                      expStarts=[10,20,30], expEnds=[15,25,35],
                      expValues=[10,0,50], limit=0, debug=True)
        self._runTest(starts=[10,20,30], ends=[15,25,35], values=[10,0,50],
                      expStarts=[], expEnds=[], expValues=[], limit=100,
                      debug=True)

    # **** Linked valued segments tests ****
    def testLinkedValuedSegments(self):
        """
        Simple test on linked valued points.
        :return: None
        """

        self._runTest(starts=[10], ends=[20], values=[10], ids=["1"],
                      edges=[["1"]], expStarts=[10], expEnds=[20],
                      expValues=[10], expIds=["1"],
                      expEdges=[["1"]], limit=5, debug=True)

        # Test with a node with no edges
        self._runTest(starts=[10,20], ends=[15,25], values=[10,20],
                      ids=["1","2"], edges=[["2"], [np.nan]],
                      expStarts=[10,20],
                      expEnds=[15,25],
                      expValues=[10,20], expIds=["1","2"],
                      expEdges=[["2"],[np.nan]], limit=5, debug=True)

        # Remove point. This creates a dangling link...
        self._runTest(starts=[10,20], ends=[15,25], values=[10,2],
                      ids=["1","2"], edges=[["2"], ["1"]],
                      expStarts=[10], expEnds=[15], expValues=[10],
                      expIds=["1"], expEdges=[["2"]], limit=5, debug=True)

    # **** Step function test ****
    def testStepFunction(self):
        """
        Simple tests on step functions. Integer values
        Only doing a simple test to check that all values are returned
        correctly
        :return: None
        """

        self._runTest(ends=[10,len(self.chr1)], values=[10,10],
                      expEnds=[10,len(self.chr1)], expValues=[10,10],
                      limit=5, debug=True)

    # **** Linked step function test ****
    def testLinkedStepFunction(self):
        """
        Simple tests on linked step functions. Integer values
        Only doing a simple test to check that all values are returned
        correctly
        :return: None
        """

        self._runTest(ends=[10,len(self.chr1)], values=[10,10],
                      ids=["1","2"], edges=[["2"],["1"]], expStarts=None,
                      expEnds=[10,len(self.chr1)], expValues=[10,10],
                      expIds=["1","2"], expEdges=[["2"],["1"]], limit=5,
                      debug=True)

    # **** Function test ****

    def testFunction(self):
        # Functions only have values. One value for each BP.
        # create a simple very small test region..

        # When doing a select on a function the resulting track will be a
        # valued points track

        self._runTest(values=[10,12,11], limit=4, expValues=[10,12,11],
                      expStarts=[1,2,3], expEnds=[1,2,3],
                      debug=True, customChrLength=3)

        self._runTest(values=[2,12,11], limit=4, expValues=[12,11],
                      expStarts=[2,3], expEnds=[2,3],
                      debug=True, customChrLength=3)

    # **** Linked Function test ****
    def testLinkedFunction(self):
        # create a simple very small test region..

        # When doing a select on a linked function the resulting track will
        # be a linked valued points track

        self._runTest(values=[10,12,11], ids=["1","2","3"],
                      edges=[["2"],["1"],["3","2"]],
                      limit=4, expValues=[10,12,11],
                      expStarts=[1,2,3], expEnds=[1,2,3],
                      expIds=["1","2","3"], expEdges= [["2"],["1"],["3","2"]],
                      debug=True, customChrLength=3)

        self._runTest(values=[2,12,11], ids=["1","2","3"],
                      edges=[["2"],["1"],["3","2"]], limit=4,
                      expValues=[12,11],expStarts=[2,3], expEnds=[2,3],
                      expIds=["2","3"], expEdges= [["1"],["3","2"]],
                      debug=True, customChrLength=3)

    # **** Linked Base Pairs test ****
    # As LBS have no value, there is no point in testing

    # **** Custom compare function ****

    def isFish(self, values, limit=None):
        """
        Example of a custom compare function.
        This function need to do an element wise comparison of the numpy
        array values using the given limit.
        :param values: Values
        :param limit: The limit
        :return: An numpy index corresponding to the index in values that
        are grate then the limit.
        """
        if limit is None:
            fish = np.array(['cod', 'salmon', 'herring', 'haddock', 'mackerel',
                            'bablefish'])
        else:
            fish = limit

        mask = np.in1d(values, fish)
        index = np.where(mask)[0]
        return index

    def testCustomCompareFunction(self):
        """
        More complex test on valued points. Integer values
        :return: None
        """

        self._runTest(starts=[10], ends=[10], values=['cod'],
                      expStarts=[10], expEnds=[10], expValues=['cod'],
                      limit=None, compareFunction=self.isFish, debug=True)

        self._runTest(starts=[10,20], ends=[10,20], values=['cod','cow'],
                      expStarts=[10], expEnds=[10], expValues=['cod'],
                      limit=None, compareFunction=self.isFish, debug=True)


if __name__ == "__main__":
    unittest.main()
