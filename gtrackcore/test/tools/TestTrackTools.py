import sys
import os
import unittest
import itertools

from gtrackcore.core.LogSetup import logMessage
from gtrackcore.preprocess.PreProcessTracksJob import PreProcessAllTracksJob
from gtrackcore.tools.TrackTools import coverage, overlap, overlap_iter, count_elements, \
    count_elements_in_all_bounding_regions, sum_of_values, sum_of_weights, sum_of_weights_iter
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.util.CommonFunctions import createOrigPath


class MockPrint(object):
    def write(self, s):
        pass


class TestTrackTools(unittest.TestCase):
    def setUp(self):
        sys.stdout = MockPrint()  # prevents a lot of annoying print messages
        for track_data in all_test_track_data.values():
            self._write_original_file(track_data)
            try:
                PreProcessAllTracksJob(track_data['genome'], track_data['track_name']).process()
            except Exception:
                logMessage('Could not preprocess %s (%s)' % (':'.join(track_data['track_name']), track_data['genome']))
        sys.stdout = sys.__stdout__

    def tearDown(self):
        pass

    def _write_original_file(self, track_data):
        dir_path = createOrigPath(track_data['genome'], track_data['track_name'])
        filename = dir_path + os.sep + 'file.gtrack'
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
        with open(filename, mode='w') as f:
            for line in itertools.chain(track_data['headers'], track_data['data']):
                f.write(line + '\n')

    def test_overlap(self):
        track_data1 = all_test_track_data['segment1']
        track_data2 = all_test_track_data['segment2']
        result = overlap(track_data1['track_name'], False,
                         track_data2['track_name'], False, track_data1['genome_regions'])

        self.assertEqual(result, 200, msg='overlap result was %d, but should be %d for track %s and %s' %
                                          (result, 200, ':'.join(track_data1['track_name']),
                                           ':'.join(track_data2['track_name'])))

    def test_overlap_with_iterator(self):
        track_data1 = all_test_track_data['segment1']
        track_data2 = all_test_track_data['segment2']
        result = overlap_iter(track_data1['track_name'], False,
                              track_data2['track_name'], False, track_data1['genome_regions'])

        self.assertEqual(result, 200, msg='overlap_iter result was %d, but should be %d for track %s and %s' %
                                          (result, 200, ':'.join(track_data1['track_name']),
                                           ':'.join(track_data2['track_name'])))

    def test_coverage(self):
        track_data = all_test_track_data['segment1']
        result = coverage(track_data['track_name'], False, track_data['genome_regions'])

        self.assertEqual(result, 250, msg='coverage result was %d, but should be %d for track %s' %
                                          (result, 250, ':'.join(track_data['track_name'])))

    def test_count_elements(self):
        track_data = all_test_track_data['genome_partition1']
        result = count_elements(track_data['track_name'], False, track_data['genome_regions'])

        self.assertEqual(result, 5, msg='element count result was %d, but should be %d for track %s' %
                                        (result, 5, ':'.join(track_data['track_name'])))

    def test_count_elements_in_all_bounding_regions(self):
        track_data = all_test_track_data['genome_partition1']
        result = count_elements_in_all_bounding_regions(track_data['genome'], track_data['track_name'], False)

        self.assertEqual(result, 5, msg='element count in all bounding regions result was %d, but should be %d '
                                        'for track %s' % (result, 5, ':'.join(track_data['track_name'])))

    def test_sum_of_values(self):
        track_data = all_test_track_data['function1']
        result = sum_of_values(track_data['track_name'], False, track_data['genome_regions'])

        self.assertAlmostEqual(result, 18.0, msg='sum of values result was %f, but should be %f for track %s' %
                                                 (result, 18.0, ':'.join(track_data['track_name'])), places=2)

        track_data = all_test_track_data['valued_segment1']
        result = sum_of_values(track_data['track_name'], True, track_data['genome_regions'])

        self.assertAlmostEqual(result, 400.4, msg='sum of values result was %f, but should be %f for track %s' %
                                                  (result, 400.4, ':'.join(track_data['track_name'])), places=2)

    def test_sum_of_weights(self):
        track_data = all_test_track_data['linked_segments1']
        result = sum_of_weights(track_data['track_name'], True, track_data['genome_regions'])

        self.assertAlmostEqual(result, 6.6, msg='sum of values result was %f, but should be %f for track %s' %
                                                (result, 6.6, ':'.join(track_data['track_name'])), places=2)

    @unittest.skip(reason='Edge iterator in GraphView uses TrackElement and not PytablesTrackElement '
                          'which causes this test to fail with index out of bounds')
    def test_sum_of_weights_with_iterator(self):
        track_data = all_test_track_data['linked_segments1']
        result = sum_of_weights_iter(track_data['track_name'], True, track_data['genome_regions'])

        self.assertAlmostEqual(result, 6.6, msg='sum of values result was %f, but should be %f for track %s' %
                                                (result, 6.6, ':'.join(track_data['track_name'])), places=2)

