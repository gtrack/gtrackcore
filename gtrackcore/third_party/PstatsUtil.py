import pkg_resources

from gtrackcore.third_party import gprof2dot

pkg_resources.require('pygraphviz')
import pygraphviz

import re
import timeit

from math import fsum
from pstats import Stats

#from rpy2 import robjects

NUMPY_CALL_COST = 6.101131439208984e-06 # the result of numpyCallCost on invitro, at 20110121
PYTHON_CALL_COST = 1.230599880218506e-07 # the result of pythonCallCost on invitro, at 20110127
PYTHON_OBJECT_CREATION_COST =  4.825901985168457e-07 # the result of pythonObjectCreationCost on invitro, at 20110127

def functionNameMatches(func, pattern):
    return re.search(pattern, func[2])

def sourceFilePathMatches(func, pattern):
    return re.search(pattern, func[0])

def sourceFileLineNumberMatches(func, lineNumber):
    return func[1] == lineNumber

def numpyCallCost():
    """
    Returns the run time of a call to numpy.sum on an empty numpy array.
    
    This is an attempt at estimating what an empty/no-op numpy call
    costs. What we're after here is the cost of a call from 'regular'
    python to a python C extension.
    """
    return timeit.timeit(stmt='np.sum(a)', setup='import numpy as np;a=np.array([])', number=1000) / 1000

def pythonCallCost():
    """
    Returns the run time of a call to a very simple python function.
    This is an attempt at estimating what a python function call costs.
    """
    return timeit.timeit(stmt='f()', setup='def f(): return 1', number=1000000) / 1000000

def pythonObjectCreationCost():
    """
    Returns the run time of the instantiation of a very simple python class.
    This is an attempt at estimating what a python object instantiation costs.
    """
    return timeit.timeit(stmt='obj = C(1)', setup="""\
class C(object):
    def __init__(self, i):
        self.i = i""", number=100000) / 100000


def isWithinBounds(actualValue, hardCodedValue, bounds=.2):
    """
    Returns True if hardCodedValue is within +/- 20% (bounds * 100 %) of actualValue, False otherwise.
    """
    return (actualValue * (1 - bounds)) < hardCodedValue < (actualValue * (1 + bounds))

class PstatsInstanceParser(gprof2dot.PstatsParser):
    """
    Overrides __init__ to let us parse Pstats from a pstats.Stats
    instance directly, without going via a file.
    """
    def __init__(self, stats):
        self.stats = stats
        self.profile = gprof2dot.Profile()
        self.function_ids = {}

# XXX This, along with DotWriterFontPath and
# TEMPERATURE_COLORMAP_WITH_FONTS is a terrible hack to work around
# the fact that graphviz is broken and can't find any fonts at all on
# invitro. So we have to help it: this writes a fontpath attribute on
# the graph, and fontname attribute on each node and edge in the
# graph.
class ThemeFontPath(gprof2dot.Theme):
    def __init__(self, *args, **kwargs):
        if kwargs.has_key('fontpath'):
            self.fontpath = kwargs['fontpath']
            del kwargs['fontpath']
        else:
            self.fontpath = None
        gprof2dot.Theme.__init__(self, *args, **kwargs)

    def graph_fontpath(self):
        return self.fontpath

class DotWriterFontPath(gprof2dot.DotWriter):
    def graph(self, profile, theme):
        self.fontpath = theme.graph_fontpath()
        gprof2dot.DotWriter.graph(self, profile, theme)

    def begin_graph(self):
        gprof2dot.DotWriter.begin_graph(self)
        if self.fontpath is not None:
            self.write('\tfontpath = "{}"'.format(self.fontpath))

TEMPERATURE_COLORMAP_WITH_FONTS = ThemeFontPath(
    mincolor = (2.0/3.0, 0.80, 0.25), # dark blue
    maxcolor = (0.0, 1.0, 0.5), # satured red
    gamma = 1.0,
    fontpath = '/usr/share/fonts/bitstream-vera',
    fontname = 'Vera'
)

