import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__))+os.sep+'..')
from multiply_dummy import dummy_platform

class TestCore(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_dummy(self):
        """
        we just check for the time beeing that the import of the
        platform dummy is working ...
        """
        assert True



if __name__ == '__main__':
    unittest.main()
