import os

from gtrackcore_memmap.track.hierarchy.ProcTrackOptions import ProcTrackOptions

class ProcTrackNameSource(object):
    def __init__(self, genome, fullAccess=False): # avoidLiterature=True
        self._genome = genome
        self._fullAccess = fullAccess
        #self._avoidLiterature = avoidLiterature
    
    def __iter__(self):
        return self.yielder([])
    
    def yielder(self, curTn):
        #if self._avoidLiterature and curTn == GenomeInfo.getPropertyTrackName(self._genome, 'literature'):
        #    return
        
        for subtype in ProcTrackOptions.getSubtypes(self._genome, curTn, self._fullAccess):
            #if self._avoidLiterature and subtype == 'Literature':
            
            if subtype[0] in ['.','_']:
                continue

            newTn = curTn + [subtype]

            doBreak = False
            for subTn in self.yielder(newTn):
                yield subTn

        if ProcTrackOptions.isValidTrack(self._genome, curTn, self._fullAccess):
            yield curTn
