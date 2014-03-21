from gtrackcore_memmap.extract.fileformats.FileFormatComposer import FileFormatComposer, MatchResult
from gtrackcore_memmap.input.wrappers.GEDependentAttributesHolder import iterateOverBRTuplesWithContainedGEs
from gtrackcore_memmap.track.format.TrackFormat import TrackFormat

class WigComposer(FileFormatComposer):
    FILE_SUFFIXES = ['wig']
    FILE_FORMAT_NAME = 'WIG'
    
    @staticmethod
    def matchesTrackFormat(trackFormat):
        return MatchResult(match=trackFormat.getValTypeName() in ['Number', 'Number (integer)'], \
                           trackFormatName=trackFormat.getFormatName().lower().replace('linked ',''))

    # Compose methods
    
    def _compose(self, out):
        trackName = self._geSource.getTrackName()
        if trackName is not None:
            name = ':'.join(self._geSource.getTrackName()).replace(' ','_')
        else:
            name = None
        
        print >>out, 'track type=wiggle_0' + (' name=%s' % name if name is not None else '')

        tf = TrackFormat.createInstanceFromGeSource(self._geSource)
        span = self._geSource.getFixedLength()
        step = self._geSource.getFixedGapSize() + span
        
        isFixedStep = (tf.reprIsDense() or step > 1 or (step == 1 and span != 1))
        
        for brt, geList in iterateOverBRTuplesWithContainedGEs(self._geSource):
            if len(geList) == 0:
                continue
            
            if isFixedStep:
                self._composeFixedStepDeclarationLine(out, brt.region, step, span)
            else:
                curChr, curSpan = self._composeVariableStepDeclarationLine(out, geList[0])
            
            for i,ge in enumerate(geList):
                if i==0 and tf.isDense() and tf.isInterval() and \
                    self._geSource.addsStartElementToDenseIntervals():
                    continue
                
                val = self._commonFormatNumberVal(ge.val)
                
                if isFixedStep:
                    cols = [val]
                else:
                    if ge.chr != curChr or self._getVariableSpan(ge) != curSpan:
                        curChr, curSpan = self._composeVariableStepDeclarationLine(out, ge)
                    cols = [str(ge.start+1), val]
                
                print >>out, '\t'.join([str(x) for x in cols])
                
    def _composeFixedStepDeclarationLine(self, out, br, step, span):
        print >>out, ('fixedStep chrom=%s start=%s step=%s' % (br.chr, br.start+1, step)) + \
                     (' span=%s' % span if span > 1 else '')
        
    def _composeVariableStepDeclarationLine(self, out, reg):
        span = self._getVariableSpan(reg)
        print >>out, ('variableStep chrom=%s' % reg.chr) + \
                     (' span=%s' % span if span > 1 else '')
        return reg.chr, span
        
    def _getVariableSpan(self, reg):
        return reg.end - reg.start if reg.end is not None else 1