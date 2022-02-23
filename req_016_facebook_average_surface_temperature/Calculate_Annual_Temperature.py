import numpy as np
import os
import sys
from dotenv import load_dotenv

load_dotenv() 
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
import urllib
import logging
import gzip
import shutil
import rasterio
import subprocess
import geopandas as gpd
import pandas as pd
from rasterstats import zonal_stats
import rasterio
import fiona
#import glob

# set up logging
# get the top-level logger object
logger = logging.getLogger()
for handler in logger.handlers: logger.removeHandler(handler)
logger.setLevel(logging.INFO)
# make it print to the console.
console = logging.StreamHandler()
logger.addHandler(console)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# name of asset on GEE where you want to upload data
# this should be an asset name that is not currently in use
dataset_name = 'req_016_facebook_average_surface_temperature' #check

logger.info('Executing script for dataset: ' + dataset_name)
# first, set the directory that you are working in with the path variable
path = os.path.abspath(os.path.join(os.getenv('BLOG_DIR'),dataset_name))
# move to this directory
os.chdir(path)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = 'data'
if not os.path.exists(data_dir):
    os.mkdir(data_dir)
os.chdir(data_dir)

'''
Download data and save to your data directory
'''
logger.info('Downloading raw data')
# list the urls used to download the data from the source website
url = 'ftp://ftp.cdc.noaa.gov/Datasets/ghcncams/air.mon.mean.nc'

# download the data from the source
raw_data_file = os.path.basename(url)
centered_data_file = 'air.mon.mean.centered.nc'
annual_data_file = 'air.annual.mean.nc'
processed_data_file_convention = 'annual_{}.nc'
urllib.request.urlretrieve(url, raw_data_file)

# Define command to shift longitude range
cmd = ('cdo sellonlatbox,-180,180,-90,90 {} {}'.format(raw_data_file,centered_data_file))
# Run command
subprocess.check_output(cmd,shell=True)

# Define command to calculate annual temperatures from monthly temperatures
cmd = ('cdo yearmean {} {}'.format(centered_data_file,annual_data_file))
# Run command
subprocess.check_output(cmd,shell=True)

#Define years to separate netcdf for
years = np.arange(1950,2021)

#Loop through years
for year in years:
    #define command to separate netcdf by one year
    cmd = ('cdo -selyear,{} {} {}'.format(year,annual_data_file,processed_data_file_convention.format(year)))
    subprocess.check_output(cmd,shell=True)

# convert the netcdf files to tif files
processed_data_files = [processed_data_file_convention.format(year) for year in years]
for raw_file in processed_data_files:
    util_files.convert_netcdf(raw_file, ['air'])
processed_data_annual = [os.path.join(raw_file[:-3]+'_air.tif') for raw_file in processed_data_files]

#Function for calculating the average temperature per year
def calculate_average_temperature_per_year(years, regionsFile, output_file,kelvinToCelsius=-273.15):
    #read in regions
    regions = gpd.read_file(regionsFile)
    #loop through years
    for year in years:
        #find raster for that year
        pathToRaster = [x for x in processed_data_annual if str(year) in x][0]
        #calculate average per region within regions geodataframe
        meanDF = pd.DataFrame(zonal_stats(regions, pathToRaster,stats=['mean']))
        #Convert kelvin to celsius
        meanDF.mean = meanDF.mean+kelvinToCelsius
        #rename column to year
        meanDF.columns = str(year)
        #concat to regions file
        regions = pd.concat([regions, meanDF], axis=1) 
    #save file
    regions.to_csv(output_file,index=False)

#Define shapefiles for global, country, and state level geometries
globalFile = os.path.join(os.getenv('GADM_DIR'),'global.shp')
countriesFile = os.path.join(os.getenv('GADM_DIR'),'gadm36_0.shp')
statesFile = os.path.join(os.getenv('GADM_DIR'),'gadm36_1.shp')

#Use function to calculate temperature anomalies and export
calculate_average_temperature_per_year(years, globalFile, 'Average_Temperature_Global_Level.csv', output_folder,kelvinToCelsius=-273.15)
calculate_average_temperature_per_year(years, countriesFile, 'Average_Temperature_Country_Level.csv', output_folder,kelvinToCelsius=-273.15)
calculate_average_temperature_per_year(years, statesFile, 'Average_Temperature_State_Level.csv', output_folder,kelvinToCelsius=-273.15)
