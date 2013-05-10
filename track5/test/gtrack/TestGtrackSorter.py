import sys
import unittest

from tempfile import NamedTemporaryFile

from track5.gtrack.GtrackSorter import UnsortedGtrackGenomeElementSource, sortGtrackFileAndReturnContents
from track5.input.core.GenomeElementSource import GenomeElementSource
from track5.input.wrappers.GEDependentAttributesHolder import GEDependentAttributesHolder
from track5.test.common.TestWithGeSourceData import TestWithGeSourceData
from track5.test.common.Asserts import TestCaseWithImprovedAsserts
from track5.track.format.TrackFormat import TrackFormat

class TestGtrackSorter(TestWithGeSourceData, TestCaseWithImprovedAsserts):
    GENOME = 'TestGenome'
    TRACK_NAME_PREFIX = ['TestGenomeElementSource']
        
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = open('/dev/null', 'w')
    
    def tearDown(self):
        sys.stdout = self.stdout
    
    def testSorting(self):
        geSourceTest = self._commonSetup()
        
        for caseName in geSourceTest.cases:
            if not caseName.startswith('gtrack'):
                continue
                
            if 'no_sort' in caseName:
                print 'Test case skipped: ' + caseName
                continue
                
            print caseName
            print
            
            case = geSourceTest.cases[caseName]
            testFn = self._writeTestFile(case)
            print open(testFn).read()
            print
            
            sortedContents = sortGtrackFileAndReturnContents(testFn, case.genome)
            print sortedContents

            sourceClass = GenomeElementSource if case.sourceClass is None else case.sourceClass
            forPreProcessor = True if case.sourceClass is None else False
            sortedGeSource = GEDependentAttributesHolder(sourceClass('sortedFile.gtrack', case.genome, \
                                                                     forPreProcessor=forPreProcessor, \
                                                                     printWarnings=False, \
                                                                     strToUseInsteadOfFn=sortedContents))
            
            
            reprIsDense = TrackFormat.createInstanceFromGeSource(sortedGeSource).reprIsDense()
            
            if not reprIsDense:
                self.assertEquals(sorted(case.assertElementList), [ge for ge in sortedGeSource])
            else:
                for ge in sortedGeSource:
                    pass
            
            self.assertEquals(sorted(case.boundingRegionsAssertList), [br for br in sortedGeSource.getBoundingRegionTuples()])
            
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestGtrackSorter().debug()
    unittest.main()