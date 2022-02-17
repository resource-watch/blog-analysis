import logging
import pandas as pd
import glob
import os
from zipfile import ZipFile
import shutil
import geopandas as gpd
import numpy as np

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
data_dir = 'data'
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
# os.chdir(data_dir)

# get boundry shapefiles from https://gadm.org/data.html
# global shapefile is too big, so download data only for selected countries
# unzip and move the data to your data folder
# read state level shapefile
state_shp_USA = gpd.read_file(u"data/gadm36_USA_shp/gadm36_USA_1.shp")

'''
Download data and save to your data directory
Data can be downloaded at the following link:
https://gwis.jrc.ec.europa.eu/apps/country.profile/downloads
A zip file was downloaded (A CSV file within the zip file)
'''
# download the data from the source
logger.info('Downloading raw data')
download = glob.glob(os.path.join(os.path.expanduser("~"), 'Downloads', 'MCD64A1_burned_area_full_dataset_2002-2019.zip'))[0]

# move this file into your data directory
raw_data_file = os.path.join(data_dir, os.path.basename(download))
shutil.move(download, raw_data_file)

# unzip historical emissions data
raw_data_file_unzipped = raw_data_file.split('.')[0]
zip_ref = ZipFile(raw_data_file, 'r')
zip_ref.extractall(raw_data_file_unzipped)
zip_ref.close()

'''
Process data
'''
# read in historical emissions csv data to pandas dataframe
filename = os.path.join(raw_data_file_unzipped, 'MCD64A1_burned_area_full_dataset_2002-2019.csv')
# filename = 'data/MCD64A1_burned_area_full_dataset_2002-2019/MCD64A1_burned_area_full_dataset_2002-2019.csv'
df = pd.read_csv(filename)

# convert the column names to lowercase
df.columns = [x.lower() for x in df.columns]
# replace all NaN with None
df = df.where((pd.notnull(df)), None)
    
# Define countries loop over
# country_list = ['United States', 'United Kingdom', 'France', 'Germany', 'Canada', 'Sweden', 'Brazil', 'Mexico', 'Belgium', 'Ireland', 'Netherlands', 'Nigeria', 'Saudi Arabia', 'South Africa', 'Spain', 'Indonesia', 'India', 'Taiwan']
# country_list = ['Brazil', 'United States', 'Canada', 'Russia', 'Democratic Republic of the Congo', 'Australia', 'Indonesia']
country_list = ['United States']
df = df[df.country.isin(country_list)]

# calculate total burned area for each state
df['total_ba_hectares'] = df['cropland_ba_hectares'] + df['forest_ba_hectares'] + df['grass_and_shrubland_ba_hectares'] + df['wetlands_ba_hectares'] + df['settlement_ba_hectares'] + df['other_ba_hectares']

# aggregate by year
df_yearly = df.groupby(['year','gid_0', 'country', 'gid_1', 'region']).sum().reset_index()
df_yearly.drop("month", axis = 1, inplace = True)
df_yearly.to_csv("data/yearly_USA.csv")

# aggregate by country
df_yearly_country = df.groupby(['year','gid_0', 'country']).sum().reset_index()
df_yearly_country.to_csv("data/yearly_7_country.csv")

# subset 2019 data
df_2019 = df_yearly[df_yearly.year == 2019]

# add geometry to the dataframe
df_2019_USA = pd.merge(df_2019, state_shp_USA[['GID_1','geometry']], left_on = 'gid_1',right_on = 'GID_1', how = 'left')
df_2019_USA.drop("GID_1", axis = 1, inplace = True)
# convert dataframe to geodataframe
gdf_2019_USA = gpd.GeoDataFrame(df_2019_USA, geometry = df_2019_USA.geometry)
gdf_2019_USA = gdf_2019_USA.set_crs(epsg = 4326)
# save to shapefile
gdf_2019_USA.to_file("data/USA_2019.shp")
# plot map
ax = gdf_2019_USA.plot(column = 'total_ba_hectares', cmap = 'YlOrRd', edgecolor = 'grey', legend = True)

