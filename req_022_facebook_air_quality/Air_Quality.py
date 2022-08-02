from __future__ import unicode_literals

import logging
import pandas as pd
import os
import geopandas as gpd
import sys
import urllib
import datetime
import subprocess
import urllib.request
import rasterstats
import rasterio
import time
from string import ascii_uppercase
from datetime import date
import sys

# Set up logging
# Get the top-level logger object
logger = logging.getLogger()
for handler in logger.handlers: logger.removeHandler(handler)
logger.setLevel(logging.INFO)
# make it print to the console.
console = logging.StreamHandler()
logger.addHandler(console)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Get script folder
os.chdir(os.path.dirname(os.path.realpath(__file__)))
# Define working folder
DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
# os.chdir(data_dir)

# url for historical air quality data
SOURCE_URL_HISTORICAL = 'https://portal.nccs.nasa.gov/datashare/gmao/geos-cf/v1/das/Y{year}/M{month}/D{day}/GEOS-CF.v01.rpl.chm_tavg_1hr_g1440x721_v1.{year}{month}{day}_{time}z.nc4'

# url for forecast air quality data
SOURCE_URL_FORECAST = 'https://portal.nccs.nasa.gov/datashare/gmao/geos-cf/v1/forecast/Y{start_year}/M{start_month}/D{start_day}/H12/GEOS-CF.v01.fcst.chm_tavg_1hr_g1440x721_v1.{start_year}{start_month}{start_day}_12z+{year}{month}{day}_{time}z.nc4'

# subdataset to be converted to tif
# should be of the format 'NETCDF:"filename.nc":variable'
SDS_NAME = 'NETCDF:"{fname}":{var}'

# list variables (as named in netcdf) that we want to pull
VARS = ['NO2', 'O3', 'PM25_RH35_GCC']

# define unit conversion factors for each compound
CONVERSION_FACTORS = {
    'NO2': 1e9, # mol/mol to ppb
    'O3': 1e9, # mol/mol to ppb
    'PM25_RH35_GCC': 1,  # keep original units
}

# define metrics to calculate for each compound
# each metric is the name of a function defined in this script
# available metrics: daily_avg, daily_max
METRIC_BY_COMPOUND = {
    'NO2': 'daily_avg',
    'O3': 'daily_max',
    'PM25_RH35_GCC': 'daily_avg',
}

# nodata value for netcdf
NODATA_VALUE = 9.9999999E14

# generate generic string that can be formatted to name each variable's asset name
FILENAME = 'gmao_air_quality_{period}_{metric}_{var}_{date}'

# date format to use in GEE
DATE_FORMAT = '%Y-%m-%d'

# load state level global shapefile as geodataframe
state_shp = gpd.read_file(os.path.join(DATA_DIR, "gadm36_1.shp"))
# convert to dataframe and drop the geometry info
state_shp_df = pd.DataFrame(state_shp)
state_shp_df.drop(['geometry'], axis=1, inplace=True)


