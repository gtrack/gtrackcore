from track5.io import load_bedgraph
from track5_test import Track5Test


class IoTest(Track5Test):
        
    def test_bedgraph(self):
        track = load_bedgraph("../data/chrY_coverage.bedgraph")
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