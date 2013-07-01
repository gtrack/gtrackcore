import unittest

from tempfile import NamedTemporaryFile

from gtrackcore.gtrack.GtrackComplementer import complementGtrackFileAndReturnContents
from gtrackcore.test.common.Asserts import TestCaseWithImprovedAsserts
from gtrackcore.util.CustomExceptions import InvalidFormatError
 
class TestGtrackComplementer(TestCaseWithImprovedAsserts):
    def testUsingElementId(self):
        contents1 = '\n'.join(\
           ['##track type: valued segments',
            '\t'.join(['###seqid', 'start', 'end', 'value', 'id']),
            '\t'.join(['chrM', '100', '120', '2.5', 'A']),
            '\t'.join(['chrM', '200', '220', '1.2', 'B'])])
        
        contents2 = '\n'.join( \
           ['##track type: points',
            '\t'.join(['###seqid', 'start', 'strand', 'sth', 'other', 'id']),
            '\t'.join(['chrM', '300', '+', 'b', 'yes', 'B']),
            '\t'.join(['chrM', '400', '-', 'c', 'yes', 'C']),
            '\t'.join(['chrM', '500', '-', 'a', 'no', 'A'])])
        
        complemented = '\n'.join( \
           ['##gtrack version: 1.0',
            '##track type: valued segments',
            '##uninterrupted data lines: true',
            '##sorted elements: true',
            '##no overlapping elements: true',
            '\t'.join(['###seqid', 'start', 'end', 'value', 'strand', 'id', 'other']),
            '\t'.join(['chrM', '100', '120', '2.5', '-', 'A', 'no']),
            '\t'.join(['chrM', '200', '220', '1.2', '+', 'B', 'yes'])])
        
        self._assertGtrackComplementer(contents1, contents2, complemented, 'id', ['strand', 'other'])
    
    def testUsingElementIdChangeTrackTypes(self):
        contents1 = '\n'.join( \
           ['##track type: points',
            '\t'.join(['###seqid', 'start', 'other', 'id']),
            '\t'.join(['chrM', '100', 'yes', 'A']),
            '\t'.join(['chrM', '200', 'no', 'B'])])
        
        contents2 = '\n'.join( \
           ['##gtrack version: 1.0',
            '##track type: valued segments',
            '##value type: character',
            '##value dimension: vector',
            '\t'.join(['###seqid', 'start', 'end', 'strand', 'sth', 'value', 'id']),
            '\t'.join(['chrM', '300', '350', '+', 'b', 'bbb', 'B']),
            '\t'.join(['chrM', '400', '450', '-', 'c', 'ccc', 'C']),
            '\t'.join(['chrM', '500', '550', '-', 'a', 'aaa', 'A'])])
        
        complemented = '\n'.join( \
           ['##gtrack version: 1.0',
            '##track type: valued segments',
            '##value type: character',
            '##value dimension: vector',
            '##uninterrupted data lines: true',
            '##sorted elements: true',
            '\t'.join(['###seqid', 'start', 'end', 'value', 'strand', 'id', 'other']),
            '\t'.join(['chrM', '100', '550', 'aaa', '-', 'A', 'yes']),
            '\t'.join(['chrM', '200', '350', 'bbb', '+', 'B', 'no'])])
        
        self._assertGtrackComplementer(contents1, contents2, complemented, 'id', ['end', 'strand', 'value'])
        
    def testUsingPositionalInfoWithMissingInfo(self):
        contents1 = '\n'.join( \
           ['##track type: segments',
            '\t'.join(['###seqid', 'start', 'end', 'sth']),
            '\t'.join(['chrM', '100', '120', 'a']),
            '\t'.join(['chrM', '200', '220', 'b']),
            '\t'.join(['chr21', '300', '320', 'c'])])
        
        contents2 = '\n'.join( \
           ['##track type: linked segments',
            '##edge weights: true',
            '##edge weight type: character',
            '##edge weight dimension: vector',
            '\t'.join(['###seqid', 'start', 'end', 'edges', 'other', 'id']),
            '\t'.join(['chrM', '100', '120', 'C=cc', 'yes', 'B']),
            '\t'.join(['chr21', '300', '320', 'B=bb', 'yes', 'C']),
            '\t'.join(['chr21', '200', '220', 'B=bb', 'no', 'A'])])
        
        complemented = '\n'.join( \
           ['##gtrack version: 1.0',
            '##track type: linked segments',
            '##edge weights: true',
            '##edge weight type: character',
            '##edge weight dimension: vector',
            '##uninterrupted data lines: true',
            '##no overlapping elements: true',
            '\t'.join(['###seqid', 'start', 'end', 'id', 'edges', 'sth']),
            '\t'.join(['chrM', '100', '120', 'B', 'C=cc', 'a']),
            '\t'.join(['chrM', '200', '220', '.', '.', 'b']),
            '\t'.join(['chr21', '300', '320', 'C', 'B=bb', 'c'])])
        
        self._assertGtrackComplementer(contents1, contents2, complemented, 'position', ['id', 'edges'])
        
    def testUsingPositionalInfoWithMissingInfo(self):
        contents1 = '\n'.join( \
           ['##track type: segments',
            '\t'.join(['###seqid', 'start', 'end', 'sth']),
            '\t'.join(['chrM', '100', '120', 'a'])])
        
        contents2 = '\n'.join( \
           ['##track type: linked segments',
            '##edge weights: true',
            '##edge weight type: character',
            '##edge weight dimension: vector',
            '\t'.join(['###seqid', 'start', 'end', 'edges', 'other', 'id']),
            '\t'.join(['chrM', '100', '120', 'C=cc', 'yes', 'B']),
            '\t'.join(['chrM', '100', '120', 'C=cc', 'no', 'C'])])
        
        origFile = self._getTempGtrackFile(contents1)
        dbFile = self._getTempGtrackFile(contents2)
        
        self.assertRaises(InvalidFormatError, complementGtrackFileAndReturnContents, origFile.name, dbFile.name, 'position', ['id', 'edges'], 'TestGenome')
        
    def _assertGtrackComplementer(self, contents1, contents2, assertComplemented, intersectingFactor, colsToAdd):
        origFile = self._getTempGtrackFile(contents1)
        dbFile = self._getTempGtrackFile(contents2)
        
        complemented = complementGtrackFileAndReturnContents(origFile.name, dbFile.name, intersectingFactor, colsToAdd, 'TestGenome')
        
        #print contents1
        #print
        #print contents2
        #print
        #print assertComplemented
        #print
        #print complemented
        
        self.assertEquals(assertComplemented, complemented.strip())
        
    def _getTempGtrackFile(self, contents):
        f = NamedTemporaryFile(suffix='.gtrack')
        f.write(contents)
        f.seek(0)
        return f
        
    def runTest(self):
        pass
        
if __name__ == "__main__":
    #TestGtrackComplementer().debug()
    unittest.main()