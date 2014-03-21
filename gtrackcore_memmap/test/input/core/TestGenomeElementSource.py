import unittest
import tempfile
import os
import sys
import numpy
import copy
from collections import OrderedDict

from gtrackcore_memmap.input.core.GenomeElement import GenomeElement
from gtrackcore_memmap.input.core.GenomeElementSource import GenomeElementSource, BoundingRegionTuple
from gtrackcore_memmap.input.fileformats.BedGenomeElementSource import BedGenomeElementSource, PointBedGenomeElementSource, \
                                                            BedCategoryGenomeElementSource, BedValuedGenomeElementSource
from gtrackcore_memmap.input.fileformats.GffGenomeElementSource import GffGenomeElementSource
from gtrackcore_memmap.input.fileformats.FastaGenomeElementSource import FastaGenomeElementSource
from gtrackcore_memmap.input.fileformats.HBFunctionGenomeElementSource import HBFunctionGenomeElementSource
from gtrackcore_memmap.input.fileformats.BedGraphGenomeElementSource import BedGraphGenomeElementSource, BedGraphTargetControlGenomeElementSource
from gtrackcore_memmap.input.fileformats.WigGenomeElementSource import WigGenomeElementSource, HbWigGenomeElementSource
from gtrackcore_memmap.input.fileformats.MicroarrayGenomeElementSource import MicroarrayGenomeElementSource
from gtrackcore_memmap.input.fileformats.GtrackGenomeElementSource import GtrackGenomeElementSource, HbGzipGtrackGenomeElementSource, \
                                                               HbGtrackGenomeElementSource
from gtrackcore_memmap.input.wrappers.GEDependentAttributesHolder import GEDependentAttributesHolder
from gtrackcore_memmap.test.common.Asserts import TestCaseWithImprovedAsserts
from gtrackcore_memmap.track.core.GenomeRegion import GenomeRegion
from gtrackcore_memmap.util.CommonConstants import BINARY_MISSING_VAL
from gtrackcore_memmap.util.CustomExceptions import InvalidFormatWarning, InvalidFormatError, Warning, ArgumentValueError

class BaseCase(object):
    def __init__(self, sourceClass, genome, headerLines, lines, suffix, trackName, targetClass):
        self.sourceClass = sourceClass
        self.genome = genome
        self.suffix = suffix
        self.headerLines = headerLines
        self.lines = lines
        self.trackName = trackName
        self.targetClass = targetClass
        
    def open(self):
        self.tf = tempfile.NamedTemporaryFile(suffix=self.suffix)
       
        if self.suffix.endswith('.gz'):
            self.tf.write(self.lines[0])
        else:
            if len(self.headerLines) > 0:
                self.tf.write( '\n'.join(self.headerLines) + '\n')
            self.tf.write( '\n'.join(self.lines) + '\n')

        self.tf.seek(0)
        self.name = self.tf.name
        
        f = open(self.tf.name)
        while True:
            l = f.readline()
            if l=='':
                break
            #print repr(l)
        
    def close(self):
        self.tf.close()

class Case(BaseCase):
    def __init__(self, sourceClass, genome, headerLines, lines, suffix, trackName, assertElementList,\
                 boundingRegionsAssertList, targetClass, prefixList, valDataType, valDim, \
                 edgeWeightDataType, edgeWeightDim):
        BaseCase.__init__(self, sourceClass, genome, headerLines, lines, suffix, trackName, targetClass)
        self.assertElementList = assertElementList
        self.boundingRegionsAssertList = boundingRegionsAssertList
        self.prefixList = prefixList
        self.valDataType = valDataType
        self.valDim = valDim
        self.edgeWeightDataType = edgeWeightDataType
        self.edgeWeightDim = edgeWeightDim

class ExceptionCase(BaseCase):
    def __init__(self, sourceClass, genome, headerLines, lines, suffix, trackName, targetClass, exceptionClass):
        BaseCase.__init__(self, sourceClass, genome, headerLines, lines, suffix, trackName, targetClass)
        self.exceptionClass = exceptionClass

