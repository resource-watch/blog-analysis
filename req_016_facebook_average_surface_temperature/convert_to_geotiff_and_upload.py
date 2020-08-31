'''
This code converts the monthly temperature NetCDF's and converts them to Geotiff format to upload to Google Earth Engine
'''

import netCDF4 as nc
import numpy as np
import os
import glob
import subprocess

from osgeo import gdal, gdalconst, osr, gdal_array
from collections import OrderedDict
import netCDF4 as nc
import rasterio
import datetime
import logging
import calendar

    
#Define collection
EE_COLLECTION = 'projects/resource-watch-gee/Facebook/TemperatureAnalysis/GHCN_CAMS'
#Define google storage bucket
GS_BUCKET = 'gs://kristine-upload'
#Define no data value (which will be overwritten later)
NDV = -9.96921e+36
#Define number of assets to upload at once
NUM_ASSETS_AT_ONCE = 50
#Set variable to pause every once in a while to allow all assets to upload
PAUSE_FOR_OVERLOAD = True

#Read no data value
with rasterio.open('air.mon.mean.centered.tif', 'r') as src:
    NDV = src.nodatavals[0]

#Change directory
os.chdir('MonthlyNetCDF')

#List all monthly NetCDF files and list them in alphabetical order
in_file_list = glob.glob('*.nc')
in_file_list.sort()

#Define empty list of task ids to save
task_ids = ['']*len(in_file_list)


#Loop through each file
for i, in_file in enumerate(in_file_list):
    #Draw out time stamps for each file, including the first day of the month and last day of the month
    date_string = in_file.split('.')[0]
    year = date_string.split('-')[0]
    month = date_string.split('-')[1]
    day = date_string.split('-')[2]
    last_day = calendar.monthrange(int(year),int(month))[1]
    start_date = datetime.datetime.strptime(date_string, '%Y-%m-%d')
    end_date = datetime.datetime.strptime('{}-{}-{}'.format(year,month,last_day), '%Y-%m-%d')
    
    #Define output name
    out_file_name = date_string.replace('-','_')

    #Convert to geotiff
    cmd = ('gdal_translate -a_srs EPSG:4326 -of GTiff -a_nodata {} NETCDF:"{}":air {}.tif'.format(NDV, in_file,out_file_name))
    subprocess.check_output(cmd,shell=True)

    #Upload geotiff to staging bucket
    cmd = ('gsutil -m cp {}.tif {}'.format(out_file_name,GS_BUCKET))
    subprocess.check_output(cmd,shell=True)

    #Define asset ID
    asset_id = os.path.join(EE_COLLECTION,out_file_name)

    #Upload tiff from bucket to image on Earth Engine and get Task ID
    cmd = ('earthengine upload image --asset_id={} --force --nodata_value={} --time_start={} --time_end={} {}'.format(asset_id,NDV,start_date.strftime("%Y-%m-%d"),end_date.strftime("%Y-%m-%d"),os.path.join(GS_BUCKET,'{}.tif'.format(out_file_name))))
    shell_output = subprocess.check_output(cmd,shell=True)
    shell_output = shell_output.decode("utf-8")
    
    #Get task id
    if 'Started upload task with ID' in shell_output:
        task_id = shell_output.split(': ')[1]
        task_id = task_id.strip()
        #Save task id to task id list
        task_ids[i] = task_id
    else:
        print('Something went wrong!')
        
    #Remove tiff from  folder
    os.remove('{}.tif'.format(out_file_name))

    #If pause for overload is set to true, every NUM_ASSETS_AT_ONCE timesteps, wait for all tasks to finish and remove files from gsutil
    if PAUSE_FOR_OVERLOAD:
        if (i% NUM_ASSETS_AT_ONCE == 0) and (i>0):
            #Wait for all tasks to finish
            cmd = ['earthengine','task','wait','all']
            subprocess.call(cmd)
            
            
#Loop thorugh and remove from google cloud storage
for i, in_file in enumerate(in_file_list):
    date_string = in_file.split('.')[0]
    out_file_name = date_string.replace('-','_')
    asset_id = os.path.join(EE_COLLECTION,out_file_name)
    
    #Make sure it finished uploading to google earth engine
    cmd = ('earthengine task wait {}'.format(task_ids[i]))
    subprocess.check_output(cmd,shell=True)

    #Remove tiff from google cloud bucket
    cmd = ('gsutil rm {}'.format(os.path.join(GS_BUCKET,'{}.tif'.format(out_file_name))))
    subprocess.check_output(cmd,shell=True)


