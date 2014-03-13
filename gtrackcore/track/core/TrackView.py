import weakref
from collections import OrderedDict
from copy import copy

import numpy

from gtrackcore.track.core.VirtualPointEnd import VirtualPointEnd
from gtrackcore.track.format.TrackFormat import TrackFormat
from gtrackcore.track.pytables.CommonFunctions import get_start_and_end_indices
from gtrackcore.track.pytables.DatabaseHandler import TrackTableReader
from gtrackcore.track.pytables.VirtualTrackColumn import VirtualTrackColumn
from gtrackcore.util.CustomExceptions import ShouldNotOccurError
from gtrackcore.util.pytables.DatabaseQueries import BoundingRegionQueries


numpy.seterr(all='raise', under='ignore', invalid='ignore')

def noneFunc():
    return None


class TrackElement(object):
    def __init__(self, trackView, index=-1):
        # Weak proxy is used to remove memory leak caused by circular reference when TrackView is deleted
        self._trackView = weakref.proxy(trackView)
        self._index = index
        
    def start(self):
        candidate = self._trackView._startList[self._index] - self._trackView.genomeAnchor.start
        return candidate if candidate > 0 else 0

    def end(self):
        rawEnd = self._trackView._endList[self._index]
        anchorEnd = self._trackView.genomeAnchor.end
        return (rawEnd if rawEnd<anchorEnd else anchorEnd) - self._trackView.genomeAnchor.start
    
    def val(self):
        return self._trackView._valList[self._index]

    def strand(self):
        return self._trackView._strandList[self._index]

    def id(self):
        return self._trackView._idList[self._index]

    def edges(self):
        return self._trackView._edgesList[self._index]

    def weights(self):
        return self._trackView._weightsList[self._index]

    def getAllExtraKeysInOrder(self):
        return self._trackView._extraLists.keys()

    def __getattr__(self, key):
        if key in self._trackView._extraLists:
            def extra():
                return self._trackView._extraLists[key][self._index]
            return extra
        else:
            raise AttributeError

    def none(self):
        return None
    
    def __len__(self):
        length = self.end() - self.start()
        assert(length >= 0)
        return length

class PytablesTrackElement(object):
    """
    TrackElements are relative to genome_anchor.start
    """
    def __init__(self, trackView):
        # Weak proxy is used to remove memory leak caused by circular reference when TrackView is deleted
        self._trackView = weakref.proxy(trackView)
        self._row = None
        self._prev_row = None

    def start(self):
        candidate = self._row['start'] - self._trackView.genomeAnchor.start
        return candidate if candidate > 0 else 0

    def end(self):
        raw_end = self._row['end']
        anchor_end = self._trackView.genomeAnchor.end

        if raw_end < anchor_end:
            end_relative_to_anchor_start = raw_end - self._trackView.genomeAnchor.start
        else:
            end_relative_to_anchor_start = anchor_end - self._trackView.genomeAnchor.start

        return end_relative_to_anchor_start

    def val(self):
        return self._row['val']

    def strand(self):
        return self._row['strand']

    def id(self):
        return self._row['id']

    def edges(self):
        return self._row['edges']

    def weights(self):
        return self._row['weights']

    def getAllExtraKeysInOrder(self):
        return self._trackView._extraLists.keys()

    def __getattr__(self, key):
        if key in self._trackView._extraLists:
            def extra():
                return self._row[key]
            return extra
        else:
            raise AttributeError

    def __len__(self):
        length = self.end() - self.start()
        assert(length >= 0)
        return length

    def none(self):
        return None

    def points_end_func(self):
        return self._row['start'] + 1

    def partition_start_func(self):
        return self._prev_row['end']


