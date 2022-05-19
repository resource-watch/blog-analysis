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
# df = df[df.country.isin(country_list)]

# calculate total burned area for each state
df['total_ba_hectares'] = df['cropland_ba_hectares'] + df['forest_ba_hectares'] + df['grass_and_shrubland_ba_hectares'] + df['wetlands_ba_hectares'] + df['settlement_ba_hectares'] + df['other_ba_hectares']

# aggregate state level data by year
df_yearly = df.groupby(['year','gid_0', 'country', 'gid_1', 'region']).sum().reset_index()
df_yearly.drop("month", axis=1, inplace=True)
df_yearly.to_csv("data/state_02_19.csv", index=False)

# aggregate by country
df_yearly_country = df.groupby(['year','gid_0', 'country']).sum().reset_index()
df_yearly_country.drop("month", axis=1, inplace=True)
df_yearly_country.to_csv("data/country_02_19.csv", index=False)

'''
Get the countries by continent data from: https://statisticstimes.com/geography/countries-by-continents.php
Data source: United Nations Statistics Division

Burned area 2002 to 2019 continent level
'''
# aggregate by continent
countries_by_continent = pd.read_csv(os.path.join(data_dir,'countries_by_continent.csv'))
df_02_19_continent = pd.merge(df_yearly_country, countries_by_continent[['ISO-alpha3 Code','Continent']], left_on='gid_0', right_on='ISO-alpha3 Code', how='left')
# fill in for regions not in the list
df_02_19_continent.loc[df_02_19_continent.country=='Taiwan', 'Continent'] = 'Asia'
df_02_19_continent.loc[df_02_19_continent.country=='Akrotiri and Dhekelia', 'Continent'] = 'Europe'
df_02_19_continent.loc[df_02_19_continent.country=='Kosovo', 'Continent'] = 'Europe'
df_02_19_continent.loc[df_02_19_continent.country=='Northern Cyprus', 'Continent'] = 'Asia'
# calculate global burned area
df_02_19_continent_agg = df_02_19_continent.groupby(['year','Continent']).sum().reset_index()
# calculate percentage
# df_02_19_continent_agg['cropland_percent'] = round(df_02_19_continent_agg['cropland_ba_hectares']/df_02_19_continent_agg['total_ba_hectares'], 4)
# df_02_19_continent_agg['forest_percent'] = round(df_02_19_continent_agg['forest_ba_hectares']/df_02_19_continent_agg['total_ba_hectares'], 4)
# df_02_19_continent_agg['grass_and_shrubland_percent'] = round(df_02_19_continent_agg['grass_and_shrubland_ba_hectares']/df_02_19_continent_agg['total_ba_hectares'], 4)
# df_02_19_continent_agg['wetlands_percent'] = round(df_02_19_continent_agg['wetlands_ba_hectares']/df_02_19_continent_agg['total_ba_hectares'], 4)
# df_02_19_continent_agg['settlement_percent'] = round(df_02_19_continent_agg['settlement_ba_hectares']/df_02_19_continent_agg['total_ba_hectares'], 4)
# df_02_19_continent_agg['other_percent'] = round(df_02_19_continent_agg['other_ba_hectares']/df_02_19_continent_agg['total_ba_hectares'], 4)
# export as csv
df_02_19_continent_agg.to_csv("data/continent_02_19.csv", index=False)

# create stacked bar chart for continents
colors = {'Cropland':'#FFFF00','Forest':'#548235', 'Grass and Shrubland':'#92D050', 'Wetlands':'#CC9900', 'Settlement':'#CC99FF', 'Other':'#B2B2B2'}
for continent in df_02_19_continent_agg['Continent'].unique():
    sub_df = df_02_19_continent_agg[df_02_19_continent_agg['Continent'] == continent]
    sub_df = sub_df.set_index('year')
    sub_df = sub_df[['cropland_ba_hectares','forest_ba_hectares', 'grass_and_shrubland_ba_hectares', 'wetlands_ba_hectares', 'settlement_ba_hectares', 'other_ba_hectares']]
    sub_df = sub_df.rename(columns={'cropland_ba_hectares':'Cropland','forest_ba_hectares':'Forest', 'grass_and_shrubland_ba_hectares':'Grass and Shrubland', 'wetlands_ba_hectares':'Wetlands', 'settlement_ba_hectares':'Settlement', 'other_ba_hectares':'Other'})

    ax = sub_df.plot.bar(stacked=True, color=colors, width=0.6)
    ax.set_xlabel('Year')
    ax.set_ylabel('Burned area (ha)')
    ax.set_title(f'Burned area by LULC {continent}')
    # ax.set_frame_on(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.tick_params(axis='x', labelrotation = 45)
    ax.legend(loc='upper left', bbox_to_anchor=(1, 0.5),frameon=False)
    ax.figure.tight_layout()
    ax.figure.set_size_inches(10, 5)

    ax.figure.savefig(f'data/{continent}_02_19.jpg', dpi=300)

