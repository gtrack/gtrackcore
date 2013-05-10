import os
import tempfile
import unittest

from track5.prototype.core import Track5, GENOMES
from track5.test import get_data_output_path

class Track5Test(unittest.TestCase):

    def get_fn(self):
        #fd, fn = tempfile.mkstemp()
        #os.close(fd)
        
        trackfn = os.path.join(get_data_output_path(), 'test_core_track')
        return trackfn
    
    def get_track(self):
        fn = self.get_fn()
        track = Track5.empty_track(fn, GENOMES["HG19"])
        return track