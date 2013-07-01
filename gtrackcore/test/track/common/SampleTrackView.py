import numpy

from collections import OrderedDict
from numpy import array, nan, arange

from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.util.CommonFunctions import isIter
from gtrackcore.util.CustomExceptions import ShouldNotOccurError
from gtrackcore.util.RandomUtil import random

def getRandSegments(size, start, end):
   segments = sorted(random.sample(xrange(start*2, end*2), size*2))
   starts, ends = [], []
   for i in xrange(size):
      starts.append(segments[i*2]/2)
      ends.append((segments[i*2+1]+1)/2)
   return [array(starts), array(ends)]

def getRandValList(size, dtype='float64'):
   if dtype == 'float64':
      return array([random.random() - 0.5 for i in xrange(size)], dtype=dtype)
   elif dtype == 'bool8':
      return array([bool(random.getrandbits(1)) for i in xrange(size)], dtype=dtype)
   else:
      return array([], dtype=dtype)

def getRandStrandList(size):
   return array([random.randint(0, 1) for i in xrange(size)], dtype='bool8')

def getStrDTypeForMaxInt(maxInt):
   return 'S' + str(max( ((maxInt/10)+1), 1 ))
   
def getRandGraphLists(size, maxNumEdges=None):
   maxNumEdges = size if maxNumEdges is None else maxNumEdges
   ids = array(arange(size), dtype=getStrDTypeForMaxInt(size-1))
   numEdges = numpy.random.randint(maxNumEdges)+1 if maxNumEdges>0 else 0
   edges = array([numpy.concatenate(( ids[numpy.random.permutation(size)[:numEdges]],
                                      array(['']*(maxNumEdges-numEdges)) )) for x in xrange(size)])
   weights = array([numpy.concatenate(( numpy.random.random_sample(numEdges),
                                        array([nan]*(maxNumEdges-numEdges)) )) for x in xrange(size)])
   return ids, edges, weights
   
def getRandExtraList(size):
   return array(numpy.random.permutation(arange(size)), dtype=getStrDTypeForMaxInt(size-1))

class SampleTV(TrackView):
   @staticmethod
   def _findMaxNumEls(target):
      return max(len(el) for el in target) if len(target) > 0 else 0

   @staticmethod
   def _appendEmptyToEnd(target, emptyVal, numEls):
      return [x + [emptyVal]*(numEls-len(x)) for x in target]

   @staticmethod
   def _createList(target, source, dtype):
      if type(target) == bool:
         if target == True:
            target = source
         else:
            return None
      return array(target, dtype=dtype)
         
   @staticmethod
   def _createExtraLists(target, dtype, size):
      if type(target) == bool:
         if target == True:
            return OrderedDict([('extra1', getRandExtraList(size)), ('extra2', getRandExtraList(size))])
         else:
            return OrderedDict()
      elif isinstance(target, dict):
         return OrderedDict([(name, array(content, dtype=dtype)) for name, content in target.items()])
      elif isIter(target):
         return OrderedDict([(name, getRandExtraList(size)) for name in target])
      else:
         raise ShouldNotOccurError
   
   def __init__(self, segments=None, starts=True, ends=True, vals=True, strands=False, ids=False, edges=False, weights=False, \
                extras=False, anchor=None, numElements=None, valDType='float64', borderHandling='crop', allowOverlaps=False):
      if type(starts) != bool and ends == True:
        ends = False
      if type(ends) != bool and starts == True:
        starts = False
      
      assert not (starts==False and ends==False)
      assert segments!=False and segments!=True
      assert starts!=None and ends!=None and vals!=None and strands!=None
      assert segments==None or (starts==True and ends==True)
      assert not (isIter(weights) and not isIter(edges))
      
      assert (any( type(x) not in [bool,type(None)] for x in [segments,starts,ends,vals,strands,ids,edges,weights,extras]) and numElements==None) \
             or numElements!=None
      #assert(( (type(segments)!=bool or type(starts)!=bool or type(ends)!=bool or \
      #       type(vals)!=bool or type(strands)!=bool) and numElements==None )\
      #       or numElements!=None)
      #
      if anchor==None:
          anchor = [10,1000]
      
      if segments != None:
          starts = []
          ends = []        
          for seg in segments:
              starts.append(seg[0])
              ends.append(seg[1])
      
      if isIter(edges):
         maxNumEdges = self._findMaxNumEls(edges)
         edges = self._appendEmptyToEnd(edges, '', maxNumEdges)
         if isIter(weights):
            weights = self._appendEmptyToEnd(weights, numpy.nan, maxNumEdges)
      
      [starts, ends, vals, strands, ids, edges, weights] + ([x for x in extras.values()] if isinstance(extras, dict) else [])
      for list in [starts, ends, vals, strands, ids, edges, weights] + ([x for x in extras.values()] if isinstance(extras, dict) else []):
          if type(list) != bool  and numElements == None:
              numElements = len(list)
          assert(type(list) == bool or len(list) == numElements)
      
      for coordList in [starts, ends]:
          if type(coordList) != bool:
              for j in range(len(coordList)):
                  coordList[j] += anchor[0]
      
      randSegmentLists = getRandSegments(numElements, anchor[0], anchor[1])
      starts = self._createList(starts, randSegmentLists[0], 'int32')
      ends = self._createList(ends, randSegmentLists[1], 'int32')
      
      vals = self._createList(vals, getRandValList(numElements, valDType), valDType)
      strands = self._createList(strands, getRandStrandList(numElements), 'bool8')
      
      randIds, randEdges, randWeights = getRandGraphLists(numElements)
      ids = self._createList(ids, randIds, randIds.dtype)
      edges = self._createList(edges, randEdges, randEdges.dtype)
      weights = self._createList(weights, randWeights, 'float64')
      
      if weights is not None and len(weights.shape) == 1:
         weights = weights.reshape(weights.shape + (0,))
      
      extras = self._createExtraLists(extras, 'S', numElements)

      if starts == None:
          if ends[0] != 0:
             ends = numpy.append([anchor[0]], ends)
             if vals != None:
                vals = numpy.append([nan], vals)
             if strands != None:
                strands = numpy.append([True], strands)
          if ends[-1] != anchor[1]:
              ends[-1] = anchor[1]
      