class AutonomousTrackElement(TrackElement):
    def __init__(self, start = None, end = None, val = None, strand = None, id = None, edges = None, weights = None, trackEl=None, **kwArgs):
        
        if trackEl is None:
            self._start = start
            self._end = end
            self._val = val
            self._strand = strand
            self._id = id
            self._edges = edges
            self._weights = weights
            self._orderedExtraKeys = []
            self._extra = {}
            for kw in kwArgs:
                self._orderedExtraKeys.append(kw)
                self._extra[kw] = kwArgs[kw]
        else:
            assert all(el is None for el in [start,end,val,strand,id,edges,weights]) and len(kwArgs) == 0
            self._start = trackEl.start()
            self._end = trackEl.end()
            self._val = trackEl.val()
            self._strand = trackEl.strand()
            self._id = trackEl.id()
            self._edges = trackEl.edges()
            self._weights = trackEl.weights()
            self._orderedExtraKeys = trackEl.getAllExtraKeysInOrder()
            self._extra = dict([(key, getattr(trackEl, key)()) for key in self._orderedExtraKeys])
            
    def start(self):
        return self._start

    def end(self):
        return self._end
    
    def val(self):
        return self._val

    def strand(self):
        return self._strand

    def id(self):
        return self._id

    def edges(self):
        return self._edges

    def weights(self):
        return self._weights

    def getAllExtraKeysInOrder(self):
        return self._orderedExtraKeys

    def __getattr__(self, key):
        try:
            def extra():
                return self.__dict__['_extra'][key]
            return extra
        except KeyError:
            raise AttributeError
    
