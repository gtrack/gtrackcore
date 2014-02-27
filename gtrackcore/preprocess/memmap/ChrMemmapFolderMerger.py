import os
import numpy as np
import shutil
import sys

from gtrackcore.preprocess.PreProcMetaDataCollector import PreProcMetaDataCollector
from gtrackcore.track.memmap.CommonMemmapFunctions import createMemmapFileFn, parseMemmapFileFn, findEmptyVal
from gtrackcore.track.pytables.TrackSource import TrackSource
from gtrackcore.util.CommonFunctions import get_dir_path
from gtrackcore.util.CustomExceptions import EmptyGESourceError

class ChrMemmapFolderMerger(object):
    @staticmethod
    def _commonAppendDimension(origArray, delta, val, allowedDims, dimIdx, stackMethod):
        origShape = list(origArray.shape)
        assert len(origShape) in allowedDims, 'Dimension of array, %s, is not in the correct range: %s' % (len(origShape), allowedDims)
        appendShape = origShape
        appendShape[dimIdx] = delta
        appendArray = np.zeros(shape=appendShape, dtype=origArray.dtype)
        val = origArray.dtype.type(val)
        appendArray[:] = val
        return stackMethod((origArray, appendArray))
    
    @staticmethod
    def appendDepth(origArray, delta, val):
        return ChrMemmapFolderMerger._commonAppendDimension(origArray, delta, val, [3], 2, np.dstack)
    
    @staticmethod
    def appendHeight(origArray, delta, val):
        return ChrMemmapFolderMerger._commonAppendDimension(origArray, delta, val, [2, 3], 1, np.hstack)
        
    @staticmethod
    def _commonReshapeArray(a, delta, appendFunc):
        return appendFunc(a, delta, findEmptyVal(str(a.dtype)))
    
    @staticmethod
    def _commonReshapeArrays(a1, a2, dimIdx, appendFunc):
        delta = a2.shape[dimIdx]-a1.shape[dimIdx]
        if delta > 0:
            a1 = ChrMemmapFolderMerger._commonReshapeArray(a1, delta, appendFunc)
        elif delta < 0:
            a2 = ChrMemmapFolderMerger._commonReshapeArray(a2, -delta, appendFunc)
        return a1, a2
    
    @staticmethod
    def mergeArrays(a1, a2):
        assert len(a1.shape) == len(a2.shape) and len(a1.shape) <= 3
        assert a1.dtype.type == a2.dtype.type
        
        if len(a1.shape) == 3:
            a1, a2 = ChrMemmapFolderMerger._commonReshapeArrays(a1, a2, 2, ChrMemmapFolderMerger.appendDepth)
                
        if len(a1.shape) >= 2:
            a1, a2 = ChrMemmapFolderMerger._commonReshapeArrays(a1, a2, 1, ChrMemmapFolderMerger.appendHeight)
        
        return np.r_[a1, a2]
        
    @staticmethod
    def _existingChrIter(path, chrList):
        for chr in chrList:
            chrDirPath = path + os.sep + chr
            if not os.path.exists(chrDirPath) or not os.path.isdir(chrDirPath):
                continue
            yield chr
    
    @staticmethod
    def merge(genome, trackName, allowOverlaps):
        path = get_dir_path(genome, trackName, allow_overlaps=allowOverlaps)

        collector = PreProcMetaDataCollector(genome, trackName)
        chrList = collector.getPreProcessedChrs(allowOverlaps)
        if not collector.getTrackFormat().reprIsDense():
            chrList = sorted(chrList)
        
        existingChrList = [chr for chr in ChrMemmapFolderMerger._existingChrIter(path, chrList)]
        if len(existingChrList) == 0:
            raise EmptyGESourceError('No data lines has been read from source file (probably because it is empty).')
            
        firstChrTrackData = TrackSource().getTrackData(trackName, genome, existingChrList[0], allowOverlaps, forceChrFolders=True)
        arrayList = firstChrTrackData.keys()
        for arrayName in arrayList:
            mergedArray = firstChrTrackData[arrayName][:]
            elementDim, dtypeDim = parseMemmapFileFn(firstChrTrackData[arrayName].filename)[1:3]
            del firstChrTrackData[arrayName]
            
            for chr in existingChrList[1:]:
                chrTrackData = TrackSource().getTrackData(trackName, genome, chr, allowOverlaps, forceChrFolders=True)
            
                mergedArray = ChrMemmapFolderMerger.mergeArrays(mergedArray, np.array(chrTrackData[arrayName][:]))
                elementDimNew, dtypeDimNew = parseMemmapFileFn(chrTrackData[arrayName].filename)[1:3]
                elementDim = max(elementDim, elementDimNew)
                dtypeDim = max(dtypeDim, dtypeDimNew)
                
                del chrTrackData[arrayName]
            
            mergedFn = createMemmapFileFn(path, arrayName, elementDim, dtypeDim, str(mergedArray.dtype))
            
            f = np.memmap(mergedFn, dtype=mergedArray.dtype, mode='w+', shape=mergedArray.shape)
            f[:] = mergedArray
            f.flush()
            del f
            del mergedArray
                    
if __name__ == "__main__":
    if not len(sys.argv) == 4:
        print 'Syntax: python ChrMemmapFolderMerger.py genome trackName:subType allowOverlaps'
        sys.exit(0)
        
    genome = sys.argv[1]
    trackName = sys.argv[2].split(':')
    allowOverlaps = eval(sys.argv[3])
    assert allowOverlaps in [False, True]
    
    ChrMemmapFolderMerger.merge(genome, trackName, allowOverlaps)
