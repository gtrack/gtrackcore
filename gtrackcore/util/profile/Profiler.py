import hotshot
import hotshot.stats
from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion


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


def profile_track_preprocessor(genome, track_name, galaxyFn=None):
    from gtrackcore.preprocess.PreProcessTracksJob import PreProcessAllTracksJob

    profiler = Profiler()
    profiler.run('PreProcessAllTracksJob(genome, track_name, username=\'\', mode=\'Real\').process()', globals(), locals())

    return profiler


def profile_operation(operation, track_name1, allow_overlaps1, genome_regions, track_name2=None, allow_overlaps2=None):
    from gtrackcore.tools.TrackOperations import count_elements, sum_of_values, \
        sum_of_weights, sum_of_weights_iter, coverage, overlap_iter, overlap

    if track_name1 is not None and track_name2 is not None:
        run_str = operation + '(track_name1, allow_overlaps1, track_name2, allow_overlaps2, genome_regions)'
    elif track_name1 is not None:
        run_str = operation + '(track_name1, allow_overlaps1, genome_regions)'
    else:
        return None

    profiler = Profiler()
    profiler.run(run_str, globals(), locals())

    return profiler

if __name__ == '__main__':

    chromosomes = (GenomeRegion('hg19', chr, 0, len)
                   for chr, len in GenomeInfo.GENOMES['hg19']['size'].iteritems())

    tn1 = 'Sequence:Repeating elements'.split(':')
    tn2 = 'Chromatin:Roadmap Epigenomics:H3K27me3:ENCODE_wgEncodeBroadHistoneGm12878H3k27me3StdPk'.split(':')

    print "Running profiler of overlap operation"
    profiler = profile_operation("overlap", tn1, False, chromosomes, track_name2=tn2, allow_overlaps2=False)
    if profiler is not None:
        profiler.printStats()