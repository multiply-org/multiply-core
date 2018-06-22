import gdal
import numpy as np
import osr
from typing import Optional, Sequence, Union

__author__ = "José Luis Gómez-Dans (University College London)," \
             "Tonio Fincke (Brockmann Consult GmbH)"


def transform_coordinates(source: osr.SpatialReference, target: osr.SpatialReference,
                          coords: Sequence[float]) -> Sequence[float]:
    """
    Returns coordinates in a target reference system that have been transformed from coordinates
    in the source reference system.
    :param source: The source spatial reference system
    :param target: The target spatial reference system
    :param coords: The coordinates to be transformed. Coordinates are expected in a sequence
    [x1, y1, x2, y2, ..., xn, yn].
    :return: The transformed coordinates. Will be in a sequence [x1, y1, x2, y2, ..., xn, yn],
    as the source coordinates.
    """
    num_coords = int(len(coords) / 2)
    target_coords = []
    coordinate_transformation = osr.CoordinateTransformation(source, target)
    for i in range(num_coords):
        target_coord = coordinate_transformation.TransformPoint(coords[i * 2], coords[i * 2 + 1])
        target_coords.append(target_coord[0])
        target_coords.append(target_coord[1])
    return target_coords


def get_spatial_reference_system_from_dataset(dataset: gdal.Dataset) -> osr.SpatialReference:
    """
    Returns the spatial reference system of a dataset
    :param dataset: A dataset
    :return: The spatial reference system of the dataset
    """
    projection = dataset.GetProjection()
    srs = osr.SpatialReference()
    srs.ImportFromWkt(projection)
    return srs


def get_target_resolutions(dataset: gdal.Dataset) -> (float, float):
    """
    Returns the resolution parameters of the geographic transform used by this dataset.
    :param dataset: A dataset
    :return: The resolution parameters of the dataset. The first value refers to the x-axis,
    the second one to the y-axis.
    """
    geo_transform = dataset.GetGeoTransform()
    return geo_transform[1], -geo_transform[5]


def reproject_dataset(dataset: Union[str, gdal.Dataset], bounds: Sequence[float], x_res: int, y_res: int,
                      destination_srs: osr.SpatialReference, bounds_srs: Optional[osr.SpatialReference],
                      resampling_mode: Optional[str]) -> gdal.Dataset:
    """
    Reprojects a gdal dataset to a reference system with the given bounds and the given spatial resolution.
    :param dataset: A dataset
    :param bounds: A 1-d float array specifying the bounds of the resulting dataset. Must consist of the following
    four float values: xmin, ymin, xmax, ymax.
    :param x_res: The resolution the resulting dataset shall have in x-direction. Must be set in accordance to
    destination_srs.
    :param y_res: The resolution the resulting dataset shall have in y-direction. Must be set in accordance to
    destination_srs.
    :param destination_srs: The spatial reference system that the resulting data set shall show.
    :param bounds_srs: The spatial reference system in which the bounds are specified. If not given, it is assumed
    that the bounds are given in the destination_srs.
    :param resampling_mode: The mode by which the values from the source dataset shall be combined to values in the
    target dataset. Available modes are:
    * near (Nearest Neighbour)
    * bilinear
    * cubic
    * cubicspline
    * lanczos
    * average
    * mode
    * max
    * min
    * med
    * q1
    * q3
    If none is selected, 'bilinear' will be selected in case the source values need to be sampled up to a finer
    destination resolution and 'average' in case the values need to be sampled down to a coarser destination resolution.
    :return: A spatial dataset with the chosen destination spatial reference system, in the bounds and the x- and y-
    resolutions that have been set.
    """
    if type(dataset) is str:
        dataset = gdal.Open(dataset)
    if bounds_srs is None:
        bounds_srs = destination_srs
    if resampling_mode is None:
        resampling_mode = _get_resampling(dataset, bounds, x_res, y_res, bounds_srs, destination_srs)
    warp_options = gdal.WarpOptions(format='Mem', outputBounds=bounds, outputBoundsSRS=bounds_srs,
                                    xRes=x_res, yRes=y_res, dstSRS=destination_srs, resampleAlg=resampling_mode)
    reprojected_data_set = gdal.Warp('', dataset, options=warp_options)
    return reprojected_data_set


def _get_resampling(dataset: gdal.Dataset, bounds: Sequence[float], x_res: float, y_res: float,
                    bounds_srs: osr.SpatialReference, destination_srs: osr.SpatialReference) -> str:
    if _need_to_sample_up(dataset, bounds, x_res, y_res, bounds_srs, destination_srs):
        return 'bilinear'
    else:
        return 'average'


def _need_to_sample_up(dataset: gdal.Dataset, bounds: Sequence[float], x_res: float, y_res: float,
                       bounds_srs: osr.SpatialReference, destination_srs: osr.SpatialReference) -> bool:
    source_srs = get_spatial_reference_system_from_dataset(dataset)
    bounds_in_source_coordinates = transform_coordinates(bounds_srs, source_srs, bounds)
    source_resolutions = get_target_resolutions(dataset)
    source_resolution_measure = _get_dist_measure(bounds_in_source_coordinates,
                                                  source_resolutions[0], source_resolutions[1])
    bounds_in_dest_coordinates = transform_coordinates(bounds_srs, destination_srs, bounds)
    dest_resolution_measure = _get_dist_measure(bounds_in_dest_coordinates, x_res, y_res)
    return dest_resolution_measure > source_resolution_measure


def _get_dist_measure(source_coordinates: Sequence[float], x_res: float, y_res: float):
    x_dist = np.sqrt(np.square(source_coordinates[0] - source_coordinates[2]))
    y_dist = np.sqrt(np.square(source_coordinates[1] - source_coordinates[3]))
    return (x_dist / x_res) * (y_dist / y_res)


class Reprojection(object):

    def __init__(self, bounds: Sequence[float], x_res: int, y_res: int, destination_srs: osr.SpatialReference,
                 bounds_srs: Optional[osr.SpatialReference]=None, resampling_mode: Optional[str]=None):
        self._bounds = bounds
        self._x_res = x_res
        self._y_res = y_res
        self._destination_srs = destination_srs
        self._resampling_mode = resampling_mode
        if bounds_srs is None:
            self._bounds_srs = destination_srs
        else:
            self._bounds_srs = bounds_srs

    def reproject(self, dataset: Union[str, gdal.Dataset]) -> gdal.Dataset:
        if type(dataset) is str:
            dataset = gdal.Open(dataset)
        if self._resampling_mode is None:
            resampling_mode = _get_resampling(dataset, self._bounds, self._x_res, self._y_res, self._bounds_srs,
                                              self._destination_srs)
        else:
            resampling_mode = self._resampling_mode
        warp_options = gdal.WarpOptions(format='Mem', outputBounds=self._bounds, outputBoundsSRS=self._bounds_srs,
                                        xRes=self._x_res, yRes=self._y_res, dstSRS=self._destination_srs,
                                        resampleAlg=resampling_mode)
        reprojected_data_set = gdal.Warp('', dataset, options=warp_options)
        return reprojected_data_set


def reproject_image(source_img, target_img, dstSRSs=None):
    # TODO: replace this method with the other functionality in this module
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
    g = gdal.Warp('', s, format='MEM', outputBounds=[xmin, ymin, xmax, ymax], xRes=xRes, yRes=yRes, dstSRS=dstSRS)
    return g
