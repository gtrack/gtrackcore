from collections import namedtuple
from cStringIO import StringIO

from gtrackcore_compressed.core.Config import Config
from gtrackcore_compressed.input.wrappers.GEDependentAttributesHolder import GEDependentAttributesHolder
from gtrackcore_compressed.util.CommonConstants import BINARY_MISSING_VAL
from gtrackcore_compressed.util.CommonFunctions import isNan, createPath
from gtrackcore_compressed.util.CustomExceptions import InvalidFormatError, AbstractClassError, NotIteratedYetError

MatchResult = namedtuple('MatchResult', ['match', 'trackFormatName'])
ComposerInfo = namedtuple('ComposerInfo', ['trackFormatName','fileFormatName','fileSuffix'])

def findMatchingFileFormatComposers(trackFormat):
    matchingComposers = []
    for composer in getAllComposers():
        matchResult = composer.matchesTrackFormat(trackFormat)
        if matchResult.match:
            matchingComposers.append(ComposerInfo(trackFormatName=matchResult.trackFormatName, \
                                                  fileFormatName=composer.FILE_FORMAT_NAME, \
                                                  fileSuffix=composer.getDefaultFileNameSuffix()))
    return matchingComposers
    
def getComposerClsFromFileFormatName(fileFormatName):
    for composerCls in getAllComposers():
        if fileFormatName.lower() == composerCls.FILE_FORMAT_NAME.lower():
            return composerCls
    raise InvalidFormatError("Error: file format composer for format '%s' was not found." % fileFormatName)

def getComposerClsFromFileSuffix(fileSuffix):
    for composerCls in getAllComposers():
        if fileSuffix.lower() in [x.lower() for x in composerCls.FILE_SUFFIXES]:
            return composerCls
    raise InvalidFormatError("Error: file format composer for file suffix '%s' was not found." % fileSuffix)
    
class FileFormatComposer(object):
    FILE_SUFFIXES = ['']
    FILE_FORMAT_NAME = ''
    
    def __init__(self, geSource):
        try:
            if not geSource.hasBoundingRegionTuples():
                self._geSource = GEDependentAttributesHolder(geSource)
            else:
                self._geSource = geSource
        except NotIteratedYetError:
            self._geSource = geSource
        
        self._emptyGeSource = True
        for ge in self._geSource:
            self._emptyGeSource = False
            break
    
    @staticmethod
    def matchesTrackFormat(trackFormat):
        return MatchResult(match=False, trackFormatName=trackFormat.getFormatName())

    def composeToFile(self, fn, ignoreEmpty=False, **kwArgs):
        createPath(fn)
        f = open(fn, 'w')
        ok = self._composeCommon(f, ignoreEmpty, **kwArgs)
        f.close()
        return ok
    
    def returnComposed(self, ignoreEmpty=False, **kwArgs):
        memFile = StringIO()
        self._composeCommon(memFile, ignoreEmpty, **kwArgs)
        return memFile.getvalue()
    
    def _composeCommon(self, out, ignoreEmpty=False, **kwArgs):
        if ignoreEmpty and self._emptyGeSource:
            return False
        
        self._compose(out, **kwArgs)
        return True
        
    def _compose(self, out, **kwArgs):
        raise AbstractClassError()
        
    def _commonFormatNumberVal(self, val):
        if isNan(val) or val is None:
            return '.'
        return ('%#.' + str(Config.OUTPUT_PRECISION) + 'g') % val
        #return '%.5f' % val
        
    def _commonFormatBinaryVal(self, val):
        if val == BINARY_MISSING_VAL:
            return '.'
        return 1 if val == True else 0
        
    @classmethod
    def getDefaultFileNameSuffix(cls):
        return cls.FILE_SUFFIXES[0]
        
def getAllComposers():
    from gtrackcore_compressed.extract.fileformats.GtrackComposer import StdGtrackComposer, ExtendedGtrackComposer
    from gtrackcore_compressed.extract.fileformats.BedComposer import BedComposer, PointBedComposer, CategoryBedComposer, ValuedBedComposer
    from gtrackcore_compressed.extract.fileformats.BedGraphComposer import BedGraphComposer, BedGraphTargetControlComposer
    from gtrackcore_compressed.extract.fileformats.GffComposer import GffComposer
    from gtrackcore_compressed.extract.fileformats.WigComposer import WigComposer
    from gtrackcore_compressed.extract.fileformats.FastaComposer import FastaComposer
    
    return [BedComposer, PointBedComposer, CategoryBedComposer, ValuedBedComposer, BedGraphComposer, \
            BedGraphTargetControlComposer, GffComposer, WigComposer, FastaComposer, StdGtrackComposer, \
            ExtendedGtrackComposer]