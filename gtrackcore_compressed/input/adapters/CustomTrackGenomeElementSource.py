from copy import copy
from gtrackcore_compressed.input.core.GenomeElementSource import GenomeElementSource

class CustomTrackGenomeElementSource(GenomeElementSource):
    _hasOrigFile = False
    
    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)
        
    def __init__(self, windowSource, genome, trackName, chr, func):
        GenomeElementSource.__init__(self, None, genome=genome, trackName=trackName)
        self._windowSource = windowSource
        self._windowIter = None
        self._genomeElement.chr = chr
        self._func = func

    def __iter__(self):
        self = copy(self)
        self._windowIter = self._windowSource.__iter__()
        return self
        
    def next(self):
        nextEl = self._windowIter.next()
        self._genomeElement.val = self._func(nextEl)
        return self._genomeElement

    def getNumElements(self):
        return len(self._windowSource)
        
    def getPrefixList(self):
        return ['val']
    
    def getValDataType(self):
        return 'float64'