
import sys
import os

from collections import OrderedDict
from cStringIO import StringIO

from gtrackcore.core.Api import importFile
from gtrackcore.core.Api import _trackNameExists
from gtrackcore.core.Api import listAvailableGenomes
from gtrackcore.core.Api import listAvailableTracks

from gtrackcore.track.core.Track import Track
from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.TrackContents import TrackContents


def isTrackInGtrack(genome, trackName):
    """
    Add this functionality to API..
    """

    with Capturing() as output:
        listAvailableTracks(genome)

    for i in output:
        if trackName in i:
            return True
    return False

def importTrackIntoGTrack(trackName, genome, path):
    """
    Load a gtrack tabular file into GTrackCore.

    :param trackName:
    :param genome:
    :param path:
    :return:
    """

    if not isTrackInGtrack(genome.name, trackName):
        print("not in gtrack")
        importFile(path, genome.name, trackName)
    else:
        print("in gtrack")


def createTrackContentFromFile(genome, path, allowOverlaps):

    #trackName = trackName.split(':')
    # NOT SYSTEM safe!! Fix this later!
    trackName = path.split('/')[-1]
    trackName = trackName.split('.')[0]

    importTrackIntoGTrack(trackName, genome, path)

    track = Track(trackName.split(':'))
    track.addFormatReq(TrackFormatReq(allowOverlaps=False,
                                      borderHandling='crop'))
    trackViewList = OrderedDict()

    for region in genome.regions:

        try:
            trackViewList[region] = track.getTrackView(region)
        except OSError:
            # There can be regions that the track does not cover..
            # This is a temp fix.. should be bare of the api
            pass

    return TrackContents(genome, trackViewList)


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