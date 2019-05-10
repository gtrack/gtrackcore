import os

from third_party import safeshelve
from util.CommonFunctions import createDirPath, ensurePathExists

HEADER_SHELVE_FILE_NAME = 'headers.shelve'


def isHeaderShelveFilename(fn):
    return HEADER_SHELVE_FILE_NAME in fn

class HeaderShelve(object):
    def __init__(self, genome, trackName, allowOverlaps):
        self._trackName = trackName
        self._fn = createDirPath(trackName, genome, allowOverlaps=allowOverlaps) + os.sep + HEADER_SHELVE_FILE_NAME
        self._headers = {}
        self._headersLoaded = False

    def fileExists(self):
        try:
            safeshelve.open(self._fn, 'r')
        except:
            return False
        return True

    def storeHeaders(self, headersDict):
        ensurePathExists(self._fn)
        headerShelve = safeshelve.open(self._fn)
        headerShelve.update(headersDict)
        headerShelve.close()

    def getHeaders(self):
        if not self._headersLoaded:
            if self.fileExists():
                self._headers = safeshelve.open(self._fn)
                self._headersLoaded = True

        return self._headers





