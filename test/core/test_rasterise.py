import sys
import os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from multiply_core.util.rasterise import rasterise_vector

RASTER_FILE="./test/test_data/T32UME_20170910T104021_B10.jp2"
VECTOR_FILE="./test/test_data/ne_50m_admin_0_countries.shp"

def test_rasterise_germany():
    the_mask = rasterise_vector(RASTER_FILE, VECTOR_FILE, "NAME='Germany'")
    nnz_pxls = the_mask.sum()
    assert nnz_pxls == 1969409


