import numpy
from numpy import array

from gtrackcore.core.Config import Config
from gtrackcore.track.core.Track import Track
from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track.format.TrackFormat import NeutralTrackFormatReq
from gtrackcore.util.CommonFunctions import isIter
from gtrackcore.util.CustomExceptions import AbstractClassError
from gtrackcore.util.RandomUtil import random

class RandomizedTrack(Track):
    IS_MEMOIZABLE = False

    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)
    
    def __init__(self, origTrack, origRegion, randIndex, **kwArgs ):
        self._origTrack = origTrack
        self.trackName = origTrack.trackName + ['Randomized', str(randIndex)]        
        self._origRegion = origRegion
        self._trackFormatReq = NeutralTrackFormatReq()
        self._cachedTV = None

    def _checkTrackFormat(self, origTV):
        pass
    
    def getTrackView(self, region):
        #print 'get tv for reg: ',region
        #print str(type(self._origRegion)) + " and " + str(type(region))
        if Config.USE_SLOW_DEFENSIVE_ASSERTS:
            assert (not isIter(self._origRegion) and self._origRegion  == region) or \
                    (isIter(self._origRegion) and region in self._origRegion) 
        
        #if self._cachedTV is None:
        self._origTrack.addFormatReq(self._trackFormatReq)
        origTV = self._origTrack.getTrackView(region)     
        self._checkTrackFormat(origTV)
        assert(not origTV.allowOverlaps)
        assert(origTV.borderHandling == 'crop')
        assert region == origTV.genomeAnchor
        starts, ends, vals, strands, ids, edges, weights, extras = \
            self._createRandomizedNumpyArrays(len(origTV.genomeAnchor), origTV.startsAsNumpyArray(), \
                                              origTV.endsAsNumpyArray(), origTV.valsAsNumpyArray(), \
                                              origTV.strandsAsNumpyArray(), origTV.idsAsNumpyArray(), \
                                              origTV.edgesAsNumpyArray(), origTV.weightsAsNumpyArray(), \
                                              origTV.allExtrasAsDictOfNumpyArrays(), origTV.trackFormat, region)
        
        from gtrackcore.util.CommonFunctions import getClassName
        self._cachedTV = TrackView(origTV.genomeAnchor, \
                                   (starts + origTV.genomeAnchor.start if starts is not None else None), \
                                   (ends + origTV.genomeAnchor.start if ends is not None else None), \
                                   vals, strands, ids, edges, weights, origTV.borderHandling, origTV.allowOverlaps, extraLists=extras)
        assert self._trackFormatReq.isCompatibleWith(self._cachedTV.trackFormat), 'Incompatible track-format: '\
               + str(self._trackFormatReq) + ' VS ' + str(self._cachedTV.trackFormat)
        return self._cachedTV
        
    def _createRandomizedNumpyArrays(self, binLen, starts, ends, vals, strands, ids, edges, weights, extras, origTrackFormat, region):
        raise AbstractClassError
