from gtrackcore.track_operations.Genome import Genome
from gtrackcore.core.Api import _convertTrackName
import os
import shutil


class BTrack(object):
    def __init__(self, path, genomePath):
        self._path = os.path.abspath(path)
        self._genome = Genome.createFromTabular(genomePath, 'hg18')
        self._trackNames = []


    def importTrackFromFile(self, filePath, trackName):
        trackName = _convertTrackName(trackName)[0]

        from gtrackcore.util.CommonFunctions import ensurePathExists
        print trackName
        origFn = os.path.join(self._path, 'toplevel', trackName, os.path.basename(filePath))

        if os.path.exists(origFn):
            shutil.rmtree(os.path.dirname(origFn))
        ensurePathExists(origFn)
        shutil.copy(filePath, origFn)
        os.chmod(origFn, 0664)

        from gtrackcore.preprocess.PreProcessTracksJob import PreProcessExternalTrackJob
        #PreProcessAllTracksJob(self._genome.name, trackName, btrackDir=os.path.join(self._path, 'toplevel')).process()
        #genome, fullFn, extTrackName, fileSuffix
        PreProcessExternalTrackJob(self._genome.name, origFn, ['__btrack__'] + [os.path.join(self._path, 'toplevel')] + [trackName], os.path.splitext(filePath)[1][1:]).process()
        self._trackNames.append(trackName)

