'''
The purpose of this analysis is to calculate statistics about aging coal-fired power plants throughout the world.

These analyses involve filtering out coal-fired power plants by country and by commissioning year to determine which 
countries have the greatest proportion of coal power plants nearing retirement age.

We also pull global statistics about how many coal power plants are nearing retirement and what their capacity is.

This analysis uses WRI's Global Power Plant Database, version 1.2; the latest version of this dataset can be downloaded at:
http://datasets.wri.org/dataset/globalpowerplantdatabase

'''
import pandas as pd
import numpy as np
import os
import urllib
import zipfile

# first, set the directory that you are working in with the dir variable
# you can use an environmental variable, as we did, or directly enter the directory name as a string
# example: dir = '/home/blog_018_aging_coal_power_plants'
dir = os.getenv(BLOG_DIR)+'blog_018_aging_coal_power_plants/'
os.chdir(dir)

# download the global power plant database and unzip
data_file = 'data'
urllib.request.urlretrieve('http://datasets.wri.org/dataset/540dcf46-f287-47ac-985d-269b04bea4c6/resource/c240ed2e-1190-4d7e-b1da-c66b72e08858/download/globalpowerplantdatabasev120', data_file+'.zip')
zip_ref = zipfile.ZipFile(data_file+'.zip', 'r')
zip_ref.extractall(data_file)
zip_ref.close()

#read in global power plant database to pandas dataframe
filename=data_file+'/global_power_plant_database.csv'
df=pd.read_csv(filename)

# get only coal power plant data
df_coal= df.loc[df.primary_fuel=='Coal']
# get coal power plant data where the commissioning year is unknown
df_coal_unknown_yr = df_coal[df_coal.commissioning_year.isnull()]
# get coal power plant data where the commissioning year is unknown
df_coal_known_yr = df_coal[~df_coal.commissioning_year.isnull()]

#ANALYSIS FOR WORLD

#create empty dataframe to store results of global analysis
results = pd.DataFrame(index=['World'],columns=['num_coal_power_plants', 'num_coal_power_plants_pre_1979', 'num_coal_power_plants_unknown_yr', 'capacity_mw_all', 'capacity_mw_pre_1979', 'p_capacity_pre_1979'])

#calculate the number of coal power plants in the world
num_coal_power_plants = len(df_coal_known_yr)
#calculate the number of coal power plants in the world that have a commissioning year before 1979
num_coal_power_plants_pre_1979 = len(df_coal_known_yr[df_coal_known_yr.commissioning_year<1979])
#calculate the number of coal power plants in the world with an unknown commissioning year
num_coal_power_plants_unknown_yr = len(df_coal_unknown_yr)
#calculate the sum of all coal capacity in the world
global_capacity_mw_all = sum(df_coal_known_yr.capacity_mw)
#calculate the sum of coal capacity in the world from a plant with a commissioning year before 1979
global_capacity_mw_pre_1979 = sum(df_coal_known_yr[df_coal_known_yr.commissioning_year<1979].capacity_mw)

#store calculated results in dataframe
results.loc['World']['num_coal_power_plants'] = num_coal_power_plants
results.loc['World']['num_coal_power_plants_pre_1979'] = num_coal_power_plants_pre_1979
results.loc['World']['num_coal_power_plants_unknown_yr'] = num_coal_power_plants_unknown_yr
results.loc['World']['capacity_mw_all'] = global_capacity_mw_all
results.loc['World']['capacity_mw_pre_1979'] = global_capacity_pre_1979
results.loc['World']['p_capacity_pre_1979'] = global_capacity_mw_pre_1979/global_capacity_mw_all

#save global stats to file
results.to_csv('stats_global.csv')



# ANALYSIS BY COUNTRY
#get list of unique countries in database
countries = np.unique(df_coal_known_yr['country'])

#create empty dataframe to store results of country analysis
results = pd.DataFrame(index=countries, columns=['total_capacity_mw', 'capacity_mw_pre_1979', 'p_country_capacity_pre_1979', 'p_global_capacity_pre_1979', 'p_global_capacity_pre_1979_in_country','plants_total_num', 'plants_num_pre_1979', 'plants_num_1979_or_after', 'plants_num_unknown_yr', 'p_plants_pre_1979', 'plants_avg_age'])

#get selected statistics for each country in the dataframe
for country in countries:
    #first, pull only the data for the current country
    sub_df= df_coal_known_yr.loc[df_coal_known_yr['country']==country]

    #calculating number of plants in various categories
    #get average age of plants in this country
    plants_avg_age = sub_df['commissioning_year'].mean()
    #get number of plants that have a commissioning year before 1979
    plants_num_pre_1979 =(sub_df['commissioning_year']<1979).sum()
    #get number of plants that have a commissioning year of 1979 or after
    plants_num_1979_or_after = (sub_df['commissioning_year']>=1979).sum()
    #get number of plants that do not have a reported commissioning year
    plants_num_unknown_yr = len(df_coal_unknown_yr.loc[df_coal_unknown_yr['country']==country])
    #get total number of plants
    plants_total_num = len(sub_df)
    #calculate proportion of plants that have a commissioning year before 1979
    p_plants_pre_1979 = plants_num_pre_1979/plants_total_num

    #capacity calculations
    #calculate the total coal capacity (MW) in this country
    total_capacity_mw = sub_df['capacity_mw'].sum()
    #calculate how much of the coal capacity (MW) is from a plant that was commissioned before 1979
    capacity_mw_pre_1979 = sub_df.loc[sub_df['commissioning_year']<1979]['capacity_mw'].sum()
    #calculate what proportion of the country's total capacity is from a plant that was commissioned before 1979
    p_country_capacity_pre_1979 = capacity_mw_pre_1979/total_capacity_mw
    #calculate the proportion of ALL global capacity that this country's pre-1979 capacity represents
    p_global_capacity_pre_1979 = capacity_mw_pre_1979/global_capacity_mw_all
    #calculate the proportion of pre-1979 global capacity that this country's pre-1979 capacity represents
    p_global_capacity_pre_1979_in_country = capacity_mw_pre_1979/global_capacity_mw_pre_1979

    # store calculated results for country in dataframe
    results.loc[country]['total_capacity_mw']=total_capacity_mw
    results.loc[country]['capacity_mw_pre_1979']=capacity_mw_pre_1979
    results.loc[country]['p_country_capacity_pre_1979']=p_country_capacity_pre_1979
    results.loc[country]['p_global_capacity_pre_1979']=p_global_capacity_pre_1979
    results.loc[country]['p_global_capacity_pre_1979_in_country']=p_global_capacity_pre_1979_in_country
    results.loc[country]['plants_total_num']=plants_total_num
    results.loc[country]['plants_num_pre_1979']=plants_num_pre_1979
    results.loc[country]['plants_num_1979_or_after']=plants_num_1979_or_after
    results.loc[country]['plants_num_unknown_yr']=plants_num_unknown_yr
    results.loc[country]['p_plants_pre_1979']=p_plants_pre_1979
    results.loc[country]['plants_avg_age']=plants_avg_age

#save country stats to file
results.to_csv('stats_ctry.csv')