def fetch(new_date, first_date, unformatted_source_url, period):
    '''
    Fetch files by datestamp
    INPUT   new_date: date we want to try to fetch, in the format YYYY-MM-DD (string)
            first_date: a day before the new date (string)
            unformatted_source_url: url for air quality data (string)
            period: period for which we want to get the data, historical or forecast (string)
    RETURN  files: list of file names for netcdfs that have been downloaded (list of strings)
            files_by_date: dictionary of file names along with the date for which they were downloaded (dictionary of strings)
    '''
    # make an empty list to store names of the files we downloaded
    files = []
    # create a list of hours to pull (24 hours per day, on the half-hour)
    # starts after noon on previous day through noon of current day
    hours = ['1230', '1330', '1430', '1530', '1630', '1730', '1830', '1930', '2030', '2130', '2230', '2330',
             '0030', '0130', '0230', '0330', '0430', '0530', '0630', '0730', '0830', '0930', '1030', '1130']
    # create an empty dictionary to store downloaded file names as value and corresponding dates as key
    files_by_date = {}
    # Loop over all hours of the new dates, check if there is data available, and download netcdfs
    # make an empty list to store names of the files we downloaded
    # this list will be used to insert values to the "files_by_date" dictionary
    files_for_current_date = []
    # loop through each hours we want to pull data for
    for hour in hours:
        # for the first half of the hours, get data from previous day
        if hours.index(hour) < 12:
            # convert date string to datetime object and go back one day
            prev_date = datetime.datetime.strptime(new_date, DATE_FORMAT) - datetime.timedelta(days=1)
            # generate a string from the datetime object
            fetching_date = datetime.datetime.strftime(prev_date, DATE_FORMAT)
        # for the second half, use the current day
        else:
            fetching_date = new_date
        # Set up the url of the filename to download historical data
        if period=='historical':
            url = unformatted_source_url.format(year=int(fetching_date[:4]), month='{:02d}'.format(int(fetching_date[5:7])), day='{:02d}'.format(int(fetching_date[8:])), time=hour)
        # Set up the url of the filename to download forecast data
        elif period=='forecast':
            url = unformatted_source_url.format(start_year=int(first_date[:4]), start_month='{:02d}'.format(int(first_date[5:7])), start_day='{:02d}'.format(int(first_date[8:])),year=int(fetching_date[:4]), month='{:02d}'.format(int(fetching_date[5:7])), day='{:02d}'.format(int(fetching_date[8:])), time=hour)
        # Create a file name to store the netcdf in after download
        f = DATA_DIR+'/'+url.split('/')[-1]
        # try to download the data
        tries = 1
        while tries <= 5:
            try:
                logging.info('Retrieving {}'.format(f))
                # download if the file does not exist already
                if not os.path.exists(f):
                    # download files from url and put in specified file location (f)
                    urllib.request.urlretrieve(url, f)
                else:
                    # otherwise skip download
                    logging.info('{} is already downloaded'.format(f))
                # if successful, add the file to the list of files we have downloaded 
                files.append(f)
                files_for_current_date.append(f)
                break
            # if unsuccessful, log that the file was not downloaded
            except Exception as e:
                logging.info('Unable to retrieve data from {}, trying again'.format(url))
                tries += 1
                time.sleep(30)
                logging.info('try {}'.format(tries))
        if tries == 6:
            logging.error('Unable to retrieve data from {}'.format(url))
            exit()

    # populate dictionary of file names along with the date for which they were downloaded
    files_by_date[new_date] = files_for_current_date

    return files, files_by_date

def getTiffName(file, period, var):
    '''
    generate names for tif files that we are going to create from netcdf
    INPUT   file: netcdf filename (string)
            period: period to be used in tif name, historical or forecast(string)
            var: variable to be used in tif name (string)
    RETURN  name: file name to save tif file created from netcdf (string)
    '''
    # get year, month, day, and time from netcdf filename
    year = file.split('/')[1][-18:-14]
    month = file.split('/')[1][-14:-12]
    day = file.split('/')[1][-12:-10]
    time = file.split('/')[1][-9:-5]
    # generate date string to be used in tif file name
    date = year+'-'+month+'-'+day +'_'+time
    # generate name for tif file
    name = os.path.join(DATA_DIR, FILENAME.format(period=period, metric=METRIC_BY_COMPOUND[var], var=var, date=date))+'.tif'
    return name


def convert(files, var, period):
    '''
    Convert netcdf files to tifs
    INPUT   files: list of file names for netcdfs that have already been downloaded (list of strings)
            var: variable which we are converting files for (string)
            period: period we are converting data for, historical or forecast (string)
    RETURN  tifs: list of file names for tifs that have been generated (list of strings)
    '''
    # make an empty list to store the names of tif files that we create
    tifs = []
    for f in files:
        logging.info('Converting {} to tiff'.format(f))
        
        
        # generate the subdatset name for current netcdf file for a particular variable
        sds_path = SDS_NAME.format(fname=f, var=var)
        # only one band available in each file, so we will pull band 1
        band = 1
        # generate a name to save the tif file we will translate the netcdf file into
        tif = getTiffName(file=f, period=period, var=var)
        # translate the netcdf into a tif
        if not os.path.exists(tif):
            cmd = ['gdal_translate', '-b', str(band), '-q', '-a_nodata', str(NODATA_VALUE), '-a_srs', 'EPSG:4326', sds_path, tif]
            subprocess.call(cmd)
        # add the new tif files to the list of tifs
        tifs.append(tif)

    return tifs

