import unittest

from numpy import array, nan, dtype
from collections import OrderedDict

from gtrackcore_compressed.test.common.Asserts import smartRecursiveAssertList, TestCaseWithImprovedAsserts
from gtrackcore_compressed.track.core.GenomeRegion import GenomeRegion
from gtrackcore_compressed.track.core.TrackView import TrackView
from gtrackcore_compressed.util.CustomExceptions import ShouldNotOccurError

class TestTrackView(TestCaseWithImprovedAsserts):
    def setUp(self):
        self.genome = 'hg18'
        self.chr = 'chr1'
    
    def testInit(self):
        starts = [1, 11, 21]
        ends = [9, 19, 29]
        values = [5.2, -5, 0]
        strands = [False, True, False]
        ids = ['a1', 'b2', 'c3']
        edges = [['b2','c3'], ['a1',''], ['','']]
        weights = [[0.2,0.3], [-0.1,nan], [nan,nan]]
        extras = OrderedDict([('extra1', ['A','B','C']), ('extra2', ['1.0','2.0','3.0'])])
        
        genomeAnchor = GenomeRegion(self.genome, self.chr, 0, 100)
    
        self.assertRaises(AssertionError, TrackView, genomeAnchor, [], ends, values, strands, ids, edges, weights, 'crop', False, extraLists=extras)
        self.assertRaises(AssertionError, TrackView, genomeAnchor, starts, [], values, strands, ids, edges, weights, 'crop', False, extraLists=extras)
        self.assertRaises(AssertionError, TrackView, genomeAnchor, starts, ends, [], strands, ids, edges, weights, 'crop', False, extraLists=extras)
        self.assertRaises(AssertionError, TrackView, genomeAnchor, starts, ends, values, [], ids, edges, weights, 'crop', False, extraLists=extras)
        self.assertRaises(AssertionError, TrackView, genomeAnchor, starts, ends, values, strands, [], edges, weights, 'crop', False, extraLists=extras)
        self.assertRaises(AssertionError, TrackView, genomeAnchor, starts, ends, values, strands, ids, [], weights, 'crop', False, extraLists=extras)
        self.assertRaises(AssertionError, TrackView, genomeAnchor, starts, ends, values, strands, ids, edges, [], 'crop', False, extraLists=extras)
        self.assertRaises(AssertionError, TrackView, genomeAnchor, starts, ends, values, strands, ids, edges, weights, 'crop', False, extraLists=OrderedDict([('extra1', [])]))
    
        t = TrackView(genomeAnchor, None, [0] + ends, [nan] + values, [True] + strands, [''] + ids, [['','']] + edges, [[nan,nan]] + weights, 'crop', False, \
                      extraLists=OrderedDict([(x,[''] + y) for x,y in extras.items()]))
        t = TrackView(genomeAnchor, starts, None, values, strands, ids, edges, weights, 'crop', False, extraLists=extras)
        t = TrackView(genomeAnchor, starts, ends, None, strands, ids, edges, weights, 'crop', False, extraLists=extras)
        t = TrackView(genomeAnchor, starts, ends, values, None, ids, edges, weights, 'crop', False, extraLists=extras)
        t = TrackView(genomeAnchor, starts, ends, values, strands, None, None, None, 'crop', False, extraLists=extras)
        t = TrackView(genomeAnchor, starts, ends, values, strands, ids, None, None, 'crop', False, extraLists=extras)
        t = TrackView(genomeAnchor, starts, ends, values, strands, ids, edges, None, 'crop', False, extraLists=extras)
        t = TrackView(genomeAnchor, starts, ends, values, strands, ids, edges, weights, 'crop', False)
    
        self.assertRaises(AssertionError, TrackView, genomeAnchor, starts[0:-1], ends, values, strands, ids, edges, weights, 'crop', False, extraLists=extras)
        self.assertRaises(AssertionError, TrackView, genomeAnchor, starts, ends[0:-1], values, strands, ids, edges, weights, 'crop', False, extraLists=extras)
        self.assertRaises(AssertionError, TrackView, genomeAnchor, starts, ends, values[0:-1], strands, ids, edges, weights, 'crop', False, extraLists=extras)
        self.assertRaises(AssertionError, TrackView, genomeAnchor, starts, ends, values, strands[0:-1], ids, edges, weights, 'crop', False, extraLists=extras)
        self.assertRaises(AssertionError, TrackView, genomeAnchor, starts, ends, values, strands, ids[0:-1], edges, weights, 'crop', False, extraLists=extras)
        self.assertRaises(AssertionError, TrackView, genomeAnchor, starts, ends, values, strands, ids, edges[0:-1], weights, 'crop', False, extraLists=extras)
        self.assertRaises(AssertionError, TrackView, genomeAnchor, starts, ends, values, strands, ids, edges, weights[0:-1], 'crop', False, extraLists=extras)
        self.assertRaises(AssertionError, TrackView, genomeAnchor, starts, ends, values, strands, ids, edges, weights, 'crop', False, extraLists={'cat': extras['extra1'][0:-1]})
                  
    def _parseElementList(self, elList, linkedAndExtra=False):
        dict = OrderedDict()
        dict['start'] = [el[0] for el in elList]
        dict['end'] = [el[1] for el in elList]
        dict['val'] = [el[2] for el in elList]
        dict['strand'] = [el[3] for el in elList]
        if linkedAndExtra:
            dict['id'] = [el[4] for el in elList]
            dict['edges'] = [el[5] for el in elList]
            dict['weights'] = [el[6] for el in elList]
            dict['extra'] = OrderedDict([('extra1', [el[7] for el in elList]),
                                         ('extra2', [el[8] for el in elList])])
        return dict
    
    def _getPointEnds(self, target):
        return [el[0]+1 for el in target]

    def _getPartitionStarts(self, target):
        prevEnd = 0
        starts = []
        for el in target:
            starts.append(prevEnd)
            prevEnd = el[1]
        return starts

    def _runAllSPP(self, target, targetRegion, source, sourceRegion, func, allowOverlaps=False, linkedAndExtra=False, **kwArgs):
        self._runAllSegPoint(target, targetRegion, source, sourceRegion, func, allowOverlaps, linkedAndExtra, **kwArgs)
        self._runAllPart(target, targetRegion, source, sourceRegion, func, allowOverlaps, linkedAndExtra, **kwArgs)

    def _runAllSegPoint(self, target, targetRegion, source, sourceRegion, func, allowOverlaps=False, linkedAndExtra=False, **kwArgs):
        sDict, tDict = [self._parseElementList(elList, linkedAndExtra) for elList in [source, target]]
        for ends,tEnds in ((None,self._getPointEnds(target)), (sDict['end'],tDict['end'])):
            self._runAllValStrands(sDict['start'], tDict['start'], ends, tEnds,\
                                   sDict, tDict, sourceRegion, targetRegion, func, allowOverlaps, linkedAndExtra, **kwArgs)
            
    def _runAllPart(self, target, targetRegion, source, sourceRegion, func, allowOverlaps=False, linkedAndExtra=False, **kwArgs):
        sDict, tDict = [self._parseElementList(elList, linkedAndExtra) for elList in [source, target]]
        sDict['val'] = [nan] + sDict['val']
        sDict['strand'] = [True] + sDict['strand']
        if linkedAndExtra:
            sDict['id'] = [''] + sDict['id']
            sDict['edges'] = [['']*len(sDict['edges'][0])] + sDict['edges']
            sDict['weights'] = [[nan]*len(sDict['weights'][0])] + sDict['weights']
            sDict['extra'] = OrderedDict([(x,[''] + y) for x,y in sDict['extra'].items()])
        self._runAllValStrands(None, self._getPartitionStarts(target), [0] + sDict['end'], tDict['end'],\
                               sDict, tDict, sourceRegion, targetRegion, func, allowOverlaps, linkedAndExtra, **kwArgs)
                
    def _runAllSegments(self, target, targetRegion, source, sourceRegion, func, allowOverlaps=False, linkedAndExtra=False, **kwArgs):
        sDict, tDict = [self._parseElementList(elList, linkedAndExtra) for elList in [source, target]]
        self._runAllValStrands(sDict['start'], tDict['start'], sDict['end'], tDict['end'],\
                               sDict, tDict, sourceRegion, targetRegion, func, allowOverlaps, linkedAndExtra, **kwArgs)
    
    def _runAllValStrands(self, starts, tStarts, ends, tEnds, sDict, tDict, sourceRegion, targetRegion, func, allowOverlaps, linkedAndExtra=False, **kwArgs):
        for vals,tVals in ((None,None), (sDict['val'],tDict['val'])):
            for strands,tStrands in ((None,None), (sDict['strand'],tDict['strand'])):
                self._runAllCommon(starts, tStarts, ends, tEnds, vals, tVals, strands, tStrands, \
                                   sDict, tDict, sourceRegion, targetRegion, func, allowOverlaps, linkedAndExtra, **kwArgs)
    
    def _runAllF(self, target, targetRegion, source, sourceRegion, func, linkedAndExtra=False, **kwArgs):
        sDict, tDict = [self._parseElementList([[None]*2 + el for el in elList], linkedAndExtra) for elList in [source, target]]
        vals, tVals = sDict['val'], tDict['val']
        for strands,tStrands in ((None,None), (sDict['strand'],tDict['strand'])):
            self._runAllCommon(None, None, None, None, vals, tVals, strands, tStrands, \
                               sDict, tDict, sourceRegion, targetRegion, func, False, linkedAndExtra, **kwArgs)
            
    def _runAllLBP(self, target, targetRegion, source, sourceRegion, func, **kwArgs):
        sDict, tDict = [self._parseElementList([[None]*3 + el for el in elList], True) for elList in [source, target]]
        for strands,tStrands in ((None,None), (sDict['strand'],tDict['strand'])):
            for weights,tWeights in ((None,None), (sDict['weights'],tDict['weights'])):
                for extras,tExtras in ((None,None), (sDict['extra'],tDict['extra'])):
                    self._runAndAssertTrackView(None, None, None, strands, sDict['id'], sDict['edges'], weights, extras, \
                                                None, None, None, tStrands, tDict['id'], tDict['edges'], tWeights, tExtras, \
                                                sourceRegion, targetRegion, func, False)
    
    def _runAllCommon(self, starts, tStarts, ends, tEnds, vals, tVals, strands, tStrands, \
                      sDict, tDict, sourceRegion, targetRegion, func, allowOverlaps, linkedAndExtra=False, **kwArgs):
        if linkedAndExtra:
            for (ids,tIds),(edges,tEdges),(weights,tWeights) in \
                (((None,None),(None,None),(None,None)),
                 ((sDict['id'],tDict['id']),(None,None),(None,None)),
                 ((sDict['id'],tDict['id']),(sDict['edges'],tDict['edges']),(None,None)),
                 ((sDict['id'],tDict['id']),(sDict['edges'],tDict['edges']),(sDict['weights'],tDict['weights']))):
                for extras,tExtras in ((None,None), (sDict['extra'],tDict['extra'])):
                    self._runAndAssertTrackView(starts, ends, vals, strands, ids, edges, weights, extras, \
                                                tStarts, tEnds, tVals, tStrands, tIds, tEdges, tWeights, tExtras, \
                                                sourceRegion, targetRegion, func, allowOverlaps, **kwArgs)
        else:
            self._runAndAssertTrackView(starts, ends, vals, strands, None, None, None, None, \
                                        tStarts, tEnds, tVals, tStrands, None, None, None, None, \
                                        sourceRegion, targetRegion, func, allowOverlaps, **kwArgs)
    
    def _runAndAssertTrackView(self, starts, ends, vals, strands, ids, edges, weights, extras, \
                               tStarts, tEnds, tVals, tStrands, tIds, tEdges, tWeights, tExtras, \
                               sourceRegion, targetRegion, func, allowOverlaps, **kwArgs):
        tv = self._createTrackView(starts, ends, vals, strands, ids, edges, weights, extras, sourceRegion, allowOverlaps, **kwArgs)
        newTv = self._runFunc(tv, func)
        self.assertEqual(tv.trackFormat, newTv.trackFormat)
        targetListLen = max(len(x) if x is not None else 0 for x in [tStarts, tEnds, tVals, tEdges])
        self.assertEqual(targetListLen, newTv.getNumElements())
        self._assertLists(newTv, tStarts, tEnds, tVals, tStrands, tIds, tEdges, tWeights, tExtras, targetRegion)
    
    def _createTrackView(self, starts, ends, vals, strands, ids, edges, weights, extras, sourceRegion, allowOverlaps, sliceFull=False):
        genomeAnchor = GenomeRegion(genome=self.genome, chr=self.chr, start=sourceRegion[0], end=sourceRegion[1])
        
        tv = TrackView(genomeAnchor, \
                       array(starts) if starts is not None else None, \
                       array(ends) if ends is not None else None, \
                       array(vals, dtype='float64') if vals is not None else None, \
                       array(strands) if strands is not None else None, \
                       array(ids) if ids is not None else None, \
                       array(edges) if edges is not None else None, \
                       array(weights) if weights is not None else None, \
                       'crop', allowOverlaps, \
                       extraLists=OrderedDict([(key, array(extra)) for key, extra in extras.iteritems()]) if extras is not None else OrderedDict())
        if sliceFull:
            tv.sliceElementsAccordingToGenomeAnchor()
        return tv
    
    def _runFunc(self, tv, func):
        if func != None:
            return func(tv)
        else:
            return tv
    
    def _smartAssertListWithNone(self, target, source):
        if target is None:
            self.assertEqual(None, source)
        else:
            smartRecursiveAssertList(target, [x for x in source], self.assertEqual, self.assertAlmostEqual)
    
    def _assertLists(self, tv, starts, ends, vals, strands, ids, edges, weights, extras, region):
        if extras is None:
            extras = OrderedDict()
        
        for attr in [starts, ends, vals, strands, ids, weights] + extras.values():
            if attr != None:
                #for el in tv:
                #    print el.start(), '-', el.end(), ',' ,
                #print
                self.assertEqual(len(attr), sum(1 for x in tv))
        
        self.assertEqual(GenomeRegion(genome=self.genome, chr=self.chr, start=region[0], end=region[1]),\
                         tv.genomeAnchor)
        
        for i, el in enumerate(tv):
            #print el.start(), el.end(), el.val(), el.strand(), el.id(), el.edges(), el.weights()
            #for key in el.getAllExtraKeysInOrder():
            #    print getattr(el, key)()
            
            self.assertEqual(starts[i] if starts != None else None, el.start())
            self.assertEqual(ends[i] if ends != None else None, el.end())
            if vals is None:
                self.assertEqual(None, el.val())
            else:
                self.assertAlmostEqual(vals[i], el.val())
            self.assertEqual(strands[i] if strands != None else None, el.strand())
            self.assertEqual(ids[i] if ids != None else None, el.id())
            self.assertListsOrDicts(edges[i] if edges != None else None, el.edges())
            self.assertListsOrDicts(weights[i] if weights != None else None, el.weights())
            for key in extras:
                self.assertEqual(extras[key][i] if extras != None else None, getattr(el, key)())
        
        self._smartAssertListWithNone(starts, tv.startsAsNumpyArray())
        self._smartAssertListWithNone(ends, tv.endsAsNumpyArray())
        self._smartAssertListWithNone(vals, tv.valsAsNumpyArray())
        self._smartAssertListWithNone(strands, tv.strandsAsNumpyArray())
        self._smartAssertListWithNone(ids, tv.idsAsNumpyArray())
        self._smartAssertListWithNone(edges, tv.edgesAsNumpyArray())
        self._smartAssertListWithNone(weights, tv.weightsAsNumpyArray())
        for key in extras:
            self._smartAssertListWithNone(extras[key], tv.extrasAsNumpyArray(key))
    
    def _commonAssertBpLevelArray(self, methodStr, methodKwArgs, dtypeStr, result, sourceRegion, allowOverlaps, starts=None, ends=None, vals=None, strands=None, ids=None, edges=None, weights=None, extras=None):
        tv = self._createTrackView(starts, ends, vals, strands, ids, edges, weights, extras, sourceRegion, allowOverlaps)
        binaryArray = getattr(tv, methodStr)(**methodKwArgs)
        self.assertListsOrDicts(result, binaryArray)
        self.assertEqual(dtype(dtypeStr), binaryArray.dtype)
        
    def _assertBinaryBpLevelArray(self, result, sourceRegion, allowOverlaps, **kwArgs):
        self._commonAssertBpLevelArray('getBinaryBpLevelArray', {}, 'bool8', result, sourceRegion, allowOverlaps, **kwArgs)
        
    def _assertCoverageBpLevelArray(self, result, sourceRegion, allowOverlaps, **kwArgs):
        self._commonAssertBpLevelArray('getCoverageBpLevelArray', {}, 'int32', result, sourceRegion, allowOverlaps, **kwArgs)
        
    def _assertValueBpLevelArray(self, result, sourceRegion, allowOverlaps, **kwArgs):
        self._commonAssertBpLevelArray('getValueBpLevelArray', {'voidValue': nan}, 'float64', result, sourceRegion, allowOverlaps, **kwArgs)
    
    def testElementIteration(self):
        self._runAllSPP([[2, 5, 1.0, True, 'a1', ['b2','c3'], [0.2,0.3], 'A', '1.0'], \
                         [6, 7, 2.0, False, 'b2', ['a1',''], [-0.1,nan], 'B', '2.0'], \
                         [8, 9, -0.5, True, 'c3', ['',''], [nan,nan], 'C', '3.0']], \
                        [0, 10], \
                        [[2, 5, 1.0, True, 'a1', ['b2','c3'], [0.2,0.3], 'A', '1.0'], \
                         [6, 7, 2.0, False, 'b2', ['a1',''], [-0.1,nan], 'B', '2.0'], \
                         [8, 9, -0.5, True, 'c3', ['',''], [nan,nan], 'C', '3.0']], \
                        [0, 10], None, allowOverlaps=False, linkedAndExtra=True)
        
        self._runAllSPP([[0, 3, 1.0, True, 'a1', ['b2','c3'], [0.2,0.3], 'A', '1.0'], \
                         [4, 5, 2.0, False, 'b2', ['a1',''], [-0.1,nan], 'B', '2.0'], \
                         [6, 7, -0.5, True, 'c3', ['',''], [nan,nan], 'C', '3.0']], \
                        [2, 10], \
                        [[2, 5, 1.0, True, 'a1', ['b2','c3'], [0.2,0.3], 'A', '1.0'], \
                         [6, 7, 2.0, False, 'b2', ['a1',''], [-0.1,nan], 'B', '2.0'], \
                         [8, 9, -0.5, True, 'c3', ['',''], [nan,nan], 'C', '3.0']], \
                        [2, 10], None, allowOverlaps=False, linkedAndExtra=True)
        
        self._runAllSPP([[1, 2, 2.0, False, 'b2', ['a1',''], [-0.1,nan], 'B', '2.0'], \
                         [3, 4, -0.5, True, 'c3', ['',''], [nan,nan], 'C', '3.0']], \
                        [4, 8], \
                        [[2, 4, 1.0, True, 'a1', ['b2','c3'], [0.2,0.3], 'A', '1.0'], \
                         [5, 6, 2.0, False, 'b2', ['a1',''], [-0.1,nan], 'B', '2.0'], \
                         [7, 9, -0.5, True, 'c3', ['',''], [nan,nan], 'C', '3.0']], \
                        [4, 8], None, allowOverlaps=False, linkedAndExtra=True, sliceFull=True)
        
        self._runAllSegments([[0, 1, 1.0, True, 'a1', ['b2','c3'], [0.2,0.3], 'A', '1.0'], \
                         [2, 3, 2.0, False, 'b2', ['a1',''], [-0.1,nan], 'B', '2.0']], \
                        [4, 8], \
                        [[2, 5, 1.0, True, 'a1', ['b2','c3'], [0.2,0.3], 'A', '1.0'], \
                         [6, 7, 2.0, False, 'b2', ['a1',''], [-0.1,nan], 'B', '2.0'], \
                         [8, 9, -0.5, True, 'c3', ['',''], [nan,nan], 'C', '3.0']], \
                        [4, 8], None, allowOverlaps=False, linkedAndExtra=True, sliceFull=True)
        
        self._runAllF([[1.0, True, 'a1', ['b2','c3'], [0.2,0.3], 'A', '1.0'], \
                       [2.0, False, 'b2', ['a1',''], [-0.1,nan], 'B', '2.0'], \
                       [-0.5, True, 'c3', ['',''], [nan,nan], 'C', '3.0'], \
                       [9.87, False, 'd3', ['d3',''], [0,nan], 'D', '4.0']], \
                      [3, 7], \
                      [[1.0, True, 'a1', ['b2','c3'], [0.2,0.3], 'A', '1.0'], \
                       [2.0, False, 'b2', ['a1',''], [-0.1,nan], 'B', '2.0'], \
                       [-0.5, True, 'c3', ['',''], [nan,nan], 'C', '3.0'], \
                       [9.87, False, 'd3', ['d3',''], [0,nan], 'D', '4.0']],
                      [3, 7], None, linkedAndExtra=True)
        
        self._runAllLBP([[True, 'a1', ['b2','c3'], [0.2,0.3], 'A', '1.0'], \
                         [False, 'b2', ['a1',''], [-0.1,nan], 'B', '2.0'], \
                         [True, 'c3', ['',''], [nan,nan], 'C', '3.0'], \
                         [False, 'd3', ['d3',''], [0,nan], 'D', '4.0']], \
                        [3, 7], \
                        [[True, 'a1', ['b2','c3'], [0.2,0.3], 'A', '1.0'], \
                         [False, 'b2', ['a1',''], [-0.1,nan], 'B', '2.0'], \
                         [True, 'c3', ['',''], [nan,nan], 'C', '3.0'], \
                         [False, 'd3', ['d3',''], [0,nan], 'D', '4.0']],
                        [3, 7], None)
    
    def testElementIterationWithOverlaps(self):
        self._runAllSegPoint([[2, 5, 1.0, True, 'a1', ['b2','c3'], [0.2,0.3], 'A', '1.0'], \
                              [4, 7, 2.0, False, 'b2', ['a1',''], [-0.1,nan], 'B', '2.0'], \
                              [4, 8, -0.5, True, 'c3', ['',''], [nan,nan], 'C', '3.0']],
                             [10, 20], \
                             [[12, 15, 1.0, True, 'a1', ['b2','c3'], [0.2,0.3], 'A', '1.0'], \
                              [14, 17, 2.0, False, 'b2', ['a1',''], [-0.1,nan], 'B', '2.0'], \
                              [14, 18, -0.5, True, 'c3', ['',''], [nan,nan], 'C', '3.0']], \
                             [10, 20], None, allowOverlaps=True, linkedAndExtra=True)
        
        self._runAllPart([[None, 5, 1.0, True, 'a1', ['b2','c3'], [0.2,0.3], 'A', '1.0'], \
                          [None, 5, 2.0, False, 'b2', ['a1',''], [-0.1,nan], 'B', '2.0'], \
                          [None, 10, -0.5, True, 'c3', ['',''], [nan,nan], 'C', '3.0']], \
                         [10, 20], \
                         [[None, 15, 1.0, True, 'a1', ['b2','c3'], [0.2,0.3], 'A', '1.0'], \
                          [None, 15, 2.0, False, 'b2', ['a1',''], [-0.1,nan], 'B', '2.0'], \
                          [None, 20, -0.5, True, 'c3', ['',''], [nan,nan], 'C', '3.0']], \
                         [10, 20], None, allowOverlaps=True, linkedAndExtra=True)
        
        self._runAllSegments([[0, 5, 1.0, True, 'a1', ['b2','c3'], [0.2,0.3], 'A', '1.0'], \
                              [4, 6, -0.5, True, 'c3', ['',''], [nan,nan], 'C', '3.0']], \
                             [10, 20], \
                             [[5, 15, 1.0, True, 'a1', ['b2','c3'], [0.2,0.3], 'A', '1.0'], \
                              [7, 10, 2.0, False, 'b2', ['a1',''], [-0.1,nan], 'B', '2.0'], \
                              [14, 16, -0.5, True, 'c3', ['',''], [nan,nan], 'C', '3.0']], \
                             [10, 20], None, allowOverlaps=True, linkedAndExtra=True)
        
        self._runAllSegments([[0, 5, 1.0, True, 'a1', ['b2','c3'], [0.2,0.3], 'A', '1.0'], \
                              [4, 10, -0.5, True, 'c3', ['',''], [nan,nan], 'C', '3.0']], \
                             [10, 20], \
                             [[5, 15, 1.0, True, 'a1', ['b2','c3'], [0.2,0.3], 'A', '1.0'], \
                              [7, 10, 2.0, False, 'b2', ['a1',''], [-0.1,nan], 'B', '2.0'], \
                              [14, 26, -0.5, True, 'c3', ['',''], [nan,nan], 'C', '3.0'], \
                              [20, 22, 2.0, False, 'd4', ['c3',''], [-0.4,4.0], 'D', '4.0']], \
                             [10, 20], None, allowOverlaps=True, linkedAndExtra=True, sliceFull=True)
        
        self._runAllSegments([[5, 10, 1.0, True, 'a1', ['b2','c3'], [0.2,0.3], 'A', '1.0'], \
                              [6, 8, 2.0, False, 'b2', ['a1',''], [-0.1,nan], 'B', '2.0']], \
                             [10, 20], \
                             [[15, 25, 1.0, True, 'a1', ['b2','c3'], [0.2,0.3], 'A', '1.0'], \
                              [16, 18, 2.0, False, 'b2', ['a1',''], [-0.1,nan], 'B', '2.0']], \
                             [10, 20], None, allowOverlaps=True, linkedAndExtra=True, sliceFull=True)
        
    def testSlicing(self):
        self._runAllSegPoint([[2, 4, 1.0, True], [5, 7, 2.0, False]], [0, 10], \
                             [[2, 4, 1.0, True], [5, 7, 2.0, False]], [0, 10], lambda x: x[:])
        self._runAllPart([[None, 4, 1.0, True], [None, 10, 2.0, False]], [0, 10], \
                         [[None, 4, 1.0, True], [None, 10, 2.0, False]], [0, 10], lambda x: x[:])
        self._runAllF([[1.0, True], [2.0, False], [-0.5, True]], [0, 3], \
                      [[1.0, True], [2.0, False], [-0.5, True]], [0, 3], lambda x: x[:])
        
        self._runAllSegPoint([[0, 2, 1.0, True], [3, 5, 2.0, False]], [2, 10], \
                             [[2, 4, 1.0, True], [5, 7, 2.0, False]], [2, 10], lambda x: x[:])
        self._runAllPart([[None, 2, 1.0, True], [None, 8, 2.0, False]], [2, 10], \
                         [[None, 4, 1.0, True], [None, 10, 2.0, False]], [2, 10], lambda x: x[:])    
        self._runAllF([[1.0, True], [2.0, False], [-0.5, True]], [2, 5], \
                      [[1.0, True], [2.0, False], [-0.5, True]], [2, 5], lambda x: x[:])
        
        self._runAllSegPoint([[0, 2, 1.0, True], [3, 5, 2.0, False]], [2, 7], \
                             [[2, 4, 1.0, True], [5, 7, 2.0, False]], [2, 10], lambda x: x[:5])
        self._runAllPart([[None, 2, 1.0, True], [None, 5, 2.0, False]], [2, 7], \
                         [[None, 4, 1.0, True], [None, 10, 2.0, False]], [2, 10], lambda x: x[:5])
        self._runAllF([[1.0, True], [2.0, False]], [2, 4], \
                      [[1.0, True], [2.0, False], [-0.5, True]], [2, 5], lambda x: x[:2])
        
        self._runAllSegPoint([[1, 3, 2.0, False]], [4, 10], \
                             [[2, 4, 1.0, True], [5, 7, 2.0, False]], [2, 10], lambda x: x[2:])
        self._runAllPart([[None, 6, 2.0, False]], [4, 10], \
                         [[None, 4, 1.0, True], [None, 10, 2.0, False]], [2, 10], lambda x: x[2:])
        self._runAllF([[2.0, False], [-0.5, True]], [3, 5], \
                      [[1.0, True], [2.0, False], [-0.5, True]], [2, 5], lambda x: x[1:])
        
        self._runAllSegPoint([[1, 3, 2.0, False]], [4, 7], \
                             [[2, 4, 1.0, True], [5, 7, 2.0, False]], [2, 10], lambda x: x[2:5])
        self._runAllPart([[None, 3, 2.0, False]], [4, 7], \
                         [[None, 4, 1.0, True], [None, 10, 2.0, False]], [2, 10], lambda x: x[2:5])
        self._runAllF([[2.0, False]], [3, 4], \
                      [[1.0, True], [2.0, False], [-0.5, True]], [2, 5], lambda x: x[1:2])
    
        self._runAllSegPoint([[1, 3, 2.0, False, 'b2', ['a1',''], [-0.1,nan], 'B', '2.0']], \
                             [4, 7], \
                             [[2, 4, 1.0, True, 'a1', ['b2','c3'], [0.2,0.3], 'A', '1.0'], \
                              [5, 7, 2.0, False, 'b2', ['a1',''], [-0.1,nan], 'B', '2.0']], \
                             [2, 10], lambda x: x[2:5], linkedAndExtra=True)
        
        self._runAllPart([[None, 3, 2.0, False, 'b2', ['a1',''], [-0.1,nan], 'B', '2.0']], \
                         [4, 7], \
                         [[None, 4, 1.0, True, 'a1', ['b2','c3'], [0.2,0.3], 'A', '1.0'], \
                          [None, 10, 2.0, False, 'b2', ['a1',''], [-0.1,nan], 'B', '2.0']], \
                         [2, 10], lambda x: x[2:5], linkedAndExtra=True)
        
        self._runAllF([[2.0, False, 'b2', ['a1',''], [-0.1,nan], 'B', '2.0']], \
                      [3, 4], \
                      [[1.0, True, 'a1', ['b2','c3'], [0.2,0.3], 'A', '1.0'], \
                       [2.0, False, 'b2', ['a1',''], [-0.1,nan], 'B', '2.0'], \
                       [-0.5, True, 'c3', ['',''], [nan,nan], 'C', '3.0']], \
                      [2, 5], lambda x: x[1:2], linkedAndExtra=True)
    
        self._runAllLBP([[False, 'b2', ['a1',''], [-0.1,nan], 'B', '2.0']], \
                        [3, 4], \
                        [[True, 'a1', ['b2','c3'], [0.2,0.3], 'A', '1.0'], \
                         [False, 'b2', ['a1',''], [-0.1,nan], 'B', '2.0'], \
                         [True, 'c3', ['',''], [nan,nan], 'C', '3.0']], \
                        [2, 5], lambda x: x[1:2])
        
        # Slicing of border segments makes no meaning for points, therefore runAllSegments
        self._runAllSegments([[0, 1, 1.0, True], [2, 3, 2.0, False]], [3, 6], \
                             [[2, 4, 1.0, True], [5, 7, 2.0, False]], [2, 10], lambda x: x[1:4])
        self._runAllPart([[None, 1, 1.0, True], [None, 3, 2.0, False]], [3, 6], \
                         [[None, 4, 1.0, True], [None, 10, 2.0, False]], [2, 10], lambda x: x[1:4])
        
        self._runAllSegPoint([], [4, 5], 
                             [[2, 4, 1.0, True], [5, 7, 2.0, False]], [2, 10], lambda x: x[2:3])
        self._runAllPart([[None, 1, 2.0, False]], [4, 5], \
                         [[None, 4, 1.0, True], [None, 10, 2.0, False]], [2, 10], lambda x: x[2:3])
        
        self._runAllSegPoint([], [7, 7], \
                             [[2, 4, 1.0, True], [5, 7, 2.0, False]], [2, 10], lambda x: x[5:5])
        self._runAllPart([], [7, 7], \
                         [[None, 4, 1.0, True], [None, 10, 2.0, False]], [2, 10], lambda x: x[5:5])
        self._runAllF([], [4, 4], \
                      [[1.0, True], [2.0, False], [-0.5, True]      ], [2, 5], lambda x: x[2:2])
    
        self._runAllSegPoint([[0, 2, 1.0, True], [3, 4, 2.0, False]], [2, 6], \
                             [[2, 4, 1.0, True], [5, 7, 2.0, False]], [2, 10], lambda x: x[:-4])
        self._runAllPart([[None, 2, 1.0, True], [None, 4, 2.0, False]], [2, 6], \
                         [[None, 4, 1.0, True], [None, 10, 2.0, False]], [2, 10], lambda x: x[:-4])
        self._runAllF([[1.0, True], [2.0, False]], [2, 4], \
                      [[1.0, True], [2.0, False], [-0.5, True]], [2, 5], lambda x: x[:-1])
        
        # Slicing of border segments makes no meaning for points, therefore runAllSegments
        self._runAllSegments([[0, 1, 1.0, True], [2, 3, 2.0, False]], [3, 6], \
                             [[2, 4, 1.0, True], [5, 7, 2.0, False]], [2, 10], lambda x: x[1:-4])
        self._runAllPart([[None, 1, 1.0, True], [None, 3, 2.0, False]], [3, 6], \
                         [[None, 4, 1.0, True], [None, 10, 2.0, False]], [2, 10], lambda x: x[1:-4])
        self._runAllF([[2.0, False]], [3, 4], \
                      [[1.0, True], [2.0, False], [-0.5, True]], [2, 5], lambda x: x[1:-1])
    
                #We do not currently want to support slicing outside trackview, as we are not sure about what result should be..
        #self._runAllSegments([], [22, 32], \
        #                     [[2, 4, 1.0, True], [5, 7, 2.0, False]], [2, 10], lambda x: x[20:30])
    
    def testBinaryBpLevelArray(self):
        #allowOverlaps = False
        self._assertBinaryBpLevelArray([False, False, False, False, False, False], \
                                       starts=[], ends=[], sourceRegion=[10,16], allowOverlaps=False)
        self._assertBinaryBpLevelArray([True, False, True, False, False, True], \
                                       starts=[10, 12, 15], sourceRegion=[10, 16], allowOverlaps=False)
        self._assertBinaryBpLevelArray([True, True, True, False, False, True], \
                                       starts=[10, 12, 15], ends=[12, 13, 16], sourceRegion=[10, 16], allowOverlaps=False)
        self._assertBinaryBpLevelArray([True, True, True, True, True, True], \
                                       ends=[0, 13, 16], sourceRegion=[10, 16], allowOverlaps=False)
        
        self._assertBinaryBpLevelArray([True, False, True, False, False, True], \
                                       starts=[10, 12, 15], vals=[1.0, 2.0, 4.0], sourceRegion=[10, 16], allowOverlaps=False)
        self._assertBinaryBpLevelArray([True, True, True, False, False, True], \
                                       starts=[10, 12, 15], ends=[12, 13, 16], vals=[1.0, 2.0, 4.0], sourceRegion=[10, 16], allowOverlaps=False)
        self._assertBinaryBpLevelArray([True, True, True, True, True, True], \
                                       ends=[0, 13, 16], vals=[nan, 1.0, 2.0], sourceRegion=[10, 16], allowOverlaps=False)
        
        self._assertBinaryBpLevelArray([True, True, True, True, True, True], \
                                       vals=[1.0, 2.0, 0.0, 0.0, nan, 3.0], sourceRegion=[10, 16], allowOverlaps=False)
        
        #allowOverlaps = True
        self._assertBinaryBpLevelArray([False, False, False, False, False, False], \
                                       starts=[], ends=[], sourceRegion=[10, 16], allowOverlaps=True)
        self._assertBinaryBpLevelArray([True, False, True, False, False, True], \
                                       starts=[10, 12, 12, 15], sourceRegion=[10, 16], allowOverlaps=True)
        self._assertBinaryBpLevelArray([True, True, True, True, False, False], \
                                       starts=[10, 11, 12], ends=[13, 12, 14], sourceRegion=[10, 16], allowOverlaps=True)
        self._assertBinaryBpLevelArray([True, True, True, True, True, True], \
                                       ends=[0, 13, 13, 16], sourceRegion=[10, 16], allowOverlaps=True)
        
        self._assertBinaryBpLevelArray([True, False, True, False, False, True], \
                                       starts=[10, 12, 12, 15], vals=[1.0, 2.0, 3.0, 4.0], sourceRegion=[10, 16], allowOverlaps=True)
        self._assertBinaryBpLevelArray([True, True, True, True, False, False], \
                                       starts=[10, 10, 12], ends=[13, 12, 14], vals=[1.0, 2.0, 4.0], sourceRegion=[10, 16], allowOverlaps=True)
        self._assertBinaryBpLevelArray([True, True, True, True, True, True], \
                                       ends=[0, 13, 13, 16], vals=[nan, 1.0, 1.5, 2.0], sourceRegion=[10, 16], allowOverlaps=True)
        
        tv = self._createTrackView(starts=None, ends=None, vals=[1.0, 2.0, 0.0, 0.0, nan, 3.0], strands=None, ids=None, edges=None, weights=None, extras=None, sourceRegion=[10, 16], allowOverlaps=True)
        self.assertRaises(ShouldNotOccurError, tv.getBinaryBpLevelArray)
        
        #Linked track format
        self._assertBinaryBpLevelArray([True, True, True, False, False, True], \
                                       starts=[10, 12, 15], ends=[12, 13, 16], vals=[1.0, 2.0, 4.0], strands=[True, False, True], ids=['a', 'b', 'c'], edges=[['b'], [''], ['']], weights=[[1.5], [nan], [nan]], sourceRegion=[10, 16], allowOverlaps=False)
    
    def testCoverageBpLevelArray(self):
        #allowOverlaps = False
        self._assertCoverageBpLevelArray([0, 0, 0, 0, 0, 0], \
                                       starts=[], ends=[], sourceRegion=[10,16], allowOverlaps=False)
        self._assertCoverageBpLevelArray([1, 0, 1, 0, 0, 1], \
                                       starts=[10, 12, 15], sourceRegion=[10, 16], allowOverlaps=False)
        self._assertCoverageBpLevelArray([1, 1, 1, 0, 0, 1], \
                                       starts=[10, 12, 15], ends=[12, 13, 16], sourceRegion=[10, 16], allowOverlaps=False)
        self._assertCoverageBpLevelArray([1, 1, 1, 1, 1, 1], \
                                       ends=[0, 13, 16], sourceRegion=[10, 16], allowOverlaps=False)
        
        self._assertCoverageBpLevelArray([1, 0, 1, 0, 0, 1], \
                                       starts=[10, 12, 15], vals=[1.0, 2.0, 4.0], sourceRegion=[10, 16], allowOverlaps=False)
        self._assertCoverageBpLevelArray([1, 1, 1, 0, 0, 1], \
                                       starts=[10, 12, 15], ends=[12, 13, 16], vals=[1.0, 2.0, 4.0], sourceRegion=[10, 16], allowOverlaps=False)
        self._assertCoverageBpLevelArray([1, 1, 1, 1, 1, 1], \
                                       ends=[0, 13, 16], vals=[nan, 1.0, 2.0], sourceRegion=[10, 16], allowOverlaps=False)
        
        self._assertCoverageBpLevelArray([1, 1, 1, 1, 1, 1], \
                                       vals=[1.0, 2.0, 0.0, 0.0, nan, 3.0], sourceRegion=[10, 16], allowOverlaps=False)
        
        #allowOverlaps = True
        self._assertCoverageBpLevelArray([0, 0, 0, 0, 0, 0], \
                                       starts=[], ends=[], sourceRegion=[10, 16], allowOverlaps=True)
        self._assertCoverageBpLevelArray([1, 0, 2, 0, 0, 1], \
                                       starts=[10, 12, 12, 15], sourceRegion=[10, 16], allowOverlaps=True)
        self._assertCoverageBpLevelArray([1, 2, 2, 1, 0, 0], \
                                       starts=[10, 11, 12], ends=[13, 12, 14], sourceRegion=[10, 16], allowOverlaps=True)
        self._assertCoverageBpLevelArray([1, 1, 1, 1, 1, 1], \
                                       ends=[0, 13, 13, 16], sourceRegion=[10, 16], allowOverlaps=True)
        
        self._assertCoverageBpLevelArray([1, 0, 2, 0, 0, True], \
                                       starts=[10, 12, 12, 15], vals=[1.0, 2.0, 3.0, 4.0], sourceRegion=[10, 16], allowOverlaps=True)
        self._assertCoverageBpLevelArray([2, 2, 2, 1, 0, 0], \
                                       starts=[10, 10, 12], ends=[13, 12, 14], vals=[1.0, 2.0, 4.0], sourceRegion=[10, 16], allowOverlaps=True)
        self._assertCoverageBpLevelArray([1, 1, 1, 1, 1, 1], \
                                       ends=[0, 13, 13, 16], vals=[nan, 1.0, 1.5, 2.0], sourceRegion=[10, 16], allowOverlaps=True)
        
        tv = self._createTrackView(starts=None, ends=None, vals=[1.0, 2.0, 0.0, 0.0, nan, 3.0], strands=None, ids=None, edges=None, weights=None, extras=None, sourceRegion=[10, 16], allowOverlaps=True)
        self.assertRaises(ShouldNotOccurError, tv.getCoverageBpLevelArray)
        
        #Linked track format
        self._assertCoverageBpLevelArray([1, 1, 1, 0, 0, 1], \
                                       starts=[10, 12, 15], ends=[12, 13, 16], vals=[1.0, 2.0, 4.0], strands=[True, False, True], ids=['a', 'b', 'c'], edges=[['b'], [''], ['']], weights=[[1.5], [nan], [nan]], sourceRegion=[10, 16], allowOverlaps=False)
    
    def testValueBpLevelArray(self):
        #allowOverlaps = False
        self._assertValueBpLevelArray([1.0, nan, 2.0, nan, nan, 4.0], \
                                       starts=[10, 12, 15], vals=[1.0, 2.0, 4.0], sourceRegion=[10, 16], allowOverlaps=False)
        self._assertValueBpLevelArray([1.0, 1.0, 2.0, nan, nan, 4.0], \
                                       starts=[10, 12, 15], ends=[12, 13, 16], vals=[1.0, 2.0, 4.0], sourceRegion=[10, 16], allowOverlaps=False)
        self._assertValueBpLevelArray([1.0, 1.0, 1.0, 2.0, 2.0, 2.0], \
                                       ends=[0, 13, 16], vals=[nan, 1.0, 2.0], sourceRegion=[10, 16], allowOverlaps=False)
        
        self._assertValueBpLevelArray([1.0, 2.0, 0.0, 0.0, nan, 3.0], \
                                       vals=[1.0 , 2.0, 0.0, 0.0, nan, 3.0], sourceRegion=[10, 16], allowOverlaps=False)
        
        #No values
        tv = self._createTrackView(starts=[10, 12, 15], ends=None, vals=None, strands=None, ids=None, edges=None, weights=None, extras=None, sourceRegion=[10, 16], allowOverlaps=True)
        self.assertRaises(AssertionError, tv.getValueBpLevelArray)
        
        #allowOverlaps = True
        self._assertValueBpLevelArray([1.0, nan, 0.0, nan, nan, 4.0], \
                                       starts=[10, 12, 12, 15], vals=[1.0, 2.0, -2.0, 4.0], sourceRegion=[10, 16], allowOverlaps=True)
        self._assertValueBpLevelArray([3.0, 3.0, 5.0, 4.0, nan, nan], \
                                       starts=[10, 10, 12], ends=[13, 12, 14], vals=[1.0, 2.0, 4.0], sourceRegion=[10, 16], allowOverlaps=True)
        self._assertValueBpLevelArray([1.0, 1.0, 1.0, 2.0, 2.0, 2.0], \
                                       ends=[0, 13, 13, 16], vals=[nan, 1.0, 1.5, 2.0], sourceRegion=[10, 16], allowOverlaps=True)
        
        tv = self._createTrackView(starts=None, ends=None, vals=[1.0, 2.0, 0.0, 0.0, nan, 3.0], strands=None, ids=None, edges=None, weights=None, extras=None, sourceRegion=[10, 16], allowOverlaps=True)
        self.assertRaises(ShouldNotOccurError, tv.getValueBpLevelArray)
        
        #Linked track format
        self._assertValueBpLevelArray([1.0, 1.0, 2.0, nan, nan, 4.0], \
                                       starts=[10, 12, 15], ends=[12, 13, 16], vals=[1.0, 2.0, 4.0], strands=[True, False, True], ids=['a', 'b', 'c'], edges=[['b'], [''], ['']], weights=[[1.5], [nan], [nan]], sourceRegion=[10, 16], allowOverlaps=False)
    
    def runTest(self):
        pass
        #self.testElementIterationWithOverlaps()
        #self.testAsNumpyArray()
    
if __name__ == "__main__":
    #TestTrackView().debug()
    unittest.main()
