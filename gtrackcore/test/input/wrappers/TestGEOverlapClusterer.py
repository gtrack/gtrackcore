import unittest
import sys
import numpy as np

from numpy import nan

from gtrackcore.core.Config import Config
from gtrackcore.input.wrappers.GEOverlapClusterer import GEOverlapClusterer
from gtrackcore.test.common.Asserts import assertDecorator, TestCaseWithImprovedAsserts
from gtrackcore.util.CommonConstants import BINARY_MISSING_VAL

MAX_CONCAT_LEN_FOR_OVERLAPPING_ELS = Config.MAX_CONCAT_LEN_FOR_OVERLAPPING_ELS

class TestGEOverlapClusterer(TestCaseWithImprovedAsserts):
    #def setUp(self):
    #    self.stdout = sys.stdout
    #    sys.stdout = open('/dev/null', 'w')
    #    
    #def tearDown(self):
    #    sys.stdout = sys.stdout
    
    def _assertClustering(self, removedList, origList, valDataType='float64', valDim=1):
        assertDecorator(GEOverlapClusterer, self.assertListsOrDicts, removedList, origList, valDataType, valDim)
        
    def testClustering(self):
        self._assertClustering([['A','chr1',0,10],['B','chr2',2,5]],\
                               [['A','chr1',0,10],['B','chr2',2,5]])
        self._assertClustering([['A','chr1',0,10],['A','chr2',2,5]],\
                               [['A','chr1',0,10],['A','chr2',2,5]])
        self._assertClustering([['A','chr1',0,10],['B','chr1',2,5]],\
                               [['A','chr1',0,10],['B','chr1',2,5]])

        self._assertClustering([['A','chr1',0,10]], \
                               [['A','chr1',0,10],['A','chr1',2,5]])
        self._assertClustering([['A','chr1',0,10]], \
                               [['A','chr1',0,10],['A','chr1',0,10]])
        
        self._assertClustering([['A','chr1',0,10],['A','chr1',10,15]],\
                               [['A','chr1',0,10],['A','chr1',10,15]])
        self._assertClustering([['A','chr1',0,15]],\
                               [['A','chr1',0,10],['A','chr1',9,15]])
        self._assertClustering([['A','chr1',0,0],['A','chr1',0,0]],\
                               [['A','chr1',0,0],['A','chr1',0,0]])
    
        self._assertClustering([['A','chr1',0,None],['A','chr1',10,None]],\
                               [['A','chr1',0,None],['A','chr1',10,None]])
        self._assertClustering([['A','chr1',10,None]],\
                               [['A','chr1',10,None],['A','chr1',10,None]])
        
        self._assertClustering([['A','chr1',None,10],['A','chr1',None,15]],\
                               [['A','chr1',None,10],['A','chr1',None,15]])
        self._assertClustering([['A','chr1',None,10],['A','chr1',None,10]],\
                               [['A','chr1',None,10],['A','chr1',None,10]])
        
        self._assertClustering([['A','chr1',0,10,{'val':3}]], \
                               [['A','chr1',0,10,{'val':3}],['A','chr1',0,10,{'val':3}]])
        self._assertClustering([['A','chr1',0,10,{'val':nan}]], \
                               [['A','chr1',0,10,{'val':3}],['A','chr1',0,10,{'val':4}]])
        
        self._assertClustering([['A','chr1',0,10,{'val':False}]], \
                               [['A','chr1',0,10,{'val':False}],['A','chr1',0,10,{'val':False}]], valDataType='int8')
        self._assertClustering([['A','chr1',0,10,{'val':BINARY_MISSING_VAL}]], \
                               [['A','chr1',0,10,{'val':False}],['A','chr1',0,10,{'val':True}]], valDataType='int8')
                
        self._assertClustering([['A','chr1',0,10,{'val':'a'}]], \
                               [['A','chr1',0,10,{'val':'a'}],['A','chr1',0,10,{'val':'a'}]], valDataType='S1')
        self._assertClustering([['A','chr1',0,10,{'val':''}]], \
                               [['A','chr1',0,10,{'val':'a'}],['A','chr1',0,10,{'val':'b'}]], valDataType='S1')
        
        self._assertClustering([['A','chr1',0,10,{'val':'aa'}]], \
                               [['A','chr1',0,10,{'val':'aa'}],['A','chr1',0,10,{'val':'aa'}]], valDataType='S')
        self._assertClustering([['A','chr1',0,10,{'val':'aa|b'}]], \
                               [['A','chr1',0,10,{'val':'aa'}],['A','chr1',0,10,{'val':'b'}]], valDataType='S')
        self._assertClustering([['A','chr1',0,10,{'val':'aa|b|c'}]], \
                               [['A','chr1',0,10,{'val':'b'}],['A','chr1',0,10,{'val':'aa'}],['A','chr1',0,10,{'val':'c'}]], valDataType='S')
        self._assertClustering([['A','chr1',0,10,{'val':'a|a|c'}]], \
                               [['A','chr1',0,10,{'val':'a'}],['A','chr1',0,10,{'val':'a'}],['A','chr1',0,10,{'val':'c'}]], valDataType='S')

        self._assertClustering([['A','chr1',0,10,{'val':[3,4]}]], \
                               [['A','chr1',0,10,{'val':[3,4]}],['A','chr1',0,10,{'val':[3,4]}]], valDim=2)
        self._assertClustering([['A','chr1',0,10,{'val':[0,0]}]], \
                               [['A','chr1',0,10,{'val':[3,4]}],['A','chr1',0,10,{'val':[4,4]}]], valDataType='int32', valDim=2)
        self._assertClustering([['A','chr1',0,10,{'val':[]}]], \
                               [['A','chr1',0,10,{'val':[3,4]}],['A','chr1',0,10,{'val':[4]}]], valDim=2)
        
        self._assertClustering([['A','chr1',0,10,{'val':[False,True]}]], \
                               [['A','chr1',0,10,{'val':[False,True]}],['A','chr1',0,10,{'val':[False,True]}]], valDataType='int8', valDim=2)
        self._assertClustering([['A','chr1',0,10,{'val':[BINARY_MISSING_VAL,BINARY_MISSING_VAL]}]], \
                               [['A','chr1',0,10,{'val':[False,True]}],['A','chr1',0,10,{'val':[True,True]}]], valDataType='int8', valDim=2)
        self._assertClustering([['A','chr1',0,10,{'val':[]}]], \
                               [['A','chr1',0,10,{'val':[False,True]}],['A','chr1',0,10,{'val':[True]}]], valDataType='int8', valDim=2)
                
        self._assertClustering([['A','chr1',0,10,{'val':['a','b']}]], \
                               [['A','chr1',0,10,{'val':['a','b']}],['A','chr1',0,10,{'val':['a','b']}]], valDataType='S1', valDim=2)
        self._assertClustering([['A','chr1',0,10,{'val':['','']}]], \
                               [['A','chr1',0,10,{'val':['a','b']}],['A','chr1',0,10,{'val':['b','b']}]], valDataType='S1', valDim=2)
        self._assertClustering([['A','chr1',0,10,{'val':[]}]], \
                               [['A','chr1',0,10,{'val':['a','b']}],['A','chr1',0,10,{'val':['b']}]], valDataType='S1', valDim=2)
        
        self._assertClustering([['A','chr1',0,10,{'val':['aa','b']}]], \
                               [['A','chr1',0,10,{'val':['aa','b']}],['A','chr1',0,10,{'val':['aa','b']}]], valDataType='S', valDim=2)
        self._assertClustering([['A','chr1',0,10,{'val':['','']}]], \
                               [['A','chr1',0,10,{'val':['aa','b']}],['A','chr1',0,10,{'val':['aa','c']}]], valDataType='S', valDim=2)
        self._assertClustering([['A','chr1',0,10,{'val':[]}]], \
                               [['A','chr1',0,10,{'val':['aa','b']}],['A','chr1',0,10,{'val':['aa']}]], valDataType='S', valDim=2)
        
        self._assertClustering([['A','chr1',0,10,{'val':np.array([3,4])}]], \
                               [['A','chr1',0,10,{'val':np.array([3,4])}],['A','chr1',0,10,{'val':np.array([3,4])}]], valDim=2)
        self._assertClustering([['A','chr1',0,10,{'val':np.array([False,True])}]], \
                               [['A','chr1',0,10,{'val':np.array([False,True])}],['A','chr1',0,10,{'val':np.array([False,True])}]], valDataType='int8', valDim=2)
        self._assertClustering([['A','chr1',0,10,{'val':np.array(['a','b'])}]], \
                               [['A','chr1',0,10,{'val':np.array(['a','b'])}],['A','chr1',0,10,{'val':np.array(['a','b'])}]], valDataType='S1', valDim=2)
        self._assertClustering([['A','chr1',0,10,{'val':np.array(['aa','b'])}]], \
                               [['A','chr1',0,10,{'val':np.array(['aa','b'])}],['A','chr1',0,10,{'val':np.array(['aa','b'])}]], valDataType='S', valDim=2)
        self._assertClustering([['A','chr1',0,10,{'val':['','']}]], \
                               [['A','chr1',0,10,{'val':np.array(['aa','b'])}],['A','chr1',0,10,{'val':np.array(['aa','c'])}]], valDataType='S', valDim=2)
        self._assertClustering([['A','chr1',0,10,{'val':[]}]], \
                               [['A','chr1',0,10,{'val':np.array(['aa','b'])}],['A','chr1',0,10,{'val':np.array(['aa'])}]], valDataType='S', valDim=2)
        
        self._assertClustering([['A','chr1',0,10,{'strand':True}]], \
                               [['A','chr1',0,10,{'strand':True}],['A','chr1',0,10,{'strand':True}]])
        self._assertClustering([['A','chr1',0,10,{'strand':BINARY_MISSING_VAL}]], \
                               [['A','chr1',0,10,{'strand':True}],['A','chr1',0,10,{'strand':False}]])
        
        self._assertClustering([['A','chr1',0,10,{'id':'a1'}]], \
                               [['A','chr1',0,10,{'id':'a1'}],['A','chr1',0,10,{'id':'a1'}]])
        self._assertClustering([['A','chr1',0,10,{'id':'a2|a1'}]], \
                               [['A','chr1',0,10,{'id':'a2'}],['A','chr1',0,10,{'id':'a1'}]])
        
        self._assertClustering([['A','chr1',0,10,{'edges':[]}]], \
                               [['A','chr1',0,10,{'edges':['a1','a2']}],['A','chr1',0,10,{'edges':['a1','a2']}]])
        self._assertClustering([['A','chr1',0,10,{'edges':[]}]], \
                               [['A','chr1',0,10,{'edges':['a1','a2']}],['A','chr1',0,10,{'edges':['a1','a3']}]])
        self._assertClustering([['A','chr1',0,10,{'edges':[]}],['A','chr1',20,30,{'edges':[]}]], \
                               [['A','chr1',0,10,{'edges':['a1','a2']}],['A','chr1',20,30,{'edges':['a1','a3']}]])
        
        self._assertClustering([['A','chr1',0,10,{'weights':[]}]], \
                               [['A','chr1',0,10,{'weights':[1,2]}],['A','chr1',0,10,{'weights':[1,2]}]])
        self._assertClustering([['A','chr1',0,10,{'weights':[]}]], \
                               [['A','chr1',0,10,{'weights':[1,2]}],['A','chr1',0,10,{'weights':[1,3]}]])
        self._assertClustering([['A','chr1',0,10,{'weights':[]}],['A','chr1',20,30,{'weights':[]}]], \
                               [['A','chr1',0,10,{'weights':[1,2]}],['A','chr1',20,30,{'weights':[1,3]}]])
        
        self._assertClustering([['A','chr1',0,10,{'name':'a1'}]], \
                               [['A','chr1',0,10,{'name':'a1'}],['A','chr1',0,10,{'name':'a1'}]])
        self._assertClustering([['A','chr1',0,10,{'name':'a2|a1'}]], \
                               [['A','chr1',0,10,{'name':'a2'}],['A','chr1',0,10,{'name':'a1'}]])
        self._assertClustering([['A','chr1',0,10,{'name':'a2|a2|a1'}]], \
                               [['A','chr1',0,10,{'name':'a2'}],['A','chr1',0,10,{'name':'a2'}],['A','chr1',0,10,{'name':'a1'}]])
        
        self._assertClustering([['A','chr1',0,10,{'name':'a1'}]], \
                               [['A','chr1',0,10,{'name':'a1'}]] * MAX_CONCAT_LEN_FOR_OVERLAPPING_ELS)
        self._assertClustering([['A','chr1',0,10,{'name':'a1|...'}]], \
                               [['A','chr1',0,10,{'name':'a1'}]] + [['A','chr1',0,10,{'name':'a2'}]] * MAX_CONCAT_LEN_FOR_OVERLAPPING_ELS)
    def runTest(self):
        #pass
        self.testClustering()
    
if __name__ == "__main__":
    #TestGEOverlapClusterer().debug()
    unittest.main()