def getDateTimeString(filename):
    '''
    get date from filename (last 10 characters of filename after removing extension)
    INPUT   filename: file name that ends in a date of the format YYYY-MM-DD (string)
    RETURN  date in the format YYYY-MM-DD (string)
    '''
    return os.path.splitext(os.path.basename(filename))[0][-10:]

def daily_avg(date, var, period, tifs_for_date):
    '''
    Calculate a daily average tif file from all the hourly tif files
    INPUT   date: list of dates we want to try to fetch, in the format YYYY-MM-DD (list of strings)
            var: variable for which we are taking daily averages (string)
            period: period for which we are calculating metric, historical or forecast (string)
            tifs_for_date: list of file names for tifs that were created from downloaded netcdfs (list of strings)
    RETURN  result_tif: file name for tif file created after averaging all the input tifs (string)
    '''
    # create a list to store the tifs and variable names to be used in gdal_calc
    gdal_tif_list=[]
    # set up calc input for gdal_calc
    calc = '--calc="('
    # go through each hour in the day to be averaged
    for i in range(len(tifs_for_date)):
        # generate a letter variable for that tif to use in gdal_calc (A, B, C...)
        letter = ascii_uppercase[i]
        # add each letter to the list to be used in gdal_calc
        gdal_tif_list.append('-'+letter)
        # pull the tif name
        tif = tifs_for_date[i]
        # add each tif name to the list to be used in gdal_calc
        gdal_tif_list.append('"'+tif+'"')
        # add the variable to the calc input for gdal_calc
        if i==0:
            # for first tif, it will be like: --calc="(A
            calc= calc +letter
        else:
            # for second tif and onwards, keep adding each letter like: --calc="(A+B
            calc = calc+'+'+letter
    # calculate the number of tifs we are averaging
    num_tifs = len(tifs_for_date)
    # finish creating calc input
    # since we are trying to find average, the algorithm is: (sum all tifs/number of tifs)*(conversion factor for corresponding variable)
    calc= calc + ')*{}/{}"'.format(CONVERSION_FACTORS[var], num_tifs)
    # generate a file name for the daily average tif
    result_tif = DATA_DIR+'/'+FILENAME.format(period=period, metric=METRIC_BY_COMPOUND[var], var=var, date=date)+'.tif'
    # create the gdal command to calculate the average by putting it all together
    cmd = ('gdal_calc.py {} --outfile="{}" {}').format(' '.join(gdal_tif_list), result_tif, calc)
    # using gdal from command line from inside python
    subprocess.check_output(cmd, shell=True)
    return result_tif

def daily_max(date, var, period, tifs_for_date):
    '''
    Calculate a daily maximum tif file from all the hourly tif files
    INPUT   date: list of dates we want to try to fetch, in the format YYYY-MM-DD (list of strings)
            var: variable for which we are taking daily averages (string)
            period: period for which we are calculating metric, historical or forecast (string)
            tifs_for_date: list of file names for tifs that were created from downloaded netcdfs (list of strings)
    RETURN  result_tif: file name for tif file created after finding the max from all the input tifs (string)
    '''
    # create a list to store the tifs and variable names to be used in gdal_calc
    gdal_tif_list=[]

    # go through each hour in the day to find the maximum
    for i in range(len(tifs_for_date)):
        # generate a letter variable for that tif to use in gdal_calc
        letter = ascii_uppercase[i]
        # add each letter to the list of tifs to be used in gdal_calc
        gdal_tif_list.append('-'+letter)
        # pull the tif name
        tif = tifs_for_date[i]
        # add each tif name to the list to be used in gdal_calc
        gdal_tif_list.append('"'+tif+'"')
        #add the variable to the calc input for gdal_calc
        if i == 0:
            calc = letter
        else:
            # set up calc input for gdal_calc to find the maximum from all tifs
            calc = 'maximum('+calc+','+letter+')'
    # finish creating calc input
    calc = '--calc="'+calc + '*{}"'.format(CONVERSION_FACTORS[var])
    #generate a file name for the daily maximum tif
    result_tif = DATA_DIR+'/'+FILENAME.format(period=period, metric=METRIC_BY_COMPOUND[var], var=var, date=date)+'.tif'
    # create the gdal command to calculate the maximum by putting it all together
    cmd = ('gdal_calc.py {} --outfile="{}" {}').format(' '.join(gdal_tif_list), result_tif, calc)
    # using gdal from command line from inside python
    subprocess.check_output(cmd, shell=True)
    return result_tif