class TrackView(object):

    def _handlePointsAndPartitions(self):
        if self._is_partition_track():
            self._startList = self._endList[:-1]
            self._endList = self._endList[1:]
            if self._valList != None:
                self._valList = self._valList[1:]
            if self._strandList != None:
                self._strandList = self._strandList[1:]
            if self._idList != None:
                self._idList = self._idList[1:]
            if self._edgesList != None:
                self._edgesList = self._edgesList[1:]
            if self._weightsList != None:
                self._weightsList = self._weightsList[1:]
            for key, extraList in self._extraLists.items():
                if extraList != None:
                    self._extraLists[key] = extraList[1:]

        elif self._is_points_track():
            self._endList = VirtualPointEnd(self._startList)

    def _handle_points_and_partitions_for_pytables(self):
        if self._is_partition_track():
            self._pytables_track_element.start = self._pytables_track_element.partition_start_func  # iteration

            self._startList = copy(self._endList)
            self._startList.update_offset(stop=-1)
            self._endList.update_offset(start=1)
            if self._valList is not None:
                self._valList.update_offset(start=1)
            if self._strandList is not None:
                self._strandList.update_offset(start=1)
            if self._idList is not None:
                self._idList.update_offset(start=1)
            if self._edgesList is not None:
                self._edgesList.update_offset(start=1)
            if self._weightsList is not None:
                self._weightsList.update_offset(start=1)
            for extraList in self._extraLists.values():
                if extraList is not None:
                    extraList.update_offset(start=1)

        elif self._is_points_track():
            self._pytables_track_element.end = self._pytables_track_element.points_end_func  # iteration

            self._endList = copy(self._startList)
            self._endList.as_numpy_array = self._endList.ends_as_numpy_array_points_func

    def _is_partition_track(self):
        return self.trackFormat.isDense() and not self.trackFormat.reprIsDense()

    def _is_points_track(self):
        return not self.trackFormat.isDense() and not self.trackFormat.isInterval()

    def __init__(self, genomeAnchor, startList, endList, valList, strandList, idList, edgesList, \
                 weightsList, borderHandling, allowOverlaps, extraLists=OrderedDict(), track_name=None):
        assert startList is not None or endList is not None or valList is not None or edgesList is not None
        assert borderHandling in ['crop']

        self._track_name = track_name
        self.genomeAnchor = copy(genomeAnchor)
        self.trackFormat = TrackFormat(startList, endList, valList, strandList, idList, edgesList, weightsList, extraLists)
        self.borderHandling = borderHandling
        self.allowOverlaps = allowOverlaps
        self._should_use_pytables = all([isinstance(l, VirtualTrackColumn)
                                         for l in [startList, endList, valList, edgesList] if l is not None])

        self._trackElement = TrackElement(self)
        self._pytables_track_element = PytablesTrackElement(self)  # For iterating pytables track table

        #self._bpLevelArray = None

        self._startList = startList
        self._endList = endList
        self._valList = valList
        self._strandList = strandList
        self._idList = idList
        self._edgesList = edgesList
        self._weightsList = weightsList
        self._extraLists = copy(extraLists)

        if not self._should_use_pytables:
            self._handlePointsAndPartitions()

        if self._startList is None:
            self._trackElement.start = noneFunc
            self._pytables_track_element.start = noneFunc
        if self._endList is None:
            self._trackElement.end = noneFunc
            self._pytables_track_element.end = noneFunc
        if self._valList is None:
            self._trackElement.val = noneFunc
            self._pytables_track_element.val = noneFunc
        if self._strandList is None:
            self._trackElement.strand = noneFunc
            self._pytables_track_element.strand = noneFunc
        if self._idList is None:
            self._trackElement.id = noneFunc
            self._pytables_track_element.id = noneFunc
        if self._edgesList is None:
            self._trackElement.edges = noneFunc
            self._pytables_track_element.edges = noneFunc
        if self._weightsList is None:
            self._trackElement.weights = noneFunc
            self._pytables_track_element.weights = noneFunc

        if self._should_use_pytables:
            self._db_handler = TrackTableReader(genomeAnchor.genome, track_name, allowOverlaps)
            self._handle_points_and_partitions_for_pytables()

        self._updateNumListElements()

        for i, list in enumerate([self._startList, self._endList, self._valList, self._strandList, self._idList, self._edgesList, self._weightsList] \
            + [extraList for extraList in self._extraLists.values()]):
                assert list is None or len(list) == self._numListElements, 'List (%s): ' % i + str(list) + ' (expected %s elements, found %s)' % (self._numListElements, len(list))

    def _generate_pytables_track_elements(self):
        start_index, end_index = get_start_and_end_indices(self.genomeAnchor, self._track_name, self.allowOverlaps, self.trackFormat)

        if start_index == end_index:
            return

        with self._db_handler as table_reader:
            track_table = table_reader.table

            rows = track_table.iterrows(start=start_index, stop=end_index)

            if self._is_partition_track():
                self._pytables_track_element._row = rows.next()

            for row in rows:
                #  Remove blind passengers
                if self.allowOverlaps and not self.trackFormat.reprIsDense():
                    if 'end' in track_table.colnames and (row['end'] <= self.genomeAnchor.start):
                        continue
                self._pytables_track_element._prev_row = self._pytables_track_element._row
                self._pytables_track_element._row = row
                yield self._pytables_track_element

    def __iter__(self):
        if self._should_use_pytables:
            self._pytables_track_element._row = None
            return self._generate_pytables_track_elements()
        else:
            self._trackElement._index = -1
            return self
    
    def _updateNumListElements(self):
        self._numListElements = self._computeNumListElements()
        
        if self.allowOverlaps and self._numListElements > 0:
            self._numIterElements = self._computeNumIterElements()
        else:
            self._numIterElements = self._numListElements

    def _computeNumListElements(self):
        for list in [self._startList, self._endList, self._valList, self._edgesList]:
            if list is not None:
                return len(list)
        raise ShouldNotOccurError

    def _computeNumIterElements(self):
        for list in [self._startList, self._endList, self._valList, self._edgesList]:
            if list is not None:
                #TODO: test
                if isinstance(list, numpy.ndarray) or isinstance(list, VirtualTrackColumn):
                    return len(self._removeBlindPassengersFromNumpyArray(list))
                else:
                    return sum(1 for _ in self)
        raise ShouldNotOccurError
            
    def __len__(self):
        return self._bpSize()
    
    def getNumElements(self):
        return self._numIterElements
    
    def _bpSize(self):        
        return len(self.genomeAnchor)
    
    def next(self):
        self._trackElement._index += 1
        
        #To remove any blind passengers - segments entirely in front of genomeanchor,
        # but sorted after a larger segment crossing the border
        if self.allowOverlaps and not self.trackFormat.reprIsDense():
            while self._trackElement._index < self._numListElements and self._endList[self._trackElement._index] <= self.genomeAnchor.start: #self._trackElement.end() <= 0:
                self._trackElement._index += 1

        if self._trackElement._index < self._numListElements:
            return self._trackElement
        else:
            raise StopIteration

    def _findLeftIndex(self):
        leftIndex = 0
        #remove track elements entirely to the left of the anchor
        while leftIndex < len(self._endList) and self._endList[leftIndex] <= self.genomeAnchor.start:
            leftIndex += 1
        return leftIndex
        
    def _findRightIndex(self):
        rightIndex = self._numListElements
        while rightIndex > 0 and self._startList[rightIndex-1] >= self.genomeAnchor.end:
            rightIndex -= 1
        return rightIndex
        
    def sliceElementsAccordingToGenomeAnchor(self):
        assert( not self.trackFormat.reprIsDense() )
        self._doScatteredSlicing()
        
    def _doScatteredSlicing(self):
        leftIndex = self._findLeftIndex()  
        rightIndex = self._findRightIndex()    
        
        if self._bpSize() == 0:
            rightIndex = leftIndex

        if self._should_use_pytables:
            self._startList.update_offset(start=leftIndex, stop=rightIndex)
            self._endList.update_offset(start=leftIndex, stop=rightIndex)
            if self._valList is not None:
                self._valList.update_offset(start=leftIndex, stop=rightIndex)
            if self._strandList is not None:
                self._strandList.update_offset(start=leftIndex, stop=rightIndex)
            if self._idList is not None:
                self._idList.update_offset(start=leftIndex, stop=rightIndex)
            if self._edgesList is not None:
                self._edgesList.update_offset(start=leftIndex, stop=rightIndex)
            if self._weightsList is not None:
                self._weightsList.update_offset(start=leftIndex, stop=rightIndex)
            for extraList in self._extraLists.values():
                extraList.update_offset(start=leftIndex, stop=rightIndex)
        else:
            self._startList = self._startList[leftIndex:rightIndex]
            self._endList = self._endList[leftIndex:rightIndex]
            if self._valList != None:
                self._valList = self._valList[leftIndex:rightIndex]
            if self._strandList != None:
                self._strandList = self._strandList[leftIndex:rightIndex]
            if self._idList != None:
                self._idList = self._idList[leftIndex:rightIndex]
            if self._edgesList != None:
                self._edgesList = self._edgesList[leftIndex:rightIndex]
            if self._weightsList != None:
                self._weightsList = self._weightsList[leftIndex:rightIndex]
            for key, extraList in self._extraLists.items():
                self._extraLists[key] = extraList[leftIndex:rightIndex]

        self._updateNumListElements()

    def _doDenseSlicing(self, i, j):
        if self._should_use_pytables:
            if self._valList is not None:
                self._valList.update_offset(start=i, stop=j)
            if self._strandList is not None:
                self._strandList.update_offset(start=i, stop=j)
            if self._idList is not None:
                self._idList.update_offset(start=i, stop=j)
            if self._edgesList is not None:
                self._edgesList.update_offset(start=i, stop=j)
            if self._weightsList is not None:
                self._weightsList.update_offset(start=i, stop=j)
            for extraList in self._extraLists.values():
                extraList.update_offset(start=i, stop=j)
        else:
            if self._valList != None:
                self._valList = self._valList[i:j]
            if self._strandList != None:
                self._strandList = self._strandList[i:j]
            if self._idList != None:
                self._idList = self._idList[i:j]
            if self._edgesList != None:
                self._edgesList = self._edgesList[i:j]
            if self._weightsList != None:
                self._weightsList = self._weightsList[i:j]
            for key, extraList in self._extraLists.items():
                self._extraLists[key] = extraList[i:j]

        self._updateNumListElements()
            
    def __getslice__(self, i, j):
        slicedTV = TrackView(self.genomeAnchor, self._startList, self._endList, \
                             self._valList, self._strandList, self._idList, \
                             self._edgesList, self._weightsList, \
                             self.borderHandling, self.allowOverlaps, \
                             extraLists=self._extraLists)
        slicedTV.trackFormat = self.trackFormat
        
        slicedTV.genomeAnchor.start += i
        if j>=0:
            try:
                slicedTV.genomeAnchor.end = min(self.genomeAnchor.end, self.genomeAnchor.start + j)
            except FloatingPointError: # Caused by trackView[:] with self.genomeAnchor.start > 0
                slicedTV.genomeAnchor.end = self.genomeAnchor.end
        if j<0:
            slicedTV.genomeAnchor.end += j

        if self.trackFormat.reprIsDense():
            slicedTV._doDenseSlicing(i,j)
        else:
            slicedTV._doScatteredSlicing()
        return slicedTV
    
    def _getBpLevelModificationArray(self, indexes, vals):
        bpLevelMod = numpy.bincount(indexes, vals)
        origLen = len(bpLevelMod)
        bpLevelMod.resize(self._bpSize()+1)
        bpLevelMod[origLen:] = 0
        return bpLevelMod
    
    def _commonGetBpLevelArray(self, vals):
        if self.trackFormat.reprIsDense():
            if self.allowOverlaps:
                raise ShouldNotOccurError()
            return vals
        else:
            bpLevelArray = numpy.zeros(self._bpSize()+1)
            numElements = self.getNumElements()
            if numElements > 0:
                bpLevelArray += self._getBpLevelModificationArray(self.startsAsNumpyArray(), vals)
                bpLevelArray -= self._getBpLevelModificationArray(self.endsAsNumpyArray(), vals)
                bpLevelArray = bpLevelArray.cumsum()
            return bpLevelArray[:-1]
            
    def getBinaryBpLevelArray(self):
        vals = numpy.ones(self.getNumElements(), dtype='int32')
        return numpy.array(self._commonGetBpLevelArray(vals), dtype='bool8')
        
    def getCoverageBpLevelArray(self):
        vals = numpy.ones(self.getNumElements(), dtype='int32')
        return numpy.array(self._commonGetBpLevelArray(vals), dtype='int32')
        
    def getValueBpLevelArray(self, voidValue=0):
        '''
        Creates a bp-level function of any valued track. In case of scattered tracks,
        uncovered aras are filled with voidValue (which would typically be set to 0 or numpy.nan).
        In the case of overlapping regions, the values are added.'''
        
        assert self.trackFormat.isValued('number'), self.trackFormat
        vals = self.valsAsNumpyArray()
        bpLevelArray = numpy.array(self._commonGetBpLevelArray(vals), dtype=vals.dtype)
        if voidValue != 0:
            bpLevelArray[~self.getBinaryBpLevelArray()] = voidValue
        return bpLevelArray
            
    def _removeBlindPassengersFromNumpyArray(self, numpyArray):
        '''
        To remove any blind passengers - segments entirely in front of genomeanchor,
        but sorted after a larger segment crossing the border.
        '''
        if self.allowOverlaps and len(numpyArray) > 0:
            numpyArray = numpyArray[numpy.where(self._endList > self.genomeAnchor.start)]
        return numpyArray

    def _commonAsNumpyArray(self, array, numpyArrayModMethod, name):
        assert(self.borderHandling in ['crop'])
        if array is None:
            return None

        numpyArray = self._removeBlindPassengersFromNumpyArray(array)

        if numpyArrayModMethod is not None:
            return numpyArrayModMethod(numpyArray)
        else:
            return numpyArray

    def startsAsNumpyArray(self):
        return self._commonAsNumpyArray(self._startList, self._startListModMethod, 'starts')
    
    def _startListModMethod(self, startList):
        return numpy.maximum(startList - self.genomeAnchor.start, \
                             numpy.zeros(len(startList), dtype='int32'))
    
    def endsAsNumpyArray(self):    
        return self._commonAsNumpyArray(self._endList, self._endListModMethod, 'ends')
    
    def _endListModMethod(self, endList):
        return numpy.minimum(endList - self.genomeAnchor.start, \
                             numpy.zeros(len(endList), dtype='int32') + len(self.genomeAnchor))
    
    def valsAsNumpyArray(self):
        return self._commonAsNumpyArray(self._valList, None, 'vals')
    
    def strandsAsNumpyArray(self):
        return self._commonAsNumpyArray(self._strandList, None, 'strands')
    
    def idsAsNumpyArray(self):
        return self._commonAsNumpyArray(self._idList, None, 'ids')
    
    def edgesAsNumpyArray(self):
        return self._commonAsNumpyArray(self._edgesList, None, 'edges')
    
    def weightsAsNumpyArray(self):
        return self._commonAsNumpyArray(self._weightsList, None, 'weights')
        
    def extrasAsNumpyArray(self, key):
        assert self.hasExtra(key)
        return self._commonAsNumpyArray(self._extraLists[key], None, 'extras')
    
    def allExtrasAsDictOfNumpyArrays(self):
        return OrderedDict([(key,self.extrasAsNumpyArray(key)) for key in self._extraLists])
        
    def hasExtra(self, key):
        return key in self._extraLists
    