# create stacked bar chart for countries
colors = {'Cropland':'#FFFF00','Forest':'#548235', 'Grass and Shrubland':'#92D050', 'Wetlands':'#CC9900', 'Settlement':'#CC99FF', 'Other':'#B2B2B2'}
for country in df_yearly_country['country'].unique():
    sub_df = df_yearly_country[df_yearly_country['country'] == country]
    sub_df = sub_df.set_index('year')
    sub_df = sub_df[['cropland_ba_hectares','forest_ba_hectares', 'grass_and_shrubland_ba_hectares', 'wetlands_ba_hectares', 'settlement_ba_hectares', 'other_ba_hectares']]
    sub_df = sub_df.rename(columns={'cropland_ba_hectares':'Cropland','forest_ba_hectares':'Forest', 'grass_and_shrubland_ba_hectares':'Grass and Shrubland', 'wetlands_ba_hectares':'Wetlands', 'settlement_ba_hectares':'Settlement', 'other_ba_hectares':'Other'})

    ax = sub_df.plot.bar(stacked=True, color=colors, width=0.6)
    ax.set_xlabel('Year')
    ax.set_ylabel('Burned area (ha)')
    ax.set_title(f'Burned area by LULC {country}')
    # ax.set_frame_on(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.tick_params(axis='x', labelrotation = 45)
    ax.legend(loc='upper left', bbox_to_anchor=(1, 0.5),frameon=False)
    ax.figure.tight_layout()
    ax.figure.set_size_inches(10, 5)

    ax.figure.savefig(f'data/{country}_02_19.jpg', dpi=300)

'''
Calculate state level total burned area for 2020
'''
# Subset to USA
country_list = ['United States']
df = df[df.country.isin(country_list)]

# aggregate state level data by year
df_yearly_usa = df.groupby(['year','gid_0', 'country', 'gid_1', 'region']).sum().reset_index()
df_yearly_usa.drop("month", axis=1, inplace=True)

# load 2020 USA state level statistics
months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
for i in months:
    filename = 'data/USA_state_level_statistics/2020' + i + '_zonal.dbf' 
    table = gpd.read_file(filename)
    table = pd.DataFrame(table)
    if i == '01':
        usa_2020 = table
    else:
        usa_2020 = usa_2020.append(table)
usa_2020 = usa_2020.drop(columns = 'geometry') 
usa_2020['AREA'] = usa_2020.SUM * 463.312716528 * 463.312716528
usa_2020 = usa_2020.groupby(['region']).sum().reset_index()
# square meters to hectres
usa_2020['total_ba_hectares'] = round(usa_2020.AREA / 10000, 0)
usa_2020 = usa_2020.drop(columns = ['ZONE_CODE', 'COUNT', 'AREA', 'SUM'])
usa_2020['year'] = 2020
usa_2020['gid_0'] = 'USA'
usa_2020['gid_1'] = np.nan
usa_2020['country'] = 'United States'
usa_2020['cropland_ba_hectares'] = 0
usa_2020['forest_ba_hectares'] = 0
usa_2020['grass_and_shrubland_ba_hectares'] = 0
usa_2020['wetlands_ba_hectares'] = 0
usa_2020['settlement_ba_hectares'] = 0
usa_2020['other_ba_hectares'] = usa_2020.total_ba_hectares
usa_2020 = usa_2020[list(df_yearly.columns)]

df_usa = df_yearly_usa.append(usa_2020).reset_index(drop=True)
df_usa.to_csv("data/USA_02_20.csv")
