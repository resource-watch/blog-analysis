'''
This code downloads national level (administrative level 0) and state/province level (administrative level 1) boundaries for desired countries, France, Germany, United Kingdom, and United States
The source of the country and state boundaries is GADM (https://gadm.org/index.html)
'''
# Import libraries
#import geopandas as gpd
import os
import shutil
import urllib.request
import zipfile
import glob

# Define working directory
working_dir = 'CountryShapes'
if not os.path.exists(working_dir):
    os.makedirs(working_dir)
os.chdir(working_dir)

# Define countries to separate (using ISO codes)
country_list = ['USA','FRA','DEU','GBR']

# Define URL to download data from GADM
url = 'https://biogeo.ucdavis.edu/data/gadm3.6/shp/gadm36_{}_shp.zip'

# Loop through countries
for country in country_list:
    # Define zip file to download data to
    zip_file_name = os.path.basename(url.format(country))
    
    # Define folder to extract files to 
    download_folder = zip_file_name.split('.')[0]
    # Download data
    urllib.request.urlretrieve(url.format(country), zip_file_name)
    # Extract data
    with zipfile.ZipFile(zip_file_name, 'r') as zip_ref:
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
        zip_ref.extractall(download_folder)
    
    # Define folders to export adm0 and adm1 data to
    adm0_folder = '{}_adm0'.format(country)
    adm1_folder = '{}_adm1'.format(country)
    if not os.path.exists(adm0_folder):
        os.makedirs(adm0_folder)
    if not os.path.exists(adm1_folder):
        os.makedirs(adm1_folder)
        
    #Move files for adm1 and adm0 data to separate folders
    adm1_files = glob.glob(os.path.join(download_folder,'gadm36_{}_1.*'.format(country)))
    for adm1_file in adm1_files:
        new_file_name = adm1_file.replace('gadm36_{}_1'.format(country), adm1_folder)
        os.rename(adm1_file,new_file_name)
        shutil.move(new_file_name, adm1_folder)
    adm0_files = glob.glob(os.path.join(download_folder,'gadm36_{}_0.*'.format(country)))
    for adm0_file in adm0_files:
        new_file_name = adm0_file.replace('gadm36_{}_0'.format(country), adm0_folder)
        os.rename(adm0_file,new_file_name)
        shutil.move(new_file_name, adm0_folder)
        
    # Remove remaining files that won't be used  
    os.remove(zip_file_name) 
    shutil.rmtree(download_folder)
        

