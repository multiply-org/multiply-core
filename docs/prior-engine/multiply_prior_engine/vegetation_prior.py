# /usr/bin/env python
__author__ = "J Timmermans"
__copyright__ = "Copyright 2017 J Timmermans"
__version__ = "1.0 (06.11.2017)"
__license__ = "GPLv3"
__email__ = "j.timmermans@cml.leidenuniv.nl"

import glob
import os
import subprocess
import time

import multiprocessing
# import datetime
import gdal
import numpy as np

from dateutil.parser import parse
from matplotlib import pyplot as plt
from scipy import interpolate as RegularGridInterpolator
from netCDF4 import Dataset

from .prior import Prior

plt.ion()


def fun(f, q_in, q_out):
    while True:
        i, x = q_in.get()
        if i is None:
            break
        q_out.put((i, f(x)))


def parmap(f, X, nprocs=multiprocessing.cpu_count()):
    """FIXME! briefly describe function

    :param f: 
    :param X: 
    :param nprocs: 
    :returns: 
    :rtype: 

    """
    q_in = multiprocessing.Queue(1)
    q_out = multiprocessing.Queue()

    proc = [multiprocessing.Process(target=fun, args=(f, q_in, q_out))
            for _ in range(nprocs)]
    for p in proc:
        p.daemon = True
        p.start()

    sent = [q_in.put((i, x)) for i, x in enumerate(X)]
    [q_in.put((None, None)) for _ in range(nprocs)]
    res = [q_out.get() for _ in range(len(sent))]

    [p.join() for p in proc]

    return [x for i, x in sorted(res)]


def processespercore(varname, PFT, PFT_ids, VegetationPrior):
    """FIXME! briefly describe function

    :param varname: 
    :param PFT: 
    :param PFT_ids: 
    :param VegetationPrior: 
    :returns: 
    :rtype: 

    """
    TRAIT_ttf_avg = PFT[:, :, 0].astype('float') * 0.
    TRAIT_ttf_unc = PFT[:, :, 0].astype('float') * 0.

    for pft_id in PFT_ids[1:]:
        PFT_id = PFT[:, :, pft_id]

        # extract statistical values for transformed variables
        at = time.time()
        b = time.time()

        if np.any(PFT_id):
            trait_id = VegetationPrior.ReadTraitDatabase([varname], pft_id)

            # filtering variables for erroneous values
            trait_f_ = trait_id[varname] * 1.

            # transform variables
            trait_tf_ = trait_f_
            # if VegetationPrior.transformations.has_key(varname):
            #     trait_tf_ = VegetationPrior.transformations[varname](trait_f_)
            # else:
            #     trait_tf_ = trait_f_

            ierror = ~np.isnan(trait_tf_)
            trait_tf_avg = np.mean(trait_tf_[ierror])
            trait_tf_unc = np.std(trait_tf_[ierror])

            # assinge avg/unc values to individual pft_id (using PFT weights)
            TRAIT_wtf_avg = PFT_id / 100. * trait_tf_avg
            TRAIT_wtf_unc = PFT_id / 100. * trait_tf_unc

            # adding two (large-matrixes) is very computationally intensive
            TRAIT_ttf_avg = TRAIT_ttf_avg + TRAIT_wtf_avg
            TRAIT_ttf_unc = TRAIT_ttf_unc + TRAIT_wtf_unc

    # post processes for erroneous data
    ierror = (TRAIT_ttf_avg == 0) + (TRAIT_ttf_unc == 0)
    TRAIT_ttf_avg[ierror] = np.NaN
    TRAIT_ttf_unc[ierror] = np.NaN

    return TRAIT_ttf_avg, TRAIT_ttf_unc


