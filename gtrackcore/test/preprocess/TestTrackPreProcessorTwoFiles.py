#!/usr/bin/env python
import os
import shutil
import unittest

from gtrackcore.extract.fileformats.GtrackComposer import StdGtrackComposer
from gtrackcore.input.adapters.TrackGenomeElementSource import FullTrackGenomeElementSource
from gtrackcore.preprocess.PreProcessTracksJob import PreProcessAllTracksJob
from gtrackcore.test import get_data_path
from gtrackcore.util.CommonFunctions import createOrigPath


class TestTrackPreProcessorTwoFiles(unittest.TestCase):
    def setUp(self):
        self.genome = 'testgenome'

    def tearDown(self):
        pass

    def _common_setup(self, track_name):
        self.original_dir_path = createOrigPath(self.genome, track_name)
        integration_test_data_dir_path = os.sep.join([get_data_path()] + track_name)

        # ensure directories exists
        if not os.path.exists(self.original_dir_path):
            os.makedirs(self.original_dir_path)
        assert os.path.isdir(integration_test_data_dir_path)
        assert os.path.isdir(self.original_dir_path)

        # copy test files to test data directory
        for file_name in os.listdir(integration_test_data_dir_path):
            full_file_name = os.path.join(integration_test_data_dir_path, file_name)
            if os.path.isfile(full_file_name) and not full_file_name[-1] == '~':
                shutil.copy(full_file_name, self.original_dir_path)

    def test_linked_valued_segments(self):
        track_name = ['integration_test_data', 'test_twofiles', 'linked_valued_segments']
        self._common_setup(track_name)

        PreProcessAllTracksJob(self.genome, track_name).process()

        self.assert_equal_content_before_and_after_preprocessing(track_name, allow_overlaps=True)

    @unittest.skip
    def test_linked_genome_partition(self):
        track_name = ['integration_test_data', 'test_twofiles', 'linked_genome_partition']
        self._common_setup(track_name)

        PreProcessAllTracksJob(self.genome, track_name).process()

        self.assert_equal_content_before_and_after_preprocessing(track_name, allow_overlaps=False)

    def assert_equal_content_before_and_after_preprocessing(self, track_name, allow_overlaps=False):
        before_preprocessing = []
        for file_path in (os.path.join(self.original_dir_path, fn) for fn in os.listdir(self.original_dir_path)):
            for line in open(file_path).readlines():
                if not line.startswith('#') and line != '':
                    before_preprocessing.append(line.rstrip())

        after_preprocessing = []
        track_content = StdGtrackComposer(FullTrackGenomeElementSource(
            self.genome, track_name, allowOverlaps=allow_overlaps)).returnComposed()
        for line in (line.rstrip() for line in track_content.split('\n')):
            if not line.startswith('#') and line != '':
                after_preprocessing.append(line)

        assert set(before_preprocessing) == set(after_preprocessing), \
            '\nBefore preprocessing:\n%s\nis not the same as after preprocessing:\n%s' % \
            ('\n'.join(sorted(before_preprocessing)), '\n'.join(sorted(after_preprocessing)))


if __name__ == "__main__":
    unittest.main()
