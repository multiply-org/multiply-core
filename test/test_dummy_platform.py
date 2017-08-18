import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__))+os.sep+'..')
from multiply_dummy import dummy_platform

def test_dummy():
    # """
    # we simply run the platform dummy
    # """
    dummy_platform
