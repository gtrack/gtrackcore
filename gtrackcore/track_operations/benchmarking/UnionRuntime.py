

from line_profiler import LineProfiler
import time
import timeit
import sys
from collections import OrderedDict
from cStringIO import StringIO


from gtrackcore.track_operations.operations.Union import Union
from gtrackcore.track_operations.TrackContents import TrackContents

from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion

from gtrackcore.core.Api import importFile
from gtrackcore.core.Api import _trackNameExists
from gtrackcore.core.Api import listAvailableGenomes
from gtrackcore.core.Api import listAvailableTracks

from gtrackcore.track.core.Track import Track
from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track.format.TrackFormat import TrackFormat



class UnionBenchmark(object):

    def __init__(self):
        self.hg18 = list((GenomeRegion('hg18', c, 0, l)
                        for c, l in GenomeInfo.GENOMES['hg18'][
                            'size'].iteritems()))

        self._importTrack()
        self.trackA = self._createTrackContent('h4k20me1', False)
        self.trackB = self._createTrackContent('h4k20me3', False)
        self.trackC = self._createTrackContent('lk-test1', False)
        self.trackD = self._createTrackContent('lk-test2', False)

    def runUnionV(self):
        resReq = TrackFormat([], None, None, None, None, None, None, None)
        #resReq = TrackFormat(name='segments')

        u = Union(self.trackA, self.trackB)
        u.setResultTrackRequirements(resReq)

        start = timeit.default_timer()

        tc = u()

        stop = timeit.default_timer()

        print("Total runtime: Union of points: {0}".format(stop-start))
        """
        for r in tc.regions:
            print "======"
            print len(self.trackA.getTrackView(r).startsAsNumpyArray())
            print len(self.trackB.getTrackView(r).startsAsNumpyArray())
            print len(tc.getTrackView(r).startsAsNumpyArray())
            print "======"
        """

    def runUnionLP(self):
        resReq = TrackFormat([], None, None, None, None, [], None, None)
        #resReq = TrackFormat(name='segments')

        u = Union(self.trackC, self.trackD)
        u.setResultTrackRequirements(resReq)

        start = timeit.default_timer()

        tc = u()

        stop = timeit.default_timer()

        print("Total runtime: Union of Linked points: {0}".format(stop-start))


    def runUnionS(self):
        resReq = TrackFormat([], [], None, None, None, None, None, None)
        #resReq = TrackFormat(name='segments')

        u = Union(self.trackA, self.trackB)
        u.setResultTrackRequirements(resReq)

        start = timeit.default_timer()

        tc = u()

        stop = timeit.default_timer()

        print("Total runtime: Union of segments: {0}".format(stop-start))

        """
        for r in tc.regions:
            print "======"
            print len(self.trackA.getTrackView(r).startsAsNumpyArray())
            print len(self.trackB.getTrackView(r).startsAsNumpyArray())
            print len(tc.getTrackView(r).startsAsNumpyArray())
            print "======"
        """
        #for t in tc.getTrackViews():

    def _trackInGtrack(self, genome, trackName):
        """
        Add this functionality to API..
        """
        with Capturing() as output:
            listAvailableTracks(genome)

        for i in output:
            if trackName in i:
                return True

        return False

    def _createTrackContent(self, trackName, allowOverlaps):

        trackName = trackName.split(':')

        track = Track(trackName)
        track.addFormatReq(TrackFormatReq(allowOverlaps=allowOverlaps,
                                          borderHandling='crop'))

        trackViewList = OrderedDict()

        for region in self.hg18:
            trackViewList[region] = track.getTrackView(region)

        return TrackContents('hg18', trackViewList)

    def _importTrack(self):
        """
        Imports the test tracks
        """

        track1Path = "./test_tracks/segment-h4k20me1.gtrack"
        track2Path = "./test_tracks/segment-h4k20me3.gtrack"
        track3Path = "./test_tracks/LK-test1.gtrack"
        track4Path = "./test_tracks/LK-test1.gtrack"
        genome = 'hg18'

        if not self._trackInGtrack(genome, 'h4k20me1'):
            importFile(track1Path, genome, 'h4k20me1')
        else:
            print("Track already imported into gtrack")

        if not self._trackInGtrack(genome, 'h4k20me3'):
            importFile(track2Path, genome, 'h4k20me3')
        else:
            print("Track already imported into gtrack")

        if not self._trackInGtrack(genome, 'lk-test1'):
            importFile(track3Path, genome, 'lk-test1')
        else:
            print("Track already imported into gtrack")

        if not self._trackInGtrack(genome, 'lk-test2'):
            importFile(track4Path, genome, 'lk-test2')
        else:
            print("Track already imported into gtrack")

class Capturing(list):
    """
    Class used to capture the print output from the API. This should be
    fixed by adding more functionality to the API.

    From stackoverflow #16571150
    """
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        sys.stdout = self._stdout


if __name__ == '__main__':

    a = UnionBenchmark()

    a.runUnionV()
    a.runUnionLP()
    a.runUnionS()
