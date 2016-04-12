import numpy as np
from collections import OrderedDict

from gtrackcore.track.core.TrackView import TrackView

from gtrackcore.track_operations.Genome import Genome
from gtrackcore.track_operations.TrackContents import TrackContents

"""
This file contains common methods used by the unittests.
"""


def createTrackView(region, startList=None, endList=None, valList=None,
                    strandList=None, idList=None, edgesList=None,
                    weightsList=None, extraLists=OrderedDict(),
                    allow_overlap=False):
    """
    Creates a trackview from Numpy Arrays.
    :param region: GenomeRegion of the TrackView
    :param startList: Numpy array. starts of track
    :param endList: Numpy array. ends of track
    :param valList: Numpy array. Values of track
    :param strandList: Numpy array. Strands of track
    :param idList: Numpy array. Ids of track
    :param edgesList: Numpy array. Edges of track
    :param weightsList: Numpy array. Weights of track
    :param extraLists: OrderedDict. Extra info of track
    :param allow_overlap: Boolean. Segments overlapping or not
    :return: A TrackView object
    """
    return TrackView(region, startList, endList, valList, strandList, idList, edgesList, weightsList,
                     borderHandling='crop', allowOverlaps=allow_overlap, extraLists=extraLists)


def createSimpleTestTrackContent(startList=None, endList=None, valList=None,
                           strandList=None, idList=None, edgeList=None,
                           weightsList=None, extraLists=OrderedDict(),
                           allow_overlap=False):
    """
    This method creates a simple TrackContent object used in testing of
    operations. It is simple in the we only create one track view.

    The genome is hg19 and the chromosome is chr1.

    Only in HG19 chr1
    :param startList: Numpy array. starts of track
    :param endList: Numpy array. ends of track
    :param valList: Numpy array. Values of track
    :param strandList: Numpy array. Strands of track
    :param idList: Numpy array. Ids of track
    :param edgeList: Numpy array. Edges of track
    :param weightsList: Numpy array. Weights of track
    :param extraLists: OrderedDict. Extra info of track
    :param allow_overlap: Boolean. Segments overlapping or not
    :return: TrackContent object.
    """
    # Create Genome

    # Create trackViewList

    genome = Genome('hg19', {"chr1": 249250621})
    chr1 = genome.regions[0]

    if startList:
        startList = np.array(startList)
    if endList:
        endList = np.array(endList)
    if valList:
        valList = np.array(valList)
    if strandList:
        strandList = np.array(strandList)
    if idList:
        idList = np.array(idList)
    if edgeList:
        edgesList = np.array(edgeList)
    if weightsList:
        weightsList = np.array(weightsList)

    tv = createTrackView(chr1, startList=startList, endList=endList,
                         valList=valList, strandList=strandList,
                         idList=idList, edgesList=edgeList,
                         weightsList=weightsList, extraLists=extraLists,
                         allow_overlap=allow_overlap)

    d = OrderedDict()
    d[chr1] = tv
    return TrackContents(genome, d)