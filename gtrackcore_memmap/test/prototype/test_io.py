import os

import gtrackcore_memmap.test

from gtrackcore_memmap.prototype.io import load_bedgraph
from gtrackcore_memmap.test import get_data_path, get_data_output_path
from gtrackcore_memmap.test.prototype.common import gtrackcoreTest

class IoTest(gtrackcoreTest):
        
    def test_bedgraph(self):
        bedgraph_fn = os.path.join(get_data_path(), "chrY_coverage.bedgraph")
        trackfn = os.path.join(get_data_output_path(), "test_io_track")
        
        track = load_bedgraph(bedgraph_fn, trackfn=trackfn)
        self.assertEquals(len(track), 60)
        first =  tuple(track[0])
        self.assertEquals(first, (24, 0L, 1000000L))
        last = tuple(track[-1])
        self.assertEquals(last, (24, 59000000, 59373566))
        self.assertRaises(KeyError, track.get_node_values, "datax")
        data = track.get_node_values("data")
        self.assertEquals(len(data), 60)
        self.assertTrue(data.shape == (60,))
        track.close()
        
if __name__ == "__main__":
    import unittest
    unittest.main()
