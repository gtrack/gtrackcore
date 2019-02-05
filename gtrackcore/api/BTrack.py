import os
import shutil

from gtrackcore.core.Api import convertTrackName
from gtrackcore.extract.TrackExtractor import TrackExtractor
from gtrackcore.preprocess.PreProcessTracksJob import PreProcessExternalTrackJob
from gtrackcore.track_operations.Genome import Genome
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.track_operations.utils.TrackHandling import extractTrackFromGTrackCore
from gtrackcore.util.CommonFunctions import ensurePathExists, getFileSuffix


class BTrack(object):
    def __init__(self, path, genomePath=''):
        self._path = os.path.abspath(path)
        self._trackContentsWrapped = []

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
            trackIdentifier = self.createTrackIdentifier(convertTrackName(trackName))
            trackContents = extractTrackFromGTrackCore(self._genome, trackIdentifier)
            self._trackContentsWrapped.append(TrackContentsWrapper(trackIdentifier, trackContents))

        print 'Tracks loaded: '
        self.listTracks()

    def createTrackIdentifier(self, trackName):
        trackIdentifier = ['__btrack__'] + [os.path.join(self._path, 'tracks', self._genome.name)] + trackName

        return trackIdentifier

    def importTrackFromFile(self, filePath, trackName=''):
        if not trackName:
            trackName = os.path.basename(filePath)
        trackName = convertTrackName(trackName)

        trackIdentifier = self.createTrackIdentifier(trackName)
        PreProcessExternalTrackJob(self._genome, filePath, trackIdentifier, os.path.splitext(filePath)[1][1:]).process()

        trackContents = extractTrackFromGTrackCore(self._genome, trackIdentifier)
        self._trackContentsWrapped.append(TrackContentsWrapper(trackIdentifier, trackContents))

        return trackContents

    def importTrack(self, trackContents, trackName, allowOverlaps=True):
        trackName = convertTrackName(trackName)
        trackIdentifier = self.createTrackIdentifier(trackName)

        trackContents.save(trackIdentifier, allowOverlaps=allowOverlaps)
        self._trackContentsWrapped.append(TrackContentsWrapper(trackIdentifier, trackContents))

    def exportTrackToFile(self, path, trackName=None, trackContents=None, allowOverlaps=True):
        if isinstance(trackName, str):
            tcWrapper = self.getTrackContentsByTrackNameAsString(trackName)
            trackContents = tcWrapper.getTrackContents()
            trackIdentifier = tcWrapper.getTrackId()
        elif isinstance(trackContents, TrackContents):
            for tcWrapper in self._trackContentsWrapped:
                if tcWrapper.getTrackContents() == trackContents:
                    trackIdentifier = tcWrapper.getTrackId()
        else:
            'Track name or TrackContents have to be provided for export'
            return

        fileSuffix = getFileSuffix(path)
        TrackExtractor.extractOneTrackManyRegsToOneFile(trackIdentifier, trackContents.regions, path,
                                                        fileSuffix=fileSuffix, globalCoords=True,
                                                        allowOverlaps=allowOverlaps)

    def listTracks(self):
        for tcWrapper in self._trackContentsWrapped:
            print tcWrapper

    def getTrackContentsByTrackNameAsString(self, trackNameAsString):
        for tcWrapper in self._trackContentsWrapped:
            if tcWrapper.getTrackNameAsString() == trackNameAsString:
                return tcWrapper

    def hasTracks(self):
        if self._trackContentsWrapped:
            return True

        return False


class TrackContentsWrapper(object):
    def __init__(self, trackIdentifier, trackContents):
        self._trackIdentifier = trackIdentifier
        self._trackContents = trackContents
        self._trackNameAsString = ':'.join(self._trackIdentifier[2:])

    def getTrackId(self):
        return self._trackIdentifier

    def getTrackName(self):
        trackName = self._trackIdentifier[2:]

        return trackName

    def getTrackNameAsString(self):
        return self._trackNameAsString

    def getTrackContents(self):
        return self._trackContents

    def __str__(self):
        return 'Track name: ' + self.getTrackNameAsString() + ' genome: ' + self._trackContents.genome.name