class OverheadStats(Stats):
    def __init__(self, *args, **kwargs):
        self._intermediate = {}
        # super(OverheadStats, self).__init__(self, *args, **kwargs)
        Stats.__init__(self, *args, **kwargs)

    @property
    def intermediate(self):
        """
        Get intermediate computations
        """
        return self._intermediate

    def store(self, ns, key, value):
        self._intermediate['.'.join([ns, key])] = value

    def totalNumpyRuntime(self):
        """
        Returns the total runtime of all numpy calls.
        """
        def getCumulativeTime(func):
            """
            Returns the cumulative time (the total time func was on
            the stack) for func if it is a numpy function, or 0
            otherwise.
            
            To determine if func is a numpy function, just about the
            only thing we can do is looking 'numpy' in the path for
            the file it is defined in, or in the function name.'
            """
            return self.stats[func][3] if sourceFilePathMatches(func, 'numpy') or functionNameMatches(func, 'numpy')  else 0
        results = map(getCumulativeTime, self.stats)
        return fsum(results)

    def totalNumpyCalls(self):
        """
        Returns the sum of call counts for all numpy functions.
        """
        def getCalls(func):
            """
            Returns the total call count for func if it is a numpy
            function, or 0 if it isn't a numpy function.
            
            To determine if func is a numpy function, just about the
            only thing we can do is looking 'numpy' in the path for
            the file it is defined in, or in the function name.'
            """
            return self.stats[func][1] if sourceFilePathMatches(func, 'numpy') or functionNameMatches(func, 'numpy')  else 0
        results = map(getCalls, self.stats)
        return sum(results)

    def totalObjectCreations(self):
        """
        Returns the total number of calls to <any object>.__new__; the
        number of object instantiations done.
        """
        return sum(func[1] for func in self.stats if functionNameMatches(func, '__new__'))

    def totalPythonCalls(self):
        """
        Returns the total number of function calls.
        """
        return sum(func[1] for func in self.stats)

    def totalNumpyCallCost(self):
        """
        Returns a two-tuple where the first element is the total cost
        of all numpy calls, and the second element is True if the used
        NUMPY_CALL_COST is within bounds, False otherwise.
        """
        return ((self.totalNumpyCalls() * NUMPY_CALL_COST), isWithinBounds(NUMPY_CALL_COST, numpyCallCost()))

    def totalPythonCallCost(self):
        """
        Returns a two-tuple where the first element is the total cost
        of all python calls, and the second element is True if the
        used PYTHON_CALL_COST is within bounds, False otherwise.
        """
        return ((self.totalPythonCalls() * PYTHON_CALL_COST), isWithinBounds(PYTHON_CALL_COST, pythonCallCost()))

    def totalPythonObjectCreationCost(self):
        """
        Returns a two-tuple where the first element is the total cost
        of all python object creations, and the second element is True
        if the used PYTHON_OBJECT_CREATION_COST is within bounds,
        False otherwise.
        """
        return ((self.totalObjectCreations() * PYTHON_OBJECT_CREATION_COST),
                isWithinBounds(PYTHON_OBJECT_CREATION_COST, pythonObjectCreationCost()))

    def totalComputeRuntime(self):
        """
        Returns the total runtime for all calls to any statistic's
        _compute() method.
        """
        def getCumulativeTime(func):
            """
            Returns the cumulative time (the total time func was on
            the stack) for func if is named _compute AND the file it
            is defined in has 'statistic' in its path. Returns 0 for
            all other funcs.
            """
            return self.stats[func][3] if sourceFilePathMatches(func, 'statistic') and functionNameMatches(func, '^_compute$') else 0
        results = map(getCumulativeTime, self.stats)
        return fsum(results)

    def overheadRatioByCompute(self):
        """
        Returns the ratio of overhead based on the model given below:

        if we say that: computation runtime = total runtime of <statistic>._compute() calls
        that gives us overhead as: overhead = total runtime - computation runtime
        this gives us the overhead ratio of: ratio = overhead / total time

        this, in turn can give us the percentage of overhead by: ratio * 100
        """
        return (self.total_tt - self.totalComputeRuntime()) / self.total_tt

    def overheadRatioByNumpy(self):
        """
        Returns the ratio of overhead based on the model given below:

        if we say that: computation runtime = total runtime of all numpy function calls
        that gives us overhead as: overhead = total runtime - computation runtime
        this gives us the overhead ratio of: ratio = overhead / total time

        this, in turn can give us the percentage of overhead by: ratio * 100
        """
        return (self.total_tt - self.totalNumpyRuntime()) / self.total_tt

    def overheadRatioByNumpyWithCallCost(self):
        """
        Returns a two-tuple where the first element is the overhead
        ratio based on the model below, and the second element is True
        if the used NUMPY_CALL_COST is within bounds, False otherwise.

        Overhead ratio model:
        if we say that: computation runtime = total runtime of all numpy function calls - (the cost of a numpy call * numpy call count)
        that gives us overhead as: overhead = total runtime - computation runtime
        this gives us the overhead ratio of: ratio = overhead / total time

        this, in turn can give us the percentage of overhead by: ratio * 100
        """
        totalNumpyCallCost, costIsWithinBounds = self.totalNumpyCallCost()
        overheadRatio = (self.total_tt - (self.totalNumpyRuntime() - totalNumpyCallCost)) / self.total_tt
        return (overheadRatio, costIsWithinBounds)

    def overheadRatioByPythonCalls(self):
        """
        Returns a two-tuple where the first element is the overhead
        ratio based on the model below, and the second element is True
        if the used PYTHON_CALL_COST is within bounds, False otherwise.

        Overhead ratio model:
        TODO
        """
        totalPythonCallCost, costIsWithinBounds = self.totalPythonCallCost()
        overheadRatio = totalPythonCallCost / self.total_tt
        return (overheadRatio, costIsWithinBounds)

    def overheadRatioByObjectCreations(self):
        """
        Returns a two-tuple where the first element is the overhead
        ratio based on the model below, and the second element is True
        if the used PYTHON_OBJECT_CREATION_COST is within bounds, False otherwise.

        Overhead ratio model:
        TODO
        """
        totalObjectCreationCost, costIsWithinBounds = self.totalPythonObjectCreationCost()
        overheadRatio = totalObjectCreationCost / self.total_tt
        return (overheadRatio, costIsWithinBounds)

    def writeDotGraph(self, filename, prune=False):
        parser = PstatsInstanceParser(self)
        profile = parser.parse()

        if prune:
            profile.prune(0.005, 0.001)
        with open(filename, 'wt') as f:
            dot = DotWriterFontPath(f)
            dot.graph(profile, TEMPERATURE_COLORMAP_WITH_FONTS)

    def renderGraph(self, dotFilename, outFilename):
        graph = pygraphviz.AGraph(dotFilename)
        graph.layout('dot')
        graph.draw(outFilename)

    def totalGetitemRuntime(self):
        results = [self.stats[func][3] for func in self.stats if functionNameMatches(func, "__getitem__")]
        self._intermediate['getitem.results'] = results
        self._intermediate['getitem.sum'] = fsum(results)
        return fsum(results)

    def totalStrConcatRuntime(self):
        results = [self.stats[func][3] for func in self.stats if functionNameMatches(func, "'join' of 'str'")]
        self._intermediate['strconcat.results'] = results
        self._intermediate['strconcat.sum'] = fsum(results)
        return fsum(results)

    def weightedOverhead(self, numpy=False):
        ns = 'weighted.numpy' if numpy else 'weighted'
        factors = {
            'strConcat': 0.8171743283710745,
            'objectInit': 162.78282024428898,
            'getListItem': 12.018827808252004,
            'functionCall': 48.613475069418904,
            'getDictItem': 0.2148913920265531,
            'methodCall': 75.36797944163118,
            'numpy': 1.0,
            }
        runtimes = {
            'strConcat': self.totalStrConcatRuntime(),
            'objectInit': self.totalObjectCreations() * PYTHON_OBJECT_CREATION_COST,
            'functionCall': self.totalPythonCalls() * PYTHON_CALL_COST,
            'getListItem': self.totalGetitemRuntime(),
            }
        if numpy:
            runtimes['numpy'] = self.totalNumpyRuntime()

        total_runtime = fsum(runtimes.values())
        c_runtimes = {key:(runtime / factors[key]) for key, runtime in runtimes.iteritems()}
        total_c_runtime = fsum(c_runtimes.values())

        self.store(ns, 'total_tt', self.total_tt)
        self.store(ns, 'total_runtime', total_runtime)
        self.store(ns, 'total_c_runtime', total_c_runtime)
        self.store(ns, 'runtimes', runtimes)
        self.store(ns, 'factors', factors)
        self.store(ns, 'c_runtimes', c_runtimes)

        return 1 - (total_c_runtime / total_runtime), (total_runtime / self.total_tt)

    def allOverheads(self):
        not_numpy_not_call = self.overheadRatioByNumpyWithCallCost()
        object_creations = self.overheadRatioByObjectCreations()
        function_calls = self.overheadRatioByPythonCalls()
        weighted = self.weightedOverhead(numpy=True)
        weighted_no_numpy = self.weightedOverhead()
        overheads = [
            {'model': 'not in _compute()', 'result': self.overheadRatioByCompute()},
            {'model': 'not numpy', 'result': self.overheadRatioByNumpy()},
            {'model': 'not numpy, not call', 'result': not_numpy_not_call[0], 'within treshold': not_numpy_not_call[1]},
            {'model': 'object creations', 'result': object_creations[0], 'within treshold': object_creations[1]},
            {'model': 'function calls', 'result': function_calls[0], 'within treshold': function_calls[1]},
            {'model': 'python/c++ weighted operations', 'result': weighted[0], 'ratio of total': weighted[1]},
            {'model': 'python/c++ weighted operations (without numpy)', 'result': weighted_no_numpy[0], 'ratio of total': weighted_no_numpy[1]},
            ]
        return overheads

    def stackFramePercentages(self):
        """
        Return tottime/total_tt * 100 for each function, in a list.

        - tottime is the total time a function has been the active stack frame
        - total_tt is the total run time

        What we get is then a percentage of time the function was the
        active function. If this percentage is high, the function might be
        a bottleneck in our program and should be investigated further.
        """
        return [(self.stats[func][2] / self.total_tt) * 100 for func in self.stats]

    def plotStackFramePercentages(self, fpath):
        runtime_ratios = self.stackFramePercentages()
        runtime_ratios = robjects.FloatVector(sorted(p, reverse=True))
        robjects.r['pdf'](fpath)
        robjects.r['plot'](robjects.IntVector(range(len(p))),
                           runtime_ratios,
                           xlab='Function calls',
                           ylab='Percentage of total run time as active stack frame',
                           main='Visualizing bottlenecks')
        robjects.r['dev.off']()

