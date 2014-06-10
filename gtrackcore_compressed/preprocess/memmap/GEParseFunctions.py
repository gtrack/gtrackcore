from gtrackcore_compressed.input.core.GenomeElement import GenomeElement
    
def getStart(ge):
    return ge.start

def getEnd(ge):
    return ge.end

def getVal(ge):
    return ge.val

def getStrand(ge):
    return ge.strand

def getId(ge):
    return ge.id
    
def getEdges(ge):
    return ge.edges
    
def getWeights(ge):
    return ge.weights
    
def getNone(ge):
    return None

class GetExtra:
    def __init__(self, prefix):
        self._prefix = prefix
        
    def parse(self, ge):
        if self._prefix == 'extra':
            return ge.extra['extra']
        return getattr(ge, self._prefix)

def writeNoSlice(mmap, index, ge, parseFunc):
    mmap[index] = parseFunc(ge)

def writeSliceFromFront(mmap, index, ge, parseFunc):
    geLen = sum(1 for x in parseFunc(ge))
    if geLen >= 1:
        mmap[index][:geLen] = parseFunc(ge)
