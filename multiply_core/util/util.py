from datetime import datetime, timedelta
import numpy as np
import os

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


def get_mime_type(file_name: str):
    if file_name.endswith('.nc'):
        return 'application/x-netcdf'
    elif file_name.endswith('.zip'):
        return 'application/zip'
    elif file_name.endswith('.json'):
        return 'application/json'
    elif os.path.isdir(file_name):
        return 'application/x-directory'
    return 'unknown mime type'
