import re

from copy import copy

from gtrackcore_memmap.metadata.GenomeInfo import GenomeInfo
from gtrackcore_memmap.util.CommonConstants import BINARY_MISSING_VAL

class GenomeRegion(object):
    def __init__(self, genome=None, chr=None, start=None, end=None, strand=None):
        """TODO: param types
        GenomeRegion('NCBI39','chr1',100,1000,'+')
        """
        self.genome = genome
        self.chr = chr
        self.start = start
        self.end = end
        self.strand = strand
    
    #def _fixChr(self, chr):
    #    """
    #    >>> GenomeRegion()._fixChr('chr1')
    #    'chr01'
    #    """
    #    return re.sub('chr([0-9])$', r'chr0\1', str(chr))
    
    def __cmp__(self, other):
        assert( self.validAsRegion() )
        if other is None:
            return -1
        else:
            #print [self.genome, self.chr, self.start, self.end, self.strand] , \
            #    [other.genome, other.chr, other.start, other.end, other.strand]
            return cmp([self.genome, self.chr, self.start, self.end, self.strand] , \
                [other.genome, other.chr, other.start, other.end, other.strand])

    def __len__(self):
        ''
        assert( self.validAsRegion() )
        return self.end - self.start
    
    def __hash__(self):
        ''
        assert( self.validAsRegion() )
        if self.strand == None:
            strandHash = '' #Using the None object for hashing is not safe between interpreters/machines
        else:
            strandHash = self.strand
        return (self.genome, str(self.chr), self.start, self.end, strandHash).__hash__()
    
    def __str__(self):
        """
        >>> str(GenomeRegion('hg18','chr1',100,1000,'+'))
        'chr1:101-1000 (Pos)'
        """
        assert( self.validAsRegion() )
        #self.start+1 because we want to show 1-indexed, end inclusive output
        return str(self.chr) + ':' + str(self.start+1 if self.start is not None else '') + '-' + str(self.end)\
            + ((' (Pos)' if self.strand else ' (Neg)') if self.strand not in [None, BINARY_MISSING_VAL] else '')
        
    def strWithCentromerInfo(self):
        return str(self) + (' (intersects centromere)' if GenomeInfo.regIntersectsCentromer(self) else '')
                
    def _shortenPosition(self, pos, addOne):
        if pos is None:
            return ''
        
        if pos % 1000000 == 0:
            return str(pos / 1000000) + 'm'
        
        if pos % 1000 == 0:
            return str(pos / 1000) + 'k'
            
        return str(pos+1) if addOne else str(pos)
                
    def strShort(self):
        shortStart = self._shortenPosition(self.start, addOne=True)
        shortEnd = self._shortenPosition(self.end, addOne=False)
        return str(self.chr) + ':' + shortStart + '-' + shortEnd
                
    def contains(self, region):
        'Whether this region contains another region. Does not consider strand.'
        assert( self.validAsRegion() )
        assert( region.validAsRegion() )
        
        if [self.genome, self.chr] != [region.genome, region.chr]:
            return False            

        return False if self.start > region.start or self.end < region.end else True

    def overlaps(self, region):
        'Whether this region overlaps with another region. Does not consider strand.'
        assert( self.validAsRegion() )
        assert( region.validAsRegion() )
        
        if [self.genome, self.chr] != [region.genome, region.chr]:
            return False            

        return False if self.start >= region.end or self.end <= region.start else True
        
    def touches(self, region):
        'Whether this region touches another region without overlapping. Does not consider strand.'
        assert( self.validAsRegion() )
        assert( region.validAsRegion() )
        
        if [self.genome, self.chr] != [region.genome, region.chr]:
            return False            

        return True if self.start == region.end or self.end == region.start else False
        
    def extend(self, extensionSize, ensureValidity=True):
        if extensionSize >= 0:
            self.end += extensionSize
        else:
            self.start += extensionSize
        
        if ensureValidity:
            self.start = max(0, self.start)
            self.end = min(self.end, GenomeInfo.getChrLen(self.genome, self.chr))
        
        return self
    
    def exclude(self, other):
        """
        Returns copies of self that does not overlap with other.
        leftOverlap : self(10,20), other(5,15) => [copy(15,20)]
        rightOverlap: self(10,20), other(15,25) => [copy(10,15)]
        inside      : self(10,20), other(12,17) => [copy(10,12),copy(17,20)]
        no overlap  : self(10,20), other(30,40) => [copy(10,20)]
        """
        assert( self.validAsRegion() )
        assert( other.validAsRegion() )
        
        if [self.genome, self.chr] != [other.genome, other.chr]:
            return [self]

        before, after = [copy(self) for i in range(2)]
        before.end = min(before.end, other.start)
        after.start = max(after.start, other.end)
        return [reg for reg in [before,after] if reg.end>reg.start]
        
    def validAsRegion(self):
        return True

    def getTotalBpSpan(self):
        #print 'SELF: ', self.chr, self.start, self.end
        if self.chr is None:            
            return sum( GenomeInfo.getChrLen(self.genome, chr) for chr in GenomeInfo.getExtendedChrList(self.genome))
        #elif not self.start:
            #return GenomeInfo.getChrLen(self.genome, self.chr)
        else:
            return len(self)
    
    def getAsRegSpec(self):
        return '%s:%i-%s' % (self.chr, self.start+1, self.end if str(self.end) else '')
    
    def isWholeChr(self):
        if self.genome is None or self.chr is None:
            return False
        
        return ( (self.start, self.end) == (0, GenomeInfo.getChrLen(self.genome, self.chr)) )
