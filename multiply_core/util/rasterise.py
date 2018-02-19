#!/usr/bin/env python

from __future__ import print_function
import gdal


gdal.UseExceptions() #Fail when can't open!

def rasterise_vector (raster_fname, vector_fname, where_statement=None, 
                      output_fname="", output_format="MEM",
                      verbose=False):
    """Rasterises a vector file to produce a mask where some condition 
    in the vector dataset is true. The mask will have the same extent and
    projection as a (provided) 'master' dataset. The selection of the feature
    for the mask will be performed by a command of the form field_name='Value',
    where the single quotes are mandatory (e.g. NAME='Ireland').
    
    Parameters
    -----------
    raster_fname: str
        A GDAL-compatible raster filename that will be used to extract the
        shape, projection, resolution, ... for the rasterisation.
    vector_fname: str
        The vector filename (e.g. Shapefile)
    where_statement: str
        The where statement (e.g. "NAME='Colombia'").
    output_fname: str, optinal
        The output filename, if not provided, an "in-memory array" will be 
        selected. If not provided and the output_format is other than `MEM`
        an error will be raised.
    output_format: str, optional
        An output format. By default, `MEM`
    verbose: Boolean
        Whether to get some extra inforamation
    
    Returns
    --------
    The mask as a Numpy array, 0 where the mask is off, 1 where it is on.    
    
    """
    if output_fname == "" and output_format != "MEM":
        raise ValueError("You need to provide an ouput filename" +
                         " for format{:s}".format(output_format))
    g = gdal.Open(raster_fname)
    if g is None:
        raise IOError("Could not open file {:s}".format(raster_fname))
    raster_proj = g.GetProjectionRef()
    geoT = g.GetGeoTransform()
    if verbose:
        print(">>> Opened file {:s}".format(raster_fname))
        print(">>> Projection: {:s}".format(raster_proj))
    xs = []
    ys = []
    for x,y in [ [0, 0], [0, g.RasterYSize], [g.RasterXSize, g.RasterYSize], [g.RasterXSize, 0]]:
        xx, yy = gdal.ApplyGeoTransform(geoT, x,y)
        xs.append(xx)
        ys.append(yy)
    extent = [min(xs), min(ys), max(xs), max(ys)]
    xRes = geoT[1]
    yRes = geoT[-1]
    nx = g.RasterXSize
    ny = g.RasterYSize
    if verbose:
        print(">>> File size {:d} rows, {:d} columns".format(nx, ny))
        print(">>> UL corner: {:g}, {:g}".format(min(xs), max(ys)))
    
    src_ds = gdal.OpenEx(vector_fname)
    if src_ds is None:
        raise IOError("Can't read the vector file {}".format(vector_fname))
    v = gdal.VectorTranslate('', src_ds, format = 'Memory', dstSRS=raster_proj,
                            where=where_statement)
    gg = gdal.Rasterize(output_fname, v,
                    format=output_format, outputType=gdal.GDT_Byte, xRes=xRes, yRes=yRes, 
                    where=where_statement,
                    outputBounds=[min(xs), min(ys), max(xs), max(ys)], 
                    width=nx, height=ny, noData=0, burnValues=1)
    
    if gg is not None:
        if verbose:
            print("Done! {:d} non-zero pixels".format(gg.ReadAsArray().sum()))
    else:
        raise ValueError("Couldn't generate the mask. Check input parameters")
    return gg.ReadAsArray()
