from gtrackcore.extract.TrackExtractor import TrackExtractor
from gtrackcore.track_operations.Genome import Genome
from gtrackcore.core.Api import _convertTrackName
import os

from gtrackcore.track_operations.utils.TrackHandling import extractTrackFromGTrackCore
from gtrackcore.util.CommonFunctions import ensurePathExists
import shutil
from gtrackcore.preprocess.PreProcessTracksJob import PreProcessExternalTrackJob


class BTrack(object):
    def __init__(self, path, genomePath=''):
        self._path = os.path.abspath(path)
        self._trackContents = []

        if not genomePath:
            genomesPath = os.path.join(self._path, 'genomes')
            if os.path.isdir(genomesPath) and os.listdir(genomesPath):
                print 'genome found'
                print os.listdir(genomesPath)
                genomePath = os.path.join(genomesPath, os.listdir(genomesPath)[0])
            else:
                raise ValueError('Genome has to be provided')

        else:
            newGenomePath = os.path.join(self._path, 'genomes', os.path.basename(genomePath))
            ensurePathExists(newGenomePath)
            shutil.copy(genomePath, newGenomePath)

        self._genome = Genome.createFromTabular(genomePath, os.path.basename(genomePath))

        self._load()

    def _load(self):
        trackDirPath = os.path.join(self._path, 'tracks', self._genome.name)
        if os.path.isdir(trackDirPath) and os.listdir(trackDirPath):
            self._loadTracks(trackDirPath)

    def _loadTracks(self, trackDirPath):
        trackNames = []
        for root, dirs, files in os.walk(trackDirPath, topdown=False):
            if 'noOverlaps' in dirs or 'withOverlaps' in dirs:
                trackNames.append(root[(len(trackDirPath) + 1):].replace(os.sep, ':'))

        for trackName in trackNames:
            trackIdentifier = self.createTrackIdentifier(_convertTrackName(trackName))
            trackContents = extractTrackFromGTrackCore(self._genome, trackIdentifier)
            self._trackContents.append(TrackContentsWrapper(trackIdentifier, trackContents))

        self.listTracks()

    def createTrackIdentifier(self, trackName):
        trackIdentifier = ['__btrack__'] + [os.path.join(self._path, 'tracks', self._genome.name)] + trackName

        return trackIdentifier

    def importTrackFromFile(self, filePath, trackName=''):
        if not trackName:
            trackName = os.path.basename(filePath)
        trackName = _convertTrackName(trackName)

        trackIdentifier = self.createTrackIdentifier(trackName)
        PreProcessExternalTrackJob(self._genome, filePath, trackIdentifier, os.path.splitext(filePath)[1][1:]).process()

        trackContents = extractTrackFromGTrackCore(self._genome, trackIdentifier)

        self._trackContents.append(TrackContentsWrapper(trackIdentifier, trackContents))

        return trackContents

    def importTrack(self, trackContents, trackName):
        trackName = _convertTrackName(trackName)
        trackIdentifier = self.createTrackIdentifier(trackName)

        trackContents.save(trackIdentifier)
        self._trackContents.append(TrackContentsWrapper(trackIdentifier, trackContents))

    def exportTrackToFile(self, trackContents, path):
        for tc in self._trackContents:
            if tc.getTrackContents() == trackContents:
                trackIdentifier = tc.getTrackId()

        fileSuffix = os.path.splitext(path)[1][1:]

        TrackExtractor.extractOneTrackManyRegsToOneFile(trackIdentifier, trackContents.regions, path,
                                                        fileSuffix=fileSuffix, globalCoords=True)

    def listTracks(self):
        for tc in self._trackContents:
            print tc

class TrackContentsWrapper(object):
    def __init__(self, trackIdentifier, trackContents):
        self._trackIdentifier = trackIdentifier
        self._trackContents = trackContents

    def getTrackId(self):
        return self._trackIdentifier

    def getTrackName(self):
        trackName = self._trackIdentifier[2:]

        return trackName

    def getTrackContents(self):
        return self._trackContents

    def __str__(self):
        return 'Track name: ' + str(self.getTrackName())