import gdal

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"


def write_gdal_raster(dataset: gdal.Dataset, output_file_name: str):
    raster_width = dataset.RasterXSize
    raster_height = dataset.RasterYSize
    driver = gdal.GetDriverByName('GTiff')
    s2_file = driver.Create(output_file_name, raster_width, raster_height, 1, gdal.GDT_Float32,
                            ['COMPRESS=DEFLATE', 'BIGTIFF=YES', 'PREDICTOR=1', 'TILED=YES'])
    tiff_data = dataset.GetRasterBand(1).ReadAsArray()
    projection = dataset.GetProjection()
    transform = dataset.GetGeoTransform()
    s2_file.SetProjection(projection)
    s2_file.SetGeoTransform(transform)
    tile_width = 256
    tile_height = 256
    for y in range(0, raster_height, tile_height):
        y_end = min(y + tile_height, raster_height)
        for x in range(0, raster_width, tile_width):
            x_end = min(x + tile_height, raster_width)
            s2_file.GetRasterBand(1).WriteArray(tiff_data[y:y_end, x:x_end], xoff=x, yoff=y)