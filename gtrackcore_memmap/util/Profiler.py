#import cProfile
import profile
import pstats

import hotshot, hotshot.stats

#from gtrackcore_memmap.util.StaticFile import GalaxyRunSpecificFile
from gtrackcore_memmap.util.CommonFunctions import ensurePathExists
from gtrackcore_memmap.util.HtmlCore import HtmlCore

class Profiler:
    PROFILE_HEADER = '--- Profile ---'
    PROFILE_FOOTER = '--- End Profile ---'

    def __init__(self):
        #self._prof = cProfile.Profile()
        self._prof = hotshot.Profile("hotspot.prof")
        self._stats = None

    def run(self, runStr, globals, locals):
        self._prof = self._prof.runctx(runStr, globals, locals)
        self._prof.close()
        #self._stats = pstats.Stats(self._prof)
        self._stats = hotshot.stats.load("hotspot.prof")
        
    def printStats(self, graphDir=None, id=None):
        if self._stats == None:
            return
        
        print Profiler.PROFILE_HEADER
        self._stats.sort_stats('cumulative')
        self._stats.print_stats()
        print Profiler.PROFILE_FOOTER
        
        print Profiler.PROFILE_HEADER
        self._stats.sort_stats('time')
        self._stats.print_stats()
        print Profiler.PROFILE_FOOTER
        
        if graphDir:
            from gtrackcore_memmap.util.PstatsUtil import OverheadStats
            import os
            id = str(id) if id else ''
            statsFn = os.path.join(graphDir, id + '_prof.stats')
            dotFn = os.path.join(graphDir, id + '_callGraph.dot')
            pngFn = os.path.join(graphDir, id + '_callGraph.png')
            self._stats.dump_stats(statsFn)
            stats = OverheadStats(statsFn)
            stats.writeDotGraph(dotFn, prune=True)
            stats.renderGraph(dotFn, pngFn)

    #def printLinkToCallGraph(self, id, galaxyFn, prune=True):
    #    statsFile = GalaxyRunSpecificFile(id + ['pstats.dump'], galaxyFn)
    #    dotFile = GalaxyRunSpecificFile(id + ['callGraph.dot'], galaxyFn)
    #    pngFile = GalaxyRunSpecificFile(id + ['callGraph.png'], galaxyFn)
    #    
    #    ensurePathExists(statsFile.getDiskPath())
    #    
    #    self._stats.dump_stats(statsFile.getDiskPath())
    #    stats = OverheadStats(statsFile.getDiskPath())
    #    stats.writeDotGraph(dotFile.getDiskPath(), prune=prune)
    #    stats.renderGraph(dotFile.getDiskPath(), pngFile.getDiskPath())
    #    
    #    print str(HtmlCore().link('Call graph based on profiling (id=%s)' % ':'.join(id), pngFile.getURL()))