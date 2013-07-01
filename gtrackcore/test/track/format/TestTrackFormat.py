import unittest

from gtrackcore.track.format.TrackFormat import TrackFormat
from gtrackcore.track.format.TrackFormat import TrackFormatReq

# NB: TrackFormat == TrackFormat is not tested

class TestTrackFormat(unittest.TestCase):
    def setUp(self):
        pass

    def _assertFunctions(self, tf, formatName, dense, valued, interval, linked, reprDense, strand, id, weighted, hasExtra, val='number', weights='number', extra=[]):
        self.assertEqual(dense, tf.isDense())
        
        self.assertEqual(valued, tf.isValued())
        if valued:
            self.assertEqual(TrackFormat.VAL_TYPE_NAME_DICT[val], tf.getValTypeName())
        
        self.assertEqual(interval, tf.isInterval())
        self.assertEqual(linked, tf.isLinked())
        
        if reprDense != None:
            self.assertEqual(reprDense, tf.reprIsDense())
        
        self.assertEqual(strand, tf.hasStrand())
        self.assertEqual(id, tf.hasId())        
        
        self.assertEqual(weighted, tf.isWeighted())
        if weighted:
            self.assertEqual(TrackFormat.VAL_TYPE_NAME_DICT[weights], tf.getWeightTypeName())
        
        self.assertEqual(hasExtra, tf.hasExtra())
        if extra:
            self.assertEqual(extra, tf.getExtraNames())

        if not str(tf).startswith('Requirement'):
            self.assertEqual(formatName, tf.getFormatName())
            #To test TrackFormatReq(name=formatName) on the standard formats in an easy way
            self.assertTrue(TrackFormatReq(name=formatName).isCompatibleWith(tf))

    def _assertTrackFormat(self, tf, start, end, val, strand, id, edges, weights, hasExtra, extra):
        if start and not end and not val and not edges:
            self._assertFunctions(tf, 'Points', dense=False, valued=False, interval=False, linked=False, \
                                  reprDense=False, strand=strand, id=id, weighted=weights, hasExtra=hasExtra, extra=extra)
        if start and not end and val and not edges:
            self._assertFunctions(tf, 'Valued points', dense=False, valued=True, interval=False, linked=False, \
                                  reprDense=False, strand=strand, id=id, weighted=weights, hasExtra=hasExtra, extra=extra)
        if start and end and not val and not edges:
            self._assertFunctions(tf, 'Segments', dense=False, valued=False, interval=True, linked=False, \
                                  reprDense=False, strand=strand, id=id, weighted=weights, hasExtra=hasExtra, extra=extra)
        if start and end and val and not edges:
            self._assertFunctions(tf, 'Valued segments', dense=False, valued=True, interval=True, linked=False, \
                                  reprDense=False, strand=strand, id=id, weighted=weights, hasExtra=hasExtra, extra=extra)
        if not start and end and not val and not edges:
            self._assertFunctions(tf, 'Genome partition', dense=True, valued=False, interval=True, linked=False, \
                                  reprDense=False, strand=strand, id=id, weighted=weights, hasExtra=hasExtra, extra=extra)
        if not start and end and val and not edges:
            self._assertFunctions(tf, 'Step function', dense=True, valued=True, interval=True, linked=False, \
                                  reprDense=False, strand=strand, id=id, weighted=weights, hasExtra=hasExtra, extra=extra)
        if not start and not end and val and not edges:
            self._assertFunctions(tf, 'Function', dense=True, valued=True, interval=False, linked=False, \
                                  reprDense=True, strand=strand, id=id, weighted=weights, hasExtra=hasExtra, extra=extra)
            
        if start and not end and not val and edges:
            self._assertFunctions(tf, 'Linked points', dense=False, valued=False, interval=False, linked=True, \
                                  reprDense=False, strand=strand, id=id, weighted=weights, hasExtra=hasExtra, extra=extra)
        if start and not end and val and edges:
            self._assertFunctions(tf, 'Linked valued points', dense=False, valued=True, interval=False, linked=True, \
                                  reprDense=False, strand=strand, id=id, weighted=weights, hasExtra=hasExtra, extra=extra)
        if start and end and not val and edges:
            self._assertFunctions(tf, 'Linked segments', dense=False, valued=False, interval=True, linked=True, \
                                  reprDense=False, strand=strand, id=id, weighted=weights, hasExtra=hasExtra, extra=extra)
        if start and end and val and edges:
            self._assertFunctions(tf, 'Linked valued segments', dense=False, valued=True, interval=True, linked=True, \
                                  reprDense=False, strand=strand, id=id, weighted=weights, hasExtra=hasExtra, extra=extra)
        if not start and end and not val and edges:
            self._assertFunctions(tf, 'Linked genome partition', dense=True, valued=False, interval=True, linked=True, \
                                  reprDense=False, strand=strand, id=id, weighted=weights, hasExtra=hasExtra, extra=extra)
        if not start and end and val and edges:
            self._assertFunctions(tf, 'Linked step function', dense=True, valued=True, interval=True, linked=True, \
                                  reprDense=False, strand=strand, id=id, weighted=weights, hasExtra=hasExtra, extra=extra)
        if not start and not end and val and edges:
            self._assertFunctions(tf, 'Linked function', dense=True, valued=True, interval=False, linked=True, \
                                  reprDense=True, strand=strand, id=id, weighted=weights, hasExtra=hasExtra, extra=extra)
        if not start and not end and not val and edges:
            self._assertFunctions(tf, 'Linked base pairs', dense=True, valued=False, interval=False, linked=True, \
                                  reprDense=True, strand=strand, id=id, weighted=weights, hasExtra=hasExtra, extra=extra)
        
    def testFormats(self):
        for start in [None, []]:
            for end in [None, []]:
                for val in [None, []]:
                    for strand in [None, []]:
                        for id,edges,weights in [(None,None,None), ([],None,None), ([],[],None), ([],[],[])]:
                            for extra in [None, {'a':[],'b':[]}]:
                                if [] in [start, end, val, edges]:
                                    tf = TrackFormat(start, end, val, strand, id, edges, weights, extra)
                                    self._assertTrackFormat(tf, start==[], end==[], val==[], strand==[], id==[], edges==[], weights==[], \
                                                            hasExtra=extra is not None, extra=extra.keys() if extra is not None else [])

    def _assertIsCompatibleWith(self, tfReq, reqList):
        for start in [None, []]:
            for end in [None, []]:
                for val in [None, []]:
                    for strand in [None, []]:
                        for id,edges,weights in [(None,None,None), ([],None,None), ([],[],None), ([],[],[])]:
                            for extra in [None, {'a':[],'b':[]}]:
                                if [] in [start, end, val]:
                                    tf = TrackFormat(start, end, val, strand, id, edges, weights, extra)
                                    propList = [tf.isDense(), tf.isValued(), tf.isInterval(), tf.isLinked(), tf.hasStrand(), tf.hasId(), tf.isWeighted(), tf.hasExtra(), \
                                                tf.getValTypeName() if tf.getValTypeName() != '' else False, \
                                                tf.getWeightTypeName() if tf.getWeightTypeName() != '' else False, \
                                                tf.getExtraNames() if tf.getExtraNames() != [] else False]
                                    isCompatible = (not False in [(r==None or r==p) for r,p in zip(reqList, propList)])
                                    self.assertEqual(isCompatible, tfReq.isCompatibleWith(tf))

    def _assertFormatsReqs(self, tfReq, dense, val, interval, linked, strand, id, weights, extra):
        valued = True if type(val) == str else val
        weighted = True if type(weights) == str else weights
        hasExtra = True if type(extra) == list else extra
        self._assertFunctions(tfReq, '', dense, valued, interval, linked, None, strand, id, weighted, hasExtra, val=val, weights=weights, extra=extra)
        reqList = [dense,valued,interval,linked,strand,id,weighted,hasExtra,\
                   TrackFormat.VAL_TYPE_NAME_DICT[val] if valued else val,\
                   TrackFormat.VAL_TYPE_NAME_DICT[weights] if weighted else weights,\
                   extra]
        self._assertIsCompatibleWith(tfReq, reqList)

    def testFormatsReqs(self):
        for dense in (False, True, None):
            for val in (False, 'number', 'category_vector', None):
                for interval in (False, True, None):
                    for linked in (False, True, None):
                        for strand in (False, True, None):
                            for id in (False, True, None):
                                if linked==True and id==False:
                                    continue
                                for weights in (False, 'tc', 'char_vector', None):
                                    if linked==False and weights not in [False, None]:
                                        continue
                                    for extra in (False, ['a','b'], None):
                                        tfReq = TrackFormatReq(dense=dense, val=val, interval=interval, linked=linked, \
                                                               strand=strand, id=id, weights=weights, extra=extra)
                                        self._assertFormatsReqs(tfReq, dense, val, interval, linked, strand, id, weights, extra)

    def testMerge(self):
        mergedTFR = TrackFormatReq.merge( TrackFormatReq(dense=False), TrackFormatReq(interval=True) )
        self.assertFalse(mergedTFR.isDense())
        self.assertTrue(mergedTFR.isInterval())
        
        mergedTFR = TrackFormatReq.merge( TrackFormatReq(dense=False, val='tc'), TrackFormatReq(interval=True, val='number') )
        self.assertEqual(None, mergedTFR)
        
        mergedTFR = TrackFormatReq.merge( TrackFormatReq(dense=False, weights='tc'), TrackFormatReq(interval=True, weights='number') )
        self.assertEqual(None, mergedTFR)
        
    def testValTypes(self):
        tf = TrackFormat.createInstanceFromPrefixList(['start', 'val'], 'float128', 2, 'float64', 1)
        
        self.assertTrue(tf.isValued(specificValType='mean_sd'))
        self.assertFalse(tf.isValued(specificValType='number'))
        
        self.assertEqual('Mean and std.dev.', tf.getValTypeName())
        self.assertEqual('Valued points', tf.getFormatName())
        
        tfq = TrackFormatReq(interval=False, val='tc')
        self.assertFalse(tfq.isCompatibleWith(tf))
        
    def testWeightTypes(self):
        tf = TrackFormat.createInstanceFromPrefixList(['id', 'edges', 'weights'], 'float64', 1, 'S8', 3)
        
        self.assertTrue(tf.isWeighted(specificWeightType='category_vector'))
        self.assertFalse(tf.isWeighted(specificWeightType='number'))

        self.assertEqual('Vector of categories', tf.getWeightTypeName())
        self.assertEqual('Linked base pairs', tf.getFormatName())
        
        tfq = TrackFormatReq(linked=True, weights='number')
        self.assertFalse(tfq.isCompatibleWith(tf))

    def testExtra(self):
        tf = TrackFormat.createInstanceFromPrefixList(['start', 'a', 'b', 'c'], 'float64', 1, 'float64', 1)
        self.assertTrue(tf.hasExtra(specificExtra='a'))
        self.assertFalse(tf.hasExtra(specificExtra='d'))
        
        self.assertEqual(['a','b','c'], tf.getExtraNames())
        
        tfq = TrackFormatReq(interval=False, extra=['a','b'])
        self.assertFalse(tfq.isCompatibleWith(tf))
        
    def testCompatibilityWithExceptions(self):
        tf = TrackFormat.createInstanceFromPrefixList(['start', 'val'], 'float64', 1, 'float64', 1)
        
        self.assertFalse(TrackFormatReq(interval=True, strand=True, val='number')\
                         .isCompatibleWith(tf))
        self.assertFalse(TrackFormatReq(interval=True, strand=True, val='number')\
                         .isCompatibleWith(tf, ['interval']))
        self.assertTrue(TrackFormatReq(interval=True, strand=True, val='number')\
                        .isCompatibleWith(tf, ['interval', 'hasStrand']))
        self.assertFalse(TrackFormatReq(interval=True, strand=True, val='tc')\
                         .isCompatibleWith(tf, ['interval', 'hasStrand']))
    
if __name__ == "__main__":
    unittest.main()
