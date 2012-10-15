import random

import numpy as np

from track5 import Track5
from track5_test import Track5Test


class CoreTest(Track5Test):
        
    def test_empty_track(self):
        track = self.get_test_track()   
        self.assertEquals(5, len(list(track.h5)))
        self.assertFalse(len(track.h5.getNode(Track5.ROOT + Track5.NODES)))
        self.assertFalse(len(track.h5.getNode(Track5.ROOT + Track5.LINKS)))
        self.assertTrue(track.is_valid_track5(track.h5))
        self.assertTrue(track._is_sealed())
        track.close()
        
    def test_paths_of_sealing(self):
        track = self.get_test_track()
        self.assertTrue(track._is_sealed())
        track.unseal()
        self.assertFalse(track._is_sealed())
        track.seal()
        self.assertRaises(ValueError, track.seal)
        self.assertTrue(track._is_sealed())
        track.unseal()
        self.assertRaises(ValueError, track.unseal)
        self.assertFalse(track._is_sealed())
        track.close()
        
    def test_sealed_default(self):
        t1 = self.get_test_track()  
        fn = t1.h5.filename
        t1.close()
        t2 = Track5(fn)
        self.assertFalse(t2._is_writeable())
        self.assertTrue(t2._is_sealed())
        self.assertRaises(ValueError, t2.add_nodes, [])
        self.assertRaises(ValueError, t2.add_links, [])
        t2.close()
        
    def test_leniter(self):
        t = self.get_test_track()
        self.assertEquals(0, len(t))
        self.assertEquals([], list(t))
        t.unseal()
        self.assertRaises(ValueError, len, t)
        self.assertRaises(ValueError, list, t)
        t.close()
        
    def test_add_earray(self):
        t = self.get_test_track()
        self.assertRaises(ValueError, t.add_node_values, "dummy")
        self.assertRaises(ValueError, t.add_link_values, "dummy")
        t.unseal()
        arr = t.add_node_values("test")
        arr.append([1.,2.])
        arr.append((3.,4.))
        arr.append(np.array([5.,6.]))
        self.assertEquals(6, arr.nrows)
        self.assertRaises(ValueError, t.seal)
        ar2 = t.add_link_values("test")
        ar2.append([1.])
        ar2.append([2.])
        self.assertEquals(2, ar2.nrows)
        # needed to close
        t.add_nodes(6 * [(1,2,3)])        
        self.assertRaises(ValueError, t.seal)
        t.add_links(2 * [(1, 2)])
        t.close()
        
    
    
    def xtest_append(self):
        track = self.get_test_track()
        # list
        nodes = [tuple(i) for i in np.random.randint(900000000, 1000000000, size=30).reshape((10,3))]
        track.add_nodes(nodes)
        self.assertEquals(10, len(track))
        b = tuple(list(track)[0])[1:]
        a = nodes[0][1:]
        self.assertEquals(a, b)
        
        a = np.ndarray(shape=(10,), dtype=[("seqid","uint8"),("start", "uint32"), ("stop", "uint32")])
        for i in xrange(len(a)):
            a[i][0] = random.randint(0,255)
            a[i][1] = random.randint(900000000, 1000000000)
            a[i][2] = random.randint(900000000, 1000000000)

        track.add_nodes(a)
        self.assertEquals(20, len(track))
        t19 = list(track)[19]
        self.assertEquals(tuple(int(i) for i in t19), tuple(int(i) for i in a[9]))
        track.close()
        
        
        
        
if __name__ == "__main__":
    import unittest
    unittest.main()