import unittest
import numpy as np
from collections import OrderedDict

from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.operations.Merge import Merge
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.test.track_operations.TestUtils import createTrackView
from gtrackcore.test.track_operations.TestUtils import \
    createSimpleTestTrackContent


class MergeTest(unittest.TestCase):

    def setUp(self):
        self.chr1 = (GenomeRegion('hg19', 'chr1', 0,
                                  GenomeInfo.GENOMES['hg19']['size']['chr1']))
        self.chromosomes = (GenomeRegion('hg19', c, 0, l)
                            for c, l in
                            GenomeInfo.GENOMES['hg19']['size'].iteritems())

    def _runTest(self, starts=None, ends=None, strands=None, values=None,
                 ids=None, edges=None, weights=None, extras=None,
                 expStarts=None, expEnds=None,expValues=None,
                 expStrands=None, expIds=None, expEdges=None,
                 expWeights=None, expExtras=None,
                 useStrands=False, useMissingStrands=False,
                 treatMissingAsPositive=True,
                 mergeValues=True, mergeValuesFunction=None,
                 mergeLinks=True, mergeLinksFunction=None,
                 debug=False):

        track = createSimpleTestTrackContent(startList=starts, endList=ends,
                                             strandList=strands,
                                             valList=values, idList=ids,
                                             edgeList=edges,
                                             weightsList=weights)

        m = Merge(track, useStrands=useStrands,
                  useMissingStrands=useMissingStrands,
                  treatMissingAsPositive=treatMissingAsPositive,
                  mergeValues=mergeValues,
                  mergeValuesFunction=mergeValuesFunction,
                  mergeLinks=mergeLinks,
                  mergeLinksFunction=mergeLinksFunction)

        self.assertTrue((m is not None))

        result = m.calculate()

        resFound = False

        for (k, v) in result.getTrackViews().items():
            newStarts = v.startsAsNumpyArray()
            newEnds = v.endsAsNumpyArray()
            newVals = v.valsAsNumpyArray()
            newStrands = v.strandsAsNumpyArray()
            newIds = v.idsAsNumpyArray()
            newEdges = v.edgesAsNumpyArray()
            newWeights = v.weightsAsNumpyArray()
            #newExtras = v.extrasAsNumpyArray()

            if cmp(k, self.chr1) == 0:
                # All test tracks are in chr1
                if debug:
                    print(v.startsAsNumpyArray())
                    print(v.endsAsNumpyArray())
                    print(expStarts)
                    print(expEnds)
                    print("expValues: {}".format(expValues))
                    print("newValues: {}".format(v.valsAsNumpyArray()))
                    print("expIds: {}".format(expIds))
                    print("newIds: {}".format(v.idsAsNumpyArray()))
                    print("expEdges: {}".format(expEdges))
                    print("newEdges: {}".format(v.edgesAsNumpyArray()))

                resFound = True

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
                    self.assertTrue(newVals is not None)
                    self.assertTrue(np.array_equal(newVals, expValues))
                else:
                    self.assertTrue(newVals is None)

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
                if newStarts is not None:
                    self.assertEqual(newStarts, 0)
                if newEnds is not None:
                    self.assertEqual(newEnds, 0)
                if newStrands is not None:
                    self.assertEqual(newStrands, 0)
                if newVals is not None:
                    self.assertEqual(newVals, 0)
                if newIds is not None:
                    self.assertEqual(newIds, 0)
                if newEdges is not None:
                    self.assertEqual(newEdges, 0)
                if newWeights is not None:
                    self.assertEqual(newWeights, 0)
                #if newExtras is not None:
                #    self.assertEqual(newExtras, 0)

        self.assertTrue(resFound)

    # **** Points ****
    def testPoints(self):
        self._runTest(starts=[10,10], expStarts=[10])

        self._runTest(starts=[1,5,5,10,32,32,43,64],
                      expStarts=[1,5,10,32,43,64])

        # Overlap at region end
        self._runTest(starts=[1,5,5,10,32,32,40,len(self.chr1)],
                      expStarts=[1,5,10,32,40,len(self.chr1)])
        self._runTest(starts=[1,5,5,10,32,32,43,len(self.chr1),len(self.chr1)],
                      expStarts=[1,5,10,32,43,len(self.chr1)])

    def testPointsWithStrands(self):
        """
        Testing merging of strand info. Here we just combine strand
        information.
        :return:
        """
        self._runTest(starts=[10,10], strands=['+','+'], expStarts=[10],
                      expStrands=['+'])

        self._runTest(starts=[1,5,5,10], strands=['+','+','+','+'],
                      expStarts=[1,5,10], expStrands=['+','+','+'])

        self._runTest(starts=[1,5,5,10], strands=['+','-','-','+'],
                      expStarts=[1,5,10], expStrands=['+','-','+'])

        self._runTest(starts=[1,5,5,10], strands=['+','-','+','+'],
                      expStarts=[1,5,10], expStrands=['+','.','+'])

    # **** Valued Points ****
    def testValuedPoints(self):
        self._runTest(starts=[10,10], values=[2,4], expStarts=[10],
                      expValues=[4], mergeValues=True, debug=True)
        self._runTest(starts=[3,10,10,25], values=[10,2,4,90],
                      expStarts=[3,10,25], expValues=[10,4,90],
                      mergeValues=True, mergeValuesFunction=np.maximum)

        # Using a custom mergeValueFunction
        self._runTest(starts=[10,10], values=[2,4], expStarts=[10],
                      expValues=[2], mergeValues=True,
                      mergeValuesFunction=np.minimum, debug=True)
        self._runTest(starts=[3,10,10,25], values=[10,2,4,90],
                      expStarts=[3,10,25], expValues=[10,2,90],
                      mergeValues=True, mergeValuesFunction=np.minimum)

        # Multiple overlap
        self._runTest(starts=[5,10,10,10,10,14,15,15,15,15],
                      values=[8,2,2,2,4,100,6,6,6,8],
                      expStarts=[5,10,14,15],
                      expValues=[8,4,100,8], mergeValues=True,
                      debug=True)

        self._runTest(starts=[10,10,10,20,20,20], values=[2,4,2,4,4,6],
                      expStarts=[10,20],
                      expValues=[4,6], mergeValues=True, debug=True)


    # **** Linked points ****
    def testLinkedPoints(self):
        self._runTest(starts=[10,10], ids=['1','2'], edges=['2','1'],
                      expStarts=[10], expIds=['merge-1'],
                      expEdges=[['merge-1','merge-1']],
                      debug=True)

        self._runTest(starts=[10,10], ids=['2','1'], edges=['2','1'],
                      expStarts=[10], expIds=['merge-1'],
                      expEdges=[['merge-1','merge-1']],
                      debug=True)

        self._runTest(starts=[10,10,20], ids=['1','2','3'],
                      edges=['2','1','3'],
                      expStarts=[10,20], expIds=['merge-1','3'],
                      expEdges=[['merge-1','merge-1'],['3','']],
                      debug=True)

        self._runTest(starts=[10,10,15], ids=['1','2','3'],
                      edges=['2','1','3'],
                      expStarts=[10,15], expIds=['merge-1', '3'],
                      expEdges=[['merge-1','merge-1'],['3', '']],
                      debug=True)

        self._runTest(starts=[10,10,15,15], ids=['1','2','3','4'],
                      edges=['2','1','4','3'],
                      expStarts=[10,15], expIds=['merge-1', 'merge-2'],
                      expEdges=[['merge-1','merge-1'],
                                ['merge-2','merge-2']],
                      debug=True)

        self._runTest(starts=[10,10,10], ids=['1','2','3'],
                      edges=['2','3','1'],
                      expStarts=[10], expIds=['merge-1'],
                      expEdges=[['merge-1','merge-1','merge-1']],
                      debug=True)

        self._runTest(starts=[10,10,10,10], ids=['1','2','3','4'],
                      edges=['2','3','4','1'],
                      expStarts=[10], expIds=['merge-1'],
                      expEdges=[['merge-1','merge-1','merge-1','merge-1']],
                      debug=True)

        self._runTest(starts=[10,10,10,10,20,20,20,20],
                      ids=['1','2','3','4','5','6','7','8'],
                      edges=['2','3','4','1','6','7','8','5'],
                      expStarts=[10,20], expIds=['merge-1','merge-4'],
                      expEdges=[['merge-1','merge-1','merge-1','merge-1'],
                                ['merge-4','merge-4','merge-4','merge-4']],
                      debug=True)

    # **** Linked valued points ****
    def atestLinkedValuedPoints(self):
        self._runTest(starts=[10,10], ids=['1','2'], edges=['2','1'],
                      values=[10,5], expValues=[10],
                      expStarts=[10], expIds=['merge-1'],
                      expEdges=[['merge-1','merge-1']],
                      debug=True)

        self._runTest(starts=[10,10], ids=['2','1'], edges=['2','1'],
                      values=[10,5], expValues=[10],
                      expStarts=[10], expIds=['merge-1'],
                      expEdges=[['merge-1','merge-1']],
                      debug=True)

        self._runTest(starts=[10,10,20], ids=['1','2','3'],
                      edges=['2','1','3'],
                      values=[10,5,20], expValues=[10,20],
                      expStarts=[10,20], expIds=['merge-1','3'],
                      expEdges=[['merge-1','merge-1'],['3','']],
                      debug=True)

        self._runTest(starts=[10,10,15], ids=['1','2','3'],
                      edges=['2','1','3'],
                      values=[10,5,20], expValues=[10,20],
                      expStarts=[10,15], expIds=['merge-1', '3'],
                      expEdges=[['merge-1','merge-1'],['3', '']],
                      debug=True)

        self._runTest(starts=[10,10,15,15], ids=['1','2','3','4'],
                      edges=['2','1','4','3'],
                      values=[10,5,20,15], expValues=[10,20],
                      expStarts=[10,15], expIds=['merge-1', 'merge-2'],
                      expEdges=[['merge-1','merge-1'],
                                ['merge-2','merge-2']],
                      debug=True)

    def testLinkedValuedPoints(self):
        self._runTest(starts=[10,10,10], ids=['1','2','3'],
                      edges=['2','3','1'],
                      values=[10,5,20], expValues=[20],
                      expStarts=[10], expIds=['merge-1'],
                      expEdges=[['merge-1','merge-1','merge-1']],
                      debug=True)

    def daf(self):
        self._runTest(starts=[10,10,10,10], ids=['1','2','3','4'],
                      edges=['2','3','4','1'],
                      values=[10,5,20,4], expValues=[20],
                      expStarts=[10], expIds=['merge-1'],
                      expEdges=[['merge-1','merge-1','merge-1','merge-1']],
                      debug=True)

        self._runTest(starts=[10,10,10,10,20,20,20,20],
                      ids=['1','2','3','4','5','6','7','8'],
                      edges=['2','3','4','1','6','7','8','5'],
                      values=[10,5,20,4,10,15,16,4], expValues=[20,16],
                      expStarts=[10,20], expIds=['merge-1','merge-4'],
                      expEdges=[['merge-1','merge-1','merge-1','merge-1'],
                                ['merge-4','merge-4','merge-4','merge-4']],
                      debug=True)

    # **** Segments ****

    def atestSegments(self):
        self._runTest(starts=[10,20], ends=[30, 25],
                      expStarts=[10], expEnds=[30])

        self._runTest(starts=[10,10], ends=[30, 30],
                      expStarts=[10], expEnds=[30])

        # Multiple overlap
        self._runTest(starts=[10,20,40], ends=[50,25,45],
                      expStarts=[10], expEnds=[50])

        # No overlap
        self._runTest(starts=[10], ends=[50],
                      expStarts=[10], expEnds=[50])
        self._runTest(starts=[10,100], ends=[50,300],
                      expStarts=[10,100], expEnds=[50,300])

        # Total overlap
        self._runTest(starts=[10,20], ends=[25, 40],
                      expStarts=[10], expEnds=[40], debug=True)

    def testSegments(self):
        # Multiple. Partial and total
        self._runTest(starts=[10,20,35], ends=[25,40,100],
                      expStarts=[10], expEnds=[100])

    # **** Valued Segments ****

    def testValuedSegments(self):

        # No overlap
        self._runTest(starts=[10,20], ends=[15,25], values=[1,2],
                      expStarts=[10,20], expEnds=[15,25], expValues=[1,2],
                      mergeValues=True)

        # Total overlap
        self._runTest(starts=[10,20], ends=[30, 25], values=[10,20],
                      expStarts=[10], expEnds=[30], expValues=[20],
                      mergeValues=True)

        # Using a custom mergeValueFunction
        self._runTest(starts=[10,20], ends=[30, 25], values=[10,20],
                      expStarts=[10], expEnds=[30], expValues=[10],
                      mergeValues=True, mergeValuesFunction=np.minimum)

        # Multiple. Partial and total
        self._runTest(starts=[10,20,35], ends=[25,40,100], values=[10,20,30],
                      expStarts=[10], expEnds=[100], expValues=[30],
                      mergeValues=True)
        self._runTest(starts=[10,20,35], ends=[25,40,100], values=[10,20,30],
                      expStarts=[10], expEnds=[100], expValues=[10],
                      mergeValues=True, mergeValuesFunction=np.minimum)

    # **** LinkedSegments ****

    def atestLinkedSegments(self):
        self._runTest(starts=[10,20], ends=[15, 25],
                      ids=['1','2'], edges=['2','1'],
                      expIds=['1','2'], expEdges=['2','1'],
                      expStarts=[10,20], expEnds=[15,25])

        self._runTest(starts=[10,20], ends=[30, 25],
                      ids=['1','2'], edges=['2','1'],
                      expIds=['merge-1'], expEdges=[['merge-1','merge-1']],
                      expStarts=[10], expEnds=[30], debug=True)

        self._runTest(starts=[10,10], ends=[30, 30],
                      ids=['1','2'], edges=['2','1'],
                      expIds=['merge-1'], expEdges=[['merge-1','merge-1']],
                      expStarts=[10], expEnds=[30])

        # Multiple overlap
        self._runTest(starts=[10,20,40], ends=[50,25,45],
                      ids=['1','2','3'], edges=['2','3','1'],
                      expIds=['merge-2'],
                      expEdges=[['merge-2','merge-2','merge-2']],
                      expStarts=[10], expEnds=[50])

        # No overlap
        self._runTest(starts=[10], ends=[50],
                      ids=['1'], edges=['1'],
                      expIds=['1'], expEdges=['1'],
                      expStarts=[10], expEnds=[50])

        self._runTest(starts=[10,100], ends=[50,300],
                      ids=['1','2'], edges=['2','1'],
                      expIds=['1','2'], expEdges=['2','1'],
                      expStarts=[10,100], expEnds=[50,300])

        # Total overlap
        self._runTest(starts=[10,20], ends=[25, 40],
                      ids=['1','2'], edges=['2','1'],
                      expIds=['merge-1'], expEdges=[['merge-1','merge-1']],
                      expStarts=[10], expEnds=[40], debug=True)

    def atestLinkedSegments(self):
        # Multiple. Partial and total
        self._runTest(starts=[10,20,35], ends=[25,40,100],
                      ids=['1','2','3'], edges=['2','3','1'],
                      expIds=['merge-2'],
                      expEdges=[['merge-2','merge-2','merge-2']],
                      expStarts=[10], expEnds=[100])


if __name__ == "__main__":
    unittest.main()