if __name__ == '__main__':
    import argparse
    from os.path import abspath
    parser = argparse.ArgumentParser(description='Find numpy and/or compute overhead in Python profile output.')
    parser.add_argument('statsfile', metavar='STATSFILE', nargs='+',
                        help='the stat file(s) we want to inspect')
    parser.add_argument('-v', action='store_true', dest='verbose',
                        default=False,
                        help='Verbose output: print intermediate computations')
    args = parser.parse_args()

    for f in args.statsfile:
        stats = OverheadStats(f)
        print abspath(f)
        print 'Overhead calculations:'
        print '_compute: {:%}'.format(stats.overheadRatioByCompute())
        print 'numpy: {:%}'.format(stats.overheadRatioByNumpy())
        overheadRatio, _ = stats.overheadRatioByNumpyWithCallCost()
        print 'numpy w/callcost: {:%}'.format(overheadRatio)

        print 'weighted operations: {0:%} (run time covered {1:%})'.format(*stats.weightedOverhead(numpy=True))
        if args.verbose:
            print '\tIntermediate computations'
            for k, v in sorted(stats.intermediate.iteritems()):
                print '\t\t{}: {}'.format(k, v)

        print 'weighted operations without numpy: {0:%}, (run time covered {1:%})'.format(*stats.weightedOverhead(numpy=False))
        if args.verbose:
            print '\tIntermediate computations'
            for k, v in sorted(stats.intermediate.iteritems()):
                print '\t\t{}: {}'.format(k, v)
