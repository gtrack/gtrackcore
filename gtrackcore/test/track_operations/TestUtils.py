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
                           allow_overlap=False, customChrLength=None):
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
    # TODO, not working..

    if customChrLength is not None:
        # We use a custom length when testing F, LF and LBP.
        genome = Genome('hg19', {"chr1": customChrLength})
    else:
        genome = Genome('hg19', {"chr1": 249250621})
    chr1 = genome.regions[0]

    if startList is not None:
        startList = np.array(startList)
    if endList is not None:
        endList = np.array(endList)
    if valList is not None:
        valList = np.array(valList)
    if strandList is not None:
        strandList = np.array(strandList)
    if idList is not None:
        idList = np.array(idList)
    if edgeList is not None:
        #edgeList = [np.array(x, dtype=object) for x in edgeList]
        # remove object and add padding.
        edgeList = np.array(edgeList, dtype=object)
    if weightsList is not None:
        weightsList = np.array(weightsList)
    if extraLists is None:
        extraLists = OrderedDict()

    tv = createTrackView(chr1, startList=startList, endList=endList,
                         valList=valList, strandList=strandList,
                         idList=idList, edgesList=edgeList,
                         weightsList=weightsList, extraLists=extraLists,
                         allow_overlap=allow_overlap)

    d = OrderedDict()
    d[chr1] = tv
    return TrackContents(genome, d)
