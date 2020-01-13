import os
import urllib
import pandas as pd
import requests
import numpy as np
from carto.datasets import DatasetManager
from carto.auth import APIKeyAuthClient

# name of the folder containing this analysis script
request_name = 'req_009_energy_decarbonization_leaders'

# set the directory that you are working in with the path variable
# you can use an environmental variable, as we did, or directly enter the directory name as a string
# example: path = '/home/req_009_energy_decarbonization_leaders'
dir = os.getenv('BLOG_DIR')+request_name
#move to this directory
os.chdir(dir)

# create a new sub-directory within your specified dir called 'data'
# this is where we will store the results of our analysis
data_dir = 'data/'
if not os.path.exists(data_dir):
    os.mkdir(data_dir)

#define function to upload final data to Carto
def upload_to_carto(csv_loc):
    print('Uploading processed data to Carto.')
    #set up carto authentication using local variables for username (CARTO_WRI_RW_USER) and API key (CARTO_WRI_RW_KEY)
    auth_client = APIKeyAuthClient(api_key=os.getenv('CARTO_WRI_RW_KEY'), base_url="https://{user}.carto.com/".format(user=os.getenv('CARTO_WRI_RW_USER')))
    #set up dataset manager with authentication
    dataset_manager = DatasetManager(auth_client)
    #upload dataset to carto
    dataset = dataset_manager.create(csv_loc)
    print('Carto table created: {}'.format(os.path.basename(csv_loc).split('.')[0]))
    #set dataset privacy to 'Public with link'
    dataset.privacy = 'LINK'
    dataset.save()
    print('Privacy set to public with link.')

'''
Electricity Consumption per Total Energy Consumption
'''
## Pull in relevant datasets

# enter Resource Watch dataset ID for Electricity Consumption data
electricity_consumption_dataset_id = 'ene034-Electricity-Consumption'
# create SQL query to pull all data from API
query = 'SELECT * from {}'.format(electricity_consumption_dataset_id)
sql_query = urllib.parse.quote(query)
# generate url for API call
url = 'https://api.resourcewatch.org/query?sql={}'.format(sql_query)
# request data and turn it into a pandas dataframe, then pull only the columns that we are interested in
r = requests.get(url)
json_data = r.json()['data']
electricity_df = pd.DataFrame.from_records(json_data)[['year', 'country', 'electricity_consumption_ktoe']]

# enter Resource Watch dataset ID for Energy Consumption data
energy_consumption_dataset_id = 'ene033-Energy-Consumption_1'
# create SQL query to pull all data from API
query = 'SELECT * from {}'.format(energy_consumption_dataset_id)
sql_query = urllib.parse.quote(query)
# generate url for API call
url = 'https://api.resourcewatch.org/query?sql={}'.format(sql_query)
# request data and turn it into a pandas dataframe, then pull only the columns that we are interested in
r = requests.get(url)
json_data = r.json()['data']
energy_df = pd.DataFrame.from_records(json_data)[['year', 'country', 'energy_consumption_ktoe']]



## Calculate Electricity Consumption per Total Energy Consumption

# merge the electricity consumption dataframe with the energy consumption dataframe, matching each by country and year
merged_df = electricity_df.merge(energy_df, left_on=['year', 'country'], right_on=['year', 'country'])
# calculate the electricity consumption per total energy consumption by dividing the two columns
merged_df['electricity_per_total_energy'] = merged_df.electricity_consumption_ktoe/merged_df.energy_consumption_ktoe
# If the total energy consumption was 0 and the electricity consumption has a non-zero value, the result of this analysis
# will be a value of infinity. This is not a logical value to use, so we will replace these with NaN.
merged_df = merged_df.replace(np.inf, np.nan)

#convert electricity_per_total_energy column to float
merged_df.electricity_per_total_energy=merged_df.electricity_per_total_energy.astype('float64')

## Save and upload results to Carto

# set the name to save this table as
sub_request_name = 'req_009a_electricity_per_total_energy'
# save the results of this analysis to a csv
csv_loc = data_dir+sub_request_name+'.csv'
merged_df.to_csv(csv_loc, index=False)
# upload this table to Carto
upload_to_carto(csv_loc)

'''
Annual Rate of Change for Energy Intensity
'''
## Pull in relevant datasets

# enter Resource Watch dataset ID for Energy Intensity data
energy_intensity_dataset_id = '2c444596-2be3-4786-bdfc-24010f99b21e'
# create SQL query to pull all data from API
query = 'SELECT * from {}'.format(energy_intensity_dataset_id)
sql_query = urllib.parse.quote(query)
# generate url for API call
url = 'https://api.resourcewatch.org/query?sql={}'.format(sql_query)
# request data and turn it into a pandas dataframe, then pull only the columns that we are interested in
r = requests.get(url)
json_data = r.json()['data']
energy_intensity_df = pd.DataFrame.from_records(json_data)[['country_name', 'country_code', 'energy_intensity', 'year']]

## Calculate Annual Rate of Change for Energy Intensity

# get list of years in the table, over which we will do this calculation
years = energy_intensity_df.year.unique()
# sort years so that they are in order
years.sort()

# create an empty dataframe to store the annual rate of change results
final_cols = ['country_name', 'country_code', 'year', 'energy_intensity_annual_rate_of_change']
final_df = pd.DataFrame(columns=final_cols)

# calculate annual rate of change for each year's energy intensity data, starting with the second year available
for year in years[1:]:
    # get subset of data for year we are calculating
    energy_intensity_df_current_year = energy_intensity_df[energy_intensity_df.year==year]
    # get subset of data for the year before
    energy_intensity_df_previous_year = energy_intensity_df[energy_intensity_df.year==year-1]
    # merge the two years of data based on country
    merged_df = energy_intensity_df_current_year.merge(energy_intensity_df_previous_year, left_on=['country_code', 'country_name'], right_on=['country_code', 'country_name'], suffixes=[year, year-1])
    # rename the current year's column to just be 'year' (because that is the year we will use as the indicator)
    merged_df = merged_df.rename(columns={'year'+str(year):'year'})
    # calculate the annual rate of change (current year energy intensity - previous year energy intensity) /  previous year energy intensity
    merged_df['energy_intensity_annual_rate_of_change'] = (merged_df['energy_intensity'+str(year)] - merged_df['energy_intensity'+str(year-1)])/merged_df['energy_intensity'+str(year-1)]
    # append the relevant columns to the final dataframe which will store all of the annual rate of change results
    final_df=final_df.append(merged_df[final_cols], ignore_index=True)

# If the energy intensity used in the denominator of the calculation was 0 and the numerator was non-zero, the result of this analysis
# will be a value of infinity. This is not a logical value to use, so we will replace these with NaN.
final_df = final_df.replace(np.inf, np.nan)

#convert energy_intensity_annual_rate_of_change column to float
final_df.energy_intensity_annual_rate_of_change=final_df.energy_intensity_annual_rate_of_change.astype('float64')

## Save and upload results to Carto

# set the name to save this table as
sub_request_name = 'req_009b_annual_rate_of_change_for_energy_intensity'
# save the results of this analysis to a csv
csv_loc = data_dir+sub_request_name+'.csv'
final_df.to_csv(csv_loc, index=False)
# upload this table to Carto
upload_to_carto(csv_loc)

