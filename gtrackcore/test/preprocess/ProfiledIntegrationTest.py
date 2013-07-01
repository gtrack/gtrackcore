import sys

from gtrackcore.util.Profiler import Profiler
from gtrackcore.test.common.Asserts import TestCaseWithImprovedAsserts
from gtrackcore.test import get_data_output_path

class ProfiledIntegrationTest(TestCaseWithImprovedAsserts):
    VERBOSE = False
    USE_PROFILER = False
    
    def setUp(self):
        if not self.VERBOSE:
            self.stdout = sys.stdout
            sys.stdout = open('/dev/null', 'w')
        sys.stdout = sys.stderr
        
    def tearDown(self):
        if not self.VERBOSE:
            sys.stdout = self.stdout
        
    def _runWithProfiling(self, runStr, globals, locals):
        if self.USE_PROFILER:    
            print 'Running with profiling..'
            profiler = Profiler()
            res = profiler.run(runStr, globals, locals)
            profiler.printStats(graphDir=get_data_output_path(), id=self.__class__.__name__)
            return res
        else:
            return eval(runStr, globals, locals)
