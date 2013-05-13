import numpy

from track5.track.random.RandomizedSegsTrack import RandomizedSegsTrack

class PermutedSegsAndIntersegsTrack(RandomizedSegsTrack):
    _createSegs = RandomizedSegsTrack._permuteSegs
    _createIntersegs = RandomizedSegsTrack._permuteIntersegs
