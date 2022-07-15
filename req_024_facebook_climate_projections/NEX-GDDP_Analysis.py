import numpy as np
import os
import sys
from dotenv import load_dotenv

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

from numpy import inf


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
dataset_name = 'req_024_facebook_climate_simulation' 

# Define working folder
data_dir = 'data'
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
os.chdir(data_dir)

#Define list of indicators
indicators = [
    'diff-annual_tasmin', #change in minimum temperature
    'diff-annual_tasmax', #change in maximum temperature
    'diff-tavg-tasmin_tasmax', #change in average temperature
    'diff-frostfree_tasmin', #change in length of frost free season
    'diff-gt-q99_tasmax', #change in number of extreme heat days
    'ch-dryspells_pr', #change in lenght of dry spells
    'ch-annual_pr', #change in cumulative precipitation
    'ch-gt-q99_pr' #change in number of extreme precipitation days
]

#Define file format of rasters for each indicator and year
fileFormat = os.path.join(os.getcwd(),'nexgddp/stacked-{}_rcp85_ens_{}_nexgddp.tif')
#Define output file format
outFileFormat = '{}_average.csv'

#Define list of periods
yearCoverageList = ['1985-2015', '1995-2025', '2005-2035', '2015-2045', '2025-2055', '2035-2065', '2045-2075', '2055-2085', '2065-2095']
#Define corresponding list of period centers
yearList = ['2000','2010','2020','2030','2040','2050','2060','2070','2080']

#Function for calculating the average temperature per year
def calculate_nexgddp_average(indicator, regionsFile, output_file):
    print(indicator)
    #read in regions
    regions = gpd.read_file(regionsFile)
    #loop through years
    for i, yearCoverage in enumerate(yearCoverageList):
        print(yearList[i])
        #find raster for that year
        pathToRaster = fileFormat.format(indicator,yearCoverage)
        print(pathToRaster)
        
        #calculate average per region within regions geodataframe
        with rasterio.open(pathToRaster) as src:
            affine = src.transform
            array = src.read(2)
            nodata = src.nodata
            array[array == -inf] = nodata
            array[array == inf] = nodata
            meanDF = pd.DataFrame(zonal_stats(regions, array, affine=affine,nodata=nodata,stats=['mean'],all_touched=True))
        #rename column to year
        meanDF.columns = [yearList[i]]
        #concat to regions file
        regions = pd.concat([regions, meanDF], axis=1) 
    #save file
    region_cols = [x for x in list(regions) if x!='geometry']
    regions = regions[region_cols]
    regions.to_csv(output_file,index=False)

#Run calculation
for i in np.arange(len(indicators)):
    calculate_nexgddp_average(indicators[i],'gadm_levels/gadm36_0.shp', outFileFormat.format(indicators[i]))