class VegetationPrior(Prior):
    """
    Description
    """
    def __init__(self, **kwargs):
        super(VegetationPrior, self).__init__(**kwargs)
        self.config = kwargs.get('config', None)
        self.priors = kwargs.get('priors', None)

        # 1. Parameters
        # 1.1 Define Study Area
        self.lon_study = [0, 10]
        self.lat_study = [50, 60]

        # 1.2 Define paths
        self.directory_data = self.config['Prior']['General']['directory_data']
        self.path2LCC_file = (self.directory_data + 'LCC/' + 'ESACCI-LC-'
                              'L4-LCCS-Map-300m-P1Y-2015-v2.0.7_updated.nc')
        self.path2Climate_file = (self.directory_data + 'Climate/' +
                                  'sdat_10012_1_20171030_081458445.tif')
        self.path2Meteo_file = (self.directory_data + 'Meteorological/' +
                                'Meteo_.nc')
        self.path2Trait_file = (self.directory_data + 'Trait_Database/' +
                                'Traits.nc')
        self.path2Traitmap_file = self.directory_data + 'Priors/' + 'Priors.nc'

        self.plotoption = 0  # [0,1,2,3,4,5,6,..]

        # 0. Define parameter transformations
        self.transformations = {
            'lai': lambda x: np.exp(-x / 2.),
            'cab': lambda x: np.exp(-x / 100.),
            'car': lambda x: np.exp(-x / 100.),
            'cw': lambda x: np.exp(-50. * x),
            'cm': lambda x: np.exp(-100. * x),
            'ala': lambda x: x / 90.}
        self.inv_transformations = {
            'lai': lambda x: -2. * np.log(x),
            'cab': lambda x: -100 * np.log(x),
            'car': lambda x: -100 * np.log(x),
            'cw': lambda x: (-1 / 50.) * np.log(x),
            'cm': lambda x: (-1 / 100.) * np.log(x),
            'ala': lambda x: 90. * x}

    def OfflineProcessing(self):
        """FIXME! briefly describe function

        :returns: 
        :rtype: 

        """
        # handle offline

        # Download Data
        self.DownloadCrossWalkingTable()

        # Preprocess Data
        self.RunCrossWalkingTable()

        # Construct Database
        self.CreateDummyDatabase()

    def StaticProcessing(self, varnames, write_output=False):
        """FIXME! briefly describe function

        :param varnames: 
        :param write_output: 
        :returns: 
        :rtype: 

        """
        # Read Data (2.5s)
        LCC_map, LCC_lon, LCC_lat, LCC_classes = self.ReadLCC()
        CLM_map, CLM_lon, CLM_lat, CLM_classes = self.ReadClimate()

        if np.all(LCC_map['Water']):

            Prior_pbm_avg = dict()
            Prior_pbm_unc = dict()
            dummy = LCC_map['Water'] * np.NaN

            for varname in varnames:
                Prior_pbm_avg[varname] = dummy
                Prior_pbm_unc[varname] = dummy

        else:
            # Process Data (12.5s)
            CLM_map_i = self.RescaleCLM(CLM_lon, CLM_lat, CLM_map,
                                        LCC_lon, LCC_lat)
            PFT, PFT_classes, Npft, PFT_ids = self.Combine2PFT(LCC_map,
                                                               CLM_map_i)

            Prior_pbm_avg, Prior_pbm_unc = self.AssignPFTTraits2Map(PFT,
                                                                    PFT_ids,
                                                                    varnames)

        if write_output:
            self.WriteOutput(LCC_lon, LCC_lat, Prior_pbm_avg, Prior_pbm_unc)

        return LCC_lon, LCC_lat, Prior_pbm_avg, Prior_pbm_unc

    def DynamicProcessing(self, varnames, LCC_lon, LCC_lat, Prior_pbm_avg,
                          Prior_pbm_unc, doystr, write_output=True):
        """FIXME! briefly describe function

        :param varnames: 
        :param LCC_lon: 
        :param LCC_lat: 
        :param Prior_pbm_avg: 
        :param Prior_pbm_unc: 
        :param doystr: 
        :param write_output: 
        :returns: 
        :rtype: 

        """

        Meteo_map, Meteo_lon, Meteo_lat = self.ReadMeteorologicalData(doystr)
        # Meteo_map_i =  RescaleCLM(Meteo_lon, Meteo_lat, Meteo_map,
        #                           LCC_lon, LCC_lat)

        Prior_avg, Prior_unc = self.PhenologicalEvolution(Prior_pbm_avg,
                                                          Prior_pbm_unc,
                                                          doystr,
                                                          Meteo_map_i=None)

        # 7. Write Output
        if write_output:
            self.WriteGeoTiff(LCC_lon, LCC_lat, Prior_avg, Prior_unc, doystr)
            # self.WriteOutput(LCC_lon, LCC_lat, Prior_avg, Prior_unc, doystr)

    def CreateDummyDatabase(self):
        """FIXME! briefly describe function

        :returns: 
        :rtype: 

        """

        # define variables
        varnames = ['lai', 'cab', 'cb', 'car', 'cw', 'cdm', 'N', 'ala',
                    'h', 'bsoil', 'psoil']
        descriptions = ['Effective Leaf Area Index',
                        'Leaf Chlorophyll Content', 'Leaf Senescent material',
                        'Leaf Carotonoid Content', 'Leaf Water Content',
                        'Leaf Dry Mass', 'Structural Parameter',
                        'Average Leaf Angle', 'hotspot parameter',
                        'Soil Brightness parameter', 'Soil Wetness parameter']
        units = ['m2/m2', 'ug/cm2', '-', 'ug/cm2', 'cm', 'g/cm2', '-',
                 'degrees', '-', '-', '-']

        # create netcdf file to hold database values
        dataset = Dataset(self.path2Trait_file, 'w', format='NETCDF4')

        # setup Netcdf file
        dataset.description = 'Database for Prior-Engine'
        dataset.history = 'Created' + time.ctime(time.time())
        dataset.source = 'Data obtained from TRY-database'

        # Define dimensions
        Npft = 16
        Nspecies = 100
        pftdim = dataset.createDimension('pft', Npft)
        speciesdim = dataset.createDimension('type', Nspecies)
        occurrencedim = dataset.createDimension('occ', None)

        # create variables in dataset
        occurrence = dataset.createVariable('Occurrences', np.float32, ('occ'))
        occurrence.description = 'Unique PFT/Species entry into database'

        pft = dataset.createVariable('PFTs', np.float32, ('pft'))
        pft.description = 'PFT classification according to ORCHIDEE'

        species = dataset.createVariable('Species', np.float32, ('type'))
        species.description = 'Species name according to ??'

        for ivar, varname in enumerate(varnames):
            var = dataset.createVariable(varname, np.float32,
                                         ('occ', 'pft', 'type'), zlib=True)
            var.units = units[ivar]
            var.description = descriptions[ivar]

            # Fill file with random variables
            Nvar = 10  # np.random.randint(1,10)
            var[0:Nvar, :, :] = np.random.uniform(size=(Nvar, Npft, Nspecies))

        dataset.close()
        os.system('chmod 755 "' + self.path2Trait_file + '"')

    def DownloadCrossWalkingTable(self):
        """FIXME! briefly describe function

        :returns: 
        :rtype: 

        """
        # According to Pulter et al, Plant Functional classification for
        # earth system models: resuls from the European Space
        # Agency's land Cover Climate Change Initiative, 2015,
        # Geosci Model Dev., 8, 2315-2328, 2015.

        link2LCC_map = ('https://storage.googleapis.com/cci-lc-v207/ESACCI-LC-'
                        'L4-LCCS-Map-300m-P1Y-2015-v2.0.7.nc.zip')
        link2CrossWalkingtable = ('http://maps.elie.ucl.ac.be/CCI/viewer/'
                                  'download/lc-user-tools-3.14.zip')

    def RunCrossWalkingTable(self, Path2CWT_tool=None, Path2LC=None):
        """FIXME! briefly describe function

        :param Path2CWT_tool: 
        :param Path2LC: 
        :returns: 
        :rtype: 

        """
        # to run the crosswalking tool, the specific requirements for BEAM need
        # to be met (java64bit + ...)
        if Path2CWT_tool is None:
            Tooldir = '~/Data/Prior_Engine/Tool/lc-user-tools-3.14/'
            Path2CWT_tool = Tooldir + 'bin/remap.sh'
            Path2CWT_file = Tooldir + 'resources/Default_LCCS2PFT_LUT.csv'
        if Path2LC is None:
            Path2LC = ('~/Data/Prior_engine/Data/LCC/'
                       'ESACCI-LC-L4-LCCS-Map-300m-P1Y-2015-v2.0.7.nc')

        string2execute = (Path2CWT_tool + ' -PuserPFTConversionTable=' +
                          Path2CWT_file + ' ' + Path2LC)
        os.system(string2execute)

        # Please note that we use the default crosswalking table over here.
        # This does not distinguish between C3/C4 crops/grasses, or identify
        # non-vascular plants. For this we need to acquire the
        # most recent cross-walking table used Druel. A et al, Towards a more
        # detailed representation of high-latitutde vegetation
        # in the global land surface model ORCHIDEE (ORC-HL-VEGv1.0).

        # Altneratively we can use the Synmap c3/c4 fraction map. to
        # distinguish make this distinction for grasses.
        return

    def ReadLCC(self):
        """FIXME! briefly describe function

        :returns: 
        :rtype: 

        """
        lon_min = self.lon_study[0]
        lon_max = self.lon_study[1]
        lat_min = self.lat_study[0]
        lat_max = self.lat_study[1]

        dataset_container = Dataset(self.path2LCC_file, 'r')
        lon = dataset_container.variables['lon'][:]
        lat = dataset_container.variables['lat'][:]

        ilon_min = np.argmin(np.abs(lon - lon_min))
        ilon_max = np.argmin(np.abs(lon - lon_max))
        ilat_min = np.argmin(np.abs(lat - lat_min))
        ilat_max = np.argmin(np.abs(lat - lat_max))

        lon_s = lon[ilon_min:ilon_max]
        lat_s = lat[ilat_max:ilat_min]

        # classes0 = dataset_container['lccs_class'][ilon_min,ilat_min]

        class_names = ['Tree_Broadleaf_Evergreen',
                       'Tree_Broadleaf_Deciduous',
                       'Tree_Needleleaf_Evergreen',
                       'Tree_Needleleaf_Deciduous',
                       'Shrub_Broadleaf_Evergreen',
                       'Shrub_Broadleaf_Deciduous',
                       'Shrub_Needleleaf_Evergreen',
                       'Shrub_Needleleaf_Deciduous',
                       'Natural_Grass', 'Managed_Grass',
                       'Bare_Soil', 'Water', 'Snow_Ice']

        Data = dict()
        for class_name in class_names:
            data = dataset_container[class_name][ilat_max:ilat_min,
                                                 ilon_min:ilon_max]
            Data[class_name] = data

        if self.plotoption == 1:
            Nc = 4
            Nv = len(Data)
            Nr = int(np.ceil(Nv / Nc + 1))

            plt.figure(figsize=[20, 20])
            for i, class_name in enumerate(class_names):
                plt.subplot(Nr, Nc, i + 1)
                plt.imshow(Data[class_name])
                plt.title(class_name)
                plt.colorbar()

        return Data, lon_s, lat_s, class_names

    def ReadTraitDatabase(self, varnames, pft_id=1):
        """FIXME! briefly describe function

        :param varnames: 
        :param pft_id: 
        :returns: 
        :rtype: 

        """

        Var = dict()
        for varname in varnames:
            Data = Dataset(self.path2Trait_file, 'r')
            V = Data[varname][:, pft_id, :]
            Var[varname] = V

        Data.close()

        return Var

    def ReadMeteorologicalData(self, doystr):
        """FIXME! briefly describe function

        :param doystr: 
        :returns: 
        :rtype: 

        """
        MeteoData = None
        Meteo_lon = None
        Meteo_lat = None

        if self.plotoption == 2:
            plt.figure(figsize=[20, 20])
            plt.imshow(MeteoData)
            plt.title('Meteorological Data (missing at this moment)')

        return MeteoData, Meteo_lon, Meteo_lat

    def ReadClimate(self):
        """FIXME! briefly describe function

        :returns: 
        :rtype: 

        """
        ds = gdal.Open(self.path2Climate_file)
        width = ds.RasterXSize
        height = ds.RasterYSize
        gt = ds.GetGeoTransform()

        minx = gt[0]
        miny = gt[3] + width * gt[4] + height * gt[5]
        maxx = gt[0] + width * gt[1] + height * gt[2]
        maxy = gt[3]

        minx = np.round(minx * 100) / 100
        miny = np.round(miny * 100) / 100
        maxx = np.round(maxx * 100) / 100
        maxy = np.round(maxy * 100) / 100

        lon = np.linspace(minx, maxx, width + 1)[0:-1]
        lat = np.linspace(maxy, miny, height + 1)[0:-1]

        lon_min = self.lon_study[0]
        lon_max = self.lon_study[1]
        lat_min = self.lat_study[0]
        lat_max = self.lat_study[1]

        ilon = np.where((lon >= lon_min) * (lon <= lon_max))[0]
        ilat = np.where((lat >= lat_min) * (lat <= lat_max))[0]

        # read data
        data = ds.ReadAsArray(ilon[0], ilat[0], len(ilon), len(ilat))
        lon_s = lon[ilon]
        lat_s = lat[ilat]

        classes = ['H20',  # Water                                        0
                   'Af',  # Tropical/rainforest                           1
                   'Am',  # Tropical Monsoon                              2
                   'Aw',  # Tropical/Savannah                             3
                   'BWh',  # Arid/Desert/Hot                              4
                   'BWk',  # Arid/Desert/Cold                             5
                   'BSh',  # Arid/Steppe/Hot                              6
                   'BSk',  # Arid/Steppe/Cold                             7
                   'Csa',  # Temperate/Dry_Symmer/Hot_summer              8
                   'Csb',  # Temperate/Dry_Symmer/Warm_summer             9
                   'Csc',  # Temperate/Dry_Symmer/Cold_summer             10
                   'Cwa',  # Temperate/Dry_Winter/Hot_summer              11
                   'Cwb',  # Temperate/Dry_Winter/warm_summer             12
                   'Cwc',  # Temperate/Dry_Winter/Cold_summer             13
                   'Cfa',  # Temperate/Without_dry_season/Hot_summer      14
                   'Cfb',  # Temperate/Without_dry_season/Warm_summer     15
                   'Cfc',  # Temperate/Without_dry_season/Cold_summer     16
                   'Dsa',  # Cold/Dry_Summer/Hot_summer                   17
                   'Dsb',  # Cold/Dry_Summer/warm_summer                  18
                   'Dsc',  # Cold/Dry_Summer/cold_summer                  19
                   'Dsd',  # Cold/Dry_Summer/very_cold_summer             20
                   'Dwa',  # Cold/Dry_Winter/Hot_summer                   21
                   'Dwb',  # Cold/Dry_Winter/Warm_summer                  22
                   'Dwc',  # Cold/Dry_Winter/Cold_summer                  23
                   'Dwd',  # Cold/Dry_Winter/Very_cold_summer             24
                   'Dfa',  # Cold/Without_dry_season/Hot_summer           25
                   'Dfb',  # Cold/Without_dry_season/Warm_summer          26
                   'Dfc',  # Cold/Without_dry_season/cold_summer          27
                   'Dfd',  # Cold/Without_dry_season/very_cold_summer     28
                   'ET(1)',  # Polar/Tundra                               29
                   'EF(1)',  # Polar/Frost                                30
                   'ET(2)',  # Polar/Tundra                               31
                   'EF(2)'  # Polar/Frost                                 32
                   ];

        if self.plotoption == 3:
            plt.figure(figsize=[20, 20])
            plt.imshow(data)
            plt.title('Koppen')

        return data, lon_s, lat_s, classes

    def RescaleCLM(self, CLM_lon, CLM_lat, CLM_map, LCC_lon, LCC_lat):
        """FIXME! briefly describe function

        :param CLM_lon: 
        :param CLM_lat: 
        :param CLM_map: 
        :param LCC_lon: 
        :param LCC_lat: 
        :returns: 
        :rtype: 

        """
        x, y = np.meshgrid(CLM_lon, CLM_lat)
        n = x.size

        F = RegularGridInterpolator.NearestNDInterpolator(
            (np.resize(x, n), np.resize(y, n)), np.resize(CLM_map, n))

        loni, lati = np.meshgrid(LCC_lon, LCC_lat)
        CLM_map_i = F(loni, lati)

        if self.plotoption == 4:
            plt.figure(figsize=[20, 20])
            plt.subplot(2, 1, 1)
            plt.imshow(CLM_map)
            plt.subplot(2, 1, 2)
            plt.imshow(CLM_map_i[0::2, 0::2])

        return CLM_map_i

    def Combine2PFT(self, LCC_map, CLM_map_i):
        """FIXME! briefly describe function

        :param LCC_map: 
        :param CLM_map_i: 
        :returns: 
        :rtype: 

        """
        iwater = (CLM_map_i == 0)
        itropical = (CLM_map_i >= 1) * (CLM_map_i <= 7)
        itemporate = (CLM_map_i >= 8) * (CLM_map_i <= 16)
        iboreal = (CLM_map_i >= 17) * (CLM_map_i <= 28)
        ipolar = (CLM_map_i >= 29) * (CLM_map_i <= 32)

        Nlon = np.shape(CLM_map_i)[0]
        Nlat = np.shape(CLM_map_i)[1]
        Npft = 16

        PFT = np.zeros([Nlon, Nlat, Npft])
        # water
        PFT[:, :, 0] = (iwater + (LCC_map['Water'] > 0)
                        + (LCC_map['Snow_Ice'] > 0))
        # Trees: Tropical: Broadleaf: Evergreen
        PFT[:, :, 1] = itropical * LCC_map['Tree_Broadleaf_Evergreen']
        # Trees: Tropical: Broadleaf: Raingreen
        PFT[:, :, 2] = itropical * LCC_map['Tree_Broadleaf_Deciduous']

        # Trees: Temperate: Needleleaf: Evergreen
        PFT[:, :, 3] = itemporate * LCC_map['Tree_Needleleaf_Evergreen']
        # Trees: Temperate: Broadleaf: Evergreen
        PFT[:, :, 4] = itemporate * LCC_map['Tree_Broadleaf_Evergreen']
        # Trees: Temperate: Broadleaf: Summergreen
        PFT[:, :, 5] = itemporate * LCC_map['Tree_Broadleaf_Deciduous']

        # Trees: Boreal: Needleleaf: Evergreen
        PFT[:, :, 6] = iboreal * LCC_map['Tree_Needleleaf_Evergreen']
        # Trees: Boreal: Broadleaf: Summergreen
        PFT[:, :, 7] = iboreal * LCC_map['Tree_Broadleaf_Deciduous']
        # Trees: Boreal: Needleleaf: Summergreen
        PFT[:, :, 8] = iboreal * LCC_map['Tree_Broadleaf_Deciduous']

        # Grasses: Natural: C3: Global
        PFT[:, :, 9] = (itemporate + iboreal) * LCC_map['Natural_Grass']
        # Grasses: Natural: C3: Arctic
        PFT[:, :, 10] = ipolar * LCC_map['Natural_Grass']
        # Grasses: Natural: C4:
        PFT[:, :, 11] = itropical * LCC_map['Natural_Grass']

        # 12  Crops: C3
        PFT[:, :, 12] = (itemporate + iboreal) * LCC_map['Managed_Grass']
        # 13  Crops: C4
        PFT[:, :, 13] = ~(itemporate + iboreal) * LCC_map['Managed_Grass']
        # 14  Shrubs
        PFT[:, :, 14] = LCC_map['Shrub_Broadleaf_Evergreen'] + \
                        LCC_map['Shrub_Broadleaf_Deciduous'] + \
                        LCC_map['Shrub_Needleleaf_Evergreen'] + \
                        LCC_map['Shrub_Needleleaf_Deciduous']

        # not accounted for in this version of the LCC.For this the
        # cross-walking table should be modified.This should be handled
        # in the beta version

        # 15  Non-Vascular (mosses)
        PFT[:, :, 15] = LCC_map['Shrub_Needleleaf_Deciduous'] * 0
        PFT_classes = ['water',
                       'Trees: Tropical: Broadleaf: Evergreen',
                       'Trees: Tropical: Broadleaf: Raingreen',
                       'Trees: Temperate: Needleleaf: Evergreen',
                       'Trees: Temperate: Broadleaf: Evergreen',
                       'Trees: Temperate: Broadleaf: Summergreen',
                       'Trees: Boreal: Needleleaf: Evergreen',
                       'Trees: Boreal: Broadleaf: Summergreen',
                       'Trees: Boreal: Needleleaf: Summergreen',
                       'Grasses: Natural: C3: Global',
                       'Grasses: Natural: C3: Arctic',
                       'Grasses: Natural: C4:',
                       'Crops: C3',
                       'Crops: C4',
                       'Shrubs',
                       'Non-Vascular']
        Npft = len(PFT_classes)
        PFT_ids = np.arange(0, Npft)

        # visualize
        if self.plotoption == 5:
            Nc = 4
            Npft = np.shape(PFT)[2]
            Nr = int(np.ceil(Npft / Nc + 1))

            plt.figure(figsize=[20, 20])
            for i in range(Npft):
                plt.subplot(Nr, Nc, i + 1)
                plt.imshow(PFT[:, :, i])
                plt.colorbar()
                plt.title(PFT_classes[i])

        return PFT, PFT_classes, Npft, PFT_ids

    def AssignPFTTraits2Map(self, PFT, PFT_ids, varnames):
        """FIXME! briefly describe function

        :param PFT: 
        :param PFT_ids: 
        :param varnames: 
        :returns: 
        :rtype: 

        """
        # from multiprocessing import Pool
        from functools import partial

        # open Trait data
        TRAITS_ttf_avg = dict()
        TRAITS_ttf_unc = dict()

        # Process in parallel
        pr = partial(processespercore, PFT=PFT, PFT_ids=PFT_ids, VegetationPrior=self)
        ret = parmap(pr, varnames, nprocs=3)
        for ivar, varname in enumerate(varnames):
            TRAITS_ttf_avg[varname] = ret[ivar][0][:, :]
            TRAITS_ttf_unc[varname] = ret[ivar][1][:, :]

        # for varname in varnames:
        #     TRAIT_ttf_avg, TRAIT_ttf_unc            =   processespercore(varname, PFT, PFT_ids, self)
        #
        #     # write back to output
        #     TRAITS_ttf_avg[varname]                 =   TRAIT_ttf_avg
        #     TRAITS_ttf_unc[varname]                 =   TRAIT_ttf_unc

        if self.plotoption == 6:
            Nc = 4.
            Nvar = len(varnames)
            Nr = int(np.ceil(Nvar / Nc))
            plt.figure(figsize=[20, 20])
            for i, varname in enumerate(varnames):
                plt.subplot(Nr, Nc, i + 1)
                plt.imshow(TRAITS_ttf_avg[varname])
                plt.colorbar()
                plt.title(varname)

            plt.figure(figsize=[20, 20])
            for i, varname in enumerate(varnames):
                plt.subplot(Nr, Nc, i + 1)
                plt.imshow(TRAITS_ttf_unc[varname])
                plt.colorbar()
                plt.title(varname + '_unc')

        return TRAITS_ttf_avg, TRAITS_ttf_unc

    def PhenologicalEvolution(self, Prior_pbm_avg, Prior_pbm_unc,
                              doystr, Meteo_map_i=None):
        """FIXME! briefly describe function

        :param Prior_pbm_avg: 
        :param Prior_pbm_unc: 
        :param doystr: 
        :param Meteo_map_i: 
        :returns: 
        :rtype: 

        """
        if Meteo_map_i is None:
            Prior_avg = Prior_pbm_avg
            Prior_unc = Prior_pbm_unc
        else:
            print("Here we are going to do some interesting bit with"
                  " phenological models at %s" % (doystr))

        return Prior_avg, Prior_unc

    def WriteOutput(self, LCC_lon, LCC_lat, Prior_avg, Prior_unc,
                    doystr='static'):
        """FIXME! briefly describe function

        :param LCC_lon: 
        :param LCC_lat: 
        :param Prior_avg: 
        :param Prior_unc: 
        :param doystr: 
        :returns: 
        :rtype: 

        """

        varnames = [name for name in Prior_avg.iterkeys()]
        latstr = ('[%02.0f' % self.lat_study[0]
                  + ' %02.0fN]' % self.lat_study[1])
        lonstr = ('[%03.0f' % self.lon_study[0]
                  + ' %03.0fE]' % self.lon_study[1])
        filename = (self.path2Traitmap_file[:-3] + '_' + doystr + '_' + latstr
                    + '_' + lonstr + '.nc')

        dataset = Dataset(filename, 'w', format='NETCDF4_CLASSIC')
        dataset.description = 'Transformed Priors at doy: ' + doystr
        dataset.history = 'Created' + time.ctime(time.time())

        dataset.cdm_data_type = 'grid'
        # dataset.comment=
        dataset.contact = 'j.timmermans@cml.leidenuniv.nl'
        dataset.Conventions = 'CF-1.6'

        dataset.creator_email = 'j.timmermans@cml.leidenuniv.nl'
        dataset.creator_name = 'Leiden University'
        dataset.date_created = '20180330T210326Z'
        dataset.geospatial_lat_max = '90.0'
        dataset.geospatial_lat_min = '-90.0'
        dataset.geospatial_lat_resolution = '0.002778'
        dataset.geospatial_lat_units = 'degrees_north'
        dataset.geospatial_lon_max = '180.0'
        dataset.geospatial_lon_min = '-180.0'
        dataset.geospatial_lon_resolution = '0.002778'
        dataset.geospatial_lon_units = 'degrees_east'
        # dataset.history=amorgos-4,0, lc-sdr-1.0, lc-sr-1.0,
        #                 lc-classification-1.0,lc-user-tools-3.12
        dataset.id = 'ESACCI-LC-L4-LCCS-Map-300m-P1Y-2015-v2.0.7'
        dataset.institution = 'Universite catholique de Louvain'
        dataset.keywords = 'land cover classification,satellite,observation'
        dataset.keywords_vocabulary = ('NASA Global Change Master Directory'
                                       '(GCMD) Science Keywords')
        dataset.license = 'ESA CCI Data Policy: free and open access'
        dataset.naming_authority = 'org.esa-cci'
        dataset.product_version = '2.0.7'
        dataset.project = 'Climate Change Initiative - European Space Agency'
        dataset.references = 'http://www.esa-landcover-cci.org/'
        dataset.source = ('MERIS FR L1B version 5.05, MERIS RR L1B version'
                          '8.0, SPOT VGT P')
        dataset.spatial_resolution = '300m'
        dataset.standard_name_vocabulary = ('NetCDF Climate and Forecast (CF)'
                                            ' Standard Names version 21')
        dataset.summary = ('This dataset contains the global ESA CCI land '
                           'cover classification map derived from satellite '
                           'data of one epoch.')
        dataset.TileSize = '2048:2048'
        dataset.time_coverage_duration = 'P1Y'
        dataset.time_coverage_end = '20151231'
        dataset.time_coverage_resolution = 'P1Y'
        dataset.time_coverage_start = '20150101'
        dataset.title = 'ESA CCI Land Cover Map'
        dataset.tracking_id = '202be995-43d8-4e3a-9607-1bd3f02a925e'
        dataset.type = 'ESACCI-LC-L4-LCCS-Map-300m-P1Y'

        #

        # create dimensions
        Nlon = len(LCC_lon)
        Nlat = len(LCC_lat)

        londim = dataset.createDimension('lon', Nlon)
        latdim = dataset.createDimension('lat', Nlat)

        # create variables in dataset
        lon = dataset.createVariable('lon', np.float32, ('lon'))
        lon.description = 'Longitude'
        lon.units = 'degrees_east'
        lon[:] = LCC_lon

        lat = dataset.createVariable('lat', np.float32, ('lat'))
        lat.description = 'Latitude'
        lat.units = 'degrees_north'
        lat[:] = LCC_lat

        for varname in varnames:
            var = dataset.createVariable(varname, np.float32,
                                         ('lon', 'lat'), zlib=True)
            var.units = ''
            var[:] = Prior_avg[varname]

            var_unc = dataset.createVariable(varname + '_unc',
                                             np.float32, ('lon', 'lat'))
            var_unc.units = ''
            var_unc[:] = Prior_unc[varname]

        dataset.close()
        os.system('chmod 755 "' + filename + '"')
        print('%s', filename)

    def WriteGeoTiff(self, LCC_lon, LCC_lat, Prior_avg,
                     Prior_unc, doystr='static'):
        """FIXME! briefly describe function

        :param LCC_lon: 
        :param LCC_lat: 
        :param Prior_avg: 
        :param Prior_unc: 
        :param doystr: 
        :returns: 
        :rtype: 

        """
        Nlayers = 2
        latstr = ('[%02.0f' % self.lat_study[0]
                  + '_%02.0fN]' % self.lat_study[1])
        lonstr = ('[%03.0f' % self.lon_study[0]
                  + '_%03.0fE]' % self.lon_study[1])

        varnames = [name for name in Prior_avg.iterkeys()]
        drv = gdal.GetDriverByName("GTIFF")
        for i, varname in enumerate(varnames):
            filename = (self.path2Traitmap_file[:-3] + '_' + varname + '_'
                        + doystr + '_' + latstr + '_' + lonstr + '.tiff')
            dst_ds = drv.Create(filename, np.shape(LCC_lon)[0],
                                np.shape(LCC_lat)[0], Nlayers,
                                gdal.GDT_Float32,
                                options=["COMPRESS=LZW", "INTERLEAVE=BAND",
                                         "TILED=YES"])
            resx = LCC_lon[1] - LCC_lon[0]
            resy = LCC_lat[1] - LCC_lat[0]

            dst_ds.SetGeoTransform([min(LCC_lon), resx, 0, max(LCC_lat),
                                    0, -np.abs(resy)])
            dst_ds.SetProjection(
                'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS84",6378137,'
                '298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY'
                '["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",'
                '0.0174532925199433],AUTHORITY["EPSG","4326"]]')

            dst_ds.GetRasterBand(1).WriteArray(Prior_avg[varname])
            dst_ds.GetRasterBand(1).SetDescription(varname + '-mean')
            dst_ds.GetRasterBand(2).WriteArray(Prior_unc[varname])
            dst_ds.GetRasterBand(2).SetDescription(varname + '-unc')
            dst_ds = None

    def CombineTiles2Virtualfile(self, variable, doystr):
        """FIXME! briefly describe function

        :param variable: 
        :param doystr: 
        :returns: 
        :rtype: 

        """
        dir = self.directory_data + 'Priors/'
        file_name = 'Priors_' + variable + '_' + doystr + '_global.vrt'
        # todo exchange 125 in upcoming versions with doy
        list_of_files = glob.glob(dir + 'Priors*' + variable + '*125*.tiff')

        list_of_files2 = []
        for filename in list_of_files:
            list_of_files2.append('"' + filename + '"')

    
        files = " ".join(list_of_files2)
        os.system('gdalbuildvrt -te -180 -90 180 90 ' + dir + file_name
                  + ' ' + files)
        return '{}{}'.format(dir, file_name)

    def ProcessData(self, variables=None, state_mask=None,
                    timestr='2007-12-31 04:23', logger=None, file_prior=None,
                    file_lcc=None, file_biome=None, file_meteo=None):
        """FIXME! briefly describe function

        :param variables: 
        :param state_mask:
        :param timestr:
        :param logger:
        :param file_prior:
        :param file_lcc:
        :param file_biome:
        :param file_meteo:

        :returns: 
        :rtype: 

        """
        import datetime
        timea = datetime.datetime.now()
        # Retrieves a state vector and an inverse covariance matrix
        #   param variables: A list of variables for which priors need to be
        #                    available those will be inferred).  check
        #   param state_mask: A georeferenced array that represents the space
        #                     where solutions will be calculated. Spatial
        #                     resolution should be set equal to highest
        #                     observation.
        #                     True values in this array represents pixels where
        #                     the inference will be carried out
        #                     False values represent pixels for which no priors
        #                     need to be defined (as those will not be used in
        #                     the inference)
        #   param time: The string representing the time for which the prior
        #               needs to be derived
        #   param logger: A logger or "traceability database"
        #   param file_lcc_biome:
        #   param file_prior_database:
        #   param file_meteo

        plt.ion()

        # # Define variables
        # if variables==None:
        #     variables = ['lai', 'cab', 'cb', 'car', 'cw', 'cdm', 'N', 'ala',
        #                  'h', 'bsoil', 'psoil']
        #
        # # 1.1 Define paths
        # directory_data = '/home/joris/Data/Prior_Engine/'
        # if file_prior is None:
        #     file_prior = directory_data + 'Trait_Database/' + 'Traits.nc'
        # if file_lcc is None:
        #     file_lcc = (directory_data +'/LCC/'
        #                 + 'ESACCI-LC-L4-LCCS-Map-300m-P1Y'
        #                 + '-2015-v2.0.7_updated.nc')
        # if file_biome==None:
        #     file_biome = (directory_data +'Climate/'
        #                   + 'sdat_10012_1_20171030_081458445.tif')
        # if file_meteo==None:
        #     file_meteo = directory_data +'Meteorological/' + 'Meteo_.nc'
        # file_output = directory_data +'Priors/' + 'Priors.nc'
        #
        # 0. Setup Processing
        # VegPrior = VegetationPrior()

        # VegPrior.path2Trait_file = file_prior
        # VegPrior.path2LCC_file = file_lcc
        # VegPrior.path2Climate_file = file_biome
        # VegPrior.path2Meteo_file = file_meteo
        # VegPrior.path2Traitmap_file = file_output

        #############
        time = parse(timestr)
        doystr = time.strftime('%j')
        lon_study_ = np.arange(-180, 180, 10)
        lat_study_ = np.arange(-90, 90, 10)

        for lon_study in lon_study_:
            for lat_study in lat_study_:
                print('%3.2f %3.2f' % (lon_study, lat_study))
                VegPrior.lon_study = [lon_study, lon_study + 10]
                VegPrior.lat_study = [lat_study, lat_study + 10]

                # 3. Perform Static processing
                lon, lat, Prior_pbm_avg, Prior_pbm_unc = \
                  VegPrior.StaticProcessing(variables)

                # 4. Perform Static processing
                VegPrior.DynamicProcessing(variables, lon, lat, Prior_pbm_avg,
                                           Prior_pbm_unc, doystr=doystr)

        filenames = self.CombineTiles2Virtualfile(variables)

    def RetrievePrior(self):
        """FIXME! briefly describe function

        :returns: 
        :rtype: 

        """
        # Define variables
        if self.variable is None:
            self.variables = ['lai', 'cab', 'cb', 'car', 'cw', 'cdm', 'N',
                              'ala', 'h', 'bsoil', 'psoil']

        # time = parse(self.datestr)
        time = self.date
        doystr = time.strftime('%j')

        if self.ptype == 'database':
            # 0. Setup Processing
            # filenames = self.CombineTiles2Virtualfile(variables, doystr)
            filenames = self.CombineTiles2Virtualfile(self.variable, doystr)

        else:
            filenames = None
            print('not implemented yet')

        return filenames


if __name__ == "__main__":
    VegPrior = VegetationPrior()

    # VegPrior.ProcessData()
    filenames = VegPrior.RetrievePrior(variables=['lai', 'cab'],
                                       datestr='2007-12-31 04:23',
                                       ptype='database')

    print('%s' % filenames)
    # this should give as output:
    #

    
    # end of file
