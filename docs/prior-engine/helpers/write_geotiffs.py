#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 T Ramsauer. All rights reserved.

"""
    Write single GeoTiffs from climatology NetCDF files created with
    geoval module.

    Copyright (C) 2018  Thomas Ramsauer
"""
import pdb
import os
import gdal
import numpy as np
from netCDF4 import Dataset


__author__ = "Thomas Ramsauer, Joris Timmermans"
__copyright__ = "Thomas Ramsauer"
__license__ = "gpl3"


def WriteGeoTiff_from_climNetCDF(filename, varname,
                                 lyr_mean='mean', lyr_unc='unc',
                                 new_no_data_value=None,
                                 upper_no_data_thres=None,
                                 upper_no_data_thres_unc=None,
                                 lower_no_data_thres=None,
                                 lower_no_data_thres_unc=0,
                                 flip_lat=True):
    """Write GeoTiffs from climatology NetCDF (generated with geoval module).

    :param filename: filename of NetCDF file to be processed.
    :param varname: name of variable to be written to Geotiffs.
    :param lyr_mean: name of mean layer/variable in NetCDF file.
    :param lyr_unc:  name of uncertainty layer/variable in NetCDF file.
    :param new_no_data_value: value to set no data values to
    :param upper_no_data_thres: values above will be set to new_no_data_value
    :param lower_no_data_thres: values below will be set to new_no_data_value
    :param flip_lat: Should latitudes be flipped
    :returns: -
    :rtype: -

    """
    d = Dataset(filename, 'r')
    lons_in = d.variables['lon'][:]
    lats_in = d.variables['lat'][:]
    Nlayers = 2

    drv = gdal.GetDriverByName("GTIFF")
    for month in np.arange(0, 12, 1):
        # print('month: ' + str(month+1))
        fn_out = filename.split('.')[0] + '_{:02d}'.format(month+1) + '.tiff'
        out_shape = (d.variables[lyr_mean][month].shape)
        # print(fn_out, out_shape[0], out_shape[1],Nlayers)
        dst_ds = drv.Create(fn_out, out_shape[1], out_shape[0],
                            Nlayers, gdal.GDT_Float32,
                            options=["COMPRESS=LZW",
                                     "INTERLEAVE=BAND",
                                     "TILED=YES"])
        resx = lons_in[0][1] - lons_in[0][0]
        resy = lats_in[1][0] - lats_in[0][0]
        dst_ds.SetGeoTransform([
             np.min(lons_in), resx, 0,
             np.max(lats_in), 0, -np.abs(resy)])
        dst_ds.SetProjection(
            'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS84",'
            '6378137,298.257223563,AUTHORITY["EPSG","7030"]],'
            'AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],'
            'UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4326"]]')

        means = d.variables[lyr_mean][month][:]
        unc = d.variables[lyr_unc][month][:]
        # pdb.set_trace()
        if new_no_data_value is not None:
            if upper_no_data_thres is not None:
                means = np.ma.masked_where(means > upper_no_data_thres, means)
            if lower_no_data_thres is not None:
                means = np.ma.masked_where(means < lower_no_data_thres, means)
            if upper_no_data_thres_unc is not None:
                unc = np.ma.masked_where(unc > upper_no_data_thres_unc, unc)
            if lower_no_data_thres_unc is not None:
                unc = np.ma.masked_where(unc < lower_no_data_thres_unc, unc)
        if flip_lat:
            i = -1
        else:
            i = 1

        means[means.mask] = new_no_data_value
        unc[unc.mask] = new_no_data_value

        dst_ds.GetRasterBand(1).WriteArray(means.data[::i])
        dst_ds.GetRasterBand(1).SetDescription(varname + '-mean')
        dst_ds.GetRasterBand(2).WriteArray(unc.data[::i])
        dst_ds.GetRasterBand(2).SetDescription(varname + '-uncertainty')
        dst_ds = None


def main():
    # TODO make actual CLI for main()
    os.chdir('/home/thomas/Code/prior-engine/aux_data')
    WriteGeoTiff_from_climNetCDF(filename=('CCI_SM_climatology_eur_merged_inv'
                                 '.nc'),
                                 varname='sm',
                                 lyr_mean='sm',
                                 lyr_unc='sm_stdev',
                                 new_no_data_value=-999,
                                 upper_no_ata_thres=10)


if __name__ == '__main__':
    main()
