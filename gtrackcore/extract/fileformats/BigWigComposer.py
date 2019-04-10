from extract.fileformats.FileFormatComposer import FileFormatComposer, MatchResult
from input.wrappers.GEDependentAttributesHolder import iterateOverBRTuplesWithContainedGEs
from gtrackcore.track.format.TrackFormat import TrackFormat
import pyBigWig
from gtrackcore.metadata.GenomeInfo import GenomeInfo
from gtrackcore.util.CommonFunctions import ensurePathExists
import numpy as np
import tempfile


class BigWigComposer(FileFormatComposer):
    FILE_SUFFIXES = ['bw', 'bigwig']
    FILE_FORMAT_NAME = 'BigWig'
    _supportsSliceSources = True

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
        tf = TrackFormat.createInstanceFromGeSource(self._geSource)
        span = self._geSource.getFixedLength()
        step = self._geSource.getFixedGapSize() + span

        isFixedStep = (tf.reprIsDense() or step > 1 or (step == 1 and span != 1))

        brGes = []
        chroms = set()
        for br, geList in iterateOverBRTuplesWithContainedGEs(self._geSource):
            brGes.append((br, geList))
            for ge in geList:
                chroms.add(ge.chr)

        brGes = sorted(brGes, key=lambda a: a[0])
        print brGes
        genome = brGes[0][1][0].genome
        chroms = sorted(list(chroms))

        chrLengths = []
        for ch in chroms:
            chrLengths.append((ch, GenomeInfo.getChrLen(genome, ch)))

        out.addHeader(chrLengths)

        for br, geList in brGes:
            if len(geList) == 0:
                continue

            geList = sorted(geList)
            if isFixedStep:
                vals = np.array([], dtype=np.float64)
                for ge in geList:
                    vals = np.append(vals, ge.val)

                if tf.isDense() and tf.isInterval() and self._geSource.addsStartElementToDenseIntervals():
                    vals = np.delete(vals, 0)

                out.addEntries(ge.chr, br.region.start, values=vals, span=span, step=step)
            else:
                for ge in geList:
                    vals = np.array([], dtype=np.float64)
                    starts = np.array([], dtype=np.int32)
                    chrs = np.array([])
                    ends = np.array([], dtype=np.int32)
                    starts = np.append(starts, ge.start)
                    vals = np.append(vals, ge.val)
                    if tf.isPoints():
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
