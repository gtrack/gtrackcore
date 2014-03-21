import os
import tempfile
import unittest

from gtrackcore_memmap.prototype.core import gtrackcore, GENOMES
from gtrackcore_memmap.test import get_data_output_path

class gtrackcoreTest(unittest.TestCase):

    def get_fn(self):
        #fd, fn = tempfile.mkstemp()
        #os.close(fd)
        
        trackfn = os.path.join(get_data_output_path(), 'test_core_track')
        return trackfn
    
    def get_track(self):
        fn = self.get_fn()
        track = gtrackcore.empty_track(fn, GENOMES["HG19"])
        return track