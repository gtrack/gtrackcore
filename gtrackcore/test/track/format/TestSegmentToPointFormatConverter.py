import unittest

from gtrackcore.test.track.common.SampleTrackView import SampleTV
from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track.format.SegmentToPointFormatConverter import SegmentToPointFormatConverter, \
    SegmentToStartPointFormatConverter, SegmentToMidPointFormatConverter, SegmentToEndPointFormatConverter
from gtrackcore.track.format.TrackFormat import TrackFormatReq

class TestFormatConverter(unittest.TestCase):
    def setUp(self):
        pass
    
    def _assertConvertSegmentToPoint(self, targetStarts, sourceTv, converterCls):
        pointFormat = TrackFormatReq(interval=False, dense=False)
        self.assertTrue(converterCls.canHandle(sourceTv.trackFormat, pointFormat))
 
        targetTv = converterCls.convert(sourceTv)
        self.assertTrue(pointFormat.isCompatibleWith(targetTv.trackFormat))
            
        self.assertEqual(targetStarts, [el.start() for el in targetTv])
        for el in targetTv:
            self.assertEqual(el.start() + 1, el.end())
            
    def testConvertSegmentToPoint(self):
        segSourceTv = SampleTV(segments=[[2,6], [10,20]], strands=[True,False])
        self._assertConvertSegmentToPoint([2,19], segSourceTv, SegmentToStartPointFormatConverter)
        self._assertConvertSegmentToPoint([4,15], segSourceTv, SegmentToMidPointFormatConverter)
        self._assertConvertSegmentToPoint([5,10], segSourceTv, SegmentToEndPointFormatConverter)
        
        #partSourceTv = SampleTV(ends=[5,11], strands=False, anchor=[0,11])
        #self._assertConvertSegmentToPoint([0,5], partSourceTv, SegmentToStartPointFormatConverter)
        #self._assertConvertSegmentToPoint([2,8], partSourceTv, SegmentToMidPointFormatConverter)
        #self._assertConvertSegmentToPoint([4,10], partSourceTv, SegmentToEndPointFormatConverter)

        segSourceTv = SampleTV(segments=[], strands=False)
        self._assertConvertSegmentToPoint([], segSourceTv, SegmentToStartPointFormatConverter)
        
    def testConvertSegmentToPointWithOverlaps(self):
        segSourceTv = SampleTV(segments=[[2,20], [7,11]], strands=False, allowOverlaps=True)
        self._assertConvertSegmentToPoint([2,7], segSourceTv, SegmentToStartPointFormatConverter)
        self._assertConvertSegmentToPoint([9,11], segSourceTv, SegmentToMidPointFormatConverter)
        self._assertConvertSegmentToPoint([10,19], segSourceTv, SegmentToEndPointFormatConverter)

        segSourceTv = SampleTV(segments=[], strands=False, allowOverlaps=True)
        self._assertConvertSegmentToPoint([], segSourceTv, SegmentToStartPointFormatConverter)

    def _assertFailedConversion(self, sourceTv, tfReq):
        self.assertFalse(SegmentToStartPointFormatConverter.canHandle(sourceTv.trackFormat, tfReq))
 
    def testConvertSegmentToPointReqFails(self):
        segSourceTv = SampleTV(segments=[[2,20], [7,11]]) 
        self._assertFailedConversion(segSourceTv, \
                                     TrackFormatReq(interval=False, dense=False, val='category'))
        self._assertFailedConversion(segSourceTv, \
                                     TrackFormatReq(interval=False, dense=False, strand=True))
    
if __name__ == "__main__":
    unittest.main()