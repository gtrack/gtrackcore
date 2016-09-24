__author__ = 'skh'

from collections import OrderedDict
from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track_operations.exeptions.Track import TrackContentsEmptyError
from gtrackcore.track_operations.Genome import Genome


class TrackContents(object):

    def __init__(self, genome, trackViews):
        assert len(trackViews) > 0
        assert isinstance(genome, Genome)
        self._genome = genome

        # TODO: Check that the regions in genome matches the ones in the
        # orderedDict

        #self._trackViews = OrderedDict([(r, tv) for r, tv in
        # trackViewList.items()])
        self._trackViews = trackViews

        # Find and set the trackFormat
        formats = [tv.trackFormat for tv in self._trackViews.values()]
        # test = [tv.trackFormat for tv.genomeAnchor in
        #        self._trackViews.values()]
        # Assume that the TrackFormat is the same for all trackViews
        assert formats.count(formats[0]) == len(formats)
        self._trackFormat = formats[0]

    def getTrackViews(self):
        # TODO remove. Check if used and change to the property
        return self._trackViews

    @property
    def trackViews(self):
        """
        Get the TrackContents trackViews as a OrderedDict.
        Possible improvement: Make the trackContents iterable instead..

        :return: OrderedDict of trackViews.
        """
        return self._trackViews

    @property
    def trackFormat(self):
        """
        Returns the trackFormat
        :return:
        """
        return self._trackFormat

    @property
    def allowOverlaps(self):
        # TODO: Do this in a better way..

        print(self._trackViews)

        return self._trackViews.items()[0][1].allowOverlaps

    @property
    def regions(self):
        return self._trackViews.keys()

    @property
    def genome(self):
        return self._genome

    @genome.setter
    def genome(self, genome):
        self._genome = genome

    def getTrackFormat(self):
        pass
        # TODO

    def getTrackView(self, region):
        return self._trackViews[region]

    def firstTrackView(self):

        if len(self._trackViews) <= 0:
            raise TrackContentsEmptyError()

        key = self._trackViews.keys()

        try:
            a = (self._trackViews[self._trackViews.keys()[0]])
        except IndexError:
            print("Index error!")
        return self._trackViews[self._trackViews.keys()[0]]
