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
from zipfile import ZipFile
import gzip
import shutil
import rasterio
import subprocess
import geopandas as gpd
import pandas as pd
from rasterstats import zonal_stats
import rasterio
import fiona
import glob

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
dataset_name = 'req_022_facebook_climate_simulation' #check

# Get script folder
#os.chdir(os.path.dirname(os.path.realpath(__file__)))
# Define working folder
data_dir = 'data'
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
# os.chdir(data_dir)

results_dir = 'results'
if not os.path.exists(results_dir):
    os.makedirs(results_dir)
# os.chdir(results_dir)
'''
Download data and save to your data directory
Data can be downloaded at the following link:
https://resourcewatch.org/data/explore/4ca6826c-718d-457d-b4e2-e9277d7ed62c?section=Discover&selectedCollection=&zoom=3&lat=0&lng=0&pitch=0&bearing=0&basemap=dark&labels=light&layers=%255B%257B%2522dataset%2522%253A%25224ca6826c-718d-457d-b4e2-e9277d7ed62c%2522%252C%2522opacity%2522%253A1%252C%2522layer%2522%253A%2522341735ff-5773-4cf2-abef-d4a90db10645%2522%257D%255D&aoi=&page=1&sort=most-viewed&sortDirection=-1
A zip file was downloaded (A series of TIF files within the zip file)
'''
# download the data from the source
logger.info('Downloading raw data')
download = (os.path.join(os.path.join(os.path.expanduser("~"),'Downloads', 'nexgddp.zip')))

# move this file into your data directory
raw_data_file = os.path.join(data_dir, os.path.basename(download))
shutil.move(download, raw_data_file)

# unzip nex-gddp data
raw_data_file_unzipped = raw_data_file.split('.')[0]
zip_ref = ZipFile(raw_data_file, 'r')
zip_ref.extractall(raw_data_file_unzipped)
zip_ref.close()

#Function for calculating the average greenhouse gas concentration over a region
def calculate_rcp_over_region(rcp, regionsFile, output_file):
    
    #extract only the files for whatever rcp parameter is given
    nexgddp_dir = "data/nexgddp/*"
    rcp_list = []
    for rcp_number in glob.glob(nexgddp_dir + "*rcp" + rcp + "*"): 
        rcp_list.append(rcp_number)
    
    #read in regions
    regions = gpd.read_file(regionsFile)
    
    count = 0
    for i in rcp_list:
        
        print("Processing", i)

        #calculate average per region within regions geodataframe
        with rasterio.open(i) as src:
            affine = src.transform
            array = src.read(2)
            df_zonal_stats = pd.DataFrame(zonal_stats(regions, array, affine=affine,nodata=1e20))
    
        #concat to regions file
        regions = pd.concat([regions, df_zonal_stats], axis=1)
        regions = regions.loc[:,~regions.columns.duplicated()]

        count = count + 1
        print("Completed", count, "out of", len(rcp_list))
 
    #save file
    regions.to_csv(output_file,index=False)

# load country and state shapefiles
countries = os.path.join(os.getenv('GADM_DIR'),'level0.shp')
states = os.path.join(os.getenv('GADM_DIR'),'level1.shp')

#Use function to calculate mean value and export 
calculate_rcp_over_region('45', countries, 'results/NEX_GDDP_45_countries.csv')
calculate_rcp_over_region('85', countries, 'results/NEX_GDDP_85_countries.csv')
calculate_rcp_over_region('45', states, 'results/NEX_GDDP_45_states.csv')
calculate_rcp_over_region('85', states, 'results/NEX_GDDP_85_states.csv')


    
    