# load 2020 USA state level statistics
months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
for i in months:
    filename = 'data/USA state level statistics/2020' + i + '_zonal.dbf' 
    table = gpd.read_file(filename)
    table = pd.DataFrame(table)
    if i == '01':
        USA_2020 = table
    else:
        USA_2020 = USA_2020.append(table)
USA_2020 = USA_2020.drop(columns = 'geometry') 
USA_2020['AREA'] = USA_2020.SUM * 463.312716528 * 463.312716528
USA_2020 = USA_2020.groupby(['region']).sum().reset_index()
# square meters to hectres
USA_2020['total_ba_hectares'] = round(USA_2020.AREA / 10000, 0)
USA_2020 = USA_2020.drop(columns = ['ZONE_CODE', 'COUNT', 'AREA', 'SUM'])
USA_2020['year'] = 2020
USA_2020['gid_0'] = 'USA'
USA_2020['gid_1'] = np.nan
USA_2020['country'] = 'United States'
USA_2020['cropland_ba_hectares'] = 0
USA_2020['forest_ba_hectares'] = 0
USA_2020['grass_and_shrubland_ba_hectares'] = 0
USA_2020['wetlands_ba_hectares'] = 0
USA_2020['settlement_ba_hectares'] = 0
USA_2020['other_ba_hectares'] = USA_2020.total_ba_hectares
USA_2020 = USA_2020[list(df_yearly.columns)]

df_yearly = df_yearly.append(USA_2020).reset_index(drop = True)
df_yearly.to_csv("data/yearly_USA_2020.csv")

# aggregate by continent
countries_by_continent = pd.read_csv('data/countries_by_continent.csv')
df_2019_continent = pd.merge(df_2019, countries_by_continent[['ISO-alpha3 Code','Continent']], left_on = 'gid_0',right_on = 'ISO-alpha3 Code', how = 'left')
# fill in for regions not in the list
df_2019_continent.loc[df_2019_continent.country == 'Taiwan', 'Continent'] = 'Asia'
df_2019_continent.loc[df_2019_continent.country == 'Akrotiri and Dhekelia', 'Continent'] = 'Europe'
df_2019_continent.loc[df_2019_continent.country == 'Kosovo', 'Continent'] = 'Europe'
df_2019_continent.loc[df_2019_continent.country == 'Northern Cyprus', 'Continent'] = 'Asia'
# calculate global burned area
df_2019_continent_agg = df_2019_continent.groupby(['year','Continent']).sum().reset_index()
df_2019_continent_agg.loc['6']= df_2019_continent_agg.sum()
df_2019_continent_agg.loc['6','year'] = 2019
df_2019_continent_agg.loc['6','Continent'] = 'Global'
# calculate percentage
df_2019_continent_agg['cropland_percent'] = round(df_2019_continent_agg['cropland_ba_hectares']/df_2019_continent_agg['total_ba_hectares'], 4)
df_2019_continent_agg['forest_percent'] = round(df_2019_continent_agg['forest_ba_hectares']/df_2019_continent_agg['total_ba_hectares'], 4)
df_2019_continent_agg['grass_and_shrubland_percent'] = round(df_2019_continent_agg['grass_and_shrubland_ba_hectares']/df_2019_continent_agg['total_ba_hectares'], 4)
df_2019_continent_agg['wetlands_percent'] = round(df_2019_continent_agg['wetlands_ba_hectares']/df_2019_continent_agg['total_ba_hectares'], 4)
df_2019_continent_agg['settlement_percent'] = round(df_2019_continent_agg['settlement_ba_hectares']/df_2019_continent_agg['total_ba_hectares'], 4)
df_2019_continent_agg['other_percent'] = round(df_2019_continent_agg['other_ba_hectares']/df_2019_continent_agg['total_ba_hectares'], 4)
# export as csv
df_2019_continent_agg.to_csv("data/continent_2019.csv")
