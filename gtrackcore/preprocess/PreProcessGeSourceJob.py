from gtrackcore.preprocess.PreProcMetaDataCollector import PreProcMetaDataCollector
from gtrackcore.preprocess.PreProcessUtils import PreProcessUtils
from gtrackcore.preprocess.pytables.OutputManager import OutputManager


class PreProcessGeSourceJob(object):
    VERSION = '0.95'
        
    def __init__(self, trackName, geSourceManager, allowOverlaps, mode='Real'):
        self._trackName = trackName
        self._allowOverlaps = allowOverlaps
        self._geSourceManager = geSourceManager
        self._mode = mode
        self._dirty = False
        
    def process(self):
        self._createPreProcFiles()
        
        if self._mode in ['UpdateMeta', 'Real']:
            self._dirty = True

    def _createPreProcFiles(self):
        geSource = self._geSourceManager.getGESource()
        genome = geSource.genome
        
        collector = PreProcMetaDataCollector(genome, self._trackName)
        collector.updateMetaDataForFinalization(geSource.getFileSuffix(), geSource.getPrefixList(),
                                                geSource.getValDataType(), geSource.getValDim(),
                                                geSource.getEdgeWeightDataType(), geSource.getEdgeWeightDim(),
                                                geSource.hasUndirectedEdges(),
                                                geSource.getVersion(), PreProcessUtils.constructId(geSource),
                                                self._geSourceManager.getNumElements(),
                                                self._geSourceManager.getBoundingRegionTuples(),
                                                self._geSourceManager.getValCategories(),
                                                self._geSourceManager.getEdgeWeightCategories(),
                                                self._allowOverlaps)

        if self._geSourceManager.getNumElements() == 0:
            return
        
        if self._mode != 'Real':
            for ge in geSource:
                pass
            return
        
        output = OutputManager(genome, self._trackName, self._allowOverlaps, self._geSourceManager)
        
        writeFunc = output.writeRawSlice if geSource.isSliceSource() else output.writeElement
        
        for ge in geSource:
            writeFunc(ge)
        
        collector.flagChrsAsPreProcessed(self._allowOverlaps, self._geSourceManager.getAllChrs())
        
        output.close()

    def hasModifiedData(self):
        return self._dirty
