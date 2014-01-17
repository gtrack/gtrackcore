#!/usr/bin/env python
import os.path
import shutil
import sys
import os

from gtrackcore.util.CommonFunctions import createPath, createOrigPath, \
                                        getDirPath #, createCollectedPath
from gtrackcore.metadata.TrackInfo import TrackInfo
from gtrackcore.track.hierarchy.ProcTrackNameSource import ProcTrackNameSource

ONLY_SIMULATION = False

def renameStdTrack(genome, oldTn, newTn):
    oldPath = createOrigPath(genome, oldTn)
    assert os.path.exists(oldPath), 'ERROR: TN did not exist in stdTracks: ' + oldPath
    
    print '(renaming track in stdTracks..)'
    newPath = createOrigPath(genome, newTn)
    if not ONLY_SIMULATION:    
        assert not os.path.exists(newPath), 'ERROR: Target path already exists: ' + newPath
        createPath(newPath)
        print 'Moving from %s to %s' % (oldPath, newPath)
        shutil.move(oldPath, newPath)
    else:
        print 'Would move %s to %s' %  (oldPath, newPath)

#def renameCollTrack(genome, oldTn, newTn):
#    oldPath = createCollectedPath(genome, oldTn)
#    if not os.path.exists(oldPath):
#        print '(TN did not exist in collTracks..)'
#    else:
#        print '(renaming track in collTracks..)'
#        newPath = createCollectedPath(genome, newTn)
#        if not ONLY_SIMULATION:    
#            assert not os.path.exists(newPath), 'ERROR: Target path already exists: ' + newPath
#            ensurePathExists(newPath)
#            shutil.move(oldPath, newPath)
#        else:
#            print 'Would move %s to %s' %  (oldPath, newPath)

def renameProcTrack(genome, oldTn, newTn):
    for allowOverlaps in [False, True]:
        oldPath = getDirPath(oldTn, genome, allowOverlaps=allowOverlaps)
        if not os.path.exists(oldPath):
            print 'Warning: TN did not exist as preproc ' + ('with overlaps' if allowOverlaps else ' without overlaps')
        else:
            print '(renaming TN in preproc ' + ('with overlaps' if allowOverlaps else ' without overlaps') + ')'
            newPath = getDirPath(newTn, genome, allowOverlaps=allowOverlaps)
            if not ONLY_SIMULATION:    
                assert not os.path.exists(newPath), 'ERROR: Target path already exists: ' + newPath
                createPath(newPath)
                shutil.move(oldPath, newPath)
            else:
                print 'Would move %s to %s' %  (oldPath, newPath)

def renameTrackInfo(genome, oldBaseTn, newBaseTn, verbose=True):
    #assert False, "need to handle category-tns... (not final..)"
    #assert False, 'need to start ProcTrackNameSource on subtree...'
    if not verbose:
        modifyCount = 0
    for fullOldTn in ProcTrackNameSource(genome, True).yielder(oldBaseTn):
        subName = fullOldTn[ len(oldBaseTn): ]
        fullNewTn = newBaseTn + subName
        modifyTnRecord(genome, fullOldTn, fullNewTn, verbose)
        if not verbose:
            modifyCount+=1
            if modifyCount%1000 == 0:
                print '(Changed 1k TNs..)'
    
def modifyTnRecord(genome, oldTn, newTn, verbose):
    trackInfo = TrackInfo(genome, oldTn)
    assert trackInfo.trackName == oldTn
    assert trackInfo.timeOfPreProcessing is not None, 'ERROR: trackInfo-object not complete for TN (is this track preprocessed?): ' + str(oldTn)
    #if trackInfo.timeOfPreProcessing is None:
        #print 'WARNING: timeOfPreProcessing is None for: ',oldTn
        
    trackInfo.trackName = newTn
    if not ONLY_SIMULATION:
        trackInfo.store()
        if verbose:
            print '(Storing track-info with new tn: %s)' % str(newTn)
    else:
        if verbose:
            print 'Would now store track-info with new tn: %s' % str(newTn)
    #Should really also delete old trackinfo-object, but ignored for now, as such removing will probably be added later as script for full overhaul..

#def renameMemoData(genome, oldTn, newTn):
    #pass
    #ignored, at least for now, not easy to do, and will anyway be regenerated..
    
def renameTrack(genome, oldTn, newTn):
    assert newTn != oldTn[:len(newTn)], 'ERROR: it is not allowed to move a track into itself (%s -> %s)' % (':'.join(oldTn), ':'.join(newTn))

    #First check to filter out misspellings..
    oldPath = getDirPath(oldTn, genome)
    assert os.path.exists(oldPath), 'ERROR: TN did not exist in processed tracks: ' + oldPath
    
    #renaming TI first, in case of problems, such as incomplete records..
    renameTrackInfo(genome, oldTn, newTn)
    try:
        renameStdTrack(genome, oldTn, newTn)
    except Exception, e:
        print e
    #renameCollTrack(genome, oldTn, newTn)
    renameProcTrack(genome, oldTn, newTn)
 
if __name__ == "__main__":
    if not len(sys.argv) == 4:
        print 'Syntax: Python RenameTrack.py genome oldTn newTn'
        sys.exit(0)
    
    genome = sys.argv[1]
    oldTn = sys.argv[2].replace('/',':').split(':')
    newTn = sys.argv[3].replace('/',':').split(':')
    renameTrack(genome, oldTn, newTn)