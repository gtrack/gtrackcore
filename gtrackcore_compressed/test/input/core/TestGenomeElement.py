import unittest
from collections import OrderedDict

from gtrackcore_compressed.input.core.GenomeElement import GenomeElement

class TestGenomeElement(unittest.TestCase):
    def setUp(self):
        pass
    
    def testAssignAndRetrieve(self):
        e = GenomeElement('TestGenome', start=5, val=1.0, extra={'a':1,'b':2}, orderedExtraKeys=['a','b'])
        self.assertEqual(e.genome, 'TestGenome')
        self.assertEqual(e.chr, None)
        self.assertEqual(e.start, 5)
        self.assertEqual(e.end, None)
        self.assertEqual(e.val, 1.0)
        self.assertEqual(e.strand, None)
        self.assertEqual(e.a, 1)
        self.assertEqual(e.b, 2)
        self.assertEqual(e.extra, {'a':1,'b':2})
        self.assertEqual(e.orderedExtraKeys, ['a', 'b'])
        
        e = GenomeElement('TestGenome', a=1)
        e.b = 2
        self.assertEqual(e.genome, 'TestGenome')
        self.assertEqual(e.a, 1)
        self.assertEqual(e.b, 2)
        self.assertEqual(e.extra, {'a':1,'b':2})
        self.assertEqual(e.orderedExtraKeys, ['a', 'b'])
        
        self.assertRaises(AttributeError, lambda : e.nonExisting)
        
        #self.assertEqual(e.get('start'), e.start)
        #self.assertEqual(e.get('end'), e.end)

    def testContains(self):
        self.assertTrue(GenomeElement('TestGenome','chr21',10,100).contains( \
                        GenomeElement('TestGenome','chr21',10,100)))
        
        self.assertTrue(GenomeElement('TestGenome','chr21',10,100).contains( \
                        GenomeElement('TestGenome','chr21',20,80)))
        
        self.assertFalse(GenomeElement('TestGenome','chr21',10,100).contains( \
                        GenomeElement('TestGenome','chr21',10,101)))
        
        self.assertFalse(GenomeElement('TestGenome','chr21',10,100).contains( \
                        GenomeElement('TestGenome','chr21',9,100)))
        
        self.assertFalse(GenomeElement('TestGenome','chr21',10,100).contains( \
                        GenomeElement('TestGenome','chr21',9,101)))
        
        self.assertFalse(GenomeElement('TestGenome','chr21',10,100).contains( \
                        GenomeElement('TestGenome','chr21',0,10)))

        self.assertFalse(GenomeElement('TestGenome','chr21',10,100).contains( \
                        GenomeElement('TestGenome','chrM',20,80)))

    def testOverlaps(self):
        self.assertTrue(GenomeElement('TestGenome','chr21',10,100).overlaps( \
                        GenomeElement('TestGenome','chr21',10,100)))
        
        self.assertTrue(GenomeElement('TestGenome','chr21',10,100).overlaps( \
                        GenomeElement('TestGenome','chr21',20,80)))
        
        self.assertTrue(GenomeElement('TestGenome','chr21',10,100).overlaps( \
                        GenomeElement('TestGenome','chr21',10,101)))
        
        self.assertTrue(GenomeElement('TestGenome','chr21',10,100).overlaps( \
                        GenomeElement('TestGenome','chr21',9,100)))
        
        self.assertTrue(GenomeElement('TestGenome','chr21',10,100).overlaps( \
                        GenomeElement('TestGenome','chr21',9,101)))
        
        self.assertFalse(GenomeElement('TestGenome','chr21',10,100).overlaps( \
                        GenomeElement('TestGenome','chr21',0,10)))

        self.assertFalse(GenomeElement('TestGenome','chr21',10,100).overlaps( \
                        GenomeElement('TestGenome','chr21',100,110)))

        self.assertFalse(GenomeElement('TestGenome','chr21',10,100).overlaps( \
                        GenomeElement('TestGenome','chrM',20,80)))

    def testTouches(self):
        self.assertFalse(GenomeElement('TestGenome','chr21',10,100).touches( \
                        GenomeElement('TestGenome','chr21',10,100)))
        
        self.assertFalse(GenomeElement('TestGenome','chr21',10,100).touches( \
                        GenomeElement('TestGenome','chr21',20,80)))
        
        self.assertFalse(GenomeElement('TestGenome','chr21',10,100).touches( \
                        GenomeElement('TestGenome','chr21',10,101)))
        
        self.assertFalse(GenomeElement('TestGenome','chr21',10,100).touches( \
                        GenomeElement('TestGenome','chr21',9,100)))
        
        self.assertFalse(GenomeElement('TestGenome','chr21',10,100).touches( \
                        GenomeElement('TestGenome','chr21',9,101)))
        
        self.assertTrue(GenomeElement('TestGenome','chr21',10,100).touches( \
                        GenomeElement('TestGenome','chr21',0,10)))

        self.assertTrue(GenomeElement('TestGenome','chr21',10,100).touches( \
                        GenomeElement('TestGenome','chr21',100,110)))
        
        self.assertFalse(GenomeElement('TestGenome','chr21',10,100).touches( \
                        GenomeElement('TestGenome','chr21',0,9)))

        self.assertFalse(GenomeElement('TestGenome','chr21',10,100).touches( \
                        GenomeElement('TestGenome','chr21',101,110)))

        self.assertFalse(GenomeElement('TestGenome','chr21',10,100).touches( \
                        GenomeElement('TestGenome','chrM',20,80)))

    def testExclude(self):
        self.assertEqual([GenomeElement('TestGenome','chr21',100,200)],\
                         GenomeElement('TestGenome','chr21',100,200).exclude( GenomeElement('TestGenome','chr21',90,100) ))
        self.assertEqual([GenomeElement('TestGenome','chr21',100,200)],\
                         GenomeElement('TestGenome','chr21',100,200).exclude( GenomeElement('TestGenome','chr21',200,210) ))
        self.assertEqual([GenomeElement('TestGenome','chr21',100,200)],\
                         GenomeElement('TestGenome','chr21',100,200).exclude( GenomeElement('TestGenome','chrM',100,110) ))

        self.assertEqual([GenomeElement('TestGenome','chr21',110,200)],\
                         GenomeElement('TestGenome','chr21',100,200).exclude( GenomeElement('TestGenome','chr21',100,110) ))
        self.assertEqual([GenomeElement('TestGenome','chr21',110,200)],\
                         GenomeElement('TestGenome','chr21',100,200).exclude( GenomeElement('TestGenome','chr21',90,110) ))
        
        self.assertEqual([GenomeElement('TestGenome','chr21',100,190)],\
                         GenomeElement('TestGenome','chr21',100,200).exclude( GenomeElement('TestGenome','chr21',190,200) ))
        self.assertEqual([GenomeElement('TestGenome','chr21',100,190)],\
                         GenomeElement('TestGenome','chr21',100,200).exclude( GenomeElement('TestGenome','chr21',190,210) ))
        
        self.assertEqual([],\
                         GenomeElement('TestGenome','chr21',100,200).exclude( GenomeElement('TestGenome','chr21',90,210) ))
        
        self.assertEqual([GenomeElement('TestGenome','chr21',100,140), GenomeElement('TestGenome','chr21',160,200)],\
                         GenomeElement('TestGenome','chr21',100,200).exclude( GenomeElement('TestGenome','chr21',140,160) ))

    def testExtend(self):
        self.assertEqual(GenomeElement('TestGenome','chr21',100,200),\
                         GenomeElement('TestGenome','chr21',100,200).extend( 0 ))

        self.assertEqual(GenomeElement('TestGenome','chr21',0,200),\
                         GenomeElement('TestGenome','chr21',100,200).extend( -100 ))
        self.assertEqual(GenomeElement('TestGenome','chr21',-100,200),\
                         GenomeElement('TestGenome','chr21',100,200).extend( -200, ensureValidity=False ))
        self.assertEqual(GenomeElement('TestGenome','chr21',0,200),\
                         GenomeElement('TestGenome','chr21',100,200).extend( -200, ensureValidity=True ))

        self.assertEqual(GenomeElement('TestGenome','chr21',100,300),\
                         GenomeElement('TestGenome','chr21',100,200).extend( 100 ))
        self.assertEqual(GenomeElement('TestGenome','chr21',100,50000200),\
                         GenomeElement('TestGenome','chr21',100,200).extend( 50000000, ensureValidity=False ))
        self.assertEqual(GenomeElement('TestGenome','chr21',100,46944323),\
                         GenomeElement('TestGenome','chr21',100,200).extend( 50000000, ensureValidity=True ))        

    def testEqual(self):
        self.assertEqual(GenomeElement('TestGenome','chr21',10,100,5,True,'id',['id2','id3'],[5,6],extra={'source':'source'}),
                         GenomeElement('TestGenome','chr21',10,100,5,True,'id',['id2','id3'],[5,6],extra={'source':'source'}))

        self.assertNotEqual(GenomeElement('TestGenome','chr21',10,100,5,True,'id',['id2','id3'],[5,6],extra={'source':'source'}),
                            GenomeElement('NCBI46','chr21',10,100,5,True,'id',['id2','id3'],[5,6],extra={'source':'source'}))

        self.assertNotEqual(GenomeElement('TestGenome','chr21',10,100,5,True,'id',['id2','id3'],[5,6],extra={'source':'source'}),
                            GenomeElement('TestGenome','chrM',10,100,5,True,'id',['id2','id3'],[5,6],extra={'source':'source'}))

        self.assertNotEqual(GenomeElement('TestGenome','chr21',10,100,5,True,'id',['id2','id3'],[5,6],extra={'source':'source'}),
                            GenomeElement('TestGenome','chr21',20,100,5,True,'id',['id2','id3'],[5,6],extra={'source':'source'}))

        self.assertNotEqual(GenomeElement('TestGenome','chr21',10,100,5,True,'id',['id2','id3'],[5,6],extra={'source':'source'}),
                            GenomeElement('TestGenome','chr21',10,110,5,True,'id',['id2','id3'],[5,6],extra={'source':'source'}))

        self.assertNotEqual(GenomeElement('TestGenome','chr21',10,100,5,True,'id',['id2','id3'],[5,6],extra={'source':'source'}),
                            GenomeElement('TestGenome','chr21',10,100,6,True,'id',['id2','id3'],[5,6],extra={'source':'source'}))

        self.assertNotEqual(GenomeElement('TestGenome','chr21',10,100,5,True,'id',['id2','id3'],[5,6],extra={'source':'source'}),
                            GenomeElement('TestGenome','chr21',10,100,5,False,'id',['id2','id3'],[5,6],extra={'source':'source'}))

        self.assertNotEqual(GenomeElement('TestGenome','chr21',10,100,5,True,'id',['id2','id3'],[5,6],extra={'source':'source'}),
                            GenomeElement('TestGenome','chr21',10,100,5,True,'id4',['id2','id3'],[5,6],extra={'source':'source'}))

        self.assertNotEqual(GenomeElement('TestGenome','chr21',10,100,5,True,'id',['id2','id3'],[5,6],extra={'source':'source'}),
                            GenomeElement('TestGenome','chr21',10,100,5,True,'id',['id2','id4'],[5,6],extra={'source':'source'}))

        self.assertNotEqual(GenomeElement('TestGenome','chr21',10,100,5,True,'id',['id2','id3'],[5,6],extra={'source':'source'}),
                            GenomeElement('TestGenome','chr21',10,100,5,True,'id',['id2','id3'],[5,7],extra={'source':'source'}))

        self.assertNotEqual(GenomeElement('TestGenome','chr21',10,100,5,True,'id',['id2','id3'],[5,6],extra={'source':'source'}),
                            GenomeElement('TestGenome','chr21',10,100,5,True,'id',['id2','id3'],[5,6],extra={'source':'source', 'other':'value'}))

if __name__ == "__main__":
    unittest.main()