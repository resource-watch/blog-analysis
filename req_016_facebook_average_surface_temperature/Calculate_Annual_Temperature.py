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
import ee
from google.cloud import storage
import logging
import gzip
import shutil
import rasterio
import subprocess


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

'''
Upload processed data to Google Earth Engine
'''
logger.info('Uploading processed data to Google Cloud Storage.')
# set up Google Cloud Storage project and bucket objects
print(os.environ.get("CLOUDSDK_CORE_PROJECT"))
gcsClient = storage.Client(os.environ.get("CLOUDSDK_CORE_PROJECT"))
gcsBucket = gcsClient.bucket(os.environ.get("GEE_STAGING_BUCKET"))

# upload files to Google Cloud Storage
gcs_uris= util_cloud.gcs_upload(processed_data_annual, dataset_name, gcs_bucket=gcsBucket)

logger.info('Uploading processed data to Google Earth Engine.')
# initialize ee and eeUtil modules for uploading to Google Earth Engine
auth = ee.ServiceAccountCredentials(os.getenv('GEE_SERVICE_ACCOUNT'), os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
ee.Initialize(auth)

# set pyramiding policy for GEE upload
pyramiding_policy = 'MEAN' #check

# create an image collection where we will put the processed data files in GEE
image_collection = f'projects/resource-watch-gee/Facebook/TemperatureAnalysis/GHCN_CAMS_annual'
ee.data.createAsset({'type': 'ImageCollection'}, image_collection)

# set image collection's privacy to public
acl = {"all_users_can_read": True}
ee.data.setAssetAcl(image_collection, acl)
print('Privacy set to public.')

# list the bands in each image
band_ids = ['b1']

task_id = []
# upload processed data files to GEE
for uri in gcs_uris:
    # generate an asset name for the current file by using the filename (minus the file type extension)
    asset_name = f'projects/resource-watch-gee/Facebook/TemperatureAnalysis/GHCN_CAMS_annual/{os.path.basename(uri)[:-4]}'
    # create the band manifest for this asset
    mf_bands = [{'id': band_id, 'tileset_band_index': band_ids.index(band_id), 'tileset_id': os.path.basename(uri)[:-4],
             'pyramidingPolicy': pyramiding_policy} for band_id in band_ids]
    # create complete manifest for asset upload
    manifest = util_cloud.gee_manifest_complete(asset_name, uri, mf_bands)
    # upload the file from GCS to GEE
    task = util_cloud.gee_ingest(manifest)
    print(asset_name + ' uploaded to GEE')
    task_id.append(task)

# remove files from Google Cloud Storage
util_cloud.gcs_remove(gcs_uris, gcs_bucket=gcsBucket)
logger.info('Files deleted from Google Cloud Storage.')


'''
Data processing on Google Earth Engine
'''
# Initialize earth engine
try:
    ee.Initialize()
except Exception as e:
    ee.Authenticate()
    ee.Initialize()

# load image collection
GHCN_CAMS_annual = ee.ImageCollection("projects/resource-watch-gee/Facebook/TemperatureAnalysis/GHCN_CAMS_annual")

# save projection (crs, crsTransform, scale)
projection = GHCN_CAMS_annual.first().projection().getInfo()
projection_gee = GHCN_CAMS_annual.first().projection()
crs = projection.get('crs')
crsTransform = projection.get('transform')
scale = GHCN_CAMS_annual.first().projection().nominalScale().getInfo()
print('crs: ', crs)
print('crsTransform: ', crsTransform)
print('scale: ', scale)

# convert ImageCollection to Image
band_names = ee.List([str(i) for i in np.arange(1950,2021)])
GHCN_CAMS_annual_img = GHCN_CAMS_annual.toBands()
GHCN_CAMS_annual_img = GHCN_CAMS_annual_img.rename(band_names)
GHCN_CAMS_annual_img = GHCN_CAMS_annual_img.add(ee.Image.constant(-273.15))

# define countries to calculate statistics for
country_list = ["USA","GBR","FRA","DEU","CAN", "SWE", "BRA", "MEX", "BEL", "IRL", "NLD", "NGA", "SAU", "ZAF", "ESP", "IND", "IDN", "TWN"]
# load country and state shapefiles
countries = ee.FeatureCollection("projects/resource-watch-gee/gadm36_0_simplified")
states = ee.FeatureCollection("projects/resource-watch-gee/gadm36_1_simplified")

# Define function for calculating average temperature over feature collection
def calculate_average_temperature_per_feature(feature_collection, output_name, output_folder):
    #Calculate average temperature anomaly for each year for each country
    average_annual_temperature = GHCN_CAMS_annual_img.reduceRegions(feature_collection, 
                                                          ee.Reducer.mean(), 
                                                          crs=crs, crsTransform=crsTransform)
    #Drop geometry information
    average_annual_temperature = average_annual_temperature.map(lambda x: x.select(x.propertyNames(),
                                                                           retainGeometry=False))

    #Export to Google Drive
    export_results_task = ee.batch.Export.table.toDrive(
        collection = average_annual_temperature, 
        description = output_name, 
        fileNamePrefix = output_name,
        folder = output_folder)

    export_results_task.start()


    
#Define countries to calculate statistics for
country_list = ["USA","GBR","FRA","DEU","CAN", "SWE", "BRA", "MEX", "BEL", "IRL", "NLD", "NGA", 
                "SAU", "ZAF", "ESP", "IND", "IDN", "TWN"]
country_list = ee.List(country_list)


#Load country data, filter to desired ISO Codes
countries = ee.FeatureCollection("projects/resource-watch-gee/gadm36_0_simplified")
countries = ee.FeatureCollection(country_list.map(lambda x: countries.filterMetadata('GID_0','equals',
                                                                                     ee.String(x)))).flatten()
# #Use function to calculate temperature anomalies and export
calculate_average_temperature_per_feature(countries,
                                          output_name='Average_Temperature_Country_Level',
                                          output_folder='Facebook')


#Load state data, filter to desired ISO Codes
states = ee.FeatureCollection("projects/resource-watch-gee/gadm36_1_simplified")
states = ee.FeatureCollection(country_list.map(lambda x: states.filterMetadata('GID_0','equals',
                                                                                   ee.String(x)))).flatten()
# #Use function to calculate temperature anomalies and export
calculate_average_temperature_per_feature(states,
                                          output_name='Average_Temperature_State_Level',
                                          output_folder='Facebook')
                                          
# define global bounds for calculating global temperature                                         
land = ee.FeatureCollection("projects/resource-watch-gee/gadm36_0_simplified")
# use bounds because the land mask has too many vertices for Earth Engine, but the data is masked anyway
global_geometry = land.geometry().bounds()

# calculate average temperature over all valid pixels
global_temperature = GHCN_CAMS_annual_img.reduceRegion(reducer=ee.Reducer.mean(), 
                                                     geometry=global_geometry, 
                                                     crs=crs, crsTransform=crsTransform, 
                                                     bestEffort=True, maxPixels=1e13)
# remove geometry
global_temperature_feature = ee.Feature(None,global_temperature)
global_temperature_feature_collection = ee.FeatureCollection(global_temperature_feature)

#Export to Google Drive
output_name='Average_Temperature_Global_Level'
output_folder='Facebook'

export_results_task = ee.batch.Export.table.toDrive(
    collection = global_temperature_feature_collection, 
    description = output_name, 
    fileNamePrefix = output_name,
    folder = output_folder)

export_results_task.start()
