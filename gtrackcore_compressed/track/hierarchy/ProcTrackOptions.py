import os

from gtrackcore_compressed.metadata.GenomeInfo import GenomeInfo
from gtrackcore_compressed.metadata.TrackInfo import TrackInfo
from gtrackcore_compressed.track.memmap.BoundingRegionShelve import isBoundingRegionFileName
from gtrackcore_compressed.util.CommonFunctions import get_dir_path

class ProcTrackOptions:
    @staticmethod
    def _getDirContents(genome, trackName):
        dirPath = get_dir_path(genome, trackName)
        return os.listdir(dirPath) if os.path.exists(dirPath) else []    
    
    @staticmethod
    def getSubtypes(genome, trackName, fullAccess=False):
        dirPath = get_dir_path(genome, trackName)
        subtypes = [fn for fn in ProcTrackOptions._getDirContents(genome, trackName) \
                    if not (fn[0] in ['.','_'] or os.path.isfile(dirPath + os.sep + fn) \
                    or GenomeInfo.isValidChr(genome, fn))]

        #fixme, just temporarily:, these dirs should start with _
        subtypes= [x for x in subtypes if not x in ['external','ucsc'] ]
        
        #if not fullAccess and not ProcTrackOptions._isLiteratureTrack(genome, trackName):
        #    subtypes = [x for x in subtypes if not TrackInfo(genome, trackName+[x]).private]

        return sorted(subtypes, key=str.lower)
    
    #@staticmethod
    #def _isLiteratureTrack(genome, trackName):
    #    return ':'.join(trackName).startswith( ':'.join(GenomeInfo.getPropertyTrackName(genome, 'literature')) )
    
    @staticmethod
    def isValidTrack(genome, trackName, fullAccess=False):
        if not TrackInfo(genome, trackName).isValid(fullAccess):
            return False
        
        for fn in ProcTrackOptions._getDirContents(genome, trackName):
            if GenomeInfo.isValidChr(genome, fn) or isBoundingRegionFileName(fn):
                return True
        return False