from input.core.GenomeElement import GenomeElement
from input.wrappers.GESourceWrapper import GESourceWrapper
import numpy as np


class GENumpyArrayConverter(GESourceWrapper):

    def __init__(self, geSource):
        GESourceWrapper.__init__(self, geSource)
        self._origGE = None
        self._npIter = iter([])
        self._colNames = self._geSource.getPrefixList()
        self._geIter = self._geSource.__iter__()

    def __iter__(self):
        self._origGE = None
        self._npIter = iter([])
        self._geIter = self._geSource.__iter__()
        return self

    def _iter(self):
        pass

    def next(self):
        vals = next(self._npIter, None)
        if not vals:
            self._origGE = self._geIter.next()

            self._npIter = np.nditer([getattr(self._origGE, col) for col in self._colNames])
            vals = next(self._npIter, None)

        ge = GenomeElement(genome=self._origGE.genome, chr=self._origGE.chr)
        for val, col in zip(vals, self._colNames):
            setattr(ge, col, val.item())

        return ge
