import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__))+os.sep+'..')
from multiply_dummy import dummy_platform
import pip

def test_dummy():
    print(sys.path)
    installed_packages = pip.get_installed_distributions()
    installed_packages_list = sorted(["%s==%s" % (i.key, i.version)
                                      for i in installed_packages])
    print(installed_packages_list)
    # """
    # we simply run the platform dummy
    # """
    dummy_platform