class TestGenomeElementSource(TestCaseWithImprovedAsserts):
    def setUp(self):
        self.cases = OrderedDict()
        
        # Testing:
        # - Basic 3-column BED file
        self.cases['gtrack_t0'] = \
            Case(GtrackGenomeElementSource,
                 'TestGenome',
                [],
                ['\t'.join(['chrM','100','165']),
                 '\t'.join(['chrM','200','299']),
                 '\t'.join(['chrM','300','399'])],
                '.gtrack',
                ['t0','gtrack'],
                [GenomeElement('TestGenome', 'chrM', start=100, end=165),
                 GenomeElement('TestGenome', 'chrM', start=200, end=299),
                 GenomeElement('TestGenome', 'chrM', start=300, end=399)],
                [],
                GtrackGenomeElementSource,
                ['start', 'end'],
                'float64',
                1,
                'float64',
                1)
        
        # Testing:
        # - Track type: points
        # - Column specification line
        self.cases['gtrack_t1'] = \
            Case(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: points',
                 '\t'.join(['###seqid','start'])],
                ['\t'.join(['chrM','100']),
                 '\t'.join(['chrM','200']),
                 '\t'.join(['chrM','300'])],
                '.gtrack',
                ['t1','gtrack'],
                [GenomeElement('TestGenome', 'chrM', start=100),
                 GenomeElement('TestGenome', 'chrM', start=200),
                 GenomeElement('TestGenome', 'chrM', start=300)],
                [],
                GtrackGenomeElementSource,
                ['start'],
                'float64',
                1,
                'float64',
                1)
        
        # Testing:
        # - Track type: segments
        # - Case-insensitive headers
        # - Spacing in headers
        # - Overlapping elements, unsorted order
        # - Column specification line: added non-core reserved columns
        # - Case-insensitive column names
        # - No genome
        self.cases['gtrack_t2'] = \
            Case(GtrackGenomeElementSource,
                 None,
                ['##TRACK TYPE:  Segments',
                 '\t'.join(['###seqid','Start','END','strand'])],
                ['\t'.join(['chrM','100','165','+']),
                 '\t'.join(['chrM','200','349','-']),
                 '\t'.join(['chrM','100','199','+'])],
                '.gtrack',
                ['t2','gtrack'],
                [GenomeElement(None, 'chrM', start=100, end=165, strand=True),
                 GenomeElement(None, 'chrM', start=200, end=349, strand=False),
                 GenomeElement(None, 'chrM', start=100, end=199, strand=True)],
                [],
                GtrackGenomeElementSource,
                ['start', 'end', 'strand'],
                'float64',
                1,
                'float64',
                1)
        
        # Testing:
        # - Track type: genome partition
        # - Uninterrupted data lines = True
        # - Single bounding region spec (with seqid as both column and in b.r.)
        self.cases['gtrack_t3_no_hb'] = \
            Case(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: genome partition',
                 '##uninterrupted data lines: true',
                 '\t'.join(['###seqid','end'])],
                ['####seqid=chrM; start=100; end=400',
                 '\t'.join(['chrM','200']),
                 '\t'.join(['chrM','300']),
                 '\t'.join(['chrM','400'])],
                '.gtrack',
                ['t3_no_hb','gtrack'],
                [GenomeElement('TestGenome', 'chrM', end=200),
                 GenomeElement('TestGenome', 'chrM', end=300),
                 GenomeElement('TestGenome', 'chrM', end=400)],
                [BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=100, end=400), elCount=3)],
                GtrackGenomeElementSource,
                ['end'],
                'float64',
                1,
                'float64',
                1)
        
        self.cases['gtrack_t3_hb'] = \
            Case(None,
                 'TestGenome',
                ['##track type: genome partition',
                 '##uninterrupted data lines: true',
                 '\t'.join(['###seqid','end'])],
                ['####seqid=chrM; start=100; end=400',
                 '\t'.join(['chrM','200']),
                 '\t'.join(['chrM','300']),
                 '\t'.join(['chrM','400'])],
                '.gtrack',
                ['t3_hb','gtrack'],
                [GenomeElement('TestGenome', 'chrM', end=100),
                 GenomeElement('TestGenome', 'chrM', end=200),
                 GenomeElement('TestGenome', 'chrM', end=300),
                 GenomeElement('TestGenome', 'chrM', end=400)],
                [BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=100, end=400), elCount=4)],
                HbGtrackGenomeElementSource,
                ['end'],
                'float64',
                1,
                'float64',
                1)
        
        # Testing:
        # - Track type: valued points
        # - Track elements in unsorted order
        # - 1-indexed positions
        self.cases['gtrack_t4_no_track_extract'] = \
            Case(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: valued points',
                 '##1-indexed: true',
                 '\t'.join(['###seqid','start','value'])],
                ['\t'.join(['chrM','201','-0.1']),
                 '\t'.join(['chrM','101','0.1']),
                 '\t'.join(['chrM','201','0.0'])],
                '.gtrack',
                ['t4','gtrack'],
                [GenomeElement('TestGenome', 'chrM', start=200, val=-0.1),
                 GenomeElement('TestGenome', 'chrM', start=100, val=0.1),
                 GenomeElement('TestGenome', 'chrM', start=200, val=0.0)],
                [],
                GtrackGenomeElementSource,
                ['start', 'val'],
                'float64',
                1,
                'float64',
                1)
        
        # Testing:
        # - Track type: valued segments
        # - No specified genome + invalid chr + positions outside sequence 
        # - Value: binary
        # - Value column: case
        # - Explicit specification of value dimension: scalar
        # - End inclusive positions
        self.cases['gtrack_t5_no_hb'] = \
            Case(GtrackGenomeElementSource,
                 None,
                ['##track type: valued segments',
                 '##value type: binary',
                 '##value dimension: scalar',
                 '##end inclusive: true',
                 '##value column: case',
                 '\t'.join(['###seqid','start','end','case'])],
                ['\t'.join(['chrS','100','165','0']),
                 '\t'.join(['chrM','200','29900','1']),
                 '\t'.join(['chrM','30000','39900','1'])],
                '.gtrack',
                ['t5_no_hb','gtrack'],
                [GenomeElement(None, 'chrS', start=100, end=166, val=0),
                 GenomeElement(None, 'chrM', start=200, end=29901, val=1),
                 GenomeElement(None, 'chrM', start=30000, end=39901, val=1)],
                [],
                GtrackGenomeElementSource,
                ['start', 'end', 'val'],
                'int8',
                1,
                'float64',
                1)
        
        # - No specified genome + valid chr and positions
        self.cases['gtrack_t5_hb'] = \
            Case(None,
                 None,
                ['##track type: valued segments',
                 '##value type: binary',
                 '##value dimension: scalar',
                 '##end inclusive: true',
                 '##value column: case',
                 '\t'.join(['###seqid','start','end','case'])],
                ['\t'.join(['chrM','100','165','0']),
                 '\t'.join(['chrM','200','2900','1']),
                 '\t'.join(['chrM','3000','3900','1'])],
                '.gtrack',
                ['t5_hb','gtrack'],
                [GenomeElement(None, 'chrM', start=100, end=166, val=0),
                 GenomeElement(None, 'chrM', start=200, end=2901, val=1),
                 GenomeElement(None, 'chrM', start=3000, end=3901, val=1)],
                [],
                HbGtrackGenomeElementSource,
                ['start', 'end', 'val'],
                'int8',
                1,
                'float64',
                1)
        
        # Testing:
        # - Track type: step function
        # - Value: category
        # - Irregular single bounding region specification
        # - SeqId specified only in bounding region
        # - Column specification line: added non-core reserved columns and non-reserved columns
        self.cases['gtrack_t6_no_hb'] = \
            Case(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: step function',
                 '##value type: category',
                 '\t'.join(['###end','value','id','conserved','extRef'])],
                ['####end=400;  start=100;SEQID=chrM',
                 '\t'.join(['200','AA','id001','0.9','EXT130']),
                 '\t'.join(['300','BB','id002','0.78','EXT012']),
                 '\t'.join(['400','AA','id003','0.79','EXT123'])],
                '.gtrack',
                ['t6_no_hb','gtrack'],
                [GenomeElement('TestGenome', 'chrM', end=200, val='AA', id='id001', extra=OrderedDict([('conserved','0.9'), ('extref','EXT130')])),
                 GenomeElement('TestGenome', 'chrM', end=300, val='BB', id='id002', extra=OrderedDict([('conserved','0.78'), ('extref','EXT012')])),
                 GenomeElement('TestGenome', 'chrM', end=400, val='AA', id='id003', extra=OrderedDict([('conserved','0.79'), ('extref','EXT123')]))],
                [BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=100, end=400), elCount=3)],
                GtrackGenomeElementSource,
                ['end', 'val', 'id', 'conserved', 'extref'],
                'S',
                1,
                'float64',
                1)
        
        self.cases['gtrack_t6_hb'] = \
            Case(None,
                 'TestGenome',
                ['##track type: step function',
                 '##value type: category',
                 '\t'.join(['###end','value','id','conserved','extRef'])],
                ['####end=400;  start=100;seqid=chrM',
                 '\t'.join(['200','AA','id001','0.9','EXT130']),
                 '\t'.join(['300','BB','id002','0.78','EXT012']),
                 '\t'.join(['400','AA','id003','0.79','EXT123'])],
                '.gtrack',
                ['t6_hb','gtrack'],
                [GenomeElement('TestGenome', 'chrM', end=100, val='', id='', extra=OrderedDict([('conserved',''), ('extref','')])),
                 GenomeElement('TestGenome', 'chrM', end=200, val='AA', id='id001', extra=OrderedDict([('conserved','0.9'), ('extref','EXT130')])),
                 GenomeElement('TestGenome', 'chrM', end=300, val='BB', id='id002', extra=OrderedDict([('conserved','0.78'), ('extref','EXT012')])),
                 GenomeElement('TestGenome', 'chrM', end=400, val='AA', id='id003', extra=OrderedDict([('conserved','0.79'), ('extref','EXT123')]))],
                [BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=100, end=400), elCount=4)],
                HbGtrackGenomeElementSource,
                ['end', 'val', 'id', 'conserved', 'extref'],
                'S',
                1,
                'float64',
                1)
        
        # Testing:
        # - Track type: function
        # - Value dimension: vector of single number
        # - Multiple bounding region specification
        self.cases['gtrack_t7a_no_check_print_no_check_expand_no_sort_no_standard_no_hb'] = \
            Case(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: function',
                 '##value dimension: vector',
                 '###value'],
                ['####seqid=chrM; start=10; end=12',
                 '4.5',
                 '-3.7',
                 '####seqid=chrM; start=1012; end=1014',
                 '2.1',
                 '11'],
                '.gtrack',
                ['t7a_no_hb','gtrack'],
                [GenomeElement('TestGenome', 'chrM', val=[4.5]),
                 GenomeElement('TestGenome', 'chrM', val=[-3.7]),
                 GenomeElement('TestGenome', 'chrM', val=[2.1]),
                 GenomeElement('TestGenome', 'chrM', val=[11])],
                [BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=10, end=12), elCount=2),
                 BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=1012, end=1014), elCount=2)],
                GtrackGenomeElementSource,
                ['val'],
                'float64',
                1,
                'float64',
                1)
        
        # - Value dimension: vector of two numbers
        self.cases['gtrack_t7a_no_check_expand_hb'] = \
            Case(None,
                 'TestGenome',
                ['##track type: function',
                 '##value dimension: vector',
                 '###value'],
                ['####seqid=chrM; start=10; end=12',
                 '4.5,1.2',
                 '-3.7,2.5',
                 '####seqid=chrM; start=1012; end=1014',
                 '2.1,-4.2',
                 '11,12'],
                '.gtrack',
                ['t7a_hb','gtrack'],
                [GenomeElement('TestGenome', 'chrM', val=[4.5, 1.2]),
                 GenomeElement('TestGenome', 'chrM', val=[-3.7, 2.5]),
                 GenomeElement('TestGenome', 'chrM', val=[2.1, -4.2]),
                 GenomeElement('TestGenome', 'chrM', val=[11, 12])],
                [BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=10, end=12), elCount=2),
                 BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=1012, end=1014), elCount=2)],
                HbGtrackGenomeElementSource,
                ['val'],
                'float64',
                2,
                'float64',
                1)
        
        # Testing:
        # - Track type: function
        # - Value: pair of characters
        # - Fixed size data lines and data line size
        # - Multiple bounding regions in unsorted order
        self.cases['gtrack_t7b_no_types_expanded_no_hb'] = \
            Case(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: function',
                 '##value type: character',
                 '##value dimension: pair',
                 '##fixed-size data lines: true',
                 '##data line size: 2',
                 '###value'],
                ['####seqid=chrM; start=1012; end=1014',
                 'TAGG',
                 '####seqid=chrM; start=10; end=13',
                 'ACGT',
                 'AT'],
                '.gtrack',
                ['t7b_no_hb','gtrack'],
                [GenomeElement('TestGenome', 'chrM', val=['T','A']),
                 GenomeElement('TestGenome', 'chrM', val=['G','G']),
                 GenomeElement('TestGenome', 'chrM', val=['A','C']),
                 GenomeElement('TestGenome', 'chrM', val=['G','T']),
                 GenomeElement('TestGenome', 'chrM', val=['A','T'])],
                [BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=1012, end=1014), elCount=2),
                 BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=10, end=13), elCount=3)],
                GtrackGenomeElementSource,
                ['val'],
                'S1',
                2,
                'float64',
                1)
        
        # - Multiple bounding regions in sorted order
        self.cases['gtrack_t7b_no_types_expanded_hb'] = \
            Case(None,
                 'TestGenome',
                ['##track type: function',
                 '##value type: character',
                 '##value dimension: pair',
                 '##fixed-size data lines: true',
                 '##data line size: 2',
                 '###value'],
                ['####seqid=chrM; start=10; end=12',
                 'ACGT',
                 '####seqid=chrM; start=1012; end=1015',
                 'TAGG',
                 'AT'],
                '.gtrack',
                ['t7b_hb','gtrack'],
                [GenomeElement('TestGenome', 'chrM', val=['A','C']),
                 GenomeElement('TestGenome', 'chrM', val=['G','T']),
                 GenomeElement('TestGenome', 'chrM', val=['T','A']),
                 GenomeElement('TestGenome', 'chrM', val=['G','G']),
                 GenomeElement('TestGenome', 'chrM', val=['A','T'])],
                [BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=10, end=12), elCount=2),
                 BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=1012, end=1015), elCount=3)],
                HbGtrackGenomeElementSource,
                ['val'],
                'S1',
                2,
                'float64',
                1)
        
        # Testing:
        # - Track type: linked points
        # - Edges with no weights
        # - Uninterrupted data lines
        self.cases['gtrack_t8'] = \
            Case(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: linked points',
                 '##uninterrupted data lines: true',
                 '\t'.join(['###seqid','start', 'id', 'edges'])],
                ['\t'.join(['chrM','100','aaa','aab;aac']),
                '\t'.join(['chrM','200','aab','aaa']),
                '\t'.join(['chrM','300','aac','aab'])],
                '.gtrack',
                ['t8','gtrack'],
                [GenomeElement('TestGenome', 'chrM', start=100, id='aaa', edges=['aab','aac']),
                 GenomeElement('TestGenome', 'chrM', start=200, id='aab', edges=['aaa']),
                 GenomeElement('TestGenome', 'chrM', start=300, id='aac', edges=['aab'])],
                [],
                GtrackGenomeElementSource,
                ['start', 'id', 'edges'],
                'float64',
                1,
                'float64',
                1)
        
        # Testing:
        # - Track type: linked segments
        # - Edges with weights
        # - Edges column: graph
        # - Fixed length
        # - Fixed gap size
        # - Sorted elements (scattered)
        # - No overlapping elements
        # - Column specification line: added non-core columns with 'problem names'
        # - Bounding region without data lines
        # - Bounding region without end or genome
        self.cases['gtrack_t9_no_check_print_no_track_extract_no_check_expand_no_sort_no_standard_compose_no_overlaps'] = \
            Case(GtrackGenomeElementSource,
                 None,
                ['##track type: linked segments',
                 '##edge weights: true',
                 '##sorted elements: true',
                 '##no overlapping elements: true',
                 '##edges column: graph',
                 '##fixed length: 25',
                 '##fixed gap size: 75',
                 '\t'.join(['###seqid','extra','val','__dir__','id','graph'])],
                ['####seqid=chr21',
                 '####seqid=chrM; start=100',
                 '\t'.join(['chrM','A','1','a','aaa','aab=1.2;aac=1.3']),
                 '\t'.join(['chrM','B','0','b','aab','aaa=0.9']),
                 '\t'.join(['chrM','B','1','c','aac','aab=1.2'])],
                '.gtrack',
                ['t9','gtrack'],
                [GenomeElement(None, 'chrM', start=100, end=125, id='aaa', edges=['aab','aac'], weights=[1.2,1.3], extra=OrderedDict([('__extra','A'), ('__val','1'), ('____dir__','a')])),
                 GenomeElement(None, 'chrM', start=200, end=225, id='aab', edges=['aaa'], weights=[0.9], extra=OrderedDict([('__extra','B'), ('__val','0'), ('____dir__','b')])),
                 GenomeElement(None, 'chrM', start=300, end=325, id='aac', edges=['aab'], weights=[1.2], extra=OrderedDict([('__extra','B'), ('__val','1'), ('____dir__','c')]))],
                [BoundingRegionTuple(region=GenomeRegion(None, 'chr21', start=0), elCount=0),
                 BoundingRegionTuple(region=GenomeRegion(None, 'chrM', start=100), elCount=3)],
                GtrackGenomeElementSource,
                ['start', 'end', 'id', 'edges', 'weights', '__extra', '__val', '____dir__'],
                'float64',
                1,
                'float64',
                1)
        
        # Testing:
        # - Track type: genome partition
        # - Edge weights: binary
        # - Empty edge lists
        # - No overlapping elements (should be ignored)
        # - 1-indexed
        # - End inclusive
        # - Multiple bounding region specs (without start and/or end)
        self.cases['gtrack_t10_no_check_expand_no_hb'] = \
            Case(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: linked genome partition',
                 '##edge weights: true',
                 '##edge weight type: binary',
                 '##no overlapping elements: true',
                 '##1-indexed: true',
                 '##end inclusive: true',
                 '\t'.join(['###end','id','edges'])],
                ['####seqid=chrM',
                 '\t'.join(['200','aaa','aab=0;aac=1']),
                 '\t'.join(['16571','aab','aaa=0']),
                 '####seqid=chr21; end=300',
                 '\t'.join(['200','aac','.']),
                 '\t'.join(['300','aad','aaa=1']),
                 '####seqid=chr21; start=302; end=400',
                 '\t'.join(['400','aae','aad=0'])],
                '.gtrack',
                ['t10_no_hb','gtrack'],
                [GenomeElement('TestGenome', 'chrM', end=200, id='aaa', edges=['aab','aac'], weights=[0, 1]),
                 GenomeElement('TestGenome', 'chrM', end=16571, id='aab', edges=['aaa'], weights=[0]),
                 GenomeElement('TestGenome', 'chr21', end=200, id='aac', edges=[], weights=[]),
                 GenomeElement('TestGenome', 'chr21', end=300, id='aad', edges=['aaa'], weights=[1]),
                 GenomeElement('TestGenome', 'chr21', end=400, id='aae', edges=['aad'], weights=[0])],
                [BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=0, end=16571), elCount=2),
                 BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chr21', start=0, end=300), elCount=2),
                 BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chr21', start=301, end=400), elCount=1)],
                GtrackGenomeElementSource,
                ['end', 'id', 'edges', 'weights'],
                'float64',
                1,
                'int8',
                1)
        
        self.cases['gtrack_t10_no_check_expand_hb'] = \
            Case(None,
                 'TestGenome',
                ['##track type: linked genome partition',
                 '##edge weights: true',
                 '##edge weight type: binary',
                 '##no overlapping elements: true',
                 '##1-indexed: true',
                 '##end inclusive: true',
                 '\t'.join(['###end','id','edges'])],
                ['####seqid=chrM',
                 '\t'.join(['200','aaa','aab=0;aac=1']),
                 '\t'.join(['16571','aab','aaa=0']),
                 '####seqid=chr21; end=300',
                 '\t'.join(['200','aac','.']),
                 '\t'.join(['300','aad','aaa=1']),
                 '####seqid=chr21; start=302; end=400',
                 '\t'.join(['400','aae','aad=0'])],
                '.gtrack',
                ['t10_hb','gtrack'],
                [GenomeElement('TestGenome', 'chrM', end=0, id='', edges=[], weights=[]),
                 GenomeElement('TestGenome', 'chrM', end=200, id='aaa', edges=['aab','aac'], weights=[0, 1]),
                 GenomeElement('TestGenome', 'chrM', end=16571, id='aab', edges=['aaa'], weights=[0]),
                 GenomeElement('TestGenome', 'chr21', end=0, id='', edges=[], weights=[]),
                 GenomeElement('TestGenome', 'chr21', end=200, id='aac', edges=[], weights=[]),
                 GenomeElement('TestGenome', 'chr21', end=300, id='aad', edges=['aaa'], weights=[1]),
                 GenomeElement('TestGenome', 'chr21', end=301, id='', edges=[], weights=[]),
                 GenomeElement('TestGenome', 'chr21', end=400, id='aae', edges=['aad'], weights=[0])],
                [BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=0, end=16571), elCount=3),
                 BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chr21', start=0, end=300), elCount=3),
                 BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chr21', start=301, end=400), elCount=2)],
                HbGtrackGenomeElementSource,
                ['end', 'id', 'edges', 'weights'],
                'float64',
                1,
                'int8',
                1)
        
        # Testing:
        # - Track type: linked valued points
        # - Value: Mean/sd (pair)
        # - Edge weights: category
        # - Added 'genome' column
        self.cases['gtrack_t11_no_standard_no_hb'] = \
            Case(GtrackGenomeElementSource,
                 None,
                ['##track type: linked valued points',
                 '##gtrack subtype: mean/sd',
                 '##value dimension: pair',
                 '##edge weights: true',
                 '##edge weight type: category',
                 '\t'.join(['###genome','seqid','start','value','id','edges'])],
                ['\t'.join(['hg17','chrM','101','0.4,2.2','aaa','aab=mv;aac=mv']),
                 '\t'.join(['hg18','chrM','110','0.6,0.8','aab','aaa=eq']),
                 '\t'.join(['hg19','chrM','110','0.6,1.8','aac','aab=eq'])],
                '.gtrack',
                ['t11_no_hb','gtrack'],
                [GenomeElement('hg17', 'chrM', start=101, val=[0.4,2.2], id='aaa', edges=['aab','aac'], weights=['mv','mv']),
                 GenomeElement('hg18', 'chrM', start=110, val=[0.6,0.8], id='aab', edges=['aaa'], weights=['eq']),
                 GenomeElement('hg19', 'chrM', start=110, val=[0.6,1.8], id='aac', edges=['aab'], weights=['eq'])],
                [],
                GtrackGenomeElementSource,
                ['start', 'val', 'id', 'edges', 'weights'],
                'float128',
                2,
                'S',
                1)
        
        # Testing:
        # - Track type: linked valued points
        # - Value: Mean/sd (pair)
        # - Edge weights: category
        # - Added 'genome' column
        # - Same genome in bounding regions
        # - No overlapping elements: false
        self.cases['gtrack_t11_hb'] = \
            Case(None,
                 None,
                ['##track type: linked valued points',
                 '##gtrack subtype: mean/sd',
                 '##value dimension: pair',
                 '##edge weights: true',
                 '##edge weight type: category',
                 '##no overlapping elements: false',
                 '\t'.join(['###genome', 'seqid','start','value','id','edges'])],
                ['\t'.join(['TestGenome','chrM','110','0.6,0.8','aab','aaa=eq']),
                 '\t'.join(['TestGenome','chrM','101','0.4,2.2','aaa','aab=mv;aac=mv']),
                 '\t'.join(['TestGenome','chrM','110','0.6,1.8','aac','aab=eq'])],
                '.gtrack',
                ['t11_hb','gtrack'],
                [GenomeElement('TestGenome', 'chrM', start=110, val=[0.6,0.8], id='aab', edges=['aaa'], weights=['eq']),
                 GenomeElement('TestGenome', 'chrM', start=101, val=[0.4,2.2], id='aaa', edges=['aab','aac'], weights=['mv','mv']),
                 GenomeElement('TestGenome', 'chrM', start=110, val=[0.6,1.8], id='aac', edges=['aab'], weights=['eq'])],
                [],
                HbGtrackGenomeElementSource,
                ['start', 'val', 'id', 'edges', 'weights'],
                'float128',
                2,
                'S',
                1)
        
        # Testing:
        # - Track type: linked valued segments
        # - Value: vector of numbers
        # - Edge weights: character
        # - Missing values
        # - Genome Bounding region
        # - Comments and empty lines
        # - CR before LF
        self.cases['gtrack_t12_no_check_track_extract_no_standard_no_hb'] = \
            Case(GtrackGenomeElementSource,
                 None,
                ['##track type: linked valued segments\r',
                 '##value dimension: vector\r',
                 '##edge weights: true\r',
                 '# Comment\r',
                 '##edge weight type: character\r',
                 '\t'.join(['###seqid','start','end','value','id','edges\r'])],
                ['####genome=TestGenome\r',
                 '# Comment\r',
                 '\t'.join(['chrM','100','165','0.1,-0.1,1.0','aaa','aab=t;aac=g\r']),
                 '\t'.join(['chrM','200','300','.,1.2e1,0','aab','aaa=.\r']),
                 '\r',
                 '####genome=hg18\r',
                 '\t'.join(['chrM','300','400','.,.,.','aac','aab=t\r']),
                 ''],
                '.gtrack',
                ['t12_no_hb','gtrack'],
                [GenomeElement('TestGenome', 'chrM', start=100, end=165, val=[0.1,-0.1,1.0], id='aaa', edges=['aab','aac'], weights=['t','g']),
                 GenomeElement('TestGenome', 'chrM', start=200, end=300, val=[numpy.nan,12,0], id='aab', edges=['aaa'], weights=['']),
                 GenomeElement('hg18', 'chrM', start=300, end=400, val=[numpy.nan]*3, id='aac', edges=['aab'], weights=['t'])],
                [BoundingRegionTuple(region=GenomeRegion('TestGenome'), elCount=2),
                 BoundingRegionTuple(region=GenomeRegion('hg18'), elCount=1)],
                GtrackGenomeElementSource,
                ['start', 'end', 'val', 'id', 'edges', 'weights'],
                'float64',
                3,
                'S1',
                1)
        
        # Testing:
        # - Same genome in bounding regions
        self.cases['gtrack_t12_no_check_track_extract_hb'] = \
            Case(None,
                 None,
                ['##track type: linked valued segments\r',
                 '##value dimension: vector\r',
                 '##edge weights: true\r',
                 '# Comment\r',
                 '##edge weight type: character\r',
                 '\t'.join(['###seqid','start','end','value','id','edges\r'])],
                ['####genome=TestGenome\r',
                 '# Comment\r',
                 '\t'.join(['chrM','100','165','0.1,-0.1,1.0','aaa','aab=t;aac=g\r']),
                 '\t'.join(['chrM','200','300','.,1.2e1,0','aab','aaa=.\r']),
                 '\r',
                 '####genome=TestGenome\r',
                 '\t'.join(['chrM','300','400','.,.,.','aac','aab=t\r']),
                 ''],
                '.gtrack',
                ['t12_hb','gtrack'],
                [GenomeElement('TestGenome', 'chrM', start=100, end=165, val=[0.1,-0.1,1.0], id='aaa', edges=['aab','aac'], weights=['t','g']),
                 GenomeElement('TestGenome', 'chrM', start=200, end=300, val=[numpy.nan,12,0], id='aab', edges=['aaa'], weights=['']),
                 GenomeElement('TestGenome', 'chrM', start=300, end=400, val=[numpy.nan]*3, id='aac', edges=['aab'], weights=['t'])],
                [BoundingRegionTuple(region=GenomeRegion('TestGenome'), elCount=2),
                 BoundingRegionTuple(region=GenomeRegion('TestGenome'), elCount=1)],
                HbGtrackGenomeElementSource,
                ['start', 'end', 'val', 'id', 'edges', 'weights'],
                'float64',
                3,
                'S1',
                1)
        
        # Testing:
        # - Track type: linked step function
        # - Value: list of binary
        # - Edge weights: mean/sd
        # - Sorted elements (dense)
        # - Fixed length (with implicit end outside bounding region)
        # - Missing values in value, strand, weights
        # - Dense track type with no main genome
        # - Genome in columns and bounding regions
        # - Spaces/encoding in bounding region seqid, id, edges and extra col
        self.cases['gtrack_t13_no_standard_no_hb'] = \
            Case(GtrackGenomeElementSource,
                 None,
                ['##track type: linked step function',
                 '##value type: binary',
                 '##value dimension: list',
                 '##edge weights: true',
                 '##edge weight dimension: pair',
                 '##sorted elements: true',
                 '##fixed length: 100',
                 '##gtrack subtype: mean/sd weights',
                 '\t'.join(['###genome','value','strand','id','edges'])],
                ['####genome=TestGenome; seqid=chr %3CM%3E; start=100; end=200',
                 '\t'.join(['TestGenome','1101','+','id001','id002=0.1,0.8;id003=0.2,0.7']),
                 '####genome=hg18; seqid=chr %3CM%3E; start=300; end=450',
                 '\t'.join(['hg18','11','.','id002','id003=1.0,.']),
                 '\t'.join(['hg18','0.10.','-','id003','id002=.,.'])],
                '.gtrack',
                ['t13_no_hb','gtrack'],
                [GenomeElement('TestGenome', 'chr <M>', end=200, val=[True, True, False, True], strand=True, id='id001', edges=['id002','id003'], weights=[[0.1,0.8],[0.2,0.7]]),
                 GenomeElement('hg18', 'chr <M>', end=400, val=[True, True], strand=BINARY_MISSING_VAL, id='id002', edges=['id003'], weights=[[1.0,numpy.nan]]),
                 GenomeElement('hg18', 'chr <M>', end=450, val=[False, BINARY_MISSING_VAL, True, False, BINARY_MISSING_VAL], strand=False, id='id003', edges=['id002'], weights=[[numpy.nan,numpy.nan]])],
                [BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chr <M>', start=100, end=200), elCount=1),
                 BoundingRegionTuple(region=GenomeRegion('hg18', 'chr <M>', start=300, end=450), elCount=2)],
                GtrackGenomeElementSource,
                ['end', 'val', 'strand', 'id', 'edges', 'weights'],
                'int8',
                0,
                'float128',
                2)
        
        # - Same genome, correct seqid
        # - Bounding regions immediately following
        # - Value: vector of binary
        self.cases['gtrack_t13_hb'] = \
            Case(None,
                 'TestGenome',
                ['##track type: linked step function',
                 '##value type: binary',
                 '##value dimension: vector',
                 '##edge weights: true',
                 '##edge weight dimension: pair',
                 '##sorted elements: true',
                 '##fixed length: 100',
                 '##gtrack subtype: mean/sd weights',
                 '\t'.join(['###genome','value','strand','id','edges'])],
                ['####genome=TestGenome; seqid=chrM; start=100; end=200',
                 '\t'.join(['TestGenome','1101','+','id001','id002=0.1,0.8;id003=0.2,0.7']),
                 '####genome=TestGenome; seqid=chrM; start=300; end=450',
                 '\t'.join(['TestGenome','11..','.','id002','id003=1.0,.']),
                 '\t'.join(['TestGenome','0.10','-','id003','id002=.,.'])],
                '.gtrack',
                ['t13_hb','gtrack'],
                [GenomeElement('TestGenome', 'chrM', end=100, val=[BINARY_MISSING_VAL], strand=True, id='', edges=[], weights=[]),
                 GenomeElement('TestGenome', 'chrM', end=200, val=[True, True, False, True], strand=True, id='id001', edges=['id002','id003'], weights=[[0.1,0.8],[0.2,0.7]]),
                 GenomeElement('TestGenome', 'chrM', end=300, val=[BINARY_MISSING_VAL], strand=True, id='', edges=[], weights=[]),
                 GenomeElement('TestGenome', 'chrM', end=400, val=[True, True, BINARY_MISSING_VAL, BINARY_MISSING_VAL], strand=BINARY_MISSING_VAL, id='id002', edges=['id003'], weights=[[1.0,numpy.nan]]),
                 GenomeElement('TestGenome', 'chrM', end=450, val=[False, BINARY_MISSING_VAL, True, False], strand=False, id='id003', edges=['id002'], weights=[[numpy.nan,numpy.nan]])],
                [BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=100, end=200), elCount=2),
                 BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=300, end=450), elCount=3)],
                HbGtrackGenomeElementSource,
                ['end', 'val', 'strand', 'id', 'edges', 'weights'],
                'int8',
                4,
                'float128',
                2)
        
        # Testing:
        # - Track type: linked function
        # - Value: vector of characters
        # - Edge weights: list of characters
        # - No edges in first element
        # - Function on several chromosomes
        self.cases['gtrack_t14_no_types_expanded_no_hb'] = \
            Case(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: linked function',
                 '##value type: character',
                 '##value dimension: vector',
                 '##edge weights: true',
                 '##edge weight type: character',
                 '##edge weight dimension: list',
                 '\t'.join(['###value','id','edges'])],
                ['####seqid=chrM; start=10; end=13',
                 '\t'.join(['...','-','.']),
                 '\t'.join(['agg','a','b=Ag;c=gCg']),
                 '\t'.join(['act','b','c=G']),
                 '####seqid=chr21; start=1012; end=1014',
                 '\t'.join(['tgg','c','a=.']),
                 '\t'.join(['...','d','c=ggg'])],
                '.gtrack',
                ['t14_no_hb','gtrack'],
                [GenomeElement('TestGenome', 'chrM', val=['','',''], id='-', edges=[], weights=[]),
                 GenomeElement('TestGenome', 'chrM', val=['a','g','g'], id='a', edges=['b','c'], weights=[['A','g'],['g','C','g']]),
                 GenomeElement('TestGenome', 'chrM', val=['a','c','t'], id='b', edges=['c'], weights=[['G']]),
                 GenomeElement('TestGenome', 'chr21', val=['t','g','g'], id='c', edges=['a'], weights=[[]]),
                 GenomeElement('TestGenome', 'chr21', val=['','',''], id='d', edges=['c'], weights=[['g','g','g']])],
                [BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=10, end=13), elCount=3),
                 BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chr21', start=1012, end=1014), elCount=2)],
                GtrackGenomeElementSource,
                ['val', 'id', 'edges', 'weights'],
                'S1',
                3,
                'S1',
                0)
        
        # - Edge weights: vector of characters
        self.cases['gtrack_t14_no_types_expanded_hb'] = \
            Case(None,
                 'TestGenome',
                ['##track type: linked function',
                 '##value type: character',
                 '##value dimension: vector',
                 '##edge weights: true',
                 '##edge weight type: character',
                 '##edge weight dimension: vector',
                 '\t'.join(['###value','id','edges'])],
                ['####seqid=chrM; start=10; end=13',
                 '\t'.join(['...','-','.']),
                 '\t'.join(['agg','a','b=Ag.;c=gCg']),
                 '\t'.join(['act','b','c=G..']),
                 '####seqid=chr21; start=1012; end=1014',
                 '\t'.join(['tgg','c','a=...']),
                 '\t'.join(['...','d','c=ggg'])],
                '.gtrack',
                ['t14_hb','gtrack'],
                [GenomeElement('TestGenome', 'chrM', val=['','',''], id='-', edges=[], weights=[]),
                 GenomeElement('TestGenome', 'chrM', val=['a','g','g'], id='a', edges=['b','c'], weights=[['A','g',''],['g','C','g']]),
                 GenomeElement('TestGenome', 'chrM', val=['a','c','t'], id='b', edges=['c'], weights=[['G','','']]),
                 GenomeElement('TestGenome', 'chr21', val=['t','g','g'], id='c', edges=['a'], weights=[['','','']]),
                 GenomeElement('TestGenome', 'chr21', val=['','',''], id='d', edges=['c'], weights=[['g','g','g']])],
                [BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=10, end=13), elCount=3),
                 BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chr21', start=1012, end=1014), elCount=2)],
                HbGtrackGenomeElementSource,
                ['val', 'id', 'edges', 'weights'],
                'S1',
                3,
                'S1',
                3)
        
        # Testing:
        # - Track type: linked base pairs
        # - Undirected edges
        # - Edge weights: pair of categories
        # - Spaces/escaping in data lines
        self.cases['gtrack_t15'] = \
            Case(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: linked base pairs',
                 '##undirected edges: true',
                 '##edge weights: true',
                 '##edge weight type: category',
                 '##edge weight dimension: pair',
                 '\t'.join(['###id','edges','test'])],
                ['####genome=TestGenome; seqid=chrM; start=10; end=13',
                 '\t'.join(['a','b%3D=near,%2Cbinding;c=far,%2Cnon-binding','%3C']),
                 '\t'.join(['b=','a=near,%2Cbinding','%3C']),
                 '\t'.join(['c','a=far,%2Cnon-binding','%09'])],
                '.gtrack',
                ['t15','gtrack'],
                [GenomeElement('TestGenome', 'chrM', id='a', edges=['b=','c'], weights=[['near',',binding'],['far',',non-binding']], extra=OrderedDict([('test','<')])),
                 GenomeElement('TestGenome', 'chrM', id='b=', edges=['a'], weights=[['near',',binding']], extra=OrderedDict([('test','<')])),
                 GenomeElement('TestGenome', 'chrM', id='c', edges=['a'], weights=[['far',',non-binding']], extra=OrderedDict([('test','\t')]))],
                [BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=10, end=13), elCount=3)],
                GtrackGenomeElementSource,
                ['id', 'edges', 'weights', 'test'],
                'float64',
                1,
                'S',
                2)
        
        #t16: GTrack compression, simple file (e.g. t1)
        self.cases['gtrack_t16_no_expand_no_sort'] = \
            Case(None,
                 'TestGenome',
                [],
                ['\x1f\x8b\x08\x08\x92_\x80N\x00\x03points.gtrack\x00SV.)JL\xceV(\xa9,H\xb5R(\xc8\xcf\xcc+)\xe6RVV.N-\xccL\xe1,.I,*\xe1J\xce(\xf2\xe5440\x800\x8c`\x0cc\x03\x03\x00\x10h\xb1\xad>\x00\x00\x00'],
                '.gtrack.gz',
                ['t16','gtrack'],
                [GenomeElement('TestGenome', 'chrM', start=100),
                 GenomeElement('TestGenome', 'chrM', start=200),
                 GenomeElement('TestGenome', 'chrM', start=300)],
                [],
                HbGzipGtrackGenomeElementSource,
                ['start'],
                'float64',
                1,
                'float64',
                1)
        
        #t17: Subtype adhersion: strict
        self.cases['gtrack_t17'] = \
            Case(GtrackGenomeElementSource,
                 'TestGenome',
                ['##subtype url: http://gtrack.no/bedgraph.gtrack'],
                ['\t'.join(['chrM','100','120','1.2']),
                 '\t'.join(['chrM','200','220','-0.1'])],
                '.gtrack',
                ['t17','gtrack'],
                [GenomeElement('TestGenome', 'chrM', start=100, end=120, val=1.2),
                 GenomeElement('TestGenome', 'chrM', start=200, end=220, val=-0.1)],
                [],
                GtrackGenomeElementSource,
                ['start', 'end', 'val'],
                'float64',
                1,
                'float64',
                1)
        
        #t18: Subtype adhersion: strict, bounding region with seqid, no seqid column, fixed length
        self.cases['gtrack_t18_no_hb'] = \
            Case(GtrackGenomeElementSource,
                 'TestGenome',
                ['##subtype url: http://gtrack.no/wig_fixedstep.gtrack',\
                 '##track type: step function',\
                 '##fixed length: 100'],
                ['####seqid=chrM; start=21; end=220',
                 '1.2',
                 '-0.1'],
                '.gtrack',
                ['t18_no_hb','gtrack'],
                [GenomeElement('TestGenome', 'chrM', end=120, val=1.2),
                 GenomeElement('TestGenome', 'chrM', end=220, val=-0.1)],
                [BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=20, end=220), elCount=2)],
                GtrackGenomeElementSource,
                ['end', 'val'],
                'float64',
                1,
                'float64',
                1)
        
        self.cases['gtrack_t18_hb'] = \
            Case(None,
                 'TestGenome',
                ['##subtype url: http://gtrack.no/wig_fixedstep.gtrack',\
                 '##track type: step function',\
                 '##fixed length: 100'],
                ['####seqid=chrM; start=21; end=220',
                 '1.2',
                 '-0.1'],
                '.gtrack',
                ['t18_hb','gtrack'],
                [GenomeElement('TestGenome', 'chrM', end=20, val=numpy.nan),
                 GenomeElement('TestGenome', 'chrM', end=120, val=1.2),
                 GenomeElement('TestGenome', 'chrM', end=220, val=-0.1)],
                [BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=20, end=220), elCount=3)],
                HbGtrackGenomeElementSource,
                ['end', 'val'],
                'float64',
                1,
                'float64',
                1)
        
        #t18.1: Subtype with fixed length, fixed gap size and no column specification line
        self.cases['gtrack_t18.1'] = \
            Case(GtrackGenomeElementSource,
                 None,
                ['##subtype url: http://gtrack.no/wig_fixedstep.gtrack',\
                 '##track type: valued segments',\
                 '##fixed length: 20',
                 '##fixed gap size: 10',
                 '####seqid=chrM; end=400'],
                ['25',
                 '26'],
                '.gtrack',
                ['t18.1','gtrack'],
                [GenomeElement(None, 'chrM', start=0, end=20, val=25),
                 GenomeElement(None, 'chrM', start=30, end=50, val=26)],
                [BoundingRegionTuple(region=GenomeRegion(None, 'chrM', start=0, end=400), elCount=2)],
                GtrackGenomeElementSource,
                ['start', 'end', 'val'],
                'float64',
                1,
                'float64',
                1)
        
        #t19: Subtype adhersion: extensible, url without http
        self.cases['gtrack_t19_no_check_track_extract_no_check_expand'] = \
            Case(GtrackGenomeElementSource,
                 'TestGenome',
                ['##subtype url: gtrack.no/bed_direct.gtrack',
                 '\t'.join(['###seqid', 'start', 'end', 'name', 'value', 'strand', 'thickStart', 'thickEnd', 'itemRgb', 'blockCount', 'blockSizes', 'blockStarts', 'description'])],
                ['\t'.join(['chr21', '1000', '5000', 'cloneA', '960', '+', '1000', '5000', '0', '2', '567,488,', '0,3512', 'Not interesting']),
                 '\t'.join(['chr21', '2000', '6000', 'cloneB', '900', '-', '2000', '6000', '0', '2', '433,399,', '0,3601', 'A very interesting gene'])],
                '.gtrack',
                ['t19','gtrack'],
                [GenomeElement('TestGenome', 'chr21', start=1000, end=5000, val=960, strand=True, extra=OrderedDict([('name', 'cloneA'), ('thickstart', '1000'), ('thickend', '5000'), ('itemrgb', '0'), ('blockcount', '2'), ('blocksizes', '567,488,'), ('blockstarts', '0,3512'), ('description', 'Not interesting')])),
                 GenomeElement('TestGenome', 'chr21', start=2000, end=6000, val=900, strand=False, extra=OrderedDict([('name', 'cloneB'), ('thickstart', '2000'), ('thickend', '6000'), ('itemrgb', '0'), ('blockcount', '2'), ('blocksizes', '433,399,'), ('blockstarts', '0,3601'), ('description', 'A very interesting gene')]))],
                [],
                GtrackGenomeElementSource,
                ['start', 'end', 'val', 'strand', 'name', 'thickstart', 'thickend', 'itemrgb', 'blockcount', 'blocksizes', 'blockstarts', 'description'],
                'float64',
                1,
                'float64',
                1)
        
        #t20: Subtype adhersion: redefinable
        self.cases['gtrack_no_check_track_extract_t20'] = \
            Case(GtrackGenomeElementSource,
                 'TestGenome',
                ['##value type: category',
                 '##subtype url: http://gtrack.no/gff_direct.gtrack',
                 '\t'.join(['###seqid', 'source', 'value', 'start', 'end', 'score', 'strand', 'phase', 'attributes'])],
                ['\t'.join(['chrM', '.', 'gene', '1000', '9000', '.', '+', '.', 'ID=gene00001;Name=EDEN']),
                 '\t'.join(['chrM', '.', 'mRNA', '1050', '7000', '.', '+', '.', 'ID=mRNA00001;Name=EDEN.1;Parent=gene00001'])],
                '.gtrack',
                ['t20','gtrack'],
                [GenomeElement('TestGenome', 'chrM', val='gene', start=999, end=9000, strand=True, extra=OrderedDict([('source', '.'), ('score', '.'), ('phase', '.'), ('attributes', 'ID=gene00001;Name=EDEN')])),
                 GenomeElement('TestGenome', 'chrM', val='mRNA', start=1049, end=7000, strand=True, extra=OrderedDict([('source', '.'), ('score', '.'), ('phase', '.'), ('attributes', 'ID=mRNA00001;Name=EDEN.1;Parent=gene00001')]))],
                [],
                GtrackGenomeElementSource,
                ['start', 'end', 'val', 'strand', 'source', 'score', 'phase', 'attributes'],
                'S',
                1,
                'float64',
                1)
        
        #t21: Subtype adhersion: reorderable
        self.cases['gtrack_t21'] = \
            Case(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: valued points',
                 '##subtype url: http://gtrack.no/mean_sd.gtrack',
                 '\t'.join(['###seqid','start','value',])],
                ['\t'.join(['chrM','101','0.5,2.1']),
                 '\t'.join(['chrM','110','0.7,0.9'])],
                '.gtrack',
                ['t21','gtrack'],
                [GenomeElement('TestGenome', 'chrM', start=101, val=[0.5,2.1]),
                 GenomeElement('TestGenome', 'chrM', start=110, val=[0.7,0.9])],
                [],
                GtrackGenomeElementSource,
                ['start', 'val'],
                'float128',
                2,
                'float64',
                1)
        
        #t22: Subtype adhersion: free
        self.cases['gtrack_t22'] = \
            Case(GtrackGenomeElementSource,
                 'TestGenome',
                ['##description: Description of track',
                 '##subtype url: http://gtrack.no/hyperbrowser.gtrack'],
                ['\t'.join(['chrM','101','110']),
                 '\t'.join(['chrM','110','120'])],
                '.gtrack',
                ['t22','gtrack'],
                [GenomeElement('TestGenome', 'chrM', start=101, end=110),
                 GenomeElement('TestGenome', 'chrM', start=110, end=120)],
                [],
                GtrackGenomeElementSource,
                ['start', 'end'],
                'float64',
                1,
                'float64',
                1)
        
        #t23: Sliding window
        self.cases['gtrack_t23'] = \
            Case(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: valued segments',
                 '##fixed length: 100',
                 '##fixed gap size: -90',
                 '###value'],
                ['####seqid=chrM; start=10',
                 '0.1',
                 '0.2',
                 '0.3',
                 '0.4'],
                '.gtrack',
                ['t23','gtrack'],
                [GenomeElement('TestGenome', 'chrM', start=10, end=110, val=0.1),
                 GenomeElement('TestGenome', 'chrM', start=20, end=120, val=0.2),
                 GenomeElement('TestGenome', 'chrM', start=30, end=130, val=0.3),
                 GenomeElement('TestGenome', 'chrM', start=40, end=140, val=0.4)],
                [BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=10, end=16571), elCount=4)],
                GtrackGenomeElementSource,
                ['start', 'end', 'val'],
                'float64',
                1,
                'float64',
                1)
        
        #t24: Circular elements
        self.cases['gtrack_t24_no_hb'] = \
            Case(GtrackGenomeElementSource,
                 'TestGenome',
                ['##circular elements: true'],
                ['####seqid=chrM; start=100; end=10',
                 '\t'.join(['chrM','110','5'])],
                '.gtrack',
                ['t24_no_hb','gtrack'],
                [GenomeElement('TestGenome', 'chrM', start=110, end=5)],
                [BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=100, end=10), elCount=1)],
                GtrackGenomeElementSource,
                ['start', 'end'],
                'float64',
                1,
                'float64',
                1)
        
        #t25: No data lines 
        self.cases['gtrack_t25_no_print_no_expand_no_sort_no_standard_no_hb'] = \
            Case(GtrackGenomeElementSource,
                 'TestGenome',
                [],
                [],
                '.gtrack',
                ['t25_no_hb','gtrack'],
                [],
                [],
                GtrackGenomeElementSource,
                ['start', 'end'],
                'float64',
                1,
                'float64',
                1)
        
        #t26: edge weight vector of length 1, no edges in first element
        self.cases['gtrack_t26_no_printcheck_no_check_expand_no_sort_no_standard_no_hb'] = \
            Case(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: linked points',
                 '##edge weights: true',
                 '##edge weight dimension: vector',
                 '\t'.join(['###seqid','start','id','edges'])],
                ['\t'.join(['chrM','10','a','.']),
                 '\t'.join(['chrM','20','b','a=1.2'])],
                '.gtrack',
                ['t26_no_hb','gtrack'],
                [GenomeElement('TestGenome', 'chrM', start=10, id='a', edges=[], weights=[]),
                GenomeElement('TestGenome', 'chrM', start=20, id='b', edges=['a'], weights=[[1.2]])],
                [],
                GtrackGenomeElementSource,
                ['start', 'id', 'edges', 'weights'],
                'float64',
                1,
                'float64',
                1)
        
        #t27: special cases of undirected edges
        self.cases['gtrack_t27'] = \
            Case(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: linked points',
                 '##edge weights: true',
                 '##undirected edges: true',
                 '\t'.join(['###seqid','start','id','edges'])],
                ['\t'.join(['chrM','10','a','a=0.9;b=.']),
                 '\t'.join(['chrM','20','b','b=.;a=.'])],
                '.gtrack',
                ['t27','gtrack'],
                [GenomeElement('TestGenome', 'chrM', start=10, id='a', edges=['a','b'], weights=[0.9,numpy.nan]),
                GenomeElement('TestGenome', 'chrM', start=20, id='b', edges=['b','a'], weights=[numpy.nan,numpy.nan])],
                [],
                GtrackGenomeElementSource,
                ['start', 'id', 'edges', 'weights'],
                'float64',
                1,
                'float64',
                1)
        
        self.cases['bed_3'] = \
            Case(None,
                 'TestGenome',
                [],
                ['\t'.join(['chrM','71','72']),
                 '\t'.join(['chrM','103','105']),
                 '\t'.join(['chr21','3','13'])],
                '.bed',
                ['My','bed-3-track'],
                [GenomeElement('TestGenome', 'chrM', start=71, end=72),
                 GenomeElement('TestGenome', 'chrM', start=103, end=105),
                 GenomeElement('TestGenome', 'chr21', start=3, end=13)],
                [],
                BedGenomeElementSource,
                ['start', 'end'],
                'int32',
                1,
                'float64',
                1)
        
        self.cases['bed_12'] = \
            Case(None,
                 'TestGenome',
                [],
                ['\t'.join(['chrM','71','82','A','1000','+','71','79','0,0,255','2','4,4,','0,8']),
                 '\t'.join(['chrM','103','105','B','800','.','103','105','0,255,0','1','2','0']),
                 '\t'.join(['chr21','3','13','C','645','-','3','13','255,0,0','3','2,2,2','0,5,8'])],
                '.bed',
                ['My','bed-12-track'],
                [GenomeElement('TestGenome', 'chrM', start=71, end=82, val=1000, strand=True, \
                                extra=OrderedDict([('name','A'), ('thickstart','71'), ('thickend','79'), ('itemrgb','0,0,255'), \
                                                   ('blockcount','2'), ('blocksizes','4,4,'), ('blockstarts','0,8')])),
                 GenomeElement('TestGenome', 'chrM', start=103, end=105, val=800, strand=BINARY_MISSING_VAL, \
                                extra=OrderedDict([('name','B'), ('thickstart','103'), ('thickend','105'), ('itemrgb','0,255,0'), \
                                                   ('blockcount','1'), ('blocksizes','2'), ('blockstarts','0')])),
                 GenomeElement('TestGenome', 'chr21', start=3, end=13, val=645, strand=False, \
                                extra=OrderedDict([('name','C'), ('thickstart','3'), ('thickend','13'), ('itemrgb','255,0,0'), \
                                                   ('blockcount','3'), ('blocksizes','2,2,2'), ('blockstarts','0,5,8')]))],
                [],
                BedGenomeElementSource,
                ['start', 'end', 'val', 'strand', 'name', 'thickstart', 'thickend', 'itemrgb', 'blockcount', 'blocksizes', 'blockstarts'],
                'int32',
                1,
                'float64',
                1)
        
        self.cases['bed_12_no_check_prints_compose_no_overlaps_no_hb'] = \
            Case(None,
                 'TestGenome',
                [],
                ['\t'.join(['chrM','71','82','A','1000','+','71','79','0,0,255','2','4,4,','0,8']),
                 '\t'.join(['chr21','3','13','C','645','-','3','13','255,0,0','3','2,2,2','0,5,8']),
                 '\t'.join(['chr21','5','13','C','645','-','5','13','255,0,0','3','2,2,2','0,3,6'])],
                '.bed',
                ['My','bed-12-overlap-track'],
                [GenomeElement('TestGenome', 'chrM', start=71, end=82, val=1000, strand=True, \
                                extra=OrderedDict([('name','A'), ('thickstart','71'), ('thickend','79'), ('itemrgb','0,0,255'), \
                                                   ('blockcount','2'), ('blocksizes','4,4,'), ('blockstarts','0,8')])),
                 GenomeElement('TestGenome', 'chr21', start=3, end=13, val=645, strand=False, \
                                extra=OrderedDict([('name','C'), ('thickstart','3'), ('thickend','13'), ('itemrgb','255,0,0'), \
                                                   ('blockcount','3'), ('blocksizes','2,2,2'), ('blockstarts','0,5,8')])),
                 GenomeElement('TestGenome', 'chr21', start=5, end=13, val=645, strand=False, \
                                extra=OrderedDict([('name','C'), ('thickstart','5'), ('thickend','13'), ('itemrgb','255,0,0'), \
                                                   ('blockcount','3'), ('blocksizes','2,2,2'), ('blockstarts','0,3,6')]))], \
                [],
                BedGenomeElementSource,
                ['start', 'end', 'val', 'strand', 'name', 'thickstart', 'thickend', 'itemrgb', 'blockcount', 'blocksizes', 'blockstarts'],
                'int32',
                1,
                'float64',
                1)
        
        self.cases['bed_strand'] = \
            Case(None,
                 'TestGenome',
                [],
                ['\t'.join(['chrM','71','72','a','0','+']),
                 '\t'.join(['chrM','103','105','b','1','+']),
                 '\t'.join(['chr21','3','13','c','2','-'])],
                '.bed',
                ['My','bed-track'],
                [GenomeElement('TestGenome', 'chrM', start=71, end=72, val=0, strand=True, name='a'),
                 GenomeElement('TestGenome', 'chrM', start=103, end=105, val=1, strand=True, name='b'),
                 GenomeElement('TestGenome', 'chr21', start=3, end=13, val=2, strand=False, name='c')],
                [],
                BedGenomeElementSource,
                ['start', 'end', 'val', 'strand', 'name'],
                'int32',
                1,
                'float64',
                1)
        
        self.cases['point.bed_strand'] = \
            Case(None,
                 'TestGenome',
                [],
                ['\t'.join(['chrM','71','72','a','0','+']),
                 '\t'.join(['chrM','103','104','b','1','+']),
                 '\t'.join(['chr21','3','4','c','2','-'])],
                '.point.bed',
                ['My','point-bed-track'],
                [GenomeElement('TestGenome', 'chrM', start=71, val=0, strand=True, name='a'),
                 GenomeElement('TestGenome', 'chrM', start=103, val=1, strand=True, name='b'),
                 GenomeElement('TestGenome', 'chr21', start=3, val=2, strand=False, name='c')],
                [],
                PointBedGenomeElementSource,
                ['start', 'val', 'strand', 'name'],
                'int32',
                1,
                'float64',
                1)
        
        self.cases['category.bed'] = \
            Case(None,
                 'TestGenome',
                [],
                ['\t'.join(['chrM','71','72','aaa','0','+']),
                 '\t'.join(['chrM','103','105','bbb','1','+']),
                 '\t'.join(['chr21','3','13','aaa','2','-'])],
                '.category.bed',
                ['My','category-bed-track'],
                [GenomeElement('TestGenome', 'chrM', start=71, end=72, val='aaa', strand=True, score='0'),
                 GenomeElement('TestGenome', 'chrM', start=103, end=105, val='bbb', strand=True, score='1'),
                 GenomeElement('TestGenome', 'chr21', start=3, end=13, val='aaa', strand=False, score='2')],
                [],
                BedCategoryGenomeElementSource,
                ['start', 'end', 'val', 'strand', 'score'],
                'S',
                1,
                'float64',
                1)
        
        self.cases['valued.bed'] = \
            Case(None,
                 'TestGenome',
                [],
                ['\t'.join(['chrM','71','72','a','0.2','+']),
                 '\t'.join(['chrM','103','105','b','1','+']),
                 '\t'.join(['chr21','3','13','c','-1.23e-3','-'])],
                '.valued.bed',
                ['My','valued-bed-track'],
                [GenomeElement('TestGenome', 'chrM', start=71, end=72, val=0.2, strand=True, name='a'),
                 GenomeElement('TestGenome', 'chrM', start=103, end=105, val=1, strand=True, name='b'),
                 GenomeElement('TestGenome', 'chr21', start=3, end=13, val=-0.00123, strand=False, name='c')],
                [],
                BedValuedGenomeElementSource,
                ['start', 'end', 'val', 'strand', 'name'],
                'float64',
                1,
                'float64',
                1)
        
        
        self.cases['microarray'] = \
            Case(None,
                 'TestGenome',
                ['track type="array" expScale=3.0 expStep=0.5 expNames=\'A,B,C,\''],
                ['\t'.join(['chrM','71','72','a','0','+','71','72','0','1','1','0','3','0,1,2,','0.01,-0.5,1.2']),
                 '\t'.join(['chrM','103','105','b','1','+','103','105','0','1','2','0','2','1,2,','2.5,3.2']),
                 '\t'.join(['chr21','3','13','c','2','-','3','13','0','1','10','0','1','0','1.4'])],
                '.microarray',
                ['My','microarray-track'],
                [GenomeElement('TestGenome', 'chrM', start=71, end=72, strand=True, val=[0.01, -0.5, 1.2]),
                 GenomeElement('TestGenome', 'chrM', start=103, end=105, strand=True, val=[numpy.nan, 2.5, 3.2]),
                 GenomeElement('TestGenome', 'chr21', start=3, end=13, strand=False, val=[1.4, numpy.nan, numpy.nan])],
                [],
                MicroarrayGenomeElementSource,
                ['start', 'end', 'val', 'strand'],
                'float64',
                3,
                'float64',
                1)
        
        self.cases['bedgraph'] = \
            Case(None,
                 'TestGenome',
                ['track type=bedGraph name=track_label'],
                ['\t'.join(['chrM','71','72','1.0']),
                 '\t'.join(['chrM','103','105','-1.5']),
                 '\t'.join(['chr21','3','13','2.7'])],
                 '.bedgraph',
                ['My','bedgraph-track'],
                [GenomeElement('TestGenome', 'chrM', start=71, end=72, val=1.0),
                 GenomeElement('TestGenome', 'chrM', start=103, end=105, val=-1.5),
                 GenomeElement('TestGenome', 'chr21', start=3, end=13, val=2.7)],
                [],
                BedGraphGenomeElementSource,
                ['start', 'end', 'val'],
                'float64',
                1,
                'float64',
                1)
        
        self.cases['targetcontrol.bedgraph'] = \
            Case(None,
                 'TestGenome',
                ['track type=bedGraph name=track_label'],
                ['\t'.join(['chrM','71','72','0']),
                 '\t'.join(['chrM','103','105','1']),
                 '\t'.join(['chr21','3','13','.'])],
                 '.targetcontrol.bedgraph',
                ['My','tc-bedgraph-track'],
                [GenomeElement('TestGenome', 'chrM', start=71, end=72, val=False),
                 GenomeElement('TestGenome', 'chrM', start=103, end=105, val=True),
                 GenomeElement('TestGenome', 'chr21', start=3, end=13, val=BINARY_MISSING_VAL)],
                [],
                BedGraphTargetControlGenomeElementSource,
                ['start', 'end', 'val'],
                'int8',
                1,
                'float64',
                1)
        
        self.cases['wig_fixed_function'] = \
            Case(WigGenomeElementSource,
                 'TestGenome',
                ['track type=wiggle_0 name=track_label'],
                [' '.join(['fixedStep','chrom=chrM','start=11','step=1']),
                 '4.5',
                 '-3.7',
                 ' '.join(['fixedStep','chrom=chrM','start=1013','step=1']),
                 '2.1',
                 '11',
                 ' '.join(['fixedStep','chrom=chr21','start=201','step=1']),
                 '21.1',
                 'nan'],
                '.wig',
                ['My','wig-fixed-function-track'],
                [GenomeElement('TestGenome', 'chrM', val=4.5),
                 GenomeElement('TestGenome', 'chrM', val=-3.7),
                 GenomeElement('TestGenome', 'chrM', val=2.1),
                 GenomeElement('TestGenome', 'chrM', val=11),
                 GenomeElement('TestGenome', 'chr21', val=21.1),
                 GenomeElement('TestGenome', 'chr21', val=numpy.nan)],
                [BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=10, end=12), elCount=2),
                 BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=1012, end=1014), elCount=2),
                 BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chr21', start=200, end=202), elCount=2)],
                WigGenomeElementSource,
                ['val'],
                'float64',
                1,
                'float64',
                1)
        
        self.cases['wig_fixed_points'] = \
            Case(WigGenomeElementSource,
                 'TestGenome',
                ['track type=wiggle_0 name=track_label'],
                [' '.join(['fixedStep','chrom=chrM','start=11','step=10']),
                 '4.5',
                 '-3.7',
                 ' '.join(['fixedStep','chrom=chrM','start=1013','step=10']),
                 '2.1',
                 '11',
                 ' '.join(['fixedStep','chrom=chr21','start=201','step=10']),
                 '21.1',
                 'nan'],
                '.wig',
                ['My','wig-fixed-points-track'],
                [GenomeElement('TestGenome', 'chrM', start=10, val=4.5),
                 GenomeElement('TestGenome', 'chrM', start=20, val=-3.7),
                 GenomeElement('TestGenome', 'chrM', start=1012, val=2.1),
                 GenomeElement('TestGenome', 'chrM', start=1022, val=11),
                 GenomeElement('TestGenome', 'chr21', start=200, val=21.1),
                 GenomeElement('TestGenome', 'chr21', start=210, val=numpy.nan)],
                [BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=10, end=21), elCount=2),
                 BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=1012, end=1023), elCount=2),
                 BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chr21', start=200, end=211), elCount=2)],
                WigGenomeElementSource,
                ['start', 'val'],
                'float64',
                1,
                'float64',
                1)
        
        self.cases['wig_fixed_segments'] = \
            Case(WigGenomeElementSource,
                 'TestGenome',
                ['track type=wiggle_0 name=track_label'],
                [' '.join(['fixedStep','chrom=chrM','start=11','step=10','span=5']),
                 '4.5',
                 '-3.7',
                 ' '.join(['fixedStep','chrom=chrM','start=1013','step=10','span=5']),
                 '2.1',
                 '11',
                 ' '.join(['fixedStep','chrom=chr21','start=201','step=10','span=5']),
                 '21.1',
                 'nan'],
                '.wig',
                ['My','wig-fixed-segments-track'],
                [GenomeElement('TestGenome', 'chrM', start=10, end=15, val=4.5),
                 GenomeElement('TestGenome', 'chrM', start=20, end=25, val=-3.7),
                 GenomeElement('TestGenome', 'chrM', start=1012, end=1017, val=2.1),
                 GenomeElement('TestGenome', 'chrM', start=1022, end=1027, val=11),
                 GenomeElement('TestGenome', 'chr21', start=200, end=205, val=21.1),
                 GenomeElement('TestGenome', 'chr21', start=210, end=215, val=numpy.nan)],
                [BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=10, end=25), elCount=2),
                 BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=1012, end=1027), elCount=2),
                 BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chr21', start=200, end=215), elCount=2)],
                WigGenomeElementSource,
                ['start', 'end', 'val'],
                'float64',
                1,
                'float64',
                1)
        
        self.cases['wig_fixed_segments_sliding_window'] = \
            Case(WigGenomeElementSource,
                 'TestGenome',
                ['track type=wiggle_0 name=track_label'],
                [' '.join(['fixedStep','chrom=chrM','start=11','step=1','span=5']),
                 '4.5',
                 '-3.7',
                 ' '.join(['fixedStep','chrom=chrM','start=1013','step=1','span=5']),
                 '2.1',
                 '11',
                 ' '.join(['fixedStep','chrom=chr21','start=201','step=1','span=5']),
                 '21.1',
                 'nan'],
                '.wig',
                ['My','wig-fixed-segments-sliding-window-track'],
                [GenomeElement('TestGenome', 'chrM', start=10, end=15, val=4.5),
                 GenomeElement('TestGenome', 'chrM', start=11, end=16, val=-3.7),
                 GenomeElement('TestGenome', 'chrM', start=1012, end=1017, val=2.1),
                 GenomeElement('TestGenome', 'chrM', start=1013, end=1018, val=11),
                 GenomeElement('TestGenome', 'chr21', start=200, end=205, val=21.1),
                 GenomeElement('TestGenome', 'chr21', start=201, end=206, val=numpy.nan)],
                [BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=10, end=16), elCount=2),
                 BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=1012, end=1018), elCount=2),
                 BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chr21', start=200, end=206), elCount=2)],
                WigGenomeElementSource,
                ['start', 'end', 'val'],
                'float64',
                1,
                'float64',
                1)
        
        self.cases['wig_fixed_step_function'] = \
            Case(WigGenomeElementSource,
                 'TestGenome',
                ['track type=wiggle_0 name=track_label'],
                [' '.join(['fixedStep','chrom=chrM','start=11','step=10','span=10']),
                 '4.5',
                 '-3.7',
                 ' '.join(['fixedStep','chrom=chrM','start=1013','step=10','span=10']),
                 '2.1',
                 '11',
                 ' '.join(['fixedStep','chrom=chr21','start=201','step=10','span=10']),
                 '21.1',
                 'nan'],
                '.wig',
                ['My','wig-fixed-step-function-track'],
                [GenomeElement('TestGenome', 'chrM', end=10, val=numpy.nan),
                 GenomeElement('TestGenome', 'chrM', end=20, val=4.5),
                 GenomeElement('TestGenome', 'chrM', end=30, val=-3.7),
                 GenomeElement('TestGenome', 'chrM', end=1012, val=numpy.nan),
                 GenomeElement('TestGenome', 'chrM', end=1022, val=2.1),
                 GenomeElement('TestGenome', 'chrM', end=1032, val=11),
                 GenomeElement('TestGenome', 'chr21', end=200, val=numpy.nan),
                 GenomeElement('TestGenome', 'chr21', end=210, val=21.1),
                 GenomeElement('TestGenome', 'chr21', end=220, val=numpy.nan)],
                [BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=10, end=30), elCount=3),
                 BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=1012, end=1032), elCount=3),
                 BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chr21', start=200, end=220), elCount=3)],
                WigGenomeElementSource,
                ['end', 'val'],
                'float64',
                1,
                'float64',
                1)
        
        # Bounding regions, in sorted order, with no gaps, and with dense elements
        self.cases['wig_fixed_step_function_no_gaps'] = \
            Case(WigGenomeElementSource,
                 'TestGenome',
                ['track type=wiggle_0 name=track_label'],
                [' '.join(['fixedStep','chrom=chrM','start=11','step=10','span=10']),
                 '4.5',
                 '-3.7',
                 ' '.join(['fixedStep','chrom=chrM','start=31','step=10','span=10']),
                 '2.1',
                 '11',
                 ' '.join(['fixedStep','chrom=chr21','start=201','step=10','span=10']),
                 '21.1',
                 'nan'],
                '.wig',
                ['My','wig-fixed-step-function-track-no-gaps'],
                [GenomeElement('TestGenome', 'chrM', end=10, val=numpy.nan),
                 GenomeElement('TestGenome', 'chrM', end=20, val=4.5),
                 GenomeElement('TestGenome', 'chrM', end=30, val=-3.7),
                 GenomeElement('TestGenome', 'chrM', end=40, val=2.1),
                 GenomeElement('TestGenome', 'chrM', end=50, val=11),
                 GenomeElement('TestGenome', 'chr21', end=200, val=numpy.nan),
                 GenomeElement('TestGenome', 'chr21', end=210, val=21.1),
                 GenomeElement('TestGenome', 'chr21', end=220, val=numpy.nan)],
                [BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=10, end=50), elCount=5),
                 BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chr21', start=200, end=220), elCount=3)],
                WigGenomeElementSource,
                ['end', 'val'],
                'float64',
                1,
                'float64',
                1)
        
        self.cases['wig_variable_points'] = \
            Case(WigGenomeElementSource,
                 'TestGenome',
                ['track type=wiggle_0 name=track_label'],
                [' '.join(['variableStep','chrom=chr21', 'span=1']),
                 '#comment',
                 '1\t4.5',
                 ' '.join(['variableStep','chrom=chrM']),
                 '21\tNA',
                 '151\t3.7',
                 '351\t2.7'],
                '.wig',
                ['My','wig_variable_points_track'],
                [GenomeElement('TestGenome', 'chr21', start=0, val=4.5),
                 GenomeElement('TestGenome', 'chrM', start=20, val=numpy.nan),
                 GenomeElement('TestGenome', 'chrM', start=150, val=3.7),
                 GenomeElement('TestGenome', 'chrM', start=350, val=2.7)],
                [],
                WigGenomeElementSource,
                ['start', 'val'],
                'float64',
                1,
                'float64',
                1)
        
        self.cases['wig_variable_segments'] = \
            Case(WigGenomeElementSource,
                 'TestGenome',
                ['track type=wiggle_0 name=track_label'],
                [' '.join(['variableStep','chrom=chr21', 'span=50']),
                 '1\t4.5',
                 ' '.join(['variableStep','chrom=chrM', 'span=100']),
                 '21\tNA',
                 '151\t3.7',
                 '351\t2.7'],
                '.wig',
                ['My','wig_variable_segments_track'],
                [GenomeElement('TestGenome', 'chr21', start=0, end=50, val=4.5),
                 GenomeElement('TestGenome', 'chrM', start=20, end=120, val=numpy.nan),
                 GenomeElement('TestGenome', 'chrM', start=150, end=250, val=3.7),
                 GenomeElement('TestGenome', 'chrM', start=350, end=450, val=2.7)],
                [],
                WigGenomeElementSource,
                ['start', 'end', 'val'],
                'float64',
                1,
                'float64',
                1)
        
        self.cases['gff'] = \
            Case(None,
                 'TestGenome',
                [],
                ['\t'.join(['chr21', 'RNG', 'Genes', '13332357', '13412440', '1.8', '+', '0', \
                            'ID=30313;Accession=NR_026916;Name=C21orf99;color=9400D3;url=http://genome.ucsc.edu/cgi-bin/hgTracks?&clade=vertebrate&org=Human&db=hg18&position=chr21:13332357-13412440&pix620&Submit=submit;']),
                 '\t'.join(['chr21', 'RNG', 'Genes', '13904368', '13935777', '2.3', '+', '0', \
                            'ID=771;Accession=NM_174981;Name=POTED;color=9400D3;url=http://genome.ucsc.edu/cgi-bin/hgTracks?&clade=vertebrate&org=Human&db=hg18&position=chr21:13904368-13935777&pix620&Submit=submit;']),
                 '\t'.join(['chr21', 'RNG', 'Genes', '14510336', '14522564', '-1.0', '+', '0', \
                            'ID=773;Accession=NM_144770;Name=RBM11;color=9400D3;url=http://genome.ucsc.edu/cgi-bin/hgTracks?&clade=vertebrate&org=Human&db=hg18&position=chr21:14510336-14522564&pix620&Submit=submit;'])],
                '.gff',
                ['My','gff-track'],
                [GenomeElement('TestGenome', 'chr21', start=13332356, end=13412440, val=1.8, strand=True, id='30313', \
                               extra=OrderedDict([('source', 'RNG'), ('type', 'Genes'), ('phase', '0'), \
                                                  ('attributes', 'ID=30313;Accession=NR_026916;Name=C21orf99;color=9400D3;url=http://genome.ucsc.edu/cgi-bin/hgTracks?&clade=vertebrate&org=Human&db=hg18&position=chr21:13332357-13412440&pix620&Submit=submit;'), \
                                                  ('name', 'C21orf99')])), \
                 GenomeElement('TestGenome', 'chr21', start=13904367, end=13935777, val=2.3, strand=True, id='771', \
                               extra=OrderedDict([('source', 'RNG'), ('type', 'Genes'), ('phase', '0'), ('attributes', 'ID=771;Accession=NM_174981;Name=POTED;color=9400D3;url=http://genome.ucsc.edu/cgi-bin/hgTracks?&clade=vertebrate&org=Human&db=hg18&position=chr21:13904368-13935777&pix620&Submit=submit;'), \
                                                  ('name', 'POTED')])), \
                 GenomeElement('TestGenome', 'chr21', start=14510335, end=14522564, val=-1.0, strand=True, id='773', \
                               extra=OrderedDict([('source', 'RNG'), ('type', 'Genes'), ('phase', '0'), ('attributes', 'ID=773;Accession=NM_144770;Name=RBM11;color=9400D3;url=http://genome.ucsc.edu/cgi-bin/hgTracks?&clade=vertebrate&org=Human&db=hg18&position=chr21:14510336-14522564&pix620&Submit=submit;'), \
                                                  ('name', 'RBM11')]))],
                [],
                GffGenomeElementSource,
                ['start', 'end', 'val', 'strand', 'id', 'source', 'type', 'phase', 'attributes', 'name'],
                'float64',
                1,
                'float64',
                1)
                                        
        self.cases['fasta'] = \
            Case(None,
                 'TestGenome',
                [],
                ['>chrM Description'] +
                 ['ac',
                 'gt'] * 40 +
                ['acg'] +
                ['>chr21 Description'] +
                ['gca'],
                '.fa',
                ['My','fasta-track'],
                [GenomeElement('TestGenome', 'chrM', val='a'),
                 GenomeElement('TestGenome', 'chrM', val='c'),
                 GenomeElement('TestGenome', 'chrM', val='g'),
                 GenomeElement('TestGenome', 'chrM', val='t')]*40 +
                [GenomeElement('TestGenome', 'chrM', val='a'),
                 GenomeElement('TestGenome', 'chrM', val='c'),
                 GenomeElement('TestGenome', 'chrM', val='g')] +
                [GenomeElement('TestGenome', 'chr21', val='g'),
                 GenomeElement('TestGenome', 'chr21', val='c'),
                 GenomeElement('TestGenome', 'chr21', val='a')],
                [BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chrM', start=0, end=163), elCount=163),
                 BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chr21', start=0, end=3), elCount=3)],
                FastaGenomeElementSource,
                ['val'],
                'S1',
                1,
                'float64',
                1)
        
        self.cases['hbfunction'] = \
            Case(None,
                 'TestGenome',
                [],
                ['Whatever'],
                '.hbfunction',
                ['My','intensity-track'],
                [GenomeElement('TestGenome', 'chr21', val=0.0)],
                [BoundingRegionTuple(region=GenomeRegion('TestGenome', 'chr21', start=0, end=1), elCount=1)],
                HBFunctionGenomeElementSource,
                ['val'],
                'float64',
                1,
                'float64',
                1)
        
        self.exceptionCases = OrderedDict()
        
        #Testing: Header line with space before/after variable name
        self.exceptionCases['gtrack_e0'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['## track name :'],
                [],
                '.gtrack',
                ['e0','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Header line with malplaced tab
        self.exceptionCases['gtrack_e1'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##myheader:  \tsomething\t'],
                [],
                '.gtrack',
                ['e1','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Column spec line before header line
        self.exceptionCases['gtrack_e1.1'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['###value',
                 '##myheader: something'],
                [],
                '.gtrack',
                ['e1.1','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Bounding region spec line before header line
        self.exceptionCases['gtrack_e1.2'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['####genome=TestGenome',
                 '##myheader: something'],
                [],
                '.gtrack',
                ['e1.2','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Bounding region spec line before column spec line
        self.exceptionCases['gtrack_e1.3'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['####genome=TestGenome',
                 '###value'],
                [],
                '.gtrack',
                ['e1.3','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Data line before header line
        self.exceptionCases['gtrack_e1.4'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['0.5',
                 '##track type: function'
                 '###value'
                 '####seqid=chrM'],
                [],
                '.gtrack',
                ['e1.4','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Empty lines with whitespace
        self.exceptionCases['gtrack_e1.5'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                [],
                ['\t\t',
                 ' '],
                '.gtrack',
                ['e1.5','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Value type not in allowed list
        self.exceptionCases['gtrack_e2'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##value type: string'],
                [],
                '.gtrack',
                ['e2','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Header line with illegal values
        self.exceptionCases['gtrack_e2.1'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##1-indexed: f'],
                [],
                '.gtrack',
                ['e2.1','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        self.exceptionCases['gtrack_e2.2'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##fixed length: ten'],
                [],
                '.gtrack',
                ['e2.2','gtrack'],
                GtrackGenomeElementSource,
                ValueError)
        
        #Tesitng: Incorrect gtrack version
        self.exceptionCases['gtrack_e2.3'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 None,
                ['##gtrack version: 2.0'],
                [],
                '.gtrack',
                ['e2.3','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Edge weight dimension not in allowed list
        self.exceptionCases['gtrack_e3'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##edge weight type: tuple'],
                [],
                '.gtrack',
                ['e3','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: start <= end
        self.exceptionCases['gtrack_e3.1'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                [],
                ['\t'.join(['chrM','100','100'])],
                '.gtrack',
                ['e3.1','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: start <= end in bounding region
        self.exceptionCases['gtrack_e3.2'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                [],
                ['####seqid=chrM; start=100; end=100'],
                '.gtrack',
                ['e3.2','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: No overlapping segments=true: consecutive overlapping data lines
        self.exceptionCases['gtrack_e4'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##no overlapping elements: true'],
                ['\t'.join(['chrM','100','165']),
                 '\t'.join(['chrM','150','200'])],
                '.gtrack',
                ['e4','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: No overlapping segments=true: consecutive overlapping data lines og points
        self.exceptionCases['gtrack_e4.1'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: points',
                 '##no overlapping elements: true',
                 '\t'.join(['seqid','start'])],
                ['\t'.join(['chrM','100']),
                 '\t'.join(['chrM','100'])],
                '.gtrack',
                ['e4.1','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Sorted elements=true for unsorted track elements
        self.exceptionCases['gtrack_e5'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 None,
                ['##sorted elements: true',
                 '\t'.join(['###genome', 'seqid', 'start', 'end'])],
                ['\t'.join(['hg18','chrM','100','165']),
                 '\t'.join(['hg17','chrM','150','200'])],
                '.gtrack',
                ['e5','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Sorted elements=true for unsorted bounding regions
        self.exceptionCases['gtrack_e6'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 None,
                ['##sorted elements: true'],
                ['####genome=hg18; seqid=chrM; start=0; end=200',
                 '\t'.join(['chrM','100','165']),
                 '####genome=hg17; seqid=chrM; start=0; end=200',
                 '\t'.join(['chrM','150','200'])],
                '.gtrack',
                ['e6','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        ##Testing: Unsorted bounding regions in HbGtrackGenomeElementSource
        #self.exceptionCases['gtrack_e6_hb'] = \
        #    ExceptionCase(None,
        #         None,
        #        [''],
        #        ['####genome=hg18; seqid=chrM; start=200; end=300',
        #         '\t'.join(['chrM','200','265']),
        #         '####genome=hg18; seqid=chrM; start=0; end=100',
        #         '\t'.join(['chrM','50','100'])],
        #        '.gtrack',
        #        ['e6_hb','gtrack'],
        #        HbGtrackGenomeElementSource,
        #        InvalidFormatError)
        
        #Testing: unsorted elements in dense bounding region
        self.exceptionCases['gtrack_e6.1'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: step function',\
                 '\t'.join(['###end','value'])],
                ['####seqid=chrM; end=200',
                 '\t'.join(['200','1.0']),
                 '\t'.join(['100','0.9'])],
                '.gtrack',
                ['e6.1','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Column specification that misses one needed column (linked track type without 'id')
        self.exceptionCases['gtrack_e7'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: linked points',
                 '\t'.join(['###genome', 'seqid', 'start', 'edges'])],
                [],
                '.gtrack',
                ['e7','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Column specification with a core column too many (segment track type with value)
        self.exceptionCases['gtrack_e7.1'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: segments',
                 '\t'.join(['###seqid', 'start', 'end', 'value'])],
                [],
                '.gtrack',
                ['e7.1','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Value column with wrong column name
        self.exceptionCases['gtrack_e7.2'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: valued segments',
                 '##value column: tesst',
                 '\t'.join(['###seqid', 'start', 'end', 'test'])],
                ['\t'.join(['chrM', '100', '110', '1.0'])],
                '.gtrack',
                ['e7.2','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Duplicate in column spec. line
        self.exceptionCases['gtrack_e7.3'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: linked segments',
                 '\t'.join(['###seqid', 'start', 'end', 'id', 'edges', 'edges'])],
                ['\t'.join(['chrM', '100', '110', 'a', 'b', 'b']),
                 '\t'.join(['chrM', '200', '210', 'b', '.', 'a'])],
                '.gtrack',
                ['e7.3','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Header variable "Edges column" with "edges" in column spec. line
        self.exceptionCases['gtrack_e7.4'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: linked segments',
                 '##edges column: undirected',
                 '\t'.join(['###seqid', 'start', 'end', 'id', 'edges', 'undirected'])],
                ['\t'.join(['chrM', '100', '110', 'a', 'b', 'b']),
                 '\t'.join(['chrM', '200', '210', 'b', '.', 'a'])],
                '.gtrack',
                ['e7.4','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Column name starting/ending with space
        self.exceptionCases['gtrack_e8'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['\t'.join(['###genome', ' seqid', 'start ', 'end'])],
                [],
                '.gtrack',
                ['e8','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Column name with illegal character
        self.exceptionCases['gtrack_e8.1'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['\t'.join(['###genome', 'seqid', 'start', 'end', 'ex\x07tra'])],
                [],
                '.gtrack',
                ['e8.1','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Dataline and column-specification do not have same amount of elements
        self.exceptionCases['gtrack_e9'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['\t'.join(['###seqid', 'start', 'end'])],
                ['\t'.join(['chrM','100','165','+'])],
                '.gtrack',
                ['e9','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Dataline with forbidden character
        self.exceptionCases['gtrack_e10'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: valued segments',
                '\t'.join(['###seqid', 'start', 'end', 'value'])],
                ['\t'.join(['chrM','100','165','abc\x07'])],
                '.gtrack',
                ['e10','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Dataline with content that starts with space
        self.exceptionCases['gtrack_e10.1'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: valued segments',
                '\t'.join(['###seqid', 'start', 'end', 'value'])],
                ['\t'.join(['chrM','100','165',' abc'])],
                '.gtrack',
                ['e10.1','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Strand is not +/-/.
        self.exceptionCases['gtrack_e11'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['\t'.join(['###seqid', 'start', 'end', 'strand'])],
                ['\t'.join(['chrM','100','165','pos'])],
                '.gtrack',
                ['e11','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Start, end < 0
        self.exceptionCases['gtrack_e12'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                [],
                ['\t'.join(['chrM','-1','165'])],
                '.gtrack',
                ['e12','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Start/end outside seqid if genome specified
        self.exceptionCases['gtrack_e13'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                [],
                ['\t'.join(['chrM','0','30000'])],
                '.gtrack',
                ['e13','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Value: number value not a number
        self.exceptionCases['gtrack_e14'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: valued segments',
                '\t'.join(['###seqid', 'start', 'end', 'value'])],
                ['\t'.join(['chrM','100','165','1-0.1'])],
                '.gtrack',
                ['e14','gtrack'],
                GtrackGenomeElementSource,
                ValueError)
        
        #Testing: Value: category value empty
        self.exceptionCases['gtrack_e14.1'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: valued segments',
                 '##value type: category',
                '\t'.join(['###seqid', 'start', 'end', 'value'])],
                ['\t'.join(['chrM','100','165',''])],
                '.gtrack',
                ['e14.1','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Value: value=NA
        self.exceptionCases['gtrack_e14.2'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: valued segments',
                '\t'.join(['###seqid', 'start', 'end', 'value'])],
                ['\t'.join(['chrM','100','165','NA'])],
                '.gtrack',
                ['e14.2','gtrack'],
                GtrackGenomeElementSource,
                ValueError)
        
        #Testing: Value dimension: list and HB
        self.exceptionCases['gtrack_e14.3_hb'] = \
            ExceptionCase(None,
                 'TestGenome',
                ['##track type: valued segments',
                 '##value dimension: list',
                '\t'.join(['###seqid', 'start', 'end', 'value'])],
                ['\t'.join(['chrM','100','165','0,1'])],
                '.gtrack',
                ['e14.3_hb','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Edge weight dimension: list and HB
        self.exceptionCases['gtrack_e14.4_hb'] = \
            ExceptionCase(None,
                 'TestGenome',
                ['##track type: linked segments',
                 '##edge weights: true',
                 '##edge weight dimension: list',
                '\t'.join(['###seqid', 'start', 'end', 'id', 'edges'])],
                ['\t'.join(['chrM','100','165','aaa','aaa=0,1'])],
                '.gtrack',
                ['e14.4_hb','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Weights: space before/after equals
        self.exceptionCases['gtrack_e15'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: linked points',
                 '##edge weights: true',
                '\t'.join(['###seqid', 'start', 'id', 'edges'])],
                ['\t'.join(['chrM','100','aaa','aab =0.1']),
                 '\t'.join(['chrM','120','aab','aaa= 1.0'])],
                '.gtrack',
                ['e15','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Weights: binary weight not a binary
        self.exceptionCases['gtrack_e16'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: linked points',
                 '##edge weights: true',
                 '##edge weight type: binary',
                 '\t'.join(['###seqid', 'start', 'id', 'edges'])],
                ['\t'.join(['chrM','100','aaa','aab=1']),
                 '\t'.join(['chrM','120','aab','aaa=y'])],
                '.gtrack',
                ['e16','gtrack'],
                GtrackGenomeElementSource,
                ValueError)
        
        #Testing: Value: character value not a character        
        self.exceptionCases['gtrack_e17'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: valued segments',
                 '##value type: character',
                 '\t'.join(['###seqid', 'start', 'end', 'value'])],
                ['\t'.join(['chrM','100','165','ab'])],
                '.gtrack',
                ['e17','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Weights: pair of number not a pair
        self.exceptionCases['gtrack_e18'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: linked points',
                 '##edge weights: true',
                 '##edge weight type: number',
                 '##edge weight dimension: pair',
                 '\t'.join(['###seqid', 'start', 'id', 'edges'])],
                ['\t'.join(['chrM','100','aaa','aab=1']),
                 '\t'.join(['chrM','120','aab','aaa=.'])],
                '.gtrack',
                ['e18','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Value: vector of numbers not equal length
        self.exceptionCases['gtrack_e19'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: valued segments',
                 '##value dimension: vector',
                 '\t'.join(['###seqid', 'start', 'end', 'value'])],
                ['\t'.join(['chrM','100','165','1,0.2,-0.2']),
                 '\t'.join(['chrM','120','165','1,-0.1'])],
                '.gtrack',
                ['e19','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Value: vector of numbers with single missing value
        self.exceptionCases['gtrack_e19.1'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: valued segments',
                 '##value dimension: vector',
                 '\t'.join(['###seqid', 'start', 'end', 'value'])],
                ['\t'.join(['chrM','100','165','1,0.2,-0.2']),
                 '\t'.join(['chrM','120','165','.'])],
                '.gtrack',
                ['e19.1','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Value: pair of binary with single missing value
        self.exceptionCases['gtrack_e19.2'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: valued segments',
                 '##value type: binary',
                 '##value dimension: pair',
                 '\t'.join(['###seqid', 'start', 'end', 'value'])],
                ['\t'.join(['chrM','100','165','01']),
                 '\t'.join(['chrM','120','165','.'])],
                '.gtrack',
                ['e19.2','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Value: vector of numbers with length 1
        self.exceptionCases['gtrack_e19.3_hb'] = \
            ExceptionCase(None,
                 'TestGenome',
                ['##track type: valued segments',
                 '##value dimension: vector',
                 '\t'.join(['###seqid', 'start', 'end', 'value'])],
                ['\t'.join(['chrM','100','165','1']),
                 '\t'.join(['chrM','120','165','.'])],
                '.gtrack',
                ['e19.3_hb','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Edge weight: vector, with no edges defined
        self.exceptionCases['gtrack_e19.4_hb'] = \
            ExceptionCase(None,
                 'TestGenome',
                ['##track type: linked points',
                 '##edge weights: true',
                 '##edge weight dimension: vector',
                 '\t'.join(['###seqid', 'start', 'id', 'edges'])],
                ['\t'.join(['chrM','100','a','.']),
                 '\t'.join(['chrM','120','b','.'])],
                '.gtrack',
                ['e19.4_hb','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Weights: vector of binary with comma
        self.exceptionCases['gtrack_e20'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: linked points',
                 '##edge weights: true',
                 '##edge weight type: binary',
                 '##edge weight dimension: pair',
                 '\t'.join(['###seqid', 'start', 'id', 'edges'])],
                ['\t'.join(['chrM','100','aaa','aab=1,1']),
                 '\t'.join(['chrM','120','aab','aaa=0,1'])],
                '.gtrack',
                ['e20','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Weights: list of category with spaces
        self.exceptionCases['gtrack_e21'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: linked points',
                 '##edge weights: true',
                 '##edge weight type: category',
                 '##edge weight dimension: list',
                 '\t'.join(['###seqid', 'start', 'id', 'edges'])],
                ['\t'.join(['chrM','100','aaa','aab=gene, exon']),
                 '\t'.join(['chrM','120','aab','aaa=.'])],
                '.gtrack',
                ['e21','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Seqid not same in bounding region and column
        self.exceptionCases['gtrack_e22'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: points',
                 '\t'.join(['###seqid', 'start'])],
                ['####seqid=chrM',
                 '\t'.join(['chr1','100'])],
                '.gtrack',
                ['e22','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Genome not same in bounding region and column
        self.exceptionCases['gtrack_e23'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 None,
                ['##track type: points',
                 '\t'.join(['###genome', 'seqid', 'start'])],
                ['####genome=hg18; seqid=chrM; start=0; end=200',
                 '\t'.join(['hg19','chrM','100'])],
                '.gtrack',
                ['e23','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Genome not same in gesource and gtrack
        self.exceptionCases['gtrack_e24'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: points',
                 '\t'.join(['###start'])],
                ['####genome=hg18; seqid=chrM'],
                '.gtrack',
                ['e24','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Seqid not in genome
        self.exceptionCases['gtrack_e25'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: points',
                 '\t'.join(['###start'])],
                ['####seqid=chr1'],
                '.gtrack',
                ['e25','gtrack'],
                GtrackGenomeElementSource,
                ArgumentValueError)
        
        #Testing: Circular elements without correct header
        self.exceptionCases['gtrack_e26'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##circular elements: false'],
                ['\t'.join(['chrM','100','0'])],
                '.gtrack',
                ['e26','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        self.exceptionCases['gtrack_e26.1'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##circular elements: false'],
                ['####seqid=chrM; start=100; end=0'],
                '.gtrack',
                ['e26.1','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: HyperBrowser does not support circular elements at all
        self.exceptionCases['gtrack_e26.2_hb'] = \
            ExceptionCase(None,
                 'TestGenome',
                ['##circular elements: true'],
                [],
                '.gtrack',
                ['e26.2_hb','gtrack'],
                HbGtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: non-unique id
        self.exceptionCases['gtrack_e27'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: linked points',
                 '\t'.join(['###seqid', 'start', 'id', 'edges'])],
                ['\t'.join(['chrM','100','aaa','.']),
                 '\t'.join(['chrM','120','aaa','aaa'])],
                '.gtrack',
                ['e27','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: edges without match in id column
        self.exceptionCases['gtrack_e27.1'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: linked points',
                 '\t'.join(['###seqid', 'start', 'id', 'edges'])],
                ['\t'.join(['chrM','100','aaa','aab;aac']),
                 '\t'.join(['chrM','120','aab','aaa'])],
                '.gtrack',
                ['e27.1','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: duplicate edge
        self.exceptionCases['gtrack_e27.2'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: linked points',
                 '\t'.join(['###seqid', 'start', 'id', 'edges'])],
                ['\t'.join(['chrM','100','aaa','aab;aab']),
                 '\t'.join(['chrM','120','aab','aaa'])],
                '.gtrack',
                ['e27.2','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: empty id
        self.exceptionCases['gtrack_e27.3'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: linked points',
                 '\t'.join(['###seqid', 'start', 'id', 'edges'])],
                ['\t'.join(['chrM','100','aaa','.']),
                 '\t'.join(['chrM','120','','aaa'])],
                '.gtrack',
                ['e27.3','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Undirected edges=true with unpaired edges
        self.exceptionCases['gtrack_e28'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: linked points',
                 '##undirected edges: true',
                 '\t'.join(['###seqid', 'start', 'id', 'edges'])],
                ['\t'.join(['chrM','100','aaa','aab;aac']),
                 '\t'.join(['chrM','120','aab','aaa']),
                 '\t'.join(['chrM','130','aac','aab'])],
                '.gtrack',
                ['e28','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Undirected edges=true with paired edges with different weights
        self.exceptionCases['gtrack_e28.1'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: linked points',
                 '##undirected edges: true',
                 '##edge weights: true',
                 '\t'.join(['###seqid', 'start', 'id', 'edges'])],
                ['\t'.join(['chrM','100','aaa','aab=1.0;aac=1.2']),
                 '\t'.join(['chrM','120','aab','aaa=1.0']),
                 '\t'.join(['chrM','130','aac','aaa=0.9'])],
                '.gtrack',
                ['e28.1','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Edge weights=true without edge weights and opposite
        self.exceptionCases['gtrack_e29'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: linked points',
                 '##edge weights: true',
                 '\t'.join(['###seqid', 'start', 'id', 'edges'])],
                ['\t'.join(['chrM','100','aaa','aab=1.0']),
                 '\t'.join(['chrM','120','aab','aaa'])],
                '.gtrack',
                ['e29','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        self.exceptionCases['gtrack_e30'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: linked points',
                 '##edge weights: false',
                 '\t'.join(['###seqid', 'start', 'id', 'edges'])],
                ['\t'.join(['chrM','100','aaa','aab=1.0']),
                 '\t'.join(['chrM','120','aab','aaa'])],
                '.gtrack',
                ['e30','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Uninterrupted data lines with multiple bounding regions
        self.exceptionCases['gtrack_e31'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 None,
                ['##uninterrupted data lines: true'],
                ['####genome=hg18',
                 '\t'.join(['chrM','100','165']),
                 '####genome=hg17',
                 '\t'.join(['chr21','150','200'])],
                '.gtrack',
                ['e31','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Uninterrupted data lines with comments
        self.exceptionCases['gtrack_e31.1'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##uninterrupted data lines: true'],
                ['\t'.join(['chrM','100','165']),
                 '#comment',
                 '\t'.join(['chr21','150','200'])],
                '.gtrack',
                ['e31.1','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Uninterrupted data lines with empty lines
        self.exceptionCases['gtrack_e31.2'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##uninterrupted data lines: true'],
                ['',
                 '\t'.join(['chrM','100','165']),
                 '',
                 '\t'.join(['chr21','150','200'])],
                '.gtrack',
                ['e31.2','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Fixed-size data lines with more than one column or column not value
        self.exceptionCases['gtrack_e32'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: function',
                 '##fixed-size data lines: true',
                 '\t'.join(['###seqid', 'value'])],
                [],
                '.gtrack',
                ['e32','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        self.exceptionCases['gtrack_e32.1'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: genome partition',
                 '##fixed-size data lines: true',
                 '###end'],
                [],
                '.gtrack',
                ['e32.1','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        self.exceptionCases['gtrack_e32.2'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: step function',
                 '##fixed length: 10',
                 '##fixed-size data lines: true',
                 '###value'],
                ['####seqid=chrM; start=0; end=100'],
                '.gtrack',
                ['e32.2','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Fixed-size data lines with line sep in the middle of a data line
        self.exceptionCases['gtrack_e33'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: function',
                 '##value type: character',
                 '##value dimension: pair',
                 '##fixed-size data lines: true',
                 '##data line size: 2',
                 '\t'.join(['###value'])],
                ['####seqid=chrM; start=0; end=3',
                 'ACT',
                 'CTA'],
                '.gtrack',
                ['e33','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Fixed length == 0
        self.exceptionCases['gtrack_e33.1'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##fixed length: 0',
                 '\t'.join(['###seqid','start'])],
                ['\t'.join(['chrM','100'])],
                '.gtrack',
                ['e33.1','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Fixed length + fixed gap size <= 0
        self.exceptionCases['gtrack_e33.2'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: valued segments',
                 '##fixed gap size: -1',
                 '###value'],
                ['####seqid=chrM',
                 '0.1'],
                '.gtrack',
                ['e33.2','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Fixed gap size outside of bounding region type B
        self.exceptionCases['gtrack_e33.3'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 None,
                ['##track type: valued points',
                 '##fixed gap size: 10',
                 '\t'.join(['###seqid','value'])],
                ['####genome=hg18',
                 '\t'.join(['chrM','0.1'])],
                '.gtrack',
                ['e33.3','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Data line size < 1
        self.exceptionCases['gtrack_e34'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: function',
                 '##fixed-size data lines: true',
                 '##data line size: 0',
                 '###value'],
                [],
                '.gtrack',
                ['e34','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Bounding region GTrack file with data lines before first b.r.
        self.exceptionCases['gtrack_e35'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 None,
                [],
                ['\t'.join(['chrM','100','165']),
                 '####genome=TestGenome',
                 '\t'.join(['chrM','200','210'])],
                '.gtrack',
                ['e35','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Overlapping bounding regions
        self.exceptionCases['gtrack_e36'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                [],
                ['####seqid=chrM; start=100; end=200',
                 '\t'.join(['chrM','100','165']),
                 '####seqid=chrM; start=400; end=500',
                 '\t'.join(['chrM','410','421']),
                 '####seqid=chrM; start=190; end=300',
                 '\t'.join(['chrM','200','210'])],
                '.gtrack',
                ['e36','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Bounding regions with no gaps in unsorted order
        self.exceptionCases['gtrack_e36.1_hb'] = \
            ExceptionCase(None,
                 'TestGenome',
                [],
                ['####seqid=chrM; start=100; end=200',
                 '\t'.join(['chrM','100','165']),
                 '####seqid=chrM; start=400; end=500',
                 '\t'.join(['chrM','410','421']),
                 '####seqid=chrM; start=200; end=300',
                 '\t'.join(['chrM','200','210'])],
                '.gtrack',
                ['e36.1','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Bounding regions of type A and B in same file
        self.exceptionCases['gtrack_e37'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 None,
                [],
                ['####genome=hg18',
                 '####seqid=chrM; start=190; end=300',
                 '\t'.join(['chrM','200','210'])],
                '.gtrack',
                ['e37','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Bounding regions of type B with no data lines between (GP)
        self.exceptionCases['gtrack_e37.1_hb'] = \
            ExceptionCase(None,
                 None,
                ['##track type: genome partition',
                 '###end'],
                ['####seqid=chrM; start=190; end=300',
                 '####seqid=chrM; start=400; end=500',
                 '500'],
                '.gtrack',
                ['e37.1','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Track-type = gp/sf/f and no bounding region type b fails
        self.exceptionCases['gtrack_e38'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 None,
                ['##track type: genome partition',
                 '###end'],
                ['####genome=hg18',
                 '100',
                 '200'],
                '.gtrack',
                ['e38','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Bounding region end not end of last data line (gp & f)
        self.exceptionCases['gtrack_e39'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: genome partition',
                 '###end'],
                ['####seqid=chrM; start=0; end=300',
                 '100',
                 '200'],
                '.gtrack',
                ['e39','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        self.exceptionCases['gtrack_e40'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                ['##track type: function',
                 '###value'],
                ['####seqid=chrM; start=0; end=3',
                 '1.1',
                 '1.2'],
                '.gtrack',
                ['e40','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Bounding region with space after '####'
        self.exceptionCases['gtrack_e41'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                [],
                ['#### seqid=chr21'],
                '.gtrack',
                ['e41','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Bounding region with no semicolons
        self.exceptionCases['gtrack_e41.1'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                [],
                ['####seqid=chr21 start=20'],
                '.gtrack',
                ['e41.1','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Bounding region with attribute without value.
        self.exceptionCases['gtrack_e41.2'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                [],
                ['####seqid=chr21; end'],
                '.gtrack',
                ['e41.2','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Bounding region with tab.
        self.exceptionCases['gtrack_e41.3'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 'TestGenome',
                [],
                ['####seqid=chr21;\tstart=0;\tend=1'],
                '.gtrack',
                ['e41.3','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Bounding region with attribute not in specification
        self.exceptionCases['gtrack_e42'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 None,
                [],
                ['####seqid=chr21; something=0'],
                '.gtrack',
                ['e42','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Bounding region with data lines outside of region
        self.exceptionCases['gtrack_e42.1'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 None,
                ['\t'.join(['###start','end'])],
                ['####seqid=chr21; start=100; end=200',
                '\t'.join(['90','120'])],
                '.gtrack',
                ['e42.1','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        self.exceptionCases['gtrack_e42.2'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 None,
                ['\t'.join(['###start','end'])],
                ['####seqid=chr21; start=100; end=200',
                '\t'.join(['180','210'])],
                '.gtrack',
                ['e42.2','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Bounding region with illegal character
        self.exceptionCases['gtrack_e42.3'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 None,
                ['\t'.join(['###start','end'])],
                ['####seqid=chrx\0821; start=100; end=200',
                '\t'.join(['180','210'])],
                '.gtrack',
                ['e42.3','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Bounding region type B for track type F without end and genome
        self.exceptionCases['gtrack_e42.4'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 None,
                ['##track type: function',
                 '###value'],
                ['####seqid=chrM; start=100',
                 '23'],
                '.gtrack',
                ['e42.4','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Bounding region type B for track type GP without end and genome
        self.exceptionCases['gtrack_e42.5'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 None,
                ['##track type: genome partition',
                 '###end'],
                ['####seqid=chrM; start=100'],
                '.gtrack',
                ['e42.5','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Subtype not equal to subtype spec
        self.exceptionCases['gtrack_e43'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 None,
                ['##gtrack subtype: wrong',
                 '##subtype url: http://gtrack.no/bedgraph.gtrack'],
                [],
                '.gtrack',
                ['e43','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Subtype does not exist
        self.exceptionCases['gtrack_e43.1'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 None,
                ['##subtype url: http://gtrack.no/nosuch.gtrack'],
                [],
                '.gtrack',
                ['e43.1','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Subtype contains header variable 'subtype url'. No subtype adherence]
        self.exceptionCases['gtrack_e43.2'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 None,
                ['##subtype url: http://gtrack.no/withsubtypeurl.gtrack'],
                [],
                '.gtrack',
                ['e43.2','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Subtype version not equal to subtype spec
        self.exceptionCases['gtrack_e44'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 None,
                ['##subtype version: 0.9',
                 '##subtype url: http://gtrack.no/bedgraph.gtrack'],
                [],
                '.gtrack',
                ['e44','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Strict with changed header
        self.exceptionCases['gtrack_e45'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 None,
                ['##value dimension: pair',
                 '##subtype url: http://gtrack.no/bedgraph.gtrack'],
                [],
                '.gtrack',
                ['e45','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Strict with changed column description line
        self.exceptionCases['gtrack_e46'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 None,
                ['##subtype url: http://gtrack.no/bedgraph.gtrack',
                 '\t'.join(['###seqid', 'start', 'end', 'values', 'strand'])],
                [],
                '.gtrack',
                ['e46','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Extensible with changed header
        self.exceptionCases['gtrack_e47'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 None,
                ['##uninterrupted data lines: false',
                 '##subtype url: http://gtrack.no/bed_direct.gtrack'],
                [],
                '.gtrack',
                ['e47','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Extensible with illegal column description line
        self.exceptionCases['gtrack_e48'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 None,
                ['##subtype url: http://gtrack.no/bed_direct.gtrack',
                 '\t'.join(['###seqid', 'start', 'end', 'id', 'value', 'strand', 'extra', 'thickStart', 'thickEnd', 'itemRgb', 'blockCount', 'blockSizes', 'blockStarts'])],
                [],
                '.gtrack',
                ['e48','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Redefinable with illegal header
        self.exceptionCases['gtrack_e49'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 None,
                ['##1-indexed: false',
                 '##subtype url: http://gtrack.no/gff_direct.gtrack'],
                [],
                '.gtrack',
                ['e49','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Redefinable with illegal column description line
        self.exceptionCases['gtrack_e50'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 None,
                ['##subtype url: http://gtrack.no/gff_direct.gtrack',
                 '\t'.join(['###seqid', 'source', 'type', 'start', 'end', 'value', 'extra', 'strand', 'phase', 'attributes'])],
                [],
                '.gtrack',
                ['e50','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Reorderable with illegal header
        self.exceptionCases['gtrack_e51'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 None,
                ['##track type: valued segments',
                 '##value type: category',
                 '##subtype url: http://gtrack.no/mean_sd.gtrack'],
                [],
                '.gtrack',
                ['e51','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Reorderable with illegal column description file
        self.exceptionCases['gtrack_e52'] = \
            ExceptionCase(GtrackGenomeElementSource,
                 None,
                ['##track type: segments',
                 '##subtype url: http://gtrack.no/mean_sd.gtrack',
                 '\t'.join(['###seqid', 'start', 'end'])],
                [],
                '.gtrack',
                ['e52','gtrack'],
                GtrackGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Mixing variableStep and fixedStep in the same file
        self.exceptionCases['wig_e0'] = \
            ExceptionCase(WigGenomeElementSource,
                 'TestGenome',
                ['track type=wiggle_0 name=track_label'],
                [' '.join(['fixedStep','chrom=chrM','start=11','step=10']),
                 '4.5',
                 '-3.7',
                 ' '.join(['variableStep','chrom=chrM','start=1013']),
                 '2.1',
                 '11'],
                '.wig',
                ['e0','wig'],
                WigGenomeElementSource,
                InvalidFormatError)
        
        #Testing: fixedStep with variable step values
        self.exceptionCases['wig_e1'] = \
            ExceptionCase(WigGenomeElementSource,
                 'TestGenome',
                ['track type=wiggle_0 name=track_label'],
                [' '.join(['fixedStep','chrom=chrM','start=11','step=10']),
                 '4.5',
                 '-3.7',
                 ' '.join(['fixedStep','chrom=chrM','start=1013','step=5']),
                 '2.1',
                 '11'],
                '.wig',
                ['e1','wig'],
                WigGenomeElementSource,
                InvalidFormatError)
        
        #Testing: fixedStep with variable span values
        self.exceptionCases['wig_e2'] = \
            ExceptionCase(WigGenomeElementSource,
                 'TestGenome',
                ['track type=wiggle_0 name=track_label'],
                [' '.join(['fixedStep','chrom=chrM','start=11','step=10','span=10']),
                 '4.5',
                 '-3.7',
                 ' '.join(['fixedStep','chrom=chrM','start=1013','step=10','span=5']),
                 '2.1',
                 '11'],
                '.wig',
                ['e2','wig'],
                WigGenomeElementSource,
                InvalidFormatError)
        
        #Testing: step < 1
        self.exceptionCases['wig_e3'] = \
            ExceptionCase(WigGenomeElementSource,
                 'TestGenome',
                ['track type=wiggle_0 name=track_label'],
                [' '.join(['fixedStep','chrom=chrM','start=11','step=-1']),
                 '4.5',
                 '-3.7'],
                '.wig',
                ['e3','wig'],
                WigGenomeElementSource,
                InvalidFormatError)
        
        #Testing: span < 1
        self.exceptionCases['wig_e4'] = \
            ExceptionCase(WigGenomeElementSource,
                 'TestGenome',
                ['track type=wiggle_0 name=track_label'],
                [' '.join(['fixedStep','chrom=chrM','start=11','step=10', 'span=-1']),
                 '4.5',
                 '-3.7'],
                '.wig',
                ['e4','wig'],
                WigGenomeElementSource,
                InvalidFormatError)
        
        #Testing: no chrom
        self.exceptionCases['wig_e4.1'] = \
            ExceptionCase(WigGenomeElementSource,
                 'TestGenome',
                ['track type=wiggle_0 name=track_label'],
                [' '.join(['fixedStep','start=11','step=10']),
                 '4.5',
                 '-3.7'],
                '.wig',
                ['e4.1','wig'],
                WigGenomeElementSource,
                InvalidFormatError)
        
        #Testing: fixedStep with no start or step
        self.exceptionCases['wig_e4.2'] = \
            ExceptionCase(WigGenomeElementSource,
                 'TestGenome',
                ['track type=wiggle_0 name=track_label'],
                [' '.join(['fixedStep','chrom=chrM']),
                 '4.5',
                 '-3.7'],
                '.wig',
                ['e4.2','wig'],
                WigGenomeElementSource,
                InvalidFormatError)
    
        #Testing: variableStep with start and step
        self.exceptionCases['wig_e4.3'] = \
            ExceptionCase(WigGenomeElementSource,
                 'TestGenome',
                ['track type=wiggle_0 name=track_label'],
                [' '.join(['variableStep','chrom=chrM', 'start=10', 'step=10']),
                 '\t'.join(['10','4.5']),
                 '\t'.join(['20','-3.7'])],
                '.wig',
                ['e4.3','wig'],
                WigGenomeElementSource,
                InvalidFormatError)
    
        #Testing: Overlapping bounding regions
        self.exceptionCases['wig_e5'] = \
            ExceptionCase(WigGenomeElementSource,
                 'TestGenome',
                ['track type=wiggle_0 name=track_label'],
                [' '.join(['fixedStep','chrom=chrM','start=11','step=10', 'span=5']),
                 '4.5',
                 '-3.7',
                 ' '.join(['fixedStep','chrom=chrM','start=22','step=10', 'span=5']),
                 '2.5',
                 '1.7'],
                '.wig',
                ['e5','wig'],
                WigGenomeElementSource,
                InvalidFormatError)
        
        #Testing: Bounding regions with no gaps
        self.exceptionCases['wig_e6_hb'] = \
            ExceptionCase(None,
                 'TestGenome',
                ['track type=wiggle_0 name=track_label'],
                [' '.join(['fixedStep','chrom=chrM','start=11','step=10', 'span=5']),
                 '4.5',
                 '-3.7',
                 ' '.join(['fixedStep','chrom=chrM','start=26','step=10', 'span=5']),
                 '2.5',
                 '1.7'],
                '.wig',
                ['e6','wig'],
                HbWigGenomeElementSource,
                InvalidFormatError)
        
        #Testing: variableStep with one column
        self.exceptionCases['wig_e7'] = \
            ExceptionCase(WigGenomeElementSource,
                 'TestGenome',
                ['track type=wiggle_0 name=track_label'],
                [' '.join(['variableStep','chrom=chrM']),
                 '4.5',
                 '-3.7'],
                '.wig',
                ['e7','wig'],
                WigGenomeElementSource,
                InvalidFormatError)
        
        #Testing: fixedStep with two columns
        self.exceptionCases['wig_e8'] = \
            ExceptionCase(WigGenomeElementSource,
                 'TestGenome',
                ['track type=wiggle_0 name=track_label'],
                [' '.join(['fixedStep','chrom=chrM','start=11','step=10', 'span=1']),
                 '\t'.join(['10','4.5']),
                 '\t'.join(['20','-3.7'])],
                '.wig',
                ['e8','wig'],
                WigGenomeElementSource,
                InvalidFormatError)
        
        #Testing: no declaration line
        self.exceptionCases['wig_e9'] = \
            ExceptionCase(WigGenomeElementSource,
                 'TestGenome',
                ['track type=wiggle_0 name=track_label'],
                ['4.5',
                 '-3.7'],
                '.wig',
                ['e9','wig'],
                WigGenomeElementSource,
                InvalidFormatError)
    
    def _getGeSource(self, case, addGEDependentAttributesHolder=True, **kwArgs):
        if case.sourceClass is None:
            sourceClass = GenomeElementSource
            forPreProcessor = True
        else:
            sourceClass = case.sourceClass
            forPreProcessor = False
        
        if addGEDependentAttributesHolder:
            return GEDependentAttributesHolder(sourceClass(case.name, case.genome, printWarnings=False, \
                                               forPreProcessor=forPreProcessor,**kwArgs))
        else:
            return sourceClass(case.name, case.genome, printWarnings=False, \
                               forPreProcessor=forPreProcessor, **kwArgs)
    
    def _testIterator(self, case, geSource):
        self.assertGenomeElementLists([x.getCopy() for x in case.assertElementList], geSource)
                
        boundingRegions = geSource.getBoundingRegionTuples()
        self.assertEqual(len(case.boundingRegionsAssertList), len(boundingRegions))
        
        for i, br in enumerate( boundingRegions ):
            try:
                assertBr = None
                assertBr = copy.copy(case.boundingRegionsAssertList[i])
                self.assertEqual(assertBr.region, br.region)
                self.assertEqual(assertBr.elCount, br.elCount)
                
            except Exception, e:
                print str(case.trackName) + ': ' + str(assertBr) + ' != ' + str(br)
                raise

    def testIterator(self):
        #print 'testIterator turned off'
        #print 'testIterator'
        for case in self.cases.values():
            case.open()
            #print case.trackName
            geSource = self._getGeSource(case)
            for i in range(2):
                self._testIterator(case, geSource)
            case.close()
                
    def _assertException(self, case):
        storedStdOut = sys.stdout
        sys.stdout = open(os.devnull, 'w')
            
        try:
            for ge in self._getGeSource(case):
                pass
                
        except Exception, e:
            #import traceback
            #traceback.print_exc(e)
            #print e
            self.assertEqual(case.exceptionClass, e.__class__)
            sys.stdout = storedStdOut
            return
        finally:
            sys.stdout = storedStdOut
        
        self.fail('Exception of class %s was not raised.' % str(case.exceptionClass.__name__))
    
    def testExceptions(self):
        #print 'testExceptions'
        for case in self.exceptionCases.values():
            case.open()
            #print case.trackName
            self._assertException(case)
            case.close()
        
    def _assertNew(self, case):
        elSource = self._getGeSource(case, addGEDependentAttributesHolder=False)
        self.assertEqual(elSource.__class__, case.targetClass)
        
    def testNew(self):
        #print 'testNew turned off'
        #print 'testNew'
        for case in self.cases.values():
            case.open()
            #print case.trackName
            self._assertNew(case)
            case.close()
            
    def _assertPrefixList(self, case):
        elSource = self._getGeSource(case)
        try:
            self.assertListsOrDicts(case.prefixList, elSource.getPrefixList())
        except Exception, e:
            #import traceback
            #traceback.print_exc(e)
            self.assertEqual(Warning, e.__class__)
        
    def testGetPrefixList(self):
        #print 'testGetPrefixList turned off'
        #print 'testGetPrefixList'
        for case in self.cases.values():
            case.open()
            #print case.trackName
            self._assertPrefixList(case)
            case.close()
        
    def _assertValDataType(self, case):
        elSource = self._getGeSource(case)
        self.assertEqual(case.valDataType, elSource.getValDataType())
            
    def testGetValDataType(self):
        #print 'testGetValDataType turned off'
        #print 'testGetValDataType'
        for case in self.cases.values():
            case.open()
            #print case.trackName
            self._assertValDataType(case)
            case.close()
        
    def _assertValDim(self, case):
        elSource = self._getGeSource(case)
        [el for el in elSource]
        self.assertEqual(case.valDim, elSource.getValDim())
            
    def testGetValDim(self):
        #print 'testGetValDim turned off'
        #print 'testGetValDim'
        for case in self.cases.values():
            case.open()
            #print case.trackName
            self._assertValDim(case)
            case.close()
    
    def _assertEdgeWeightDataType(self, case):
        elSource = self._getGeSource(case)
        self.assertEqual(case.edgeWeightDataType, elSource.getEdgeWeightDataType())
            
    def testGetEdgeWeightDataType(self):
        #print 'testGetEdgeWeightDataType turned off'
        #print 'testGetEdgeWeightDataType'
        for case in self.cases.values():
            case.open()
            #print case.trackName
            self._assertEdgeWeightDataType(case)
            case.close()
    
    def _assertEdgeWeightDim(self, case):
        elSource = self._getGeSource(case)
        [el for el in elSource]
        self.assertEqual(case.edgeWeightDim, elSource.getEdgeWeightDim())
            
    def testGetEdgeWeightDim(self):
        #print 'testGetEdgeWeightDim turned off'
        #print 'testGetEdgeWeightDim'
        for case in self.cases.values():
            case.open()
            #print case.trackName
            self._assertEdgeWeightDim(case)
            case.close()
    
    def runTest(self):
        pass
        #self.testDirtyFlagSortedWigFixedElementSource()
    
if __name__ == "__main__":
#    TestGenomeElementSource().debug()
    unittest.main()         
