from gtrackcore.track.core.VirtualNumpyArray import VirtualNumpyArray

class VirtualPointEnd(VirtualNumpyArray):
    def __init__(self, startArray):
        VirtualNumpyArray.__init__(self)
        self._startArray = startArray
        
    #def __getitem__(self, key):
    #    return self._startArray[key] + 1
    #
    #def __getslice__(self, i, j):
    #    return VirtualPointEnd(self._startArray[i:j])
    
    #To support lazy loading, i.e. to not load the modified array in the __init__ method of TrackView
    def __len__(self):
        return len(self._startArray)
    
    def as_numpy_array(self):
        return self._startArray + 1