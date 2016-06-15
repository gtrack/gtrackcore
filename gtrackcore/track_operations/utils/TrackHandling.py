
import sys
import os
import numpy as np
import logging

from collections import OrderedDict
from cStringIO import StringIO

from gtrackcore.core.Api import importFile
from gtrackcore.core.Api import _trackNameExists
from gtrackcore.core.Api import listAvailableGenomes
from gtrackcore.core.Api import listAvailableTracks

from gtrackcore.track.core.Track import Track
from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track.format.TrackFormat import TrackFormat
from gtrackcore.track.core.TrackView import TrackView

from gtrackcore.track_operations.TrackContents import TrackContents

# *** Gtrackcore API ***

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

# *** Track handling ***

def printTrackView(tv):
    """
    Print the contents of a trackView
    :param tv:
    :return:
    """

    output = OrderedDict()

    starts = tv.getStartsAsNumpyArray()
    ends = tv.getEndsAsNUmpyArray()

    output['starts'] = starts
    output['ends'] = ends

    vals = tv.getValsAsNumpyArray()
    strands = tv.getStrandsAsNumpyArray()
    ids = tv.getIdsAsNumpyArray()
    edges = tv.getEdgesAsNumpyArray()
    weights = tv.getWeightsAsNympyArray()

    if vals != None and len(vals) > 0:
        output['vals'] = vals

    if strands != None and len(starts) > 0:
        output['strands'] = strands

    if ids != None and len(ids) > 0:
        output['ids'] = ids

    if edges != None and len(edges) > 0:
        output['edges'] = edges

    if weights != None and len(edges) > 0:
        output['weights'] = weights


def createRawResultTrackView(starts, ends, index, region, baseTrack,
                             allowOverlap):
    """

    TODO: Expand to support more track types.

    Used by operations of create a TrackView out of the result of the raw
    operation.

    This method may not be suitable for all Raw operations.

    When calculating a new track using a raw operation we sometimes want to
    keep other information than the start, ends. To make this easier we
    return the starts, end and an index corresponding to where in track A
    these values are stored.

    This method finds these values if they are defined in track A and
    returns a new TrackView object.

    :param starts: Numpy array. Starts of the new track.
    :param ends: Numpy array. Ends of the new track.
    :param index: Numpy array. Index in track A corresponding track segment
    in the result
    :param region: Genomic region of the trackView
    :param baseTrack: trackViews. Track used as basis
    :return: TrackView.
    """

    logging.debug("Creating new raw result track view")

    assert len(starts) == len(ends)

    if index is None:
        # TODO: fix for strands
        tv = TrackView(region, starts, ends, None, None, None,
                   None, None, borderHandling='crop',
                   allowOverlaps=allowOverlap)
        return tv
    else:
        assert len(ends) == len(index)

    vals = None
    strands = None
    ids = None
    edges = None
    weights = None

    resTrackIndex = slice(0,-1)
    trackIndex = index

    v = baseTrack.valsAsNumpyArray()
    if v is not None:
        vals = np.zeros(len(starts))
        vals[resTrackIndex] = v[trackIndex]

    s = baseTrack.strandsAsNumpyArray()
    if s is not None:
        strands = np.zeros(len(starts))
        strands[resTrackIndex] = s[trackIndex]

    i = baseTrack.idsAsNumpyArray()
    if i is not None:
        ids = np.zeros(len(starts))
        ids[resTrackIndex] = i[trackIndex]

    e = baseTrack.edgesAsNumpyArray()
    if e is not None:
        edges = np.zeros(len(starts))
        edges[resTrackIndex] = e[trackIndex]

    w = baseTrack.weightsAsNumpyArray()
    if w is not None:
        vals = np.zeros(len(starts))
        weights[resTrackIndex] = w[trackIndex]

    # TODO fix extras
    # TODO: Fix for other border handling then crop
    tv = TrackView(region, starts, ends, vals, strands, ids,
                   edges, weights, borderHandling='crop',
                   allowOverlaps=allowOverlap)
    return tv

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

def createTrackContentFromTrack(track, genome):
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