def processNewData(var, all_files, files_by_date, period):
    '''
    Process and upload clean new data
    INPUT   var: variable that we are processing data for (string)
            all_files: list of file names for netcdfs that have been downloaded (list of strings)
            files_by_date: dictionary of netcdf file names along with the date for which they were downloaded (dictionary of strings)
            period: period for which we want to process the data, historical or forecast (string)
    RETURN  assets: list of file names for netcdfs that have been downloaded (list of strings)
    '''
    # if files is empty list do nothing, otherwise, process data
    if all_files:
        # create an empty list to store the names of the tifs we generate
        tifs = []
        # create an empty list to store the list of dates from the averaged or maximum tifs
        dates = []
        # create an empty list to store the list of datetime objects from the averaged or maximum tifs
        datestamps = []
        # loop over each downloaded netcdf file
        for date, files in files_by_date.items():
            logging.info('Converting files')
            # Convert new files from netcdf to tif files
            hourly_tifs = convert(files, var, period)
            # take relevant metric (daily average or maximum) of hourly tif files for days we have pulled
            metric = METRIC_BY_COMPOUND[var]
            tif = globals()[metric](date, var, period, hourly_tifs)
            # add the averaged or maximum tif file to the list of files to upload to GEE
            tifs.append(tif)
            # get new list of date strings (in case order is different) from the processed tifs
            dates.append(getDateTimeString(tif))
            # generate datetime objects for each tif date
            datestamps.append(datetime.datetime.strptime(date, DATE_FORMAT))

        return tifs
    #if no new assets, return empty list
    else:
        return []

def zonal_statistics(tifs, var, state_shp_df):
    '''
    Zonal statistics to calculate the state-level daily mean or max
    INPUT   tifs: list of file names for tifs (list)
            var: variable that we are processing data for (string)
            state_shp_df: state-level shapefile without geometry info (dataframe)
    RETURN  assets: list of file names for netcdfs that have been downloaded (list of strings)
    '''
    for tif in tifs:
        if var == 'O3':
            #calculate average per region within regions geodataframe
            with rasterio.open(tif) as src:
                affine = src.transform
                array = src.read(1)
                stats = rasterstats.zonal_stats(os.path.join(DATA_DIR, 'gadm36_1.shp'), array, affine=affine,nodata = NODATA_VALUE,stats=['max'],all_touched=True)
                stats_df = pd.DataFrame(stats)
            
            state_max = state_shp_df.copy()
            state_max[str(var)+'_max'] = stats_df['max']
            return state_max
            # state_max.to_csv(tif.split('.')[0]+'_state_max.csv', index = False)
        else:
            with rasterio.open(tif) as src:
                affine = src.transform
                array = src.read(1)
                stats = rasterstats.zonal_stats(os.path.join(DATA_DIR, 'gadm36_1.shp'), array, affine=affine, nodata = NODATA_VALUE, stats = ['mean'],all_touched=True)
                stats_df = pd.DataFrame(stats)
            
            state_mean = state_shp_df.copy()
            state_mean[str(var)+'_mean'] = stats_df['mean']
            return state_mean
            # state_mean.to_csv(tif.split('.')[0]+'_state_mean.csv', index = False)

def delete_local(ext=None):
    '''
    This function will delete local files in the Docker container with a specific extension, if specified.
    If no extension is specified, all local files will be deleted.
    INPUT   ext: optional, file extension for files you want to delete, ex: '.tif' (string)
    '''
    try:
        if ext:
            files = [file for file in os.listdir(DATA_DIR) if file.endswith(ext)]
        else:
            files = os.listdir(DATA_DIR)
        for f in files:
            logging.info('Removing {}'.format(f))
            os.remove(DATA_DIR+'/'+f)
    except NameError:
        logging.info('No local files to clean.')

