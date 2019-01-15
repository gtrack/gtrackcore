from gtrackcore.track_operations.Genome import Genome
from gtrackcore.core.Api import _convertTrackName
import os
from gtrackcore.util.CommonFunctions import ensurePathExists
import shutil

class BTrack(object):
    def __init__(self, path, genomePath):
        self._path = os.path.abspath(path)
        self._genome = Genome.createFromTabular(genomePath, 'hg18')
        self._trackNames = []

        newGenomePath = os.path.join(self._path, 'genomes', os.path.basename(genomePath))
        ensurePathExists(newGenomePath)
        shutil.copy(genomePath, newGenomePath)



    def importTrackFromFile(self, filePath, trackName):
        trackName = _convertTrackName(trackName)
        print trackName

        from gtrackcore.preprocess.PreProcessTracksJob import PreProcessExternalTrackJob
        PreProcessExternalTrackJob(self._genome.name, filePath, ['__btrack__'] + [os.path.join(self._path, 'toplevel')] + trackName, os.path.splitext(filePath)[1][1:]).process()
        self._trackNames.append(trackName)

