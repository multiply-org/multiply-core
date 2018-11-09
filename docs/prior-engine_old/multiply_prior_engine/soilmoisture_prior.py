#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Soil Priors for Prior Engine in MULTIPLY.

    Copyright (C) 2017  Thomas Ramsauer
"""


import datetime
import os
import tempfile
import re
import numpy as np
import shapely
import shapely.wkt
# import yaml

from netCDF4 import Dataset
from scipy import spatial

from .prior import Prior


__author__ = ["Alexander Löw", "Thomas Ramsauer"]
__copyright__ = "Copyright 2017, Thomas Ramsauer"
__credits__ = ["Alexander Löw", "Thomas Ramsauer"]
__license__ = "GPLv3"
__version__ = "0.0.1"
__maintainer__ = "Thomas Ramsauer"
__email__ = "t.ramsauer@iggf.geo.uni-muenchen.de"
__status__ = "Prototype"


class SoilMoisturePrior(Prior):
    """
    Soil moisture prior class.
    Calculation of climatological prior.
    """

    def __init__(self, **kwargs):
        super(SoilMoisturePrior, self).__init__(**kwargs)

    def RetrievePrior(self):
        """
        Initialize prior specific (climatological, ...) calculation.

        :returns: nothing
        """
        self.sm_dir = None  # set None as old sm_dir may be present from loop.
        try:
            if self.ptype == 'climatology':
                # TODO adjust after creating GeoTiffs
                self.sm_dir = (self.config['Prior']['sm']['climatology']
                               ['climatology_dir'])

            elif self.ptype == 'munich':
                self.sm_dir = (self.config['Prior']['sm']['munich']
                               ['munich_dir'])

            elif self.ptype == 'recent':
                return self._get_recent_sm_proxy()

            else:
                assert False, '{} prior for sm not implemented'.format(
                    self.ptype)

        except KeyError as e:
            assert self.sm_dir is not None, \
                ('Soil Moisture Prior: Cannot find directory information for '
                 '"{}" prior in config file!'.format(self.ptype))
        else:
            assert os.path.isdir(self.sm_dir), ('Directory does not exist or'
                                                ' cannot be found: {}'
                                                .format(self.sm_dir))
        return self._provide_prior_files()

    def _calc_climatological_prior(self):
        """
        Calculate climatological prior.
        Reads climatological file and extracts proper values for given
        timespan and -interval.
        Then converts the means and stds to state vector and covariance
        matrices.

        :returns: state vector and covariance matrix
        :rtype: tuple

        """
        self._get_climatology_file()
        self._extract_climatology()

        # TODO limit to months

        # date_format = ('%Y-%m-%d')
        s = self.config['General']['start_time']
        e = self.config['General']['end_time']
        interval = self.config['General']['time_interval']
        t_span = (e - s).days + 1
        # print(t_span)

        # create list of month ids for every queried point in time:
        idt = [(s + (datetime.timedelta(int(x)))).month
               for x in np.arange(0, t_span, interval)]
        # idt_unique = list(set(idt))

        # create nd array with correct dimensions (time, x, y):
        p = np.ndarray(shape=(len(idt), self.clim.shape[1],
                              self.clim.shape[2]),
                       dtype=float)
        std = p.copy()

        # read correspending data into mean and std arrays:
        for i in range(len(idt)):
            p[i, :, :] = self.clim[idt[i] - 1, :, :]
            std[i, :, :] = self.std[idt[i] - 1, :, :]

        # calculate uncertainty with normalization via coefficient of variation
        # TODO scale uncertainty
        sm_unc = (std / np.mean(self.clim))
        # inverse covariance matrix
        diagon = (1. / sm_unc)
        # print(diagon.shape)

        # def create_sparse_matrix(a):
        #     return sp.sparse.lil_matrix(np.eye(t_span)*a)

        # C_prior_inv = np.apply_along_axis(create_sparse_matrix, 0, diagon)
        C_prior_inv = diagon

        # DISCUSS TODO
        # rather write to self.'prior_key' to easy concatenate afterwards
        # via concat_priors.

        return p, C_prior_inv

    def _get_climatology_file(self):
        """
        Load pre-processed climatology into self.clim_data.
        Part of prior._calc_climatological_prior().

        """
        assert (self.config['Prior']['sm']['climatology']
                           ['climatology_file']) is not None,\
            'There is no climatology file specified in the config!'

        # use xarray:
        # self.clim_data = xr.open_dataset(self.config['priors']['sm_clim']
        self.clim_data = Dataset(self.config['Prior']['sm']['climatology']
                                 ['climatology_file'])

    def _provide_prior_files(self):
        """provide file names, bands .. for inference engine

        :returns: 2 dictionaries (mean, var) w keys being variables\
        (SM, LAI, ..) and values being file name/descriptors pointing\
        to bands in netcdf files.
        :rtype: dict

        """
        # self.date
        def _get_files(dir, vrt=True):
            """get filenames of climatological prior files from directory.

            :param dir: directory conataining the files (mentioned in config)
            :param desc: descriptor of information ('mean'/'unc')
            :returns: returns list of filenames
            :rtype: list

            """
            fn = None
            if self.ptype == 'climatology':
                # TODO pattern from config file > make engine more accessible?
                pattern = (r"ESA_CCI_SM_clim_{:02d}.tiff$"
                           .format(self.date_month_id))
            elif self.ptype == 'munich':
                pattern = (r"{}.tiff$"
                           .format(self.date.date()))
            elif self.ptype == 'recent':
                pattern = (r"recent_prior_{}_{}.tiff$"
                           .format(desc, self.date))
            else:
                # TODO specify other name patterns
                pattern = (r"*")

            for dir_, _, files in os.walk(dir):
                for fileName in files:
                    if re.match(pattern, fileName) is not None:
                        fn = fileName

                    # temp fix for munich files
                    elif re.match(self.datestr, fileName) is not None:
                        fn = fileName
                        # return '{}{}'.format(dir, fn)
            # AssertionError is caught by the prior engine:
            assert fn is not None, ('Soil Moisture Prior: Did not find {} {} '
                                    'prior files in {} (pattern: \'{}\')!'
                                    .format(self.variable, self.ptype,
                                            self.sm_dir, pattern))
            # TODO should be an option in config?!
            if vrt:
                try:
                    temp_fn = ('{}_prior_{}_{:02d}.vrt'
                               .format(self.variable,
                                       self.ptype,
                                       self.date_month_id))
                    os.system('gdalbuildvrt -te -180 -90 180 90 '
                              '{} {}'.format(self.sm_dir + temp_fn,
                                             self.sm_dir + fn))
                    # os.system('gdalwarp {} {} -te -180 -90 180 90'
                    #           '-t_srs EPSG:4326 -of VRT'
                    #           .format(self.sm_dir+fn,
                    #                   self.sm_dir+temp_fn))
                    res = '{}{}'.format(dir, temp_fn)
                    # TODO does not catch gdal error:
                    if os.path.isfile(res):
                        return res
                    else:
                        raise AssertionError('Cannot create .vrt prior file.')
                except AssertionError as e:
                    return '{}{}'.format(dir, fn)
            else:
                return '{}{}'.format(dir, fn)

        return (_get_files(self.sm_dir))

    def _extract_climatology(self):
        """
        Extract climatology values for ROI.
        Part of _clac_climatological_prior().

        """
        clim = self.clim_data.variables['sm'][:]
        std = self.clim_data.variables['sm_stdev'][:]
        lats = self.clim_data.variables['lat'][:]
        lons = self.clim_data.variables['lon'][:]

        ROI_wkt = shapely.wkt.loads(self.config['General']['roi'])

        # minx, miny, maxx, maxy:
        minx, miny, maxx, maxy = ROI_wkt.bounds
        ROI = [(minx, miny), (maxx, maxy)]

        # TODO insert check for ROI bounds:
        # if POI[0] < np.amin(lats) or POI[0] > np.amax(lats) or\
        #    POI[1] < np.amin(lons) or POI[1] > np.amax(lons):
        #     raise ValueError("POI's latitude and longitude out of bounds.")

        # stack all raveled lats and lons from climatology
        # combined_LAT_LON results in e.g.
        # [[ 34.625 -10.875]
        #  [ 34.625 -10.625]
        #  [ 34.625 -10.375]...]
        combined_LAT_LON = np.dstack([lats.ravel(), lons.ravel()])[0]
        mytree = spatial.cKDTree(combined_LAT_LON)
        idx, idy = [], []
        # for all coordinate pairs in ROI search indexes in combined_LAT_LON:
        for i in range(len(ROI)):
            dist, indexes = mytree.query(ROI[i])
            x, y = tuple(combined_LAT_LON[indexes])
            idx.append(indexes % clim.shape[2])
            idy.append(int(np.ceil(indexes / clim.shape[2])))

        # TODO check assignment
        # print(idx, idy)

        # extract sm data
        sm_area_ = clim[:, min(idy):max(idy) + 1, :]
        sm_area = sm_area_[:, :, min(idx):max(idx) + 1]

        # extract sm stddef data
        sm_area_std_ = std[:, min(idy):max(idy) + 1, :]
        sm_area_std = sm_area_std_[:, :, min(idx):max(idx) + 1]
        # sm_area_std = np.std(sm_area, axis=(1, 2))
        # sm_area_mean = np.mean(sm_area, axis=(1, 2))

        # TODO Respect spatial resolution in config file.
        #      Adjust result accordingly.

        # print(sm_area)
        self.clim = sm_area
        self.std = sm_area_std

    def _get_recent_sm_proxy(self):
        assert False, "recent sm proxy not implemented"


class MapPrior(Prior):
    """
    Prior which is based on a LC map and a LUT
    """

    def __init__(self, **kwargs):
        """
        Parameters
        ----------
        lut_file : str
            filename of LUT file
        lc_file : str
            filename of landcover file
        """
        super(MapPrior, self).__init__(**kwargs)
        self.lut_file = kwargs.get('lut_file', None)
        assert self.lut_file is not None, 'LUT needs to be provided'

        self.lc_file = kwargs.get('lc_file', None)
        assert self.lc_file is not None, 'LC file needs to be provided'

        # check that files exist
        assert os.path.exists(self.lc_file)
        assert os.path.exists(self.lut_file)


class RoughnessPrior(MapPrior):

    def __init__(self, **kwargs):
        super(RoughnessPrior, self).__init__(**kwargs)

    def calc(self):
        if self.ptype == 'climatology':
            self._read_lut()
            self._read_lc()
            self._map_lut()
            self.file = self.save()
        else:
            assert False

    def _read_lut(self):
        self.lut = 'abc'

    def _read_lc(self):
        self.lc = 'efg'

    def _map_lut(self):
        """
        should do the mapping of s, l, ACL type
        """
        self.roughness = self.lut + self.lc

    def save(self):
        """
        save mapped roughness data to file
        """
        return tempfile.mktemp(suffix='.nc')
