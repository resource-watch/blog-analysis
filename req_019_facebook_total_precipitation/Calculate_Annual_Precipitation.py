import numpy as np
import os
import sys
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
dataset_name = 'req_019_facebook_total_precipitation' #check

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
raw_data_file = [os.path.join(data_dir,os.path.basename(url)) for url in url_list]
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

processed_data_annual=[os.path.join(data_dir,'full_data_annual_v2020_'+str(year)+'_025_precip.tif') for year in range(1891,2020)]
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
Upload processed data to Google Earth Engine
'''
logger.info('Uploading processed data to Google Cloud Storage.')
# set up Google Cloud Storage project and bucket objects
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
image_collection = f'projects/resource-watch-gee/Facebook/PrecipitationAnalysis/GPCC_annual'
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
    asset_name = f'projects/resource-watch-gee/Facebook/PrecipitationAnalysis/GPCC_annual/{os.path.basename(uri)[:-4]}'
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
GPCC_annual = ee.ImageCollection("projects/resource-watch-gee/Facebook/PrecipitationAnalysis/GPCC_annual")

# save projection (crs, crsTransform, scale)
projection = GPCC_annual.first().projection().getInfo()
projection_gee = GPCC_annual.first().projection()
crs = projection.get('crs')
crsTransform = projection.get('transform')
scale = GPCC_annual.first().projection().nominalScale().getInfo()
print('crs: ', crs)
print('crsTransform: ', crsTransform)
print('scale: ', scale)

# convert ImageCollection to Image
band_names = ee.List([str(i) for i in np.arange(1891,2020)])
GPCC_annual_img = GPCC_annual.toBands()
GPCC_annual_img = GPCC_annual_img.rename(band_names)

# define countries to calculate statistics for
country_list = ["USA","GBR","FRA","DEU","CAN", "SWE", "BRA", "MEX", "BEL", "IRL", "NLD", "NGA", "SAU", "ZAF", "ESP", "IND", "IDN", "TWN"]
# load country and state shapefiles
countries = ee.FeatureCollection("projects/resource-watch-gee/gadm36_0_simplified")
states = ee.FeatureCollection("projects/resource-watch-gee/gadm36_1_simplified")

for country_ios in country_list:
    # national-level analysis
    # load country data, filter to desired ISO Codes
    country = countries.filterMetadata('GID_0', 'equals', ee.String(country_ios))

    # export to Google Drive
    output_name='GPCC_annual_country_'+country_ios
    output_folder='Facebook'
    export_results_task = ee.batch.Export.table.toDrive(
        collection = GPCC_annual_img.reduceRegions(country, ee.Reducer.mean(), scale = scale, tileScale = 16).select(ee.List(['GID_0','NAME_0']).cat(band_names), retainGeometry = False), 
        description = output_name, 
        fileNamePrefix = output_name,
        folder = output_folder)
    # start the task
    export_results_task.start()


    # state-level analysis
    # load state data, filter to desired ISO Codes
    state = states.filterMetadata('GID_0', 'equals', ee.String(country_ios))

    # export to Google Drive
    output_name='GPCC_annual_state_'+country_ios
    output_folder='Facebook'
    export_results_task = ee.batch.Export.table.toDrive(
        collection = GPCC_annual_img.reduceRegions(state, ee.Reducer.mean(), scale = scale, tileScale = 16).select(ee.List(['CC_1','ENGTYPE_1','GID_0','GID_1','HASC_1','NAME_0','NAME_1','NL_NAME_1','TYPE_1','VARNAME_1']).cat(band_names), retainGeometry = False), 
        description = output_name, 
        fileNamePrefix = output_name,
        folder = output_folder)
    # start the task
    export_results_task.start()