all_test_track_data = {
    'segment1': {
        'genome': 'testgenome',
        'track_name': ['integration_test_data', 'tools', 'segment1'],
        'headers': [
            '##track type: segments',
            '\t'.join(['###seqid', 'start', 'end']),
        ],
        'data': [
            '\t'.join(map(str, ['chr21', 100, 200])),
            '\t'.join(map(str, ['chr21', 150, 250])),
            '\t'.join(map(str, ['chr21', 200, 250])),
            '\t'.join(map(str, ['chrM', 100, 200])),
        ],
        'genome_regions': [
            GenomeRegion('testgenome', 'chr21', 0, 46944323),
            GenomeRegion('testgenome', 'chrM', 0, 16571),
        ]
    },
    'segment2': {
        'genome': 'testgenome',
        'track_name': ['integration_test_data', 'tools', 'segment2'],
        'headers': [
            '##track type: segments',
            '\t'.join(['###seqid', 'start', 'end']),
        ],
        'data': [
            '\t'.join(map(str, ['chr21', 150, 250])),
            '\t'.join(map(str, ['chrM', 0, 200])),
        ],
        'genome_regions': [
            GenomeRegion('testgenome', 'chr21', 0, 46944323),
            GenomeRegion('testgenome', 'chrM', 0, 16571),
        ]
    },
    'valued_segment1': {
        'genome': 'testgenome',
        'track_name': ['integration_test_data', 'tools', 'valued_segment1'],
        'headers': [
            '##track type: valued segments',
            '\t'.join(['###seqid', 'start', 'end', 'value']),
        ],
        'data': [
            '\t'.join(map(str, ['chr21', 100, 200, 100.1])),
            '\t'.join(map(str, ['chr21', 110, 200, 100.1])),
            '\t'.join(map(str, ['chr21', 120, 200, 100.1])),
            '\t'.join(map(str, ['chrM', 100, 200, 100.1])),
        ],
        'genome_regions': [
            GenomeRegion('testgenome', 'chr21', 0, 46944323),
            GenomeRegion('testgenome', 'chrM', 0, 16571),
        ]
    },
    'linked_segments1': {
        'genome': 'testgenome',
        'track_name': ['integration_test_data', 'tools', 'linked_segments1'],
        'headers': [
            '##track type: linked segments',
            '##edge weight type: number',
            '##edge weight dimension: scalar',
            '##edge weights: true',
            '\t'.join(['###seqid', 'start', 'end', 'id', 'edges']),
        ],
        'data': [
            '\t'.join(map(str, ['chr21', 100, 200, 'a', 'b=1.1'])),
            '\t'.join(map(str, ['chr21', 150, 250, 'b', 'a=1.1;c=1.1'])),
            '\t'.join(map(str, ['chr21', 200, 250, 'c', 'a=1.1;d=1.1'])),
            '\t'.join(map(str, ['chrM', 100, 200, 'd', 'c=1.1'])),
        ],
        'genome_regions': [
            GenomeRegion('testgenome', 'chr21', 0, 46944323),
            GenomeRegion('testgenome', 'chrM', 0, 16571),
        ]
    },
    'genome_partition1': {
        'genome': 'testgenome',
        'track_name': ['integration_test_data', 'tools', 'genome_partition1'],
        'headers': [
            '##track type: genome partition',
            '\t'.join(['###end']),
        ],
        'data': [
            '####seqid=chr21; start=0;  end=1000',
            '\t'.join(map(str, [250])),
            '\t'.join(map(str, [500])),
            '\t'.join(map(str, [750])),
            '\t'.join(map(str, [1000])),
            '####seqid=chrM; start=0;  end=200',
            '\t'.join(map(str, [200])),
        ],
        'genome_regions': [
            GenomeRegion('testgenome', 'chr21', 0, 1000),
            GenomeRegion('testgenome', 'chrM', 0, 200),
        ]
    },
    'function1': {
        'genome': 'testgenome',
        'track_name': ['integration_test_data', 'tools', 'function1'],
        'headers': [
            '##track type: function',
            '\t'.join(['###value']),
        ],
        'data': [
            '####genome=testgenome; seqid=chr21; start=0; end=5',
            '\t'.join(map(str, [1.0])),
            '\t'.join(map(str, [2.0])),
            '\t'.join(map(str, [3.0])),
            '\t'.join(map(str, [4.0])),
            '\t'.join(map(str, [5.0])),
            '####genome=testgenome; seqid=chrM; start=0; end=2',
            '\t'.join(map(str, [1.0])),
            '\t'.join(map(str, [2.0])),
        ],
        'genome_regions': [
            GenomeRegion('testgenome', 'chr21', 0, 5),
            GenomeRegion('testgenome', 'chrM', 0, 2),
        ]
    },
}


if __name__ == "__main__":
    unittest.main()
