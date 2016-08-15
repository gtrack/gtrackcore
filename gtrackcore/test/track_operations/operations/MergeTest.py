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

    def _runMergeSegmentTest(self, starts, ends, expStarts, expEnds,
                             strands=None, expStrands=None,
                             values=None, expValues=None,
                             useValues=False, valueFunction=None,
                             debug=False):

        track = createSimpleTestTrackContent(startList=starts, endList=ends,
                                             strandList=strands,
                                             valList=values)

        m = Merge(track, useValues=useValues, valueFunction=valueFunction)

        self.assertTrue((m is not None))

        result = m.calculate()

        resFound = False

        for (k, v) in result.getTrackViews().items():
            if cmp(k, self.chr1) == 0:
                # All test tracks are in chr1
                if debug:
                    print(v.startsAsNumpyArray())
                    print(v.endsAsNumpyArray())
                    print(expStarts)
                    print(expEnds)

                if strands is not None:
                    self.assertTrue(np.array_equal(v.strandsAsNumpyArray(),
                                                   expStrands))
                if values is not None:
                    if debug:
                        print("Exp values: {}".format(expValues))
                        print("Res values: {}".format(v.valsAsNumpyArray()))
                    self.assertTrue(np.array_equal(v.valsAsNumpyArray(),
                                                   expValues))

                self.assertTrue(np.array_equal(v.startsAsNumpyArray(),
                                               expStarts))
                self.assertTrue(np.array_equal(v.endsAsNumpyArray(), expEnds))
                resFound = True
                if strands is not None:
                    pass
            else:
                # Tests if all tracks no in chr1 have a size of 0.
                self.assertEqual(v.startsAsNumpyArray().size, 0)
                self.assertEqual(v.endsAsNumpyArray().size, 0)

        self.assertTrue(resFound)

    # **** Points ****

    def testMergePointsSimple(self):
        self._runMergeSegmentTest(starts=[10,10], ends=[10, 10],
                                  expStarts=[10], expEnds=[10])

    def testMergePointsComplex(self):
        self._runMergeSegmentTest(starts=[1,5,5,10,32,32,43,64],
                                  ends=[1,5,5,10,32,32,43,64],
                                  expStarts=[1,5,10,32,43,64],
                                  expEnds=[1,5,10,32,43,64])

    # **** Valued Points ****

    def testMergeValuedPointsSimpleMaximum(self):
        self._runMergeSegmentTest(starts=[10,10], ends=[10,10],
                                  expStarts=[10], expEnds=[10], values=[2,4],
                                  expValues=[4], useValues=True,
                                  valueFunction=np.maximum, debug=True)
        self._runMergeSegmentTest(starts=[3,10,10,25], ends=[3,10,10,25],
                                  expStarts=[3,10,25], expEnds=[3,10,25],
                                  values=[10,2,4,90], expValues=[10,4,90],
                                  useValues=True, valueFunction=np.maximum)

    def testMergeValuedPointsSimpleMinimum(self):
        self._runMergeSegmentTest(starts=[10,10], ends=[10,10],
                                  expStarts=[10], expEnds=[10], values=[2,4],
                                  expValues=[2], useValues=True,
                                  valueFunction=np.minimum, debug=True)
        self._runMergeSegmentTest(starts=[3,10,10,25], ends=[3,10,10,25],
                                  expStarts=[3,10,25], expEnds=[3,10,25],
                                  values=[10,2,4,90], expValues=[10,2,90],
                                  useValues=True, valueFunction=np.minimum)

    # **** Segments ****

    def testMergeSegmentsSimple(self):
        self._runMergeSegmentTest(starts=[10,20], ends=[30, 25],
                                  expStarts=[10], expEnds=[30])

    def testMergeSegmentsEqual(self):
        self._runMergeSegmentTest(starts=[10,10], ends=[30, 30],
                                  expStarts=[10], expEnds=[30])

    def testMergeSegmentsMultiple(self):
        self._runMergeSegmentTest(starts=[10,20,40], ends=[50,25,45],
                                  expStarts=[10], expEnds=[50])

    def testMergeSegmentsNoOverlap(self):
        self._runMergeSegmentTest(starts=[10], ends=[50], expStarts=[10],
                                  expEnds=[50])
        self._runMergeSegmentTest(starts=[10,100], ends=[50,300],
                                  expStarts=[10,100], expEnds=[50,300])

    def testMergeSegmentsPartialSimple(self):
        self._runMergeSegmentTest(starts=[10,20], ends=[25, 40],
                                  expStarts=[10], expEnds=[40], debug=True)

    def testMergeSegmentsPartialAndTotal(self):
        self._runMergeSegmentTest(starts=[10,20,35], ends=[25,40,100],
                                  expStarts=[10], expEnds=[100])

    # **** Valued Segments ****

    def testMergeValuedSegmentsSimple(self):
        self._runMergeSegmentTest(starts=[10,20], ends=[30, 25],
                                  values=[10,20], expStarts=[10],
                                  expEnds=[30], expValues=[20],
                                  useValues=True, valueFunction=np.maximum)


if __name__ == "__main__":
    unittest.main()
