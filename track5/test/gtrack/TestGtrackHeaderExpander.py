import os
import sys
import unittest

from tempfile import NamedTemporaryFile

from track5.gtrack.GtrackHeaderExpander import expandHeadersOfGtrackFileAndReturnContents, \
    EXPANDABLE_HEADERS, NOT_GUARANTEED_EXPANDABLE_HEADERS, VALUE_NOT_KEPT_HEADERS
from track5.input.core.GenomeElementSource import GenomeElementSource
from track5.input.fileformats.GtrackGenomeElementSource import GtrackGenomeElementSource as Gtrack
from track5.input.wrappers.GEDependentAttributesHolder import GEDependentAttributesHolder
from track5.test.common.Asserts import TestCaseWithImprovedAsserts
from track5.test.common.TestWithGeSourceData import TestWithGeSourceData

class TestGtrackHeaderExpander(TestWithGeSourceData, TestCaseWithImprovedAsserts):
    GENOME = 'TestGenome'
    TRACK_NAME_PREFIX = ['TestGenomeElementSource']
        
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = open('/dev/null', 'w')
    
    def tearDown(self):
        sys.stdout = self.stdout
    
    def _isHeaderLine(self, line):
        return len(line) > 3 and \
                line.startswith('##') and \
                line[2] != '#' and \
                ':' in line
            
    def _isExpandableHeader(self, line, onlyGuaranteed):
        return self._isHeaderLine(line) and \
                ( (Gtrack.getHeaderKeyValue(line)[0] in EXPANDABLE_HEADERS) or \
                   (not onlyGuaranteed and Gtrack.getHeaderKeyValue(line)[0] in NOT_GUARANTEED_EXPANDABLE_HEADERS) )
        
    def _isValueNotKeptHeader(self, line):
        return self._isHeaderLine(line) and \
                Gtrack.getHeaderKeyValue(line)[0] in VALUE_NOT_KEPT_HEADERS
        
    def testHeaderExpansion(self):
        geSourceTest = self._commonSetup()
        
        for caseName in geSourceTest.cases:
            if not caseName.startswith('gtrack'):
                continue
                
            if 'no_expand' in caseName:
                print 'Test case skipped: ' + caseName
                continue
                
            onlyGuaranteed = 'no_types_expanded' in caseName
            
            print caseName
            print '==========='
            case = geSourceTest.cases[caseName]
            
            headerLines = [line if not self._isHeaderLine(line) else
                            '##' + ': '.join([str(x).lower() for x in Gtrack.getHeaderKeyValue(line.strip())])
                             for line in case.headerLines]
            
            fullContents = os.linesep.join(headerLines + case.lines)
            print 'Original:\n\n' + fullContents
            
            case.headerLines = [line for line in headerLines if not self._isExpandableHeader(line, onlyGuaranteed)]
            print '-----'
            print 'With headers removed:\n\n' + os.linesep.join(case.headerLines + case.lines)
            
            testFn = self._writeTestFile(case)
            
            expandedContents = expandHeadersOfGtrackFileAndReturnContents(testFn, case.genome, onlyNonDefault=False)

            print '-----'
            print 'With expanded headers:\n\n' + expandedContents
            
            expandedContentsOnlyNonDefaults = expandHeadersOfGtrackFileAndReturnContents(testFn, case.genome, onlyNonDefault=True)

            print '-----'
            print 'With expanded headers (only non-default headers):\n\n' + expandedContentsOnlyNonDefaults
            
            origExpandableHeaders = dict([Gtrack.getHeaderKeyValue(line) for line in headerLines \
                                          if self._isExpandableHeader(line, onlyGuaranteed=False)])
            notExpandableHeaders = dict([Gtrack.getHeaderKeyValue(line) for line in case.headerLines \
                                          if self._isHeaderLine(line) and not self._isValueNotKeptHeader(line)])
            expandedHeaders = dict([Gtrack.getHeaderKeyValue(line) for line in expandedContents.split(os.linesep) \
                                    if self._isHeaderLine(line)])
            
            if 'no_check_expand' in caseName:
                print 'No checks for case: ' + caseName
            else:
                for header in origExpandableHeaders:
                    self.assertEquals(origExpandableHeaders[header], expandedHeaders[header])
                for header in notExpandableHeaders:
                    self.assertEquals(notExpandableHeaders[header], expandedHeaders[header])
                    
                for contents in [expandedContents, expandedContentsOnlyNonDefaults]:
                    
                    sourceClass = GenomeElementSource if case.sourceClass is None else case.sourceClass
                    forPreProcessor = True if case.sourceClass is None else False

                    stdGeSource = GEDependentAttributesHolder(sourceClass('expanded.gtrack', case.genome, \
                                                                          forPreProcessor=forPreProcessor, \
                                                                          printWarnings=False, \
                                                                          strToUseInsteadOfFn=contents))
                    
                    self.assertEquals(case.assertElementList, [ge for ge in stdGeSource])
                    self.assertEquals(case.boundingRegionsAssertList, [br for br in stdGeSource.getBoundingRegionTuples()])
            
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestGtrackHeaderExpander().debug()
    unittest.main()