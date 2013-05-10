from copy import copy

from track5.input.core.GenomeElement import GenomeElement

class GenomeElementTvWrapper:
    def __init__(self, tv):
        self._tv = tv
        
    def __iter__(self):        
        self._tvIter = self._tv.__iter__()
        return copy(self)
    
    def next(self):
        trackEl = self._tvIter.next()
        ge = GenomeElement.createGeFromTrackEl(trackEl, self._tv.trackFormat)
        return ge
    
    def __len__(self):
        return len(self._tv.valsAsNumpyArray())
    
    
class FuncValTvWrapper:
    def __init__(self, tv):
        self._tv = tv
        
    def __iter__(self):        
        self._tvIter = self._tv.__iter__()
        return copy(self)
    
    def next(self):
        return self._tvIter.next().val()
    
    def __len__(self):
        return len(self._tv.valsAsNumpyArray())
    
class GenomeElementTvWrapperBpLevel:
    def __init__(self, tv):
        self._tv = tv
        
    def __iter__(self):        
        self._tvIter = self._tv.__iter__()
        self._curPos = -1
        self._curEl = None
        self._exhausted = False
        return copy(self)
    
    def next(self):
        self._curPos += 1
        if self._curPos%10e6==0:
            print '.',
            
        if self._curPos >= len(self._tv.genomeAnchor):
            raise StopIteration

        if self._exhausted:
            return None

        if self._curEl is None:
            try:
                self._curEl = self._tvIter.next()
            except StopIteration:
                self._exhausted = True
                return None
        
        if self._curPos == self._curEl.start():
            trackEl = self._curEl
            genome = self._tv.genomeAnchor.genome
            chr = self._tv.genomeAnchor.chr
            #print 'EL: ',GenomeElement(genome,chr, trackEl.start(), trackEl.end(), trackEl.val(), trackEl.strand())
            outEl = GenomeElement(genome,chr, trackEl.start(), trackEl.end(), trackEl.val(), trackEl.strand())
            self._curEl = None
            return outEl
        else:
            #print self._curPos,' AND ', self._curEl.start()
            #print 'None'
            return None
    
    def __len__(self):
        return len(self._tv.valsAsNumpyArray())