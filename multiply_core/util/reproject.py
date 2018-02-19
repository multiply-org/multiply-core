import gdal
import osr

__author__ = "José Luis Gómez-Dans (NCEO/UCL)," \
             "Tonio Fincke (Brockmann Consult GmbH)"


class Reproject(object):

    @staticmethod
    def reproject_image(source_img, target_img, dstSRSs=None):
        """Reprojects/Warps an image to fit exactly another image.
        Additionally, you can set the destination SRS if you want
        to or if it isn't defined in the source image."""
        if type(target_img) is str:
            g = gdal.Open(target_img)
        else:
            g = target_img
        if type(source_img) is str:
            s = gdal.Open(source_img)
        else:
            s = source_img
        geo_t = g.GetGeoTransform()
        x_size, y_size = g.RasterXSize, g.RasterYSize
        xmin = min(geo_t[0], geo_t[0] + x_size * geo_t[1])
        xmax = max(geo_t[0], geo_t[0] + x_size * geo_t[1])
        ymin = min(geo_t[3], geo_t[3] + y_size * geo_t[5])
        ymax = max(geo_t[3], geo_t[3] + y_size * geo_t[5])
        xRes, yRes = abs(geo_t[1]), abs(geo_t[5])
        if dstSRSs is None:
            dstSRS = osr.SpatialReference()
            raster_wkt = g.GetProjection()
            dstSRS.ImportFromWkt(raster_wkt)
        else:
            dstSRS = dstSRSs
        g = gdal.Warp('', s, format='MEM', 
                      outputBounds=[xmin, ymin, xmax, ymax], 
                      xRes=xRes, yRes=yRes, dstSRS=dstSRS)
        return g

    # @staticmethod
    # def resample_image_to_resolution(self, image, xRes: float, yRes: float):
    #     """
    #     Reprojects/Warps an image to the given projection.
    #     Additionally, you can set the destination SRS if you want
    #     to or if it isn't defined in the source image.
    #     :return:
    #     """
    #     dataset = gdal.Open(image)
    #     proj = dataset.GetProjection()
    #     geoT = np.array(dataset.GetGeoTransform())
    #     new_geoT = geoT * 1.
    #     new_geoT[1] = xRes
    #     new_geoT[5] = -yRes
    #     dataset = gdal.Warp('', image, format='MEM',
    #                   outputBounds=[xmin, ymin, xmax, ymax], xRes=xRes, yRes=yRes,
    #                   dstSRS=dstSRS)
    #
    #     return proj, new_geoT.tolist()
