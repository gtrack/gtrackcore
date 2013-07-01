from gtrackcore.util.CustomExceptions import AbstractClassError

class FormatConverter(object):
    VERSION = '1.0'
    
    def __new__(cls, sourceFormat=None, reqFormat=None):
        if sourceFormat is None: #then we have explicitly created a subclass
            return object.__new__(cls)
        else:
            if cls.canHandle(sourceFormat, reqFormat):
                return object.__new__(cls)
            else:
                return None
        
    def __init__(self, sourceFormat=None, reqFormat=None):
        self._sourceFormat = sourceFormat
        self._reqFormat = reqFormat

    @classmethod
    def canHandle(cls, sourceFormat, reqFormat):
        return cls._canHandle(sourceFormat, reqFormat) and \
            reqFormat.isCompatibleWith(sourceFormat, cls._getTrackFormatExceptionList())

    @classmethod
    def _canHandle(cls, sourceFormat, reqFormat):
        raise AbstractClassError
    
    @classmethod
    def _getTrackFormatExceptionList(cls):
        return []
            
class TrivialFormatConverter(FormatConverter):
    def getOutputDescription(self, sourceFormatName):
        return "Original format ('" + sourceFormatName + "')"
    
    @classmethod
    def convert(cls, trackView):
        return trackView
    
    @classmethod
    def _canHandle(cls, sourceFormat, reqFormat):
        return True
    
    @classmethod
    def _getTrackFormatExceptionList(cls):
        return []