#        print (starts, ends, vals, strands, anchor)
      TrackView.__init__(self, GenomeRegion('TestGenome', 'chr21', anchor[0], anchor[1]), starts, ends, vals, \
                         strands, ids, edges, weights, borderHandling, allowOverlaps, extraLists=extras)

   def __eq__(self, other):
      #print self.genomeAnchor, other.genomeAnchor
      #print self.borderHandling, other.borderHandling
      #print self.allowOverlaps, other.allowOverlaps
      #print self._startList, other._startList
      #print self._endList, other._endList
      #print repr(self._valList), repr(other._valList)
      #print self._strandList, other._strandList
      #print self._idList, other._idList
      #print self._edgesList, other._edgesList
      #print self._weightsList, other._weightsList
      
      return other is not None and \
            self.genomeAnchor == other.genomeAnchor and \
            self.borderHandling == other.borderHandling and \
            self.allowOverlaps == other.allowOverlaps and \
            ((self._startList is None and other._startList is None) or (self._startList == other._startList).all()) and \
            ((self._endList is None and other._endList is None) or (self._endList == other._endList).all()) and \
            ((self._valList is None and other._valList is None) or (self._valList == other._valList).all()) and \
            ((self._strandList is None and other._strandList is None) or (self._strandList == other._strandList).all()) and \
            ((self._idList is None and other._idList is None) or (self._idList == other._idList).all()) and \
            ((self._edgesList is None and other._edgesList is None) or (self._edgesList == other._edgesList).all()) and \
            ((self._weightsList is None and other._weightsList is None) or (self._weightsList == other._weightsList).all())
            
class SampleTV_Num(SampleTV):
   def __init__(self, vals=True, strands=True, anchor=None, valDType='float64'):
      assert(vals!=True or anchor!=None)
      
      if anchor==None:
          numElements = len(vals)
          anchor = [10, 10 + numElements]
      else:
          numElements = anchor[1] - anchor[0]
      
      vals = self._createList(vals, getRandValList(numElements), valDType)
      strands = self._createList(strands, getRandStrandList(numElements), 'bool8')
      
      #print (vals, strands, anchor)
      TrackView.__init__(self, GenomeRegion('TestGenome', 'chr21', anchor[0], anchor[1]), None, None,
                         vals, strands, None, None, None, 'crop', False)
#
#def printTv(tv):
#    for el in tv:
#        print el.start(), el.end(), el.val(), el.strand(), tv.genomeAnchor.start, tv.genomeAnchor.end
#    print '--'
#
#tv = SampleTV(anchor=[22,123], numElements=2)
#printTv(tv)
#printTv(tv[0:50])
#
#printTv(SampleTV(numElements=5))
#
#printTv(SampleTV_Num(strands=False, anchor=[2,10]))
#
#printTv(SampleTV(segments=[[1,2],[3,4]]))
#printTv(SampleTV(segments=[[1,2],[3,4]], anchor=[20,30]))
#printTv(SampleTV(segments=[[1,2],[3,4]], vals=False))
#printTv(SampleTV(segments=[[1,2],[3,4]], strands=False))
#printTv(SampleTV(segments=[[1,2],[3,4]], vals=False, strands=False))
#
#printTv(SampleTV(starts=[1,3], ends=[2,4]))
#printTv(SampleTV(starts=[20,40]))
#printTv(SampleTV(ends=[20,40,990]))
#
#printTv(SampleTV(vals=False, strands=False, anchor=[22,100], numElements=9))
#printTv(SampleTV(starts=False, vals=False, strands=False, anchor=[22,100], numElements=9))

