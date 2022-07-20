import numpy as np
import os
import sys
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import urllib
import logging
import gzip
import shutil
import rasterio
import rasterstats
import dotenv
import geopandas as gpd
import pandas as pd

# set up logging
# get the top-level logger object
logger = logging.getLogger()
for handler in logger.handlers: logger.removeHandler(handler)
logger.setLevel(logging.INFO)
# make it print to the console.
console = logging.StreamHandler()
logger.addHandler(console)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# name of the current folder with script
dataset_name = 'req_019_facebook_total_precipitation' #check

logger.info('Executing script for dataset: ' + dataset_name)
# first, set the directory that you are working in with the path variable
path = os.path.abspath(os.path.join(os.getenv('BLOG_DIR'), dataset_name))
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)
# move to data directory
# os.chdir(DATA_DIR)

'''
Download data and save to your data directory
'''
logger.info('Downloading raw data')
# list the urls used to download the data from the source website
url_list = ['https://opendata.dwd.de/climate_environment/GPCC/full_data_monthly_v2020/025/full_data_monthly_v2020_1891_1900_025.nc.gz',
            'https://opendata.dwd.de/climate_environment/GPCC/full_data_monthly_v2020/025/full_data_monthly_v2020_1901_1910_025.nc.gz',
            'https://opendata.dwd.de/climate_environment/GPCC/full_data_monthly_v2020/025/full_data_monthly_v2020_1911_1920_025.nc.gz',
            'https://opendata.dwd.de/climate_environment/GPCC/full_data_monthly_v2020/025/full_data_monthly_v2020_1921_1930_025.nc.gz',
            'https://opendata.dwd.de/climate_environment/GPCC/full_data_monthly_v2020/025/full_data_monthly_v2020_1931_1940_025.nc.gz',
            'https://opendata.dwd.de/climate_environment/GPCC/full_data_monthly_v2020/025/full_data_monthly_v2020_1941_1950_025.nc.gz',
            'https://opendata.dwd.de/climate_environment/GPCC/full_data_monthly_v2020/025/full_data_monthly_v2020_1951_1960_025.nc.gz',
            'https://opendata.dwd.de/climate_environment/GPCC/full_data_monthly_v2020/025/full_data_monthly_v2020_1961_1970_025.nc.gz',
            'https://opendata.dwd.de/climate_environment/GPCC/full_data_monthly_v2020/025/full_data_monthly_v2020_1971_1980_025.nc.gz',
            'https://opendata.dwd.de/climate_environment/GPCC/full_data_monthly_v2020/025/full_data_monthly_v2020_1981_1990_025.nc.gz',
            'https://opendata.dwd.de/climate_environment/GPCC/full_data_monthly_v2020/025/full_data_monthly_v2020_1991_2000_025.nc.gz',
            'https://opendata.dwd.de/climate_environment/GPCC/full_data_monthly_v2020/025/full_data_monthly_v2020_2001_2010_025.nc.gz',
            'https://opendata.dwd.de/climate_environment/GPCC/full_data_monthly_v2020/025/full_data_monthly_v2020_2011_2019_025.nc.gz']

# download the data from the source
raw_data_file = [os.path.join(DATA_DIR,os.path.basename(url)) for url in url_list]
for url, file in zip(url_list, raw_data_file):
     urllib.request.urlretrieve(url, file)

# unzip source data
raw_data_file_unzipped = [file[:-3] for file in raw_data_file]
for file,file_unzipped in zip(raw_data_file,raw_data_file_unzipped):
    with gzip.open(file, 'rb') as f_in:
        with open(file_unzipped, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

# convert the netcdf files to tif files
for raw_file in raw_data_file_unzipped:
    util_files.convert_netcdf(raw_file, ['precip'])
processed_data_file = [os.path.join(raw_file[:-3]+'_precip.tif') for raw_file in raw_data_file_unzipped]

processed_data_annual=[os.path.join(DATA_DIR,'full_data_annual_v2020_'+str(year)+'_025_precip.tif') for year in range(1891,2020)]
n_layers=[int(rasterio.open(file).meta['count']/12) for file in processed_data_file]

# calculate annual total precipitation
for id, file in enumerate(processed_data_file,start=0):
    with rasterio.open(file) as src0:
        # update metedata for annual aggregation
        meta = src0.meta
        meta.update(count = 1)
        meta.update(nodata = meta['nodata']*12)
        # sum and export annual total precipitation as tif file
        for i in range(int(src0.meta['count']/12)):
            with rasterio.open(processed_data_annual[sum(n_layers[:id])+i], 'w', **meta) as dst:
                dst.write_band(1,np.sum(src0.read(range((i*12+1), (i*12+13))), axis = 0))

'''
Calculate country-level and state-level mean annual total precipitation
'''
# define countries to calculate statistics for
country_list = ["USA","GBR","FRA","DEU","CAN", "SWE", "BRA", "MEX", "BEL", "IRL", "NLD", "NGA", "SAU", "ZAF", "ESP", "IND", "IDN", "TWN"]

# load country and state shapefile
shapefile_country = gpd.read_file(os.path.join(DATA_DIR, 'gadm36_0.shp'))
shapefile_state = gpd.read_file(os.path.join(DATA_DIR, 'gadm36_1.shp'))

# subset to selected countries
shapefile_country_sub = shapefile_country[shapefile_country['GID_0'].isin(country_list)]
shapefile_state_sub = shapefile_state[shapefile_state['GID_0'].isin(country_list)]

# convert to dataframe and drop the geometry info
shapefile_country_df = pd.DataFrame(shapefile_country_sub)
shapefile_country_df.drop(['geometry'], axis=1, inplace=True)
shapefile_state_df = pd.DataFrame(shapefile_state_sub)
shapefile_state_df.drop(['geometry'], axis=1, inplace=True)

country_mean = shapefile_country_df.copy().reset_index().drop(['index'], axis=1)
state_mean = shapefile_state_df.copy().reset_index().drop(['index'], axis=1)

for tif in processed_data_annual:
    country_stats = rasterstats.zonal_stats(shapefile_country_sub, tif, stats = ['mean'])
    country_stats_df = pd.DataFrame(country_stats)
    country_mean[str(tif[-19:-15])] = country_stats_df['mean']

    state_stats = rasterstats.zonal_stats(shapefile_state_sub, tif, stats = ['mean'])
    state_stats_df = pd.DataFrame(state_stats)
    state_mean[str(tif[-19:-15])] = state_stats_df['mean']
    
# export to csv files
country_mean.to_csv(os.path.join('results', 'GPCC_annual_country_level_mean.csv'), index = False)
state_mean.to_csv(os.path.join('results', 'GPCC_annual_state_level_mean.csv'), index = False)
