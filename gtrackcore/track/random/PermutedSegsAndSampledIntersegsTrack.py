import numpy

from gtrackcore.track.random.RandomizedSegsTrack import RandomizedSegsTrack

class PermutedSegsAndSampledIntersegsTrack(RandomizedSegsTrack):
    _createSegs = RandomizedSegsTrack._permuteSegs
    
    def _createIntersegs(self, starts, ends, binLen):        
        return self._sampleIntervals(binLen - (ends.sum() - starts.sum()), len(starts)+1)
