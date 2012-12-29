import os
import tempfile
import unittest

from prototype.core import Track5, GENOMES

class Track5Test(unittest.TestCase):

    def get_fn(self):
        fd, fn = tempfile.mkstemp()
        os.close(fd)
        return fn
    
    def get_test_track(self):
        fn = self.get_fn()
        track = Track5.empty_track(fn, GENOMES["HG19"])
        return track
