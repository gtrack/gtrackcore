__author__ = 'skh'

from collections import OrderedDict
from gtrackcore.track.core.TrackView import TrackView


class TrackContents(object):

    def __init__(self, genome, trackViewList):
        self.genome = genome
        self._trackViews = OrderedDict([(r, tv) for r, tv in trackViewList.items()])

    def getTrackViews(self):
        """
        Get the TrackContents trackViews as a OrderedDict.
        Possible improvement: Make the trackContents iterable instead..

        :return: OrderedDict of trackViews.
        """
        return self._trackViews

    @property
    def regions(self):
        return self._trackViews.keys()

    def getTrackView(self, region):
        return self._trackViews[region]

    def firstTrackView(self):
        return self._trackViews[self._trackViews.keys()[0]]
