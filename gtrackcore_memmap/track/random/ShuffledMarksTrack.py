import numpy

from gtrackcore_memmap.track.random.RandomizedTrack import RandomizedTrack
from gtrackcore_memmap.util.CustomExceptions import IncompatibleTracksError

class ShuffledMarksTrack(RandomizedTrack):    
    def _checkTrackFormat(self, origTV):
        if not origTV.trackFormat.isValued():
            raise IncompatibleTracksError(str(origTV.trackFormat))
        
    def _createRandomizedNumpyArrays(self, binLen, starts, ends, vals, strands, ids, edges, weights, extras, origTrackFormat, region):
        #isPointTrack = (not origTrackFormat.isInterval())

        #if len(vals)==0:
        #    assert len(ends)==len(starts)==0
        #    return starts, (ends if not isPointTrack else None), vals, strands
            
        newVals = numpy.copy(vals)
        numpy.random.shuffle(newVals)        
        
        #return starts,(ends if not isPointTrack else None),newVals,strands
        return starts, ends, newVals, strands, ids, edges, weights, extras
    
 
