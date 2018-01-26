import gdal
import numpy as np
import os
import osr

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"

S2_FILE = './test/test_data/T32UME_20170910T104021_B10.jp2'
S2_TIFF_FILE = './test/test_data/T32UME_20170910T104021_B10.tiff'
LAI_TIFF_FILE = './test/test_data/Priors_lai_125_[50_60N]_[000_010E].tiff'
ALA_TIFF_FILE = './test/test_data/Priors_ala_125_[50_60N]_[000_010E].tiff'
GLOBAL_VRT_FILE = './test/test_data/Priors_lai_060_global.vrt'


def test_resample_image_to_resolution():
    xRes = 60.
    yRes = 10.
    vrt_dataset = gdal.Open(GLOBAL_VRT_FILE)
    s2_dataset = gdal.Open(S2_FILE)
    s2_projection = s2_dataset.GetProjection()
    s2_transform = s2_dataset.GetGeoTransform()

    x_size, y_size = s2_dataset.RasterXSize, s2_dataset.RasterYSize
    xmin = min(s2_transform[0], s2_transform[0] + x_size * s2_transform[1])
    xmax = max(s2_transform[0], s2_transform[0] + x_size * s2_transform[1])
    ymin = min(s2_transform[3], s2_transform[3] + y_size * s2_transform[5])
    ymax = max(s2_transform[3], s2_transform[3] + y_size * s2_transform[5])

    srs = osr.SpatialReference()
    srs.ImportFromWkt(s2_projection)
    reprojected_tiff = gdal.Warp('', vrt_dataset,
                                 format='Mem',
                                 outputBounds=[xmin, ymin, xmax, ymax],
                                 xRes=xRes, yRes=yRes, dstSRS=srs)
    reprojected_projection = reprojected_tiff.GetProjection()
    reprojected_transform = reprojected_tiff.GetGeoTransform()
    raster_width = reprojected_tiff.RasterXSize
    raster_height = reprojected_tiff.RasterYSize
    reprojected_tiff_data = reprojected_tiff.GetRasterBand(1).ReadAsArray()

    driver = gdal.GetDriverByName('GTiff')
    s2_file = driver.Create(S2_TIFF_FILE, raster_width, raster_height, 1, gdal.GDT_Float32,
                            ['COMPRESS=DEFLATE', 'BIGTIFF=YES', 'PREDICTOR=1', 'TILED=YES'])
    s2_file.SetProjection(reprojected_projection)
    s2_file.SetGeoTransform(reprojected_transform)

# def

    tile_width = 256
    tile_height = 256
    for y in range(0, raster_height, tile_height):
        y_end = min(y + tile_height, raster_height)
        for x in range(0, raster_width, tile_width):
            x_end = min(x + tile_height, raster_width)
            s2_file.GetRasterBand(1).WriteArray(reprojected_tiff_data[y:y_end, x:x_end], xoff=x, yoff=y)
