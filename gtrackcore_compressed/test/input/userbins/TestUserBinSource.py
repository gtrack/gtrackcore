import unittest

from gtrackcore_compressed.input.userbins.UserBinSource import UserBinSource

class TestUserBinSource(unittest.TestCase):
    def setUp(self):
        pass
    
    def testUserBinSource(self):
        bins = [bin for bin in UserBinSource('*','*', genome='TestGenome')]
        self.assertEqual(2, len(bins))
        self.assertEqual('chr21:1-46944323', str(bins[0]))

    def runTest(self):
        self.testUserBinSource()
    
if __name__ == "__main__":
    #TestUserBinSource().debug()
    unittest.main()