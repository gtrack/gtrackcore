__author__ = 'skh'


from gtrackcore.track_operations.tests.UnionTest import UnionTest
from gtrackcore.track.core.TrackView import TrackView
from collections import OrderedDict


def createTrackView(region, startList=None, endList=None, valList=None, strandList=None, idList=None,
                     edgesList=None, weightsList=None, extraLists=OrderedDict(), allow_overlap=False):
    """
    Small helper class
    :param region:
    :param startList:
    :param endList:
    :param valList:
    :param strandList:
    :param idList:
    :param edgesList:
    :param weightsList:
    :param extraLists:
    :param allow_overlap:
    :return:
    """
    return TrackView(region, startList, endList, valList, strandList, idList, edgesList, weightsList,
                     borderHandling='crop', allowOverlaps=allow_overlap, extraLists=extraLists)


if __name__ == '__main__':
    a  = UnionTest()
    a.main()