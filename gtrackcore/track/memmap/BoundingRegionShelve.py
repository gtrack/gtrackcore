import os

from collections import namedtuple, OrderedDict
from bisect import bisect_right

import gtrackcore.third_party.safeshelve as safeshelve

from gtrackcore.metadata.GenomeInfo import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.util.CustomExceptions import InvalidFormatError, OutsideBoundingRegionError, \
                                         BoundingRegionsNotAvailableError
from gtrackcore.util.CompBinManager import CompBinManager
from gtrackcore.util.CommonFunctions import createDirPath, ensurePathExists

BoundingRegionInfo = namedtuple('BoundingRegionInfo', \
                                ['start', 'end', 'startIdx', 'endIdx', 'startBinIdx', 'endBinIdx'])
BrInfoHolder = namedtuple('BrInfoHolder', ['brStarts', 'brInfos'])

BR_SHELVE_FILE_NAME = 'boundingRegions.shelve'

def isBoundingRegionFileName(fn):
    return fn == BR_SHELVE_FILE_NAME
    
class BoundingRegionShelve(object):
    def __init__(self, genome, trackName, allowOverlaps):
        assert allowOverlaps in [False, True]
        
        self._genome = genome
        self._trackName = trackName
        
        self._fn = createDirPath(trackName, genome, allowOverlaps=allowOverlaps) + os.sep + BR_SHELVE_FILE_NAME
        self._contents = {} #None
        self._updatedChrs = set([])
        
        from gtrackcore.input.userbins.UserBinSource import MinimalBinSource
        minimalBinList = MinimalBinSource(genome)
        self._minimalRegion = minimalBinList[0] if minimalBinList is not None else None
        
    def fileExists(self):
        return os.path.exists(self._fn)

    def storeBoundingRegions(self, boundingRegionTuples, genomeElementChrList, sparse):
        assert sparse in [False, True]

        tempContents = OrderedDict()

        genomeElementChrs = set(genomeElementChrList)    
        lastRegion = None
        chrStartIdxs = OrderedDict()
        chrEndIdxs = OrderedDict()
        totElCount = 0
        totBinCount = 0
        
        for br in boundingRegionTuples:
            if lastRegion is None or br.region.chr != lastRegion.chr:
                if br.region.chr in tempContents:
                    raise InvalidFormatError("Error: bounding region (%s) is not grouped with previous bounding regions of the same chromosome (sequence)." % br.region)
                
                lastRegion = None
                tempContents[br.region.chr] = OrderedDict()
                if sparse:
                    chrStartIdxs[br.region.chr] = totElCount
            else:
                if br.region < lastRegion:
                    raise InvalidFormatError("Error: bounding regions in the same chromosome (sequence) are unsorted: %s > %s." % (lastRegion, br.region))
                if lastRegion.overlaps(br.region):
                    raise InvalidFormatError("Error: bounding regions '%s' and '%s' overlap." % (lastRegion, br.region))
                if lastRegion.end == br.region.start:
                    raise InvalidFormatError("Error: bounding regions '%s' and '%s' are adjoining (there is no gap between them)." % (lastRegion, br.region))
            
            if len(br.region) < 1:
                raise InvalidFormatError("Error: bounding region '%s' does not have positive length." % br.region)
                
            if not sparse and len(br.region) != br.elCount:
                raise InvalidFormatError("Error: track type representation is dense, but the length of bounding region '%s' is not equal to the element count: %s != %s" % (br.region, len(br.region), br.elCount))
            
            startIdx, endIdx = (totElCount, totElCount + br.elCount) if not sparse else (None, None)
            totElCount += br.elCount
            if sparse:
                chrEndIdxs[br.region.chr] = totElCount
            
            tempContents[br.region.chr][br.region.start] = BoundingRegionInfo(br.region.start, br.region.end, startIdx, endIdx, 0, 0)
            
            lastRegion = br.region
        
        if sparse:
            totBinCount = 0
            for chr in tempContents:
                chrLen = GenomeInfo.getChrLen(self._genome, chr)
                numBinsInChr = CompBinManager.getNumOfBins(GenomeRegion(start=0, end=chrLen))
                for key in tempContents[chr].keys():
                    startBinIdx = totBinCount
                    endBinIdx = totBinCount + numBinsInChr
                    brInfo = tempContents[chr][key]
                    
                    if chr in genomeElementChrs:
                        tempContents[chr][key] = BoundingRegionInfo(brInfo.start, brInfo.end, \
                                                                    chrStartIdxs[chr], chrEndIdxs[chr], \
                                                                    startBinIdx, endBinIdx)
                    else:
                        if chrEndIdxs[chr] - chrStartIdxs[chr] > 0:
                            raise InvalidFormatError("Error: bounding region '%s' has incorrect element count: %s > 0" % (GenomeRegion(chr=chr, start=brInfo.start, end=brInfo.end), chrEndIdxs[chr] - chrStartIdxs[chr]))
                        tempContents[chr][key] = BoundingRegionInfo(brInfo.start, brInfo.end, 0, 0, 0, 0)
                
                if chr in genomeElementChrs:
                    totBinCount += numBinsInChr
        
        if len(genomeElementChrs - set(tempContents.keys())) > 0:
            raise InvalidFormatError('Error: some chromosomes (sequences) contains data, but has no bounding regions: %s' % ', '.join(genomeElementChrs - set(tempContents.keys())))
        
        ensurePathExists(self._fn)
        
        for chr in tempContents:
            brInfoDict = tempContents[chr]
            tempContents[chr] = BrInfoHolder(tuple(brInfoDict.keys()), tuple(brInfoDict.values()))
        
        brShelve = safeshelve.open(self._fn)
        brShelve.update(tempContents)
        brShelve.close()
        
        while not self.fileExists():
            from gtrackcore.core.LogSetup import logMessage
            logMessage("Bounding region shelve file '%s' has yet to be created" % self._fn)
            import time
            time.sleep(0.2)
    
    def _updateContentsIfNecessary(self, chr):
        #if self._contents is None:
        #    self._contents = {}
        #    if self.fileExists():
        #        self._contents.update(safeshelve.open(self._fn, 'r'))
        if not chr in self._updatedChrs:
            if self.fileExists():
                brListForChr = safeshelve.open(self._fn, 'r').get(chr)
                if brListForChr is not None:
                    self._contents[chr] = brListForChr
            self._updatedChrs.add(chr)
    
    def getBoundingRegionInfo(self, region):
        self._updateContentsIfNecessary(region.chr)
        
        if region.chr in self._contents:
            brInfoHolder = self._contents[region.chr]
            
            #Temporary, to store old preprocessed boundingRegion.shelve files
            isDict = isinstance(brInfoHolder, dict)
            if isDict:
                brStarts = brInfoHolder.keys()
            else:
                brStarts = brInfoHolder.brStarts
                
            #idx = self._contents[region.chr].keys().bisect_right(region.start)
            idx = bisect_right(brStarts, region.start)
            
            if idx > 0:
                if isDict:
                    brInfo = brInfoHolder[brStarts[idx-1]]
                else:
                    brInfo = brInfoHolder.brInfos[idx-1]
                
                if region.start < brInfo.end and region.end <= brInfo.end:
                    return brInfo
                    
            if not self._minimalRegion == region:
                #
                #There are bounding regions in the same chromosome, but not any encompassing the user bin
                #Thus the bounding regions are explicitly defined (not just the complete chromosome)
                #
                from gtrackcore.util.CommonFunctions import prettyPrintTrackName
                raise OutsideBoundingRegionError("The analysis region '%s' is outside the bounding regions of track: %s" \
                                                 % (region, prettyPrintTrackName(self._trackName)))
        
        return BoundingRegionInfo(region.start, region.end, 0, 0, 0, 0)
        
        
    def getTotalElementCountForChr(self, chr):
        self._updateContentsIfNecessary(chr)
        
        if chr in self._contents:
            #Temporary
            brInfoHolder = self._contents[chr]
            if isinstance(brInfoHolder, dict):
                brInfosForChr = brInfoHolder.values()
            else:
                brInfosForChr = brInfoHolder.brInfos
            return brInfosForChr[-1].endIdx - brInfosForChr[0].startIdx
        else:
            return 0
            
    def getTotalElementCount(self):
        return sum(self.getTotalElementCountForChr(chr) for chr in GenomeInfo.getExtendedChrList(self._genome))
            
    def getAllBoundingRegionsForChr(self, chr):
        self._updateContentsIfNecessary(chr)
        
        if chr in self._contents:
            #Temporary
            brInfoHolder = self._contents[chr]
            if isinstance(brInfoHolder, dict):
                brInfosForChr = brInfoHolder.values()
            else:
                brInfosForChr = brInfoHolder.brInfos
            for brInfo in brInfosForChr:
                yield GenomeRegion(self._genome, chr, brInfo.start, brInfo.end)
                
    def getAllBoundingRegions(self):
        if not self.fileExists():
            from gtrackcore.util.CommonFunctions import prettyPrintTrackName
            raise BoundingRegionsNotAvailableError('Bounding regions not available for track: ' + \
                prettyPrintTrackName(self._trackName))
        
        for chr in GenomeInfo.getExtendedChrList(self._genome):
            for reg in self.getAllBoundingRegionsForChr(chr):
                yield reg