from extract.fileformats.FileFormatComposer import FileFormatComposer, MatchResult
from input.wrappers.GEDependentAttributesHolder import iterateOverBRTuplesWithContainedGEs
from gtrackcore.track.format.TrackFormat import TrackFormat
import pyBigWig
from gtrackcore.metadata.GenomeInfo import GenomeInfo
from gtrackcore.util.CommonFunctions import ensurePathExists
import numpy as np


class BigWigComposer(FileFormatComposer):

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
                vals = np.array([])
                for ge in geList:
                    vals = np.append(vals, ge.val)

                if tf.isDense() and tf.isInterval() and self._geSource.addsStartElementToDenseIntervals():
                    vals = np.delete(vals, 0)

                out.addEntries(ge.chr, br.region.start, values=vals, span=span, step=step)
            else:
                vals = np.array([])
                starts = np.array([], dtype=np.int64)
                ends = np.array([], dtype=np.int64)
                chrs = np.array([])
                for ge in geList:
                    starts = np.append(starts, ge.start)
                    end = ge.end
                    if not end:
                        end = ge.start + 1
                    ends = np.append(ends, end)
                    vals = np.append(vals, ge.val)
                    ch = ge.chr
                    if isinstance(ge.val, np.ndarray):
                        ch = [ge.chr] * ge.val.size
                    chrs = np.append(chrs, ch)

                out.addEntries(chrs, starts, ends=ends, values=vals)
