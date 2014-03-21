import numpy

from gtrackcore_memmap.track.random.RandomizedSegsTrack import RandomizedSegsTrack

class PermutedSegsAndIntersegsTrack(RandomizedSegsTrack):
    _createSegs = RandomizedSegsTrack._permuteSegs
    _createIntersegs = RandomizedSegsTrack._permuteIntersegs
