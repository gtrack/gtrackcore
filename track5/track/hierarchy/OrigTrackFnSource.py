import os

from track5.util.CommonFunctions import createOrigPath, extractTrackNameFromOrigPath

class OrigTrackNameSource(object):
    def __init__(self, genome, trackNameFilter, avoidLiterature=True):
        self._genome = genome
        self._trackNameFilter = trackNameFilter
        self._avoidLiterature = avoidLiterature
    
    def __iter__(self):
        return self.yielder()
    
    def yielder(self):
        #literatureTN = GenomeInfo.getPropertyTrackName(self._genome, 'literature')
        #literatureTNBase = literatureTN[:-1]
        
        basePath = createOrigPath(self._genome, self._trackNameFilter)
        for root, dirs, files in os.walk(basePath,topdown=True):
            dirsToRemove = []
            if root==basePath:
                dirsToRemove.append('Trash')
                dirsToRemove.append('Trashcan')
            
            trackName = extractTrackNameFromOrigPath(root)
            #if self._avoidLiterature and trackName == literatureTNBase:
                    #dirsToRemove.append(literatureTN[-1])

            for oneDir in dirs:
                if oneDir[0] in ['.','_','#']:
                    dirsToRemove.append(oneDir)

            for rmDir in dirsToRemove:
                if rmDir in dirs:
                    dirs.remove(rmDir)
            
            #if sum(1 for f in files if f[0] not in ['.','_','#']) == 0:
            #    continue
            
            #if any([part[0]=='.' for part in trackName]):
            #    continue

            filterLen = len(self._trackNameFilter)

            if (self._trackNameFilter != trackName[:filterLen]):
                continue
                
            yield trackName
                

