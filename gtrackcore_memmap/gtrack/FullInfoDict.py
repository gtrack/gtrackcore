from gtrackcore_memmap.core.LogSetup import logMessage
from gtrackcore_memmap.input.core.GenomeElementSource import GenomeElementSource
from gtrackcore_memmap.util.CustomExceptions import AbstractClassError, InvalidFormatError

class FullInfoDict(dict):
    #@takes(GenomeElementSource, tuple)
    def __init__(self, geSource, columnHeader):
        dict.__init__(self)
        
        for ge in geSource:
            self[ge] = dict([(col, getattr(ge, geSource.convertNameFromGtrack(col))) for col in columnHeader])
        
    def _extractKey(self, genomeElement):
        raise AbstractClassError
    
    def __setitem__(self, ge, value):
        key = self._extractKey(ge)
        if dict.has_key(self, key):
            value = dict.__getitem__(self, key).append(value)
        dict.__setitem__(self, key, [value])
    
    def get(self, ge):
        key = self._extractKey(ge)
        return self._handleGetItem(key, dict.get(self, key))
    
    def has_key(self, ge):
        return dict.has_key(self, self._extractKey(ge))
    
    def __delitem__(self, ge):
        dict.__delitem__(self, self._extractKey(ge))
    
    def __getitem__(self, ge):
        key = self._extractKey(ge)
        return self._handleGetItem(key, dict.__getitem__(self, key))
    
    def __contains__(self, ge):
        return dict.__contains__(self, self._extractKey(ge))
        
    def _handleGetItem(self, key, item):
        if item is not None and len(item) > 1:
            raise InvalidFormatError('Error: duplicate match on the same key, "%s"' % str(key))
        return item[0]


class IdFullInfoDict(FullInfoDict):        
    def _extractKey(self, genomeElement):
        return genomeElement.id
    
    def getKey(self, genomeElement):
        return self[self._extractKey(genomeElement)]


class TupleFullInfoDict(FullInfoDict):       
    def _extractKey(self, genomeElement):
        return (genomeElement.genome, genomeElement.chr, genomeElement.start, genomeElement.end)
        
    def getKey(self, genomeElement):
        return self[self._extractKey(genomeElement)]