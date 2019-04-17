import tempfile

import numpy as np
import pyBigWig

from extract.fileformats.FileFormatComposer import FileFormatComposer, MatchResult
from gtrackcore.metadata.GenomeInfo import GenomeInfo
from gtrackcore.track.format.TrackFormat import TrackFormat
from gtrackcore.util.CommonFunctions import ensurePathExists
from input.wrappers.GEDependentAttributesHolder import iterateOverBRTuplesWithContainedGEs


class BigWigComposer(FileFormatComposer):
    FILE_SUFFIXES = ['bw', 'bigwig']
    FILE_FORMAT_NAME = 'BigWig'
    _supportsSliceSources = True

    def __init__(self, geSource):
        FileFormatComposer.__init__(self, geSource)
        self._span = geSource.getFixedLength()
        self._step = geSource.getFixedGapSize() + self._span
        self._tf = TrackFormat.createInstanceFromGeSource(geSource)
        self._isFixedStep = (self._tf.reprIsDense() or self._step > 1 or (self._step == 1 and self._span != 1))

    @staticmethod
    def matchesTrackFormat(trackFormat):
        return MatchResult(match=trackFormat.getValTypeName() in ['Number', 'Number (integer)'], \
                           trackFormatName=trackFormat.getFormatName().lower().replace('linked ',
                                                                                       ''))

    def composeToFile(self, fn, ignoreEmpty=False, **kwArgs):
        ensurePathExists(fn)
        f = pyBigWig.open(fn, 'w')
        ok = self._composeCommon(f, ignoreEmpty, **kwArgs)
        f.close()
        return ok

    def returnComposed(self, ignoreEmpty=False, **kwArgs):
        tmpFile = tempfile.NamedTemporaryFile(suffix='.bw')
        tmpFile.close()
        f = pyBigWig.open(tmpFile.name, 'w')
        self._composeCommon(f, ignoreEmpty, **kwArgs)
        f.close()
        tmpFile = open(tmpFile.name, 'rb')
        composedStr = tmpFile.read()
        tmpFile.close()

        return composedStr

    def _compose(self, out):
        brGes = []
        chroms = set()
        for br, geList in iterateOverBRTuplesWithContainedGEs(self._geSource):
            brGes.append((br, geList))
            for ge in geList:
                chroms.add(ge.chr)

        self._composeHeader(chroms, out)

        brGes = sorted(brGes, key=lambda a: a[0])
        for br, geList in brGes:
            if len(geList) == 0:
                continue

            geList = sorted(geList)
            if self._isFixedStep:
                self._composeFixedStep(geList, br, out)
            else:
                self._composeVariableStep(geList, out)

    def _composeHeader(self, chroms, out):
        chroms = sorted(list(chroms))

        chrLengths = []
        for ch in chroms:
            chrLengths.append((ch, GenomeInfo.getChrLen(self._geSource.getGenome(), ch)))
        out.addHeader(chrLengths)

    def _composeFixedStep(self, geList, br, out):
        vals = np.array([], dtype=np.float64)
        for ge in geList:
            vals = np.append(vals, ge.val)

        if self._tf.isDense() and self._tf.isInterval() and self._geSource.addsStartElementToDenseIntervals():
            vals = np.delete(vals, 0)

        out.addEntries(ge.chr, br.region.start, values=vals, span=self._span, step=self._step)

    def _composeVariableStep(self, geList, out):
        for ge in geList:
            vals = np.array([], dtype=np.float64)
            starts = np.array([], dtype=np.int32)
            chrs = np.array([])
            ends = np.array([], dtype=np.int32)
            starts = np.append(starts, ge.start)
            vals = np.append(vals, ge.val)
            # compose points as varible step, rest as bedgraph
            if self._tf.isPoints():
                out.addEntries(ge.chr, starts, values=vals, span=1)
            else:
                end = ge.end
                if end is None:
                    end = ge.start + 1
                ends = np.append(ends, end)
                ch = ge.chr
                if isinstance(ge.val, np.ndarray):
                    ch = [ge.chr] * ge.val.size
                chrs = np.append(chrs, ch)
                out.addEntries(chrs, starts, ends=ends, values=vals)
