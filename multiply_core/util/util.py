from datetime import datetime, timedelta
import scipy.sparse
import numpy as np
import os
from shapely.geometry import Point, Polygon
from shapely.wkt import loads
from typing import Union

__author__ = "MULTIPLY Team"


class AttributeDict(object):
    """
    A class to convert a nested Dictionary into an object with key-values
    accessibly using attribute notation (AttributeDict.attribute) instead of
    key notation (Dict["key"]). This class recursively sets Dicts to objects,
    allowing you to recurse down nested dicts (like: AttributeDict.attr.attr)
    """
    def __init__(self, **entries):
        self.add_entries(**entries)

    def add_entries(self, **entries):
        for key, value in entries.items():
            if type(value) is dict:
                self.__dict__[key] = AttributeDict(**value)
            else:
                self.__dict__[key] = value

    def has_entry(self, entry: str):
        return self._has_entry(entry, 0)

    def _has_entry(self, entry: str, current_index: int):
        entry_keys = entry.split('.')
        if entry_keys[current_index] in self.__dict__.keys():
            if current_index < len(entry_keys):
                dict_entry = self.__dict__[entry_keys[current_index]]
                if type(dict_entry) is not dict:
                    return False
                return dict_entry._has_entry(entry, current_index + 1)
            return True
        return False

    def __getitem__(self, key):
        """
        Provides dict-style access to attributes
        """
        return getattr(self, key)


class FileRef:
    """
    A reference to the physical location of a file.
    """

    def __init__(self, url: str, start_time: str, end_time: str, mime_type: str):
        self._url = url
        self._start_time = start_time
        self._end_time = end_time
        self._mime_type = mime_type

    @property
    def url(self) -> str:
        """The URL indicating where the file is physically located."""
        return self._url

    @property
    def start_time(self) -> str:
        """The dataset's start time."""
        return self._start_time

    @property
    def end_time(self) -> str:
        """The dataset's end time."""
        return self._end_time

    @property
    def mime_type(self):
        """The mime type of the file in question."""
        return self._mime_type


def compute_distance(lon_0: float, lat_0: float, lon_1: float, lat_1: float, sphere_radius: float) -> float:
    lat_0_rad = np.deg2rad(lat_0)
    lat_1_rad = np.deg2rad(lat_1)
    delta_lon = np.deg2rad(lon_0) - np.deg2rad(lon_1)
    cos_delta_lon = np.cos(delta_lon)
    sin_lat = np.sin(lat_0_rad) * np.sin(lat_1_rad)
    cos_lat = np.cos(lat_0_rad) * np.cos(lat_1_rad)
    distance = sphere_radius * np.arccos(sin_lat + cos_lat * cos_delta_lon)
    return distance


def get_time_from_string(time_string: str, adjust_to_last_day: bool = False) -> datetime:
    # note: This an excerpt of a method in cate_core
    """
    Retrieves a datetime object from a string. If this is not possible, a ValueError is thrown.
    :param time_string: A string in UTC time format
    :param adjust_to_last_day: If true (and if the time string has no information about the number of days of
    the month), the returned datetime will be set to the last day of the month; otherwise to the first.
    :return: A datetime object corresponding to the UTC string that ahs been passed in.
    """
    format_to_timedelta = [("%Y-%m-%dT%H:%M:%S", timedelta(), False),
                           ("%Y-%m-%d %H:%M:%S", timedelta(), False),
                           ("%Y-%m-%d", timedelta(hours=24, seconds=-1), False),
                           ("%Y-%m", timedelta(), True),
                           ("%Y", timedelta(days=365, seconds=-1), False)]
    for f, td, adjust in format_to_timedelta:
        try:
            dt = datetime.strptime(time_string, f)
            if adjust:
                td = timedelta(days=get_days_of_month(dt.year, dt.month), seconds=-1)
            return dt + td if adjust_to_last_day else dt
        except ValueError:
            pass
    raise ValueError('Invalid date/time value: "%s"' % time_string)


def get_time_from_year_and_day_of_year(year: int, day_of_year: int):
    """
    :param year: The year
    :param day_of_year: The day of year. Supposed to start with 1 for January 1st.
    :return: A datetime object reperesenting the year and the day of year
    """
    days_per_months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if is_leap_year(year):
        days_per_months[1] = 29
    accumulated_days = 0
    month = 0
    for i, days_per_month in enumerate(days_per_months):
        month += 1
        if accumulated_days + days_per_month > day_of_year:
            break
        accumulated_days += days_per_month
    day_of_month = day_of_year - accumulated_days
    return datetime(2017, month, day_of_month)


def get_days_of_month(year: int, month: int) -> int:
    """
    Determines the number of days for a given month
    :param year: The year (required to determine whether it is a leap year)
    :param month: The month
    :return: The number of days of this month
    """
    if month < 1 or month > 12:
        raise ValueError('Invalid month: %', month)
    if month in [1, 3, 5, 7, 8, 10, 12]:
        return 31
    if month in [4, 6, 9, 11]:
        return 30
    if is_leap_year(year):
        return 29
    return 28


