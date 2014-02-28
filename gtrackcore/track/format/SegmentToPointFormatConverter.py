import numpy

from math import floor, ceil

from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track.core.VirtualNumpyArray import VirtualNumpyArray
from gtrackcore.track.format.FormatConverter import FormatConverter

class VirtualStartFromInterval(VirtualNumpyArray):
    def __init__(self, startArray, endArray, strandArray):
        VirtualNumpyArray.__init__(self)
        self._startArray = startArray
        self._endArray = endArray
        self._strandArray = strandArray
            
    #To support lazy loading, i.e. to not load the modified array in the __init__ method of TrackView
    def __len__(self):
        return len(self._startArray)
    
class VirtualStartFromIntervalStart(VirtualStartFromInterval):
    def as_numpy_array(self):
        if self._strandArray is None:
            return self._startArray
        else:
            return numpy.where(self._strandArray, self._startArray, self._endArray-1)
        
class VirtualStartFromIntervalMid(VirtualStartFromInterval):
    def as_numpy_array(self):
        return (self._endArray + self._startArray) / 2

class VirtualStartFromIntervalEnd(VirtualStartFromInterval):
    def as_numpy_array(self):
        if self._strandArray == None:
            return self._endArray - 1
        else:
            return numpy.where(self._strandArray, self._endArray-1, self._startArray)

class SegmentToPointFormatConverter(FormatConverter):
    @classmethod
    def convert(cls, tv):
        startList = cls._virtualListClass(tv._startList, tv._endList, tv._strandList)
        valList = tv._valList
        strandList = tv._strandList
        idList = tv._idList
        edgesList = tv._edgesList
        weigthsList = tv._weightsList
        extraLists = tv._extraLists
        
        if len(startList) > 0:
            sortIndexes = numpy.argsort(startList)
            startList = startList[sortIndexes]
            if valList is not None:
                valList = valList[sortIndexes]
            if strandList is not None:
                strandList = strandList[sortIndexes]
            if idList is not None:
                idList = idList[sortIndexes]
            if edgesList is not None:
                edgesList = edgesList[sortIndexes]
            if weigthsList is not None:
                weigthsList = weigthsList[sortIndexes]
            for key in extraLists:
                if extraLists[key] is not None:
                    extraLists[key] = extraLists[key][sortIndexes]
            
        newTv = TrackView(tv.genomeAnchor, startList, None, valList, strandList, idList, edgesList, weigthsList, tv.borderHandling, tv.allowOverlaps, extraLists=extraLists)
        newTv = newTv[:]
        return newTv
    
    @classmethod
    def _canHandle(cls, sourceFormat, reqFormat):
        isSegmentToPoint = sourceFormat.isInterval() and not sourceFormat.isDense() and not reqFormat.isInterval() and not reqFormat.isDense()
        return isSegmentToPoint
    
    @classmethod
    def _getTrackFormatExceptionList(cls):
        return ['interval','dense']
    
class SegmentToStartPointFormatConverter(SegmentToPointFormatConverter):
    _virtualListClass = VirtualStartFromIntervalStart
    def getOutputDescription(self, sourceFormatName):
        return "The upstream end point of every segment (converted from '" + sourceFormatName + "')"
    
class SegmentToMidPointFormatConverter(SegmentToPointFormatConverter):
    _virtualListClass = VirtualStartFromIntervalMid
    def getOutputDescription(self, sourceFormatName):
        return "The middle point of every segment (converted from '" + sourceFormatName + "')"

class SegmentToEndPointFormatConverter(SegmentToPointFormatConverter):
    _virtualListClass = VirtualStartFromIntervalEnd
    def getOutputDescription(self, sourceFormatName):
        return "The downstream end point of every segment (converted from '" + sourceFormatName + "')"
