import shutil, os, sys, numpy

def importFile(fileName, genome, trackName):
    """fileName genome trackName"""

    trackName = _convertTrackName(trackName)

    from gtrackcore.util.CommonFunctions import createOrigPath, ensurePathExists
    origFn = createOrigPath(genome, trackName, os.path.basename(fileName))
    if os.path.exists(origFn):
        shutil.rmtree(os.path.dirname(origFn))
    ensurePathExists(origFn)
    shutil.copy(fileName, origFn)
    os.chmod(origFn, 0664)

    from gtrackcore.preprocess.PreProcessTracksJob import PreProcessAllTracksJob
    PreProcessAllTracksJob(genome, trackName).process()

def _convertTrackName(trackName):
    from gtrackcore.util.CommonFunctions import convertTNstrToTNListFormat
    return convertTNstrToTNListFormat(trackName, doUnquoting=True)

def _trackNameExists(genome, trackName):
    from gtrackcore.track.hierarchy.ProcTrackOptions import ProcTrackOptions
    if not ProcTrackOptions.isValidTrack(genome, trackName):
        print 'Track "%s" of genome "%s" is not valid.' % (':'.join(trackName), genome)
        return False
    return True

def _getDirPath(genome=''):
    from gtrackcore.util.CommonFunctions import createDirPath, ensurePathExists
    dirPath = createDirPath([], '')
    ensurePathExists(dirPath)
    return dirPath

def listAvailableGenomes():
    ""
    print 'List of available genomes:'
    dirPath = _getDirPath()
    for dir in os.listdir(dirPath):
        if dir[0] != '.':
            print '    ' + dir

def listAvailableTracks(genome):
    "genome"
    print 'List of available tracks for genome "%s":' % genome
    _getDirPath(genome)

    from gtrackcore.track.hierarchy.ProcTrackNameSource import ProcTrackNameSource
    for trackName in ProcTrackNameSource(genome):
        print '    ' + ':'.join(trackName)

def getExtractionOptions(genome, trackName):
    """genome trackName"""

    trackName = _convertTrackName(trackName)
    if not _trackNameExists(genome, trackName):
        return

    print
    print 'Available extraction options for track "%s" of genome "%s":' % (':'.join(trackName), genome)
    print
    print '{:<19}'.format('fileFormatName') + '{:<17}'.format('allowOverlaps') + 'Description'
    print '-'*80

    from gtrackcore.extract.TrackExtractor import TrackExtractor
    for text, suffix in TrackExtractor.getTrackExtractionOptions(genome, trackName):
        fileFormatName, asOriginal, allowOverlaps = TrackExtractor.getAttrsFromExtractionFormat(text)
        print '{:<19}'.format(fileFormatName) + '{:<17}'.format(str(allowOverlaps)) + text

def _commonExportFile(outFileName, genome, trackName, fileFormatName, allowOverlaps, bins):
    trackName = _convertTrackName(trackName)
    if not _trackNameExists(genome, trackName):
        return

    outFileName = os.path.abspath(outFileName)

    from gtrackcore.extract.TrackExtractor import TrackExtractor
    TrackExtractor.extractOneTrackManyRegsToOneFile(trackName, bins, outFileName, fileFormatName=fileFormatName, \
                                                    globalCoords=True, asOriginal=False, \
                                                    allowOverlaps=allowOverlaps)

def exportFile(outFileName, genome, trackName, fileFormatName, allowOverlaps):
    """outFileName genome trackName fileFormatName allowOverlaps"""

    from gtrackcore.input.userbins.UserBinSource import UserBinSource
    bins = UserBinSource('*', '*', genome, includeExtraChrs=True)

    _commonExportFile(outFileName, genome, trackName, fileFormatName, allowOverlaps, bins)

def exportFileInRegion(outFileName, genome, trackName, fileFormatName, allowOverlaps, region):
    """outFileName genome trackName fileFormatName allowOverlaps region (e.g. chr21:1m-2m)"""

    from gtrackcore.input.userbins.UserBinSource import UserBinSource
    bins = UserBinSource(region, '*', genome, includeExtraChrs=True)

    _commonExportFile(outFileName, genome, trackName, fileFormatName, allowOverlaps, bins)


def _getTrackData(genome, trackName, chr, allowOverlaps):
    from gtrackcore.track.memmap.TrackSource import TrackSource
    trackSource = TrackSource()
    return trackSource.getTrackData(trackName, genome, chr, allowOverlaps.lower() in ('yes', 'true', 't', '1'))


def countTrackElements(genome, trackName, chr, allowOverlaps):
    trackName = _convertTrackName(trackName)
    if not _trackNameExists(genome, trackName):
        print 'There is no track %s for genome %s' % (trackName, genome)
        return
    trackData = _getTrackData(genome, trackName, chr, allowOverlaps)

    print numpy.shape(trackData['start'])[0]


def _usage():
    print 'syntax: '
    print 'to use: [name] [args]'
    print 'available commands: '
    print ', '.join(funcList.keys())
    sys.exit(0)

if __name__ == "__main__":
    from collections import OrderedDict
    import types
    import sys
    thisModule = sys.modules[__name__]

    funcList = OrderedDict((a, thisModule.__dict__.get(a)) for a in sorted(dir(thisModule))
                if isinstance(thisModule.__dict__.get(a), types.FunctionType) and a[0] != '_')

    if len(sys.argv) == 1:
        _usage()
    else:
        assert( len(sys.argv) >= 2)
        if not sys.argv[1] in funcList:
            _usage()
        else:
            try:
                func = funcList[sys.argv[1]]
                func(*sys.argv[2:])
            except:
                print
                print 'usage: python Api.py ' + str(func.__name__) + ' ' + str(func.__doc__)
                print
                raise
