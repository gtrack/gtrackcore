from track5.track.format.FormatConverter import FormatConverter
#from track5.track.format.SegmentToPointFormatConverter import SegmentToStartPointFormatConverter, \
#    SegmentToMidPointFormatConverter, SegmentToEndPointFormatConverter

class JoinedFormatConverter(FormatConverter):
    _formatConverterClsList=[]
    
    def __init__(self, sourceFormat=None, reqFormat=None):
        FormatConverter.__init__(self, sourceFormat, reqFormat)
        self._formatConverters = []
        for formatConverterCls in self._formatConverterClsList:
            formatConverter = object.__new__(formatConverterCls, sourceFormat, reqFormat)
            formatConverter.__init__(sourceFormat, reqFormat)
            self._formatConverters.append(formatConverter)
        
    def convert(self, tv):
        for formatConverter in self._formatConverters:
            tv = formatConverter.convert(tv)
        return tv
    
    @classmethod
    def _canHandle(self, sourceFormat, reqFormat):
        return all([formatConverterCls._canHandle(sourceFormat, reqFormat) \
                    for formatConverterCls in self._formatConverterClsList])
    
    @classmethod
    def _getTrackFormatExceptionList(cls):
        return reduce(lambda l1,l2:l1+l2, [formatConverterCls._getTrackFormatExceptionList() \
                                           for formatConverterCls in cls._formatConverterClsList])

    @classmethod
    def getOutputDescription(self, sourceFormatName):
        return "Combined format converter (converted from '" + sourceFormatName + "')"

#class IterateUniqueValsAndSegmentToStartPointFormatConverter(JoinedFormatConverter):
#    _formatConverterClsList=[IterateUniqueValsFormatConverter, SegmentToStartPointFormatConverter]
#
#    def getOutputDescription(self, sourceFormatName):
#        return "For all categories, with the upstream end point of every segment (converted from '" + sourceFormatName + "')"
#    
#class IterateUniqueValsAndSegmentToMidPointFormatConverter(JoinedFormatConverter):
#    _formatConverterClsList=[IterateUniqueValsFormatConverter, SegmentToMidPointFormatConverter]
#
#    def getOutputDescription(self, sourceFormatName):
#        return "For all categories, with the middle point of every segment (converted from '" + sourceFormatName + "')"
#
#class IterateUniqueValsAndSegmentToEndPointFormatConverter(JoinedFormatConverter):
#    _formatConverterClsList=[IterateUniqueValsFormatConverter, SegmentToEndPointFormatConverter]
#
#    def getOutputDescription(self, sourceFormatName):
#        return "For all categories, with the downstream end point of every segment (converted from '" + sourceFormatName + "')"

