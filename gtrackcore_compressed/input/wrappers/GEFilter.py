from copy import copy

from gtrackcore_compressed.input.wrappers.GESourceWrapper import GESourceWrapper
from gtrackcore_compressed.track.format.TrackFormat import TrackFormat
from gtrackcore_compressed.util.CustomExceptions import NotSupportedError

class GEFilter(GESourceWrapper):
    def __init__(self, geSource):
        GESourceWrapper.__init__(self, geSource)
        self._geIter = None    

    def __iter__(self):
        self = copy(self)
        
        #does not support function, partitions and points:
        if (False in [attrs in self._geSource.getPrefixList() for attrs in ['start', 'end']]):
            raise NotSupportedError('Binning file must be segments. Current file format: ' + \
                                    TrackFormat.createInstanceFromPrefixList(self._geSource.getPrefixList(), \
                                                                             self._geSource.getValDataType(), \
                                                                             self._geSource.getValDim(), \
                                                                             self._geSource.getEdgeWeightDataType(), \
                                                                             self._geSource.getEdgeWeightDim()).getFormatName() )

        self._geIter = self._geSource.__iter__()
        return self

    def  __len__(self):
        return sum(1 for i in self)