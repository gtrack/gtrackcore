import numpy

from gtrackcore_compressed.track.random.RandomizedSegsTrack import RandomizedSegsTrack

class PermutedSegsAndIntersegsTrack(RandomizedSegsTrack):
    _createSegs = RandomizedSegsTrack._permuteSegs
    _createIntersegs = RandomizedSegsTrack._permuteIntersegs