class TrackViewSlider(object):
    def __init__(self, fullTV):
        self._fullTV = fullTV
        self._slideTV = None
        self._prevStart = None
        self._prevEnd = None
        self._prevLeftIndex = None
        self._prevRightIndex = None
        
    def slideTo(self, start, end):
        if self._fullTV.trackFormat.reprIsDense():
            return self._fullTV[start:end]
        
        if self._slideTV is None:
            self._slideTV = self._fullTV[start:end]
            self._prevStart = start
            self._prevEnd = end
            
            tempFullTVStart = self._fullTV.genomeAnchor.start
            tempFullTVEnd = self._fullTV.genomeAnchor.end
            self._fullTV.genomeAnchor.start = start
            self._fullTV.genomeAnchor.end = end
            self._prevLeftIndex = self._fullTV._findLeftIndex()  
            self._prevRightIndex = self._fullTV._findRightIndex()
            self._fullTV.genomeAnchor.start = tempFullTVStart
            self._fullTV.genomeAnchor.end = tempFullTVEnd
        else:        
            assert start in [self._prevStart, self._prevStart+1]
            assert end in [self._prevEnd, self._prevEnd+1]
        
            if start == self._prevStart+1:
                self._slideStart()
            if end == self._prevEnd+1:
                self._slideEnd()
        return self._slideTV

    def _slideStart(self):
        start = self._prevStart+1
        if len(self._slideTV._endList) == 0:
            self._prevStart += 1
            return
        
        if self._slideTV._endList[0] <= start:
            self._slideTV._startList = self._slideTV._startList[1:]
            self._slideTV._endList = self._slideTV._endList[1:]
    
            if self._slideTV._valList != None:
                self._slideTV._valList = self._slideTV._valList[1:]
            if self._slideTV._strandList != None:
                self._slideTV._strandList = self._slideTV._strandList[1:]
            if self._slideTV._idList != None:
                self._slideTV._idList = self._slideTV._idList[1:]
            if self._slideTV._edgesList != None:
                self._slideTV._edgesList = self._slideTV._edgesList[1:]
            if self._slideTV._weightsList != None:
                self._slideTV._weightsList = self._slideTV._weightsList[1:]
            for key, extraList in self._slideTV._extraLists.items():
                if extraList != None:
                    self._slideTV._extraLists[key] = extraList[1:]
            self._slideTV._updateNumListElements()
            self._prevLeftIndex += 1
            
        self._slideTV.genomeAnchor.start += 1         
        self._prevStart = start
        
    def _slideEnd(self):
        end = self._prevEnd+1
        endIndex = self._prevRightIndex
        if endIndex >= len(self._fullTV._startList):
            self._prevEnd += 1
            return

        if self._fullTV._startList[endIndex] < end:
            self._slideTV._startList = self._fullTV._startList[self._prevLeftIndex:endIndex+1]
            self._slideTV._endList = self._fullTV._endList[self._prevLeftIndex:endIndex+1]
    
            if self._slideTV._valList != None:
                self._slideTV._valList = self._fullTV._valList[self._prevLeftIndex:endIndex+1]
            if self._slideTV._strandList != None:
                self._slideTV._strandList = self._fullTV._strandList[self._prevLeftIndex:endIndex+1]
            if self._slideTV._idList != None:
                self._slideTV._idList = self._fullTV._idList[self._prevLeftIndex:endIndex+1]
            if self._slideTV._edgesList != None:
                self._slideTV._edgesList = self._fullTV._edgesList[self._prevLeftIndex:endIndex+1]
            if self._slideTV._weightsList != None:
                self._slideTV._weightsList = self._fullTV._weightsList[self._prevLeftIndex:endIndex+1]
            for key, extraList in self._slideTV._extraLists.items():
                if extraList != None:
                    self._slideTV._extraLists[key] = self._fullTV._extraLists[key][self._prevLeftIndex:endIndex+1]
            self._slideTV._updateNumListElements()
            self._prevRightIndex = endIndex + 1
        
        self._slideTV.genomeAnchor.end += 1         
        self._prevEnd = end