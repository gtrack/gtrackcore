import numpy as np
import os

from stat import S_IRWXU, S_IRWXG, S_IROTH

from gtrackcore_compressed.preprocess.memmap.GEParseFunctions import getStart, getEnd, getStrand, getVal, getId, getEdges, \
                                                      getWeights, getNone, GetExtra, \
                                                      writeNoSlice, writeSliceFromFront
from gtrackcore_compressed.track.memmap.CommonMemmapFunctions import createMemmapFileFn, findEmptyVal, calcShapeFromMemmapFileFn
from gtrackcore_compressed.util.CommonFunctions import product
from gtrackcore_compressed.util.CustomExceptions import ShouldNotOccurError, InvalidFormatError

class OutputFile(object):
    def _setup(self, prefix, thisPrefix, parseFunc, writeFunc, elementDim, dataType, dataTypeDim, setEmptyVal):
        if prefix == thisPrefix:
            self._parseFunc = parseFunc
            self._writeFunc = writeFunc
            self._elementDim = elementDim
            self._dataType = dataType
            self._dataTypeDim = dataTypeDim
            self._setEmptyVal = setEmptyVal
    
    def __init__(self, path, prefix, size, valDataType='float64', valDim=1, weightDataType='float64', weightDim=1, maxNumEdges=0, maxStrLens={}, allowAppend=True):
        assert valDim >= 1 and weightDim >= 1
        
        if valDataType == 'S':
            valDataType = 'S' + str(max(2, maxStrLens['val']))
        if weightDataType == 'S':
            weightDataType = 'S' + str(max(2, maxStrLens['weights']))
            
        self._setup(prefix, 'start', getStart, writeNoSlice, None, 'int32', 1, False)
        self._setup(prefix, 'end', getEnd, writeNoSlice, None, 'int32', 1, False)
        self._setup(prefix, 'strand', getStrand, writeNoSlice, None, 'int8', 1, False)
        self._setup(prefix, 'val', getVal, writeNoSlice, None, valDataType, valDim, True)
        self._setup(prefix, 'id', getId, writeNoSlice, None, 'S' + str(maxStrLens.get('id')), 1, False)
        self._setup(prefix, 'edges', getEdges, writeSliceFromFront, maxNumEdges, 'S' + str(maxStrLens.get('edges')), 1, False)
        self._setup(prefix, 'weights', getWeights, writeSliceFromFront, maxNumEdges, weightDataType, weightDim, True)
        self._setup(prefix, 'leftIndex', getNone, writeNoSlice, None, 'int32', 1, False)
        self._setup(prefix, 'rightIndex', getNone, writeNoSlice, None, 'int32', 1, False)
        
        if not hasattr(self, '_parseFunc'):
            self._geParseClass = GetExtra(prefix)
            self._setup(prefix, prefix, self._geParseClass.parse, writeNoSlice, None, 'S' + str(maxStrLens.get(prefix)), 1, False)

        # If there is one number in the path, it is the data type dimension.
        # Only one value is allowed per element, no extra dimensions are added
        # to the array and the element dimension is None.
        #
        # Example: val.4.float64 contains, per element, a vector of 4 numbers.
        #          The shape is (n,4) for n elements.
        #
        # If there are two numbers in the path, the first is the maximal element
        # dimension and the second is the data type dimension.
        #
        # Example: weights.3.4.float64 contains, per element, at most 3 vectors
        #          of 4 numbers each. The shape is (n,3,4) for n elements.
        
        self._fn = createMemmapFileFn(path, prefix, self._elementDim, self._dataTypeDim, self._dataType)
        self._index = 0
        
        shape = [size] + \
                 ([max(1, self._elementDim)] if self._elementDim is not None else []) + \
                 ([self._dataTypeDim] if self._dataTypeDim > 1 else [])
        
        append = os.path.exists(self._fn)
        if append:
            if not allowAppend:
                raise InvalidFormatError('Error: different genome element sources (e.g. different input files) tries to write to index file for the same chromosome (%s). This is probably caused by different files in the same folder containing elements from the same chromosome.' % self._fn)
            
            try:
                f = np.memmap( self._fn, dtype=self._dataType, mode='r+' )
                self._index = len(f) / product(shape[1:])
                del f

                existingShape = calcShapeFromMemmapFileFn(self._fn)
                self._contents = np.array( np.memmap(self._fn, dtype=self._dataType, mode='r+', shape=tuple(existingShape)) )
                self._contents = np.r_[self._contents, np.zeros( dtype=self._dataType, shape=tuple(shape) )]
            except Exception:
                print 'Error when opening file: ', self._fn
                raise
        else:
            self._contents = np.zeros( dtype=self._dataType, shape=tuple(shape) )
            
        if not append and self._setEmptyVal:
            self._contents[:] = findEmptyVal(self._dataType)
        
    def __len__(self):
        return len(self._contents)
    
    def close(self):
        memmapFile = np.memmap(self._fn, dtype=self._dataType, mode='w+', shape=self._contents.shape)
        memmapFile[:] = self._contents
        memmapFile.flush()
        os.chmod(self._fn, S_IRWXU|S_IRWXG|S_IROTH)
        
        self._contents = None

    def writeElement(self, genomeElement):
        self._writeFunc(self._contents, self._index, genomeElement, self._parseFunc)
        self._index += 1

    def write(self, value):
        self._contents[self._index] = value
        self._index += 1
        
    def writeRawSlice(self, genomeElement):
        "Only works correctly for some files"
        assert self._writeFunc == writeNoSlice

        slice = self._parseFunc(genomeElement)
        assert slice.dtype == np.dtype(self._dataType), \
            'Datatypes do not match: %s != %s' % (str(slice.dtype), self._dataType)
        
        self._contents[self._index:self._index+len(slice)] = slice
        self._index += len(slice)
        
    def sort(self, sortOrder=None):
        if sortOrder is None:
            sortOrder = self._contents.argsort()
            self._contents = self._contents[sortOrder]
            return sortOrder
        else:
            self._contents = self._contents[sortOrder]
        
    def getContents(self):
        return self._contents
