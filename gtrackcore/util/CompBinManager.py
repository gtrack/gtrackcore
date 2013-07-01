from gtrackcore.core.Config import Config
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.metadata.GenomeInfo import GenomeInfo
from gtrackcore.util.CommonFunctions import isIter

COMP_BIN_SIZE = Config.COMP_BIN_SIZE

class CompBinManager:
    ALLOW_COMP_BIN_SPLITTING = False    
    
    @staticmethod
    def splitUserBin(region):
        'Splits a region into several compBins, based on borders as defined by getCompBinSize'
        #assert( len(region) > 0 )
        start = (int(region.start) / CompBinManager.getCompBinSize()) * CompBinManager.getCompBinSize() #round off to nearest whole compBin border        
        compBins = []
    
        while start < region.end:
            part = GenomeRegion(region.genome, region.chr)
            end = start + CompBinManager.getCompBinSize()
            part.start =  max(start, region.start)
            part.end = min(end, region.end)
            compBins.append( part )
            start += CompBinManager.getCompBinSize()   
    
        return compBins

    @staticmethod
    def getIndexBinSize():
        return COMP_BIN_SIZE
    
    @staticmethod
    def getCompBinSize():
        return COMP_BIN_SIZE    

    @staticmethod
    def getBinNumber(pos):
        return pos / CompBinManager.getCompBinSize()

    @staticmethod
    def getPosFromBinNumber(binNum):
        return binNum * CompBinManager.getCompBinSize()

    @staticmethod
    def getOffset(pos, bin):
        return pos - (bin * CompBinManager.getCompBinSize())

    @staticmethod
    def isMemoBin(region):
        return CompBinManager.isCompBin(region)
        
        #if CompBinManager.ALLOW_COMP_BIN_SPLITTING:
        #    isCompBin = CompBinManager.isCompBin(region)
        #    return isCompBin
        #else:
        #    isChr = not hasattr(region, '__iter__') and any([region.chr, region.start, region.end] == [r.chr, r.start, r.end] \
        #                                                    for r in GenomeInfo.getChrRegs(region.genome))
        #    return isChr
        
    @staticmethod
    def isCompBin(region):
        if isIter(region):
            return False
        
        offsetOK = (CompBinManager.getOffset( region.start, CompBinManager.getBinNumber(region.start) ) == 0)
        lengthOK = (len(region) == min(CompBinManager.getCompBinSize(), GenomeInfo.getChrLen(region.genome, region.chr) - region.start))
        return offsetOK and lengthOK
    
    @staticmethod
    def getNumOfBins(region):
        #assert( len(region) > 0 )
        start = CompBinManager.getBinNumber(region.start)
        end = CompBinManager.getBinNumber(region.end - 1)        
        return end - start + 1
    
    @staticmethod
    def canBeSplitted(region):
        return CompBinManager.ALLOW_COMP_BIN_SPLITTING and CompBinManager.getNumOfBins(region) > 1
