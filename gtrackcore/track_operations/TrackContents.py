__author__ = 'skh'

from collections import OrderedDict
from gtrackcore.track.core.TrackView import TrackView


class TrackContents(object):
    def __init__(self, genome, trackViewList):

        print trackViewList

        self.genome = genome
        print "before"
        self._trackViews = OrderedDict([(r, tv) for r, tv in trackViewList.items()])
        print "after"

    @property
    def regions(self):
        return self._trackViews.keys()

    def getTrackView(self, region):
        return self._trackViews[region]

    def firstTrackView(self):
        return self._trackViews[self._trackViews.keys()[0]]