def is_leap_year(year: int) -> bool:
    """
    Determines whether a year is a leap year.
    :param year: The year.
    :return: True, when the given year is a leap year
    """
    if year % 4 > 0:
        return False
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    return True


def are_times_equal(time_1: Union[str, datetime], time_2: Union[str, datetime]):
    if type(time_1) == str:
        time_1 = get_time_from_string(time_1)
    if type(time_2) == str:
        time_2 = get_time_from_string(time_2)
    return time_1 == time_2


def get_mime_type(file_name: str):
    if file_name.endswith('.nc'):
        return 'application/x-netcdf'
    elif file_name.endswith('.zip'):
        return 'application/zip'
    elif file_name.endswith('.json'):
        return 'application/json'
    elif file_name.endswith('.hdf'):
        return 'application/x-hdf'
    elif file_name.endswith('.pkl'):
        return 'application/octet-stream'
    elif file_name.endswith('tiff') or file_name.endswith('tif'):
        return 'image/tiff'
    elif file_name.endswith('.vrt'):
        return 'x-world/x-vrt'
    elif os.path.isdir(file_name):
        return 'application/x-directory'
    return 'unknown mime type'


def are_polygons_almost_equal(polygon_1: Union[str, Polygon], polygon_2: Union[str, Polygon]):
    if type(polygon_2) == str:
        polygon_2 = loads(polygon_2)
    if type(polygon_1 == str):
        polygon_1 = loads(polygon_1)
    if polygon_1.almost_equals(polygon_2):
        return True
    x_list, y_list = polygon_1.exterior.coords.xy
    reversed_points = []
    for i in range(len(x_list) - 1, -1, -1):
        reversed_points.append(Point(x_list[i], y_list[i]))
    reversed_polygon = Polygon([[p.x, p.y] for p in reversed_points])
    return reversed_polygon.almost_equals(polygon_2)


def block_diag(matrices, format: str=None, dtype: type=None) -> scipy.sparse.coo.coo_matrix:
    """
    Build a block diagonal sparse matrix from provided matrices.
    This is a faster version for equally-sized blocks. Currently, open PR on scipy's github
    (https://github.com/scipy/scipy/pull/5619)

    Parameters
    ----------
    mats : sequence of matrices
        Input matrices. Can be any combination of lists, numpy.array,
         numpy.matrix or sparse matrix ("csr', 'coo"...)
    format : str, optional
        The sparse format of the result (e.g. "csr").  If not given, the matrix
        is returned in "coo" format.
    dtype : dtype specifier, optional
        The data-type of the output matrix.  If not given, the dtype is
        determined from that of `blocks`.

    Returns
    -------
    res : sparse matrix

    Notes
    -----
    Providing a sequence of equally shaped matrices
     will provide marginally faster results

    .. versionadded:: 0.18.0

    See Also
    --------
    bmat, diags, block_diag

    Examples
    --------
    >>> from scipy.sparse import coo_matrix, block_diag
    >>> A = coo_matrix([[1, 2], [3, 4]])
    >>> B = coo_matrix([[5, 6], [7, 8]])
    >>> C = coo_matrix([[9, 10], [11,12]])
    >>> block_diag((A, B, C)).toarray()
    array([[ 1,  2,  0,  0,  0,  0],
           [ 3,  4,  0,  0,  0,  0],
           [ 0,  0,  5,  6,  0,  0],
           [ 0,  0,  7,  8,  0,  0],
           [ 0,  0,  0,  0,  9, 10],
           [ 0,  0,  0,  0, 11, 12]])
    """
    from scipy.sparse.coo import coo_matrix
    from scipy.sparse import issparse

    num_matrices = len(matrices)
    mats_ = [None] * num_matrices
    for ia, a in enumerate(matrices):
        if hasattr(a, 'shape'):
            mats_[ia] = a
        else:
            mats_[ia] = coo_matrix(a)

    if any(mat.shape != mats_[-1].shape for mat in mats_) or (any(issparse(mat) for mat in mats_)):
        data = []
        col = []
        row = []
        origin = np.array([0, 0], dtype=np.int)
        for mat in mats_:
            if issparse(mat):
                data.append(mat.data)
                row.append(mat.row + origin[0])
                col.append(mat.col + origin[1])

            else:
                data.append(mat.ravel())
                row_, col_ = np.indices(mat.shape)
                row.append(row_.ravel() + origin[0])
                col.append(col_.ravel() + origin[1])

            origin += mat.shape

        data = np.hstack(data)
        col = np.hstack(col)
        row = np.hstack(row)
        total_shape = origin
    else:
        shape = mats_[0].shape
        data = np.array(mats_, dtype).ravel()
        row_, col_ = np.indices(shape)
        row = (np.tile(row_.ravel(), num_matrices) +
               np.arange(num_matrices).repeat(shape[0] * shape[1]) * shape[0]).ravel()
        col = (np.tile(col_.ravel(), num_matrices) +
               np.arange(num_matrices).repeat(shape[0] * shape[1]) * shape[1]).ravel()
        total_shape = (shape[0] * num_matrices, shape[1] * num_matrices)

    return coo_matrix((data, (row, col)), shape=total_shape).asformat(format)