def main(new_date_historical):
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)

    '''
    Process Historical Data
    '''
    logging.info('Starting Historical Data Processing')

    # Get a new date that we want to pull data for.
    logging.info('Getting new dates to pull.')

    # convert date string to datetime object and go back one day, and generate a string from the datetime object
    first_date = (datetime.datetime.strptime(new_date_historical, DATE_FORMAT) - datetime.timedelta(days=1)).strftime(DATE_FORMAT)

    # Fetch new files
    logging.info('Fetching files for {}'.format(new_date_historical))
    files, files_by_date = fetch(new_date_historical, first_date, SOURCE_URL_HISTORICAL, period='historical')

    # Process historical data, one variable at a time
    for var_num in range(len(VARS)):
        logging.info('Processing {}'.format(VARS[var_num]))
        # get variable name
        var = VARS[var_num]

        # Process new data files, don't delete any historical assets
        new_tifs_historical = processNewData(var, files, files_by_date, period='historical')
        state_zonal_var = zonal_statistics(new_tifs_historical, var, state_shp_df)
        if var_num == 0:
            state_zonal = state_zonal_var.copy()
        else:
            state_zonal = state_zonal.join(state_zonal_var.iloc[:,-1])

        # create a list of hours to pull (24 hours per day, on the half-hour)
        # starts after noon on previous day through noon of current day
        hours = ['1230', '1330', '1430', '1530', '1630', '1730', '1830', '1930', '2030', '2130', '2230', '2330',
                '0030', '0130', '0230', '0330', '0430', '0530', '0630', '0730', '0830', '0930', '1030', '1130']
        for hour in hours:
            # Delete local tiff files because we will run out of space
            delete_local(ext=hour+'.tif')

    state_zonal.to_csv(os.path.join(DATA_DIR, f'gmao_air_quality_historical_{new_date_historical}'+'_state.csv'), index = False)
    # Delete local netcdf files because we will run out of space
    delete_local(ext='.nc4')

    '''
    Process Forecast Data
    '''
    logging.info('Starting Forecast Data Processing')

    # Get a list of the dates that are available.
    logging.info('Getting new dates to pull.')
    new_dates_forecast = [(datetime.datetime.strptime(new_date_historical, DATE_FORMAT)+ datetime.timedelta(days=x)).strftime(DATE_FORMAT) for x in [1,2,3,4,5]]
    logging.info('New dates:',new_dates_forecast)

    if new_dates_forecast:
        # convert date string to datetime object and go back one day
        first_date = datetime.datetime.strptime(new_dates_forecast[0], DATE_FORMAT) - datetime.timedelta(days=1)
        # generate a string from the datetime object
        first_date = datetime.datetime.strftime(first_date, DATE_FORMAT)
    # Fetch new files
    logging.info('Fetching files for {}'.format(new_dates_forecast))
    
    for new_date_forecast in new_dates_forecast:
        files, files_by_date = fetch(new_date_forecast, first_date, SOURCE_URL_FORECAST, period='forecast')

        # Process forecast data, one variable at a time
        for var_num in range(len(VARS)):
            logging.info('Processing {}'.format(VARS[var_num]))
            # get variable name
            var = VARS[var_num]

            # Process new data files, delete all forecast assets currently in collection
            if new_date_forecast == new_dates_forecast[0]:
                new_tifs_forecast = processNewData(var, files, files_by_date, period='forecast')
            else:
                new_tifs_forecast = processNewData(var, files, files_by_date, period='forecast')
            state_zonal_var = zonal_statistics(new_tifs_forecast, var, state_shp_df)
            
            if var_num == 0:
                state_zonal = state_zonal_var.copy()
            else:
                state_zonal = state_zonal.join(state_zonal_var.iloc[:,-1])

            # create a list of hours to pull (24 hours per day, on the half-hour)
            # starts after noon on previous day through noon of current day
            hours = ['1230', '1330', '1430', '1530', '1630', '1730', '1830', '1930', '2030', '2130', '2230', '2330',
                    '0030', '0130', '0230', '0330', '0430', '0530', '0630', '0730', '0830', '0930', '1030', '1130']
            for hour in hours:
                # Delete local tiff files because we will run out of space
                delete_local(ext=hour+'.tif')

        state_zonal.to_csv(os.path.join(DATA_DIR, f'gmao_air_quality_forecast_{new_date_forecast}'+'_state.csv'), index = False)
        # Delete local netcdf files because we will run out of space
        delete_local(ext='.nc4')

#Check if the argument is set for the date to download data
if len(sys.argv) == 1:
    logging.info('Please add an arugment for the date you want to download air quality forecasts for in the format YYYY-MM-DD')
    logging.info('For example run: python Air_Quality.py 2022-07-12')
#If it is then run the program
else:  
    main(sys.argv[1])
