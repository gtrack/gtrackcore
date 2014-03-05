import hotshot
import hotshot.stats
import os
import shutil
import sys

from gtrackcore.util.CommonFunctions import convertTNstrToTNListFormat, get_dir_path


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
            from gtrackcore.third_party.PstatsUtil import OverheadStats
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
    #    print str(HtmlCore().link('Call graph based on profile (id=%s)' % ':'.join(id), pngFile.getURL()))

def profile_track_preprocessor(genome, track_name):
    from gtrackcore.preprocess.PreProcessTracksJob import PreProcessAllTracksJob
    track_name = convertTNstrToTNListFormat(track_name, doUnquoting=True)

    for allow_overlaps in [True, False]:
        track_path = get_dir_path(genome, track_name, allow_overlaps=allow_overlaps)
        print track_path
        if os.path.exists(track_path):
            shutil.rmtree(os.path.dirname(track_path))

    profiler = Profiler()
    profiler.run('PreProcessAllTracksJob(genome, track_name, username=\'\', mode=\'Real\').process()', globals(), locals())
    profiler.printStats()

if __name__ == '__main__':
    track_name = 'testcat:stor'
    genome = 'testgenome'

    if sys.argv[1] == 'preprocessing':
        profile_track_preprocessor(genome, track_name)
