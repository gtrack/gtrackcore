from track5.metadata.TrackInfo import TrackInfo
from track5.track.hierarchy.ExternalTrackManager import ExternalTrackManager
from track5.track.format.AllFormatConverters import getFormatConverters, getFormatConverterByName
from track5.track.format.TrackFormat import TrackFormatReq, NeutralTrackFormatReq, TrackFormat
from track5.track.memmap.TrackSource import TrackSource
from track5.track.memmap.TrackViewLoader import TrackViewLoader 
from track5.util.CommonFunctions import getClassName, prettyPrintTrackName
from track5.util.CustomExceptions import IncompatibleTracksError

class Track(object):
    IS_MEMOIZABLE = True
    def __new__(cls, trackName):
        if trackName == [] or trackName is None:
            return None
        else:
            if ExternalTrackManager.isVirtualTrack(trackName):
                return VirtualMinimalTrack.__new__(VirtualMinimalTrack)
            else:
                return object.__new__(cls)
    
    def __init__(self, trackName):
        self.trackName = trackName
        self._trackSource = TrackSource()
        self._trackViewLoader = TrackViewLoader()
        self._trackFormatReq = NeutralTrackFormatReq()
        self.formatConverters = None
        self._trackId = None
        
    def _getRawTrackView(self, region, borderHandling, allowOverlaps):
        trackData = self._trackSource.getTrackData(self.trackName, region.genome, region.chr, allowOverlaps)
        return self._trackViewLoader.loadTrackView(trackData, region, borderHandling, allowOverlaps, self.trackName)
    
    def getTrackView(self, region):
        allowOverlaps = self._trackFormatReq.allowOverlaps()
        borderHandling = self._trackFormatReq.borderHandling()
        assert(allowOverlaps is not None) 
        assert(borderHandling is not None) 
        
        origTrackView = self._getRawTrackView(region, borderHandling, allowOverlaps)
        
        if self.formatConverters is None:
            self.formatConverters = getFormatConverters(origTrackView.trackFormat, self._trackFormatReq)
        
        if self.formatConverters == []:
            raise IncompatibleTracksError(prettyPrintTrackName(self.trackName) + ' with format: '\
                                          + str(origTrackView.trackFormat) +
                                          ('(' + origTrackView.trackFormat._val + ')' if origTrackView.trackFormat._val else '') + \
                                          ' does not satisfy ' + str(self._trackFormatReq))
        
        if not self.formatConverters[0].canHandle(origTrackView.trackFormat, self._trackFormatReq):
            raise IncompatibleTracksError(getClassName(self.formatConverters[0]) +\
                                          ' does not support conversion from ' + str(origTrackView.trackFormat) + \
                                          ' to ' + str(self._trackFormatReq))
        return self.formatConverters[0].convert(origTrackView)

    def addFormatReq(self, requestedTrackFormat):
        prevFormatReq = self._trackFormatReq
        self._trackFormatReq = TrackFormatReq.merge(self._trackFormatReq, requestedTrackFormat)
        if self._trackFormatReq is None:
            raise IncompatibleTracksError(str(prevFormatReq ) + \
                                          ' is incompatible with additional ' + str(requestedTrackFormat))
    
    def setFormatConverter(self, converterClassName):
        assert( self.formatConverters is None )
        if converterClassName is not None:        
            self.formatConverters = [getFormatConverterByName(converterClassName)]
    
    def getUniqueKey(self, genome):
        assert self.formatConverters is not None and len(self.formatConverters) == 1, 'FC: '+str(self.formatConverters)
        assert( not None in [self._trackFormatReq.allowOverlaps(), \
                             self._trackFormatReq.borderHandling()] )
        
        if not self._trackId:
            self._trackId = TrackInfo(genome, self.trackName).id
            
        return hash((tuple(self.trackName), self._trackId, getClassName(self.formatConverters[0]), \
                     self.formatConverters[0].VERSION, self._trackFormatReq.allowOverlaps(), \
                     self._trackFormatReq.borderHandling()))

