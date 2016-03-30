
from gtrackcore.track_operations.Genome import Genome
from gtrackcore.track.core.GenomeRegion import GenomeRegion

class RawOperationContent(object):
    """
    Placeholder object for rawOperations input
    """

    def __init__(self, genome, region, tv=None):
        assert isinstance(genome, Genome)
        self.__genome = genome

        assert isinstance(region, GenomeRegion)
        self.__region = region

        self.__starts = None
        self.__ends = None
        self.__vals = None
        self.__strands = None
        self.__ids = None
        self.__edges = None
        self.__weights = None
        self.__extras = None

        if tv:
            self.__tv = tv
            self._createFromTrackView(tv)

    def __len__(self):
        """
        Returns the length of the arrays. Has nothing to do with the length
        of the underlying region.
        :return:
        """
        if self.__starts is not None:
            return len(self.__starts)
        elif self.__ends is not None:
            return len(self.__ends)
        else:
            return 0

    def _createFromTrackView(self, tv):
        """
        Set all the variables form a TrackView
        :param tv:
        :return:
        """
        self.__starts = tv.startsAsNumpyArray()
        self.__ends = tv.endsAsNumpyArray()
        self.__vals = tv.valsAsNumpyArray()
        self.__strands = tv.strandsAsNumpyArray()
        self.__ids = tv.idsAsNumpyArray()
        self.__edges = tv.edgesAsNumpyArray()
        self.__weights = tv.weightsAsNumpyArray()
        # Extras need key. Fixing this later
        # self.extras = tv.extrasAsNumpyArray()

    # **** Properties ****
    @property
    def genome(self):
        return self.__genome

    @genome.setter
    def genome(self, genome):
        assert isinstance(genome, Genome)
        self.__genome = genome

    @property
    def region(self):
        return self.__region

    @region.setter
    def region(self, region):
        assert isinstance(region, GenomeRegion)
        self.__region = region

    @property
    def starts(self):
        return self.__starts

    @starts.setter
    def starts(self, starts):
        self.__starts = starts

    @property
    def ends(self):
        return self.__ends

    @ends.setter
    def ends(self, ends):
        self.__ends = ends

    @property
    def vals(self):
        return self.__vals

    @vals.setter
    def vals(self, vals):
        self.__vals = vals

    @property
    def strands(self):
        return self.__starts

    @strands.setter
    def strands(self, strands):
        self.__starts = strands

    @property
    def ids(self):
        return self.__ids

    @ids.setter
    def ids(self, ids):
        self.__ids = ids

    @property
    def edges(self):
        return 1

    @edges.setter
    def edges(self, edges):
        self.__edges = edges

    @property
    def weights(self):
        return 1

    @weights.setter
    def weights(self, weights):
        self.__weights = weights

    @property
    def extras(self):
        return 1

    @extras.setter
    def extras(self, extras):
        self.__extras = extras
