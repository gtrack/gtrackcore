#!/usr/bin/env python
import os
import unittest

from gtrackcore.core.Config import Config
from gtrackcore.extract.fileformats.GtrackComposer import StdGtrackComposer
from gtrackcore.input.adapters.TrackGenomeElementSource import FullTrackGenomeElementSource
from gtrackcore.preprocess.PreProcessTracksJob import PreProcessAllTracksJob
from gtrackcore.util.CommonFunctions import get_dir_path


class TestTrackPreProcessorTwoFiles(unittest.TestCase):
    def setUp(self):
        self.genome = 'testgenome'
        self.track_name = ['integration_test_data', 'test_twofiles']
        self.dir_path = get_dir_path(self.genome, self.track_name, base_path=Config.ORIG_DATA_PATH)

    def tearDown(self):
        pass

    @unittest.skip
    def test_preprocessor_with_two_files(self):
        assert os.path.exists(self.dir_path)

        from gtrackcore.metadata.TrackInfo import TrackInfo
        TrackInfo(self.genome, self.track_name).resetTimeOfPreProcessing()

        PreProcessAllTracksJob(self.genome, self.track_name).process()

        before_preprocessing = []
        for filename in (os.path.join(self.dir_path, fn) for fn in os.listdir(self.dir_path)):
            for line in open(filename).readlines():
                if not line.startswith('#'):
                    before_preprocessing.append(line.rstrip())

        after_preprocessing = [line.rstrip() for line in StdGtrackComposer(FullTrackGenomeElementSource(
                               self.genome, self.track_name, allowOverlaps=True)).returnComposed().split('\n')
                               if not line.startswith('#') and line != '']

        assert set(before_preprocessing) == set(after_preprocessing), \
            '\nBefore preprocessing:\n%s\nis not the same as after preprocessing:\n%s' % \
            ('\n'.join(sorted(before_preprocessing)), '\n'.join(sorted(after_preprocessing)))


if __name__ == "__main__":
    unittest.main()
