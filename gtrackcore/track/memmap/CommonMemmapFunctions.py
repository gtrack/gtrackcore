import os
import numpy

def createMemmapFileFn(path, prefix, elementDim, dataTypeDim, dataType):
    return path + os.sep + prefix + \
        ( ('.' + str( max(1, elementDim)) ) if elementDim is not None else '' ) + \
        ( ('.' + str(dataTypeDim)) if dataTypeDim > 1 or elementDim is not None else '' ) + \
        '.' + dataType.replace('|', '')

def parseMemmapFileFn(fn):
    fn = os.path.basename(fn)
    splittedFn = fn.split('.')
    prefix = splittedFn[0]
    elementDim = int(splittedFn[1]) if len(splittedFn)==4 else None
    dtypeDim = int(splittedFn[-2]) if len(splittedFn) in [3,4] else 1
    dtype = splittedFn[-1]
    return prefix, elementDim, dtypeDim, dtype
    
def calcShape(fn, elementDim, dtypeDim, dtype):
    dTypeSize = numpy.dtype(dtype).itemsize
    elementSize = dTypeSize * (elementDim if elementDim is not None else 1) * dtypeDim
    shape = [(os.path.getsize(fn) / elementSize)] + \
             ([elementDim] if elementDim is not None else []) + \
             ([dtypeDim] if dtypeDim > 1 else [])
    return shape
    
def calcShapeFromMemmapFileFn(fn):
    prefix, elementDim, dtypeDim, dtype = parseMemmapFileFn(fn)
    return calcShape(fn, elementDim, dtypeDim, dtype)

def findEmptyVal(valDataType):
    if any(x in valDataType for x in ['str', 'S']):
        baseVal = ''
    elif 'int' in valDataType:
        from gtrackcore.util.CommonConstants import BINARY_MISSING_VAL
        baseVal = BINARY_MISSING_VAL
    elif 'float' in valDataType:
        baseVal = numpy.nan
    elif 'bool' in valDataType:
        baseVal = False
    else:
        from gtrackcore.util.CustomExceptions import ShouldNotOccurError
        raise ShouldNotOccurError('Error: valDataType (%s) not supported.' % valDataType)
    return baseVal