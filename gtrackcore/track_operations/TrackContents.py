__author__ = 'skh'

from collections import OrderedDict

class TrackContents(object):
    def __init__(self, genome, trackViewList):
        self.genome = genome
        self._trackViews = OrderedDict([(tv.region, tv) for tv in trackViewList])

    @property
    def regions(self):
        return self._trackViews.keys()

    def getTrackView(self, region):
        return self._trackViews[region]

    def firstTrackView(self):
        return self._trackViews[self._trackViews.keys()[0]]
