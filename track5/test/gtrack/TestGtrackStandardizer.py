import sys
import unittest

from tempfile import NamedTemporaryFile

from track5.gtrack.GtrackStandardizer import standardizeGtrackFileAndReturnContents
from track5.input.fileformats.GtrackGenomeElementSource import GtrackGenomeElementSource
from track5.test.common.Asserts import TestCaseWithImprovedAsserts
from track5.test.common.TestWithGeSourceData import TestWithGeSourceData
from track5.track.format.TrackFormat import TrackFormat

class TestGtrackStandardizer(TestWithGeSourceData, TestCaseWithImprovedAsserts):
    GENOME = 'TestGenome'
    TRACK_NAME_PREFIX = ['TestGenomeElementSource']
        
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = open('/dev/null', 'w')
    
    def tearDown(self):
        sys.stdout = self.stdout
    
    def testStandardizing(self):
        geSourceTest = self._commonSetup()
        
        for caseName in geSourceTest.cases:
            if not caseName.startswith('gtrack'):
                continue
                
            if 'no_standard' in caseName:
                print 'Test case skipped: ' + caseName
                continue
                
            print caseName
            print
            
            case = geSourceTest.cases[caseName]
            testFn = self._writeTestFile(case)
            print open(testFn).read()
            print
            
            stdContents = standardizeGtrackFileAndReturnContents(testFn, case.genome)
            print stdContents

            self.assertTrue('##track type: linked valued segments' in stdContents)
            self.assertTrue('\t'.join(['###seqid', 'start', 'end', 'value', 'strand', 'id', 'edges']) in stdContents)
            
            geSource = GtrackGenomeElementSource('', case.genome, strToUseInsteadOfFn=stdContents)
            for ge in geSource:
                pass
            
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestGtrackSorter().debug()
    unittest.main()