class PlainTrack(Track):
    def __new__(cls, trackName):
        if len(trackName) == 0 or trackName is None:
            return None
        else:
            if ExternalTrackManager.isVirtualTrack(trackName):
                return VirtualMinimalPlainTrack.__new__(VirtualMinimalPlainTrack)
            else:
                return object.__new__(cls)
    
    def __init__(self, trackName, **kwArgs):
        Track.__init__(self, trackName, **kwArgs)
        self.addFormatReq(TrackFormatReq(allowOverlaps=False, borderHandling='crop'))
        
    def getUniqueKey(self, genome):
        assert( not None in [self._trackFormatReq.allowOverlaps(), \
                             self._trackFormatReq.borderHandling()] )
        
        if not self._trackId:
            self._trackId = TrackInfo(genome, self.trackName).id
            
        return hash((tuple(self.trackName), self._trackId, self._trackFormatReq.allowOverlaps(), \
                     self._trackFormatReq.borderHandling()))

class VirtualMinimalTrack(Track):
    def __new__(cls):
        return object.__new__(cls)

    def _getRawTrackView(self, region, borderHandling, allowOverlaps):
        assert len(region) == 1
        
        from collections import OrderedDict
        from track5.track.memmap.CommonMemmapFunctions import findEmptyVal
        from track5.track.core.TrackView import TrackView
        import numpy as np
        
        geSource = ExternalTrackManager.getGESourceFromGalaxyOrVirtualTN(self.trackName, region.genome)
        prefixList = geSource.getPrefixList()
        valDataType = geSource.getValDataType()
        valDim = geSource.getValDim()
        weightDataType = geSource.getEdgeWeightDataType()
        weightDim = geSource.getEdgeWeightDim()

        startList, endList, valList, strandList, idList, edgesList, weightsList = [None]*7
        extraLists=OrderedDict()
        
        tf = TrackFormat.createInstanceFromPrefixList(prefixList, valDataType, valDim, \
                                                      weightDataType, weightDim)
        if allowOverlaps and (tf.isDense() or geSource.hasNoOverlappingElements()):
            raise IncompatibleTracksError(prettyPrintTrackName(self.trackName) + ' with format: '\
                                          + str(tf) + ' does not satisfy ' + str(self._trackFormatReq))
        
        denseAndInterval = tf.isDense() and tf.isInterval()
        numEls = 2 if denseAndInterval else 1
        
        if valDataType == 'S':
            valDataType = 'S2'
        if weightDataType == 'S':
            weightDataType = 'S2'
        
        for prefix in prefixList:
            if prefix == 'start':
                startList = np.array([-1], dtype='int32')
            elif prefix == 'end':
                if denseAndInterval:
                    endList = np.array([0, 1], dtype='int32')
                else:
                    endList = np.array([0], dtype='int32')
            elif prefix == 'val':
                valList = np.array([findEmptyVal(valDataType)] * valDim * numEls, \
                                   dtype=valDataType).reshape((numEls, valDim) if valDim > 1 else numEls)
            elif prefix == 'strand':
                strandList = np.array([1] * numEls, dtype='int8')
            elif prefix == 'id':
                idList = np.array([''] * numEls, dtype='S1')
            elif prefix == 'edges':
                edgesList = np.array([['']] * numEls, dtype='S1')
            elif prefix == 'weights':
                weightsList = np.array([[[findEmptyVal(weightDataType)]]] * weightDim * numEls, \
                                       dtype=weightDataType).reshape((numEls, 1, weightDim) if weightDim > 1 else (numEls, 1))
            else:
                extraLists[prefix] = np.array([''] * numEls, dtype='S1')
        
        return TrackView(region, startList, endList, valList, strandList, idList, edgesList, weightsList, borderHandling, allowOverlaps, extraLists)

class VirtualMinimalPlainTrack(VirtualMinimalTrack, PlainTrack):
    def __new__(cls):
        return object.__new__(cls)