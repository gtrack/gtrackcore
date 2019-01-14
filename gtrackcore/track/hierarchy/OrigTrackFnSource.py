import os

from gtrackcore.util.CommonFunctions import createOrigPath, extractTrackNameFromOrigPath

class OrigTrackNameSource(object):
    def __init__(self, genome, trackNameFilter, btrackDir, avoidLiterature=True):
        self._genome = genome
        self._trackNameFilter = trackNameFilter
        self._avoidLiterature = avoidLiterature
        self._btrackDir = btrackDir
    
    def __iter__(self):
        return self.yielder()
    
    def yielder(self):
        #literatureTN = GenomeInfo.getPropertyTrackName(self._genome, 'literature')
        #literatureTNBase = literatureTN[:-1]
        if self._btrackDir:
            basePath = os.path.join(self._btrackDir, self._trackNameFilter)
        else:
            basePath = createOrigPath(self._genome, self._trackNameFilter)
        for root, dirs, files in os.walk(basePath,topdown=True):
            dirsToRemove = []
            if root==basePath:
                dirsToRemove.append('Trash')
                dirsToRemove.append('Trashcan')

            if self._btrackDir:
                trackName = extractTrackNameFromOrigPath(root, os.path.dirname(basePath))
            else:
                trackName = extractTrackNameFromOrigPath(root)
                print "tn " + trackName
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

            # print "filter"
            # print self._trackNameFilter
            # print "name"
            # print trackName
            # print trackName[:filterLen]

            #if (self._trackNameFilter != trackName[:filterLen]):
                #continue

            if trackName:
                print "yield"
                yield trackName
                

