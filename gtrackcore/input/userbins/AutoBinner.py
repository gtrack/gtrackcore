from gtrackcore.metadata.GenomeInfo import GenomeInfo 
from gtrackcore.track.core.GenomeRegion import GenomeRegion

class AutoBinner(object):
    def __init__(self, userBinSource, binLen, genome=None):
        #binLen of -1 gives whole chromosomes as bins
        self.genome = userBinSource.genome if hasattr(userBinSource, 'genome') else genome
        
        self._userBinSource = userBinSource
        self._binLen = binLen

    def __iter__(self):
        return self.nextBin()
    
    def nextBin(self):
        for region in self._userBinSource:
            start = region.start if region.start is not None else 0

            chrLen = GenomeInfo.getChrLen(region.genome, region.chr) if region.genome is not None else None
            regEnd = min([x for x in [region.end, chrLen] if x is not None])
            
            if self._binLen is None:
                yield GenomeRegion(region.genome, region.chr, start, regEnd)
            else:
                while start < regEnd:
                    end = min(start + self._binLen, regEnd)
                    yield GenomeRegion(region.genome, region.chr, start, end)
                    start += self._binLen

    def __len__(self):
        return sum(1 for bin in self)        