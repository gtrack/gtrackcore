from gtrackcore.extract.TrackExtractor import TrackExtractor
from gtrackcore.track_operations.Genome import Genome
from gtrackcore.core.Api import _convertTrackName
import os

from gtrackcore.track_operations.TrackContents import TrackContents
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

        #self.listTracks()

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

    def importTrack(self, trackContents, trackName, allowOverlaps=True):
        trackName = _convertTrackName(trackName)
        trackIdentifier = self.createTrackIdentifier(trackName)

        trackContents,allowOverlaps = allowOverlaps
        trackContents.save(trackIdentifier)
        self._trackContents.append(TrackContentsWrapper(trackIdentifier, trackContents))

    def exportTrackToFile(self, path, trackName=None, trackContents=None, allowOverlaps=True):
        if isinstance(trackName, str):
            trackName = _convertTrackName(trackName)
            for tc in self._trackContents:
                if tc.getTrackName() == trackName:
                    trackContents = tc.getTrackContents()
                    trackIdentifier = tc.getTrackId()
                    break
        elif isinstance(trackContents, TrackContents):
            for tc in self._trackContents:
                if tc.getTrackContents() == trackContents:
                    trackIdentifier = tc.getTrackId()
        else:
            'Track name or TrackContes have to be provided for export'
            return

        fileSuffix = os.path.splitext(path)[1][1:]

        TrackExtractor.extractOneTrackManyRegsToOneFile(trackIdentifier, trackContents.regions, path,
                                                        fileSuffix=fileSuffix, globalCoords=True,
                                                        allowOverlaps=allowOverlaps)

    def listTracks(self):
        for tc in self._trackContents:
            print tc

    def getTrackContentsByTrackNameAsString(self, trackNameAsString):
        for tc in self._trackContents:
            if tc.getTrackNameAsString() == trackNameAsString:
                return tc.getTrackContents()


class TrackContentsWrapper(object):
    def __init__(self, trackIdentifier, trackContents):
        self._trackIdentifier = trackIdentifier
        self._trackContents = trackContents

    def getTrackId(self):
        return self._trackIdentifier

    def getTrackName(self):
        trackName = self._trackIdentifier[2:]

        return trackName

    def getTrackNameAsString(self):
        trackName = ':'.join(self._trackIdentifier[2:])

        return trackName

    def getTrackContents(self):
        return self._trackContents

    def __str__(self):
        return 'Track name: ' + str(self.getTrackName())