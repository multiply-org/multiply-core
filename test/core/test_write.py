import gdal
import osr
import multiply_core.util.reproject as reproject
import pytest

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"

S2_FILE = './test/test_data/T32UME_20170910T104021_B10.jp2'
# S2_TIFF_FILE = './test/test_data/T32UME_20170910T104021_B10.tiff'
# LAI_TIFF_FILE = './test/test_data/Priors_lai_125_[50_60N]_[000_010E].tiff'
ALA_TIFF_FILE = './test/test_data/Priors_ala_125_[50_60N]_[000_010E].tiff'
# GLOBAL_VRT_FILE = './test/test_data/Priors_lai_060_global.vrt'