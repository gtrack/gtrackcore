import os

from gtrackcore.track.memmap.CommonMemmapFunctions import parseMemmapFileFn
from gtrackcore.track.memmap.SmartMemmap import SmartMemmap
from gtrackcore.track.memmap.BoundingRegionShelve import BoundingRegionShelve, isBoundingRegionFileName
from gtrackcore.util.CommonFunctions import createDirPath
from input.core.HeaderShelve import isHeaderShelveFilename


class TrackData(dict):
    def __init__(self, other=None):
        if other is not None:
            dict.__init__(self, other)
        else:
            dict.__init__(self)
        
        self.boundingRegionShelve = None

class TrackSource:
    def __init__(self):
        self._chrInUse = None
        self._fileDict = {}
    
    def getTrackData(self, trackName, genome, chr, allowOverlaps, forceChrFolders=False):
        trackData = TrackData()
        
        brShelve = BoundingRegionShelve(genome, trackName, allowOverlaps)        
        if not forceChrFolders and brShelve.fileExists():
            chr = None
        
        dir = createDirPath(trackName, genome, chr, allowOverlaps)

        for fn in os.listdir(dir):
            fullFn = dir + os.sep + fn
            
            if fn[0] == '.' or os.path.isdir(fullFn):
                continue
                
            if isBoundingRegionFileName(fn):
                if fullFn not in self._fileDict:
                    self._fileDict[fullFn] = brShelve
                trackData.boundingRegionShelve = self._fileDict[fullFn]
                continue

            if not isHeaderShelveFilename(fn):
                prefix, elementDim, dtypeDim, dtype = parseMemmapFileFn(fn)
            
                assert prefix not in trackData
                trackData[prefix] = self._getFile(chr, dir, fullFn, elementDim, dtype, dtypeDim)
        
        return trackData
    
    def _getFile(self, chr, dir, fullFn, elementDim, dtype, dtypeDim):
        if chr is not None and chr != self._chrInUse:
            self._fileDict = {}
            self._chrInUse = chr
            
        if fullFn not in self._fileDict:
            self._fileDict[fullFn] = SmartMemmap(fullFn, elementDim=elementDim, dtype=dtype, dtypeDim=dtypeDim, mode='r')
        
        return self._fileDict[fullFn]        
