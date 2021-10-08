import logging
import pandas as pd
import glob
import os
from zipfile import ZipFile
import shutil
import requests
import json

# Set up logging
# Get the top-level logger object
logger = logging.getLogger()
for handler in logger.handlers: logger.removeHandler(handler)
logger.setLevel(logging.INFO)
# make it print to the console.
console = logging.StreamHandler()
logger.addHandler(console)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# read wri_countries_a from carto to get the ios_a3
api_key = os.getenv('CARTO_WRI_RW_KEY')
username = os.getenv('CARTO_WRI_RW_USER')
sql = 'SELECT * FROM wri_countries_a'
url = f'https://{username}.carto.com/api/v2/sql'
r = requests.get(url, params={'api_key': api_key, 'q': sql}).text
df_dict = json.loads(r)
df_carto = pd.DataFrame(df_dict['rows'])

# Get script folder
os.chdir(os.path.dirname(os.path.realpath(__file__)))
# Define working folder
data_dir = 'data'
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
# os.chdir(data_dir)

######## Historical GHG Emissions - CAIT ########
'''
Download data and save to your data directory
Data can be downloaded at the following link:
https://www.climatewatchdata.org/data-explorer
A csv file was downloaded from the explorer
after selecting the following options from menu:
    Data source: CAIT
    Countries and regions: All selected
    Sectors: Total including LUCF
    Gases: All GHG
    Start year: 1990
    End year: 2018
'''

# download the data from the source
logger.info('Downloading raw data')
download = glob.glob(os.path.join(os.path.expanduser("~"), 'Downloads', 'historical_emissions.zip'))[0]

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
filename = os.path.join(raw_data_file_unzipped, 'historical_emissions.csv')
# filename = 'data/historical_emissions/historical_emissions.csv'
df = pd.read_csv(filename)

# add iso_a3 to the dataframe
df_edit = pd.merge(df, df_carto[['iso_a3','name']], left_on = 'Country',right_on = 'name', how = 'left')

# deal with exceptions
df_edit.loc[df_edit['Country'] == 'United States','iso_a3'] = 'USA'
df_edit.loc[df_edit['Country'] == 'Tanzania','iso_a3'] = 'TZA'
df_edit.loc[df_edit['Country'] == 'Serbia','iso_a3'] = 'SRB'
df_edit.loc[df_edit['Country'] == "Côte d'Ivoire",'iso_a3'] = 'CIV'
df_edit.loc[df_edit['Country'] == 'Guinea-Bissau','iso_a3'] = 'GNB'
df_edit.loc[df_edit['Country'] == 'Eswatini','iso_a3'] = 'SWZ'
df_edit.loc[df_edit['Country'] == 'Bahamas','iso_a3'] = 'BHS'
df_edit.loc[df_edit['Country'] == 'Micronesia','iso_a3'] = 'FSM'
df_edit.loc[df_edit['Country'] == 'Cook Islands','iso_a3'] = 'COK'
df_edit.loc[df_edit['Country'] == 'Niue','iso_a3'] = 'NIU'

# drop duplicate column
df_edit = df_edit.drop('name', axis= 1)
df_edit = df_edit.reset_index()

# replace spaces and special characters in column headers with '_" 
df_edit.columns = df_edit.columns.str.replace(' ', '_')
df_edit.columns = df_edit.columns.str.replace('/', '_')
df_edit.columns = df_edit.columns.str.replace('-', '_')

# convert the column names to lowercase
df_edit.columns = [x.lower() for x in df_edit.columns]

# replace all NaN with None
df_edit = df_edit.where((pd.notnull(df_edit)), None)

# convert the data type of the numeric columns to float
for i in range(1990, 2019):
    df_edit[str(i)] = df_edit[str(i)].astype('float64')
    
# Define countries loop over
# country_list = ['United States', 'United Kingdom', 'France', 'Germany', 'Canada', 'Sweden', 'Brazil', 'Mexico', 'Belgium', 'Ireland', 'Netherlands', 'Nigeria', 'Saudi Arabia', 'South Africa', 'Spain', 'Indonesia', 'India', 'Taiwan']
# df_edit = df_edit[df_edit.country.isin(country_list)]

# remove index column
df_edit = df_edit.iloc[:, 1:]

# move iso_a3 to the first column
cols = list(df_edit.columns)
cols = [cols[-1]] + cols[:-1]
df_edit = df_edit[cols]

# save processed dataset to csv
processed_data_file = os.path.join(data_dir, 'historical_emissions_edit.csv')
df_edit.to_csv(processed_data_file, index = False)

######## NDCs ########
'''
Download data and save to your data directory
Data can be downloaded at the following link:
https://www.climatewatchdata.org/data-explorer
A csv file was downloaded from the explorer
go to Download Bulk Data -> NDC TARGETS
'''
# download the data from the source
logger.info('Downloading raw data')
download = glob.glob(os.path.join(os.path.expanduser("~"), 'Downloads', 'NDC_quantification.zip'))[0]

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
# read in NDC excel data to pandas dataframe
filename = os.path.join(raw_data_file_unzipped,'NDC_quantification', 'CW_NDC_quantification.xlsx')
# filename = 'data/NDC_quantification/NDC_quantification/CW_NDC_quantification.xlsx'
df = pd.read_excel(filename)

# drop rows with NAs
df.dropna(inplace=True)

# get unique country list
df_edit = df.loc[:,['ISO','Country']]
df_edit = df_edit.drop_duplicates()

# deal with exceptions
df_edit.loc[df_edit.Country == 'Tonga','ISO'] = 'TON'
df_edit = df_edit[df_edit.Country != 'Russian Federation']

# add links
df_edit['NDC_Overview'] = [f'https://climatewatchdata.org/ndcs/country/{ISO_Code}' for ISO_Code in df_edit['ISO']]
df_edit['NDC_Full'] = [f'https://climatewatchdata.org/ndcs/country/{ISO_Code}/full' for ISO_Code in df_edit['ISO']]

# rename column
df_edit = df_edit.rename(columns={"ISO": "iso_a3"})

# convert the column names to lowercase
df_edit.columns = [x.lower() for x in df_edit.columns]

# replace all NaN with None
df_edit = df_edit.where((pd.notnull(df_edit)), None)

# save processed dataset to csv
processed_data_file = os.path.join(data_dir, 'NDC_links_edit.csv')
df_edit.to_csv(processed_data_file, index = False)

# # Define countries loop over
# country_iso_list = ["USA","GBR","FRA","DEU","CAN", "SWE", "BRA", "MEX", "BEL", "IRL", "NLD", "NGA", "SAU", "ZAF", "ESP", "IND", "IDN", "TWN"]
# df = df[df.ISO.isin(country_iso_list)]

# df = df.reset_index()

# # convert the column names to lowercase
# df.columns = [x.lower() for x in df.columns]

# # replace all NaN with None
# df = df.where((pd.notnull(df)), None)

# # convert the data type of the column 'year' to integer
# df['year'] = df['year'].astype('int64')

# # convert the years in the 'year' column to datetime objects and store them in a new column 'datetime'
# df['datetime'] = [datetime.datetime(x, 1, 1) for x in df.year]

# # convert the data type of the numeric columns to float
# df['value'] = df['value'].astype('float64')

# df = df.iloc[: , 1:]

# # save processed dataset to csv
# processed_data_file = os.path.join(data_dir, 'NDC_quantification_edit.csv')
# df.to_csv(processed_data_file, index = False)


######## Pathway - GCAM ########
'''
Download data and save to your data directory
Data can be downloaded at the following link:
https://www.climatewatchdata.org/data-explorer
A csv file was downloaded from the explorer
go to Download Bulk Data -> PATHWAYS
'''
# download the data from the source
logger.info('Downloading raw data')
download = glob.glob(os.path.join(os.path.expanduser("~"), 'Downloads', 'pathways.zip'))[0]

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
filename = os.path.join(raw_data_file_unzipped,'Pathways', 'GCAM.xlsx')
# filename = 'data/pathways/Pathways/GCAM.xlsx'
df = pd.read_excel(filename, sheet_name='GCAM_Timeseries data')

# subset dataset to GHG Emissions
df = df[df['ESP Indicator Name'].str.contains('GHG Emissions by gas with LULUCF')]
df_edit= df.drop_duplicates(subset = ['Scenario', 'Region'],keep = 'last').reset_index(drop = True)

# sum four gases of each (scenario, region, year)
years = ['2005', '2010', '2020', '2030', '2040', '2050', '2060', '2070', '2080','2090', '2100']
for i in range(len(df_edit)):
    for year in years:
        df_edit[year].iloc[i] = df.loc[(df['Scenario'] == df_edit.Scenario[i]) & (df['Region'] == df_edit.Region[i]), year].sum()

# add iso_a3 to countries
df_edit.loc[df_edit['Region'] == 'Argentina','iso_a3']='ARG'
df_edit.loc[df_edit['Region'] == 'Brazil','iso_a3']='BRA'
df_edit.loc[df_edit['Region'] == 'Canada','iso_a3']='CAN'
df_edit.loc[df_edit['Region'] == 'China','iso_a3']='CHN'
df_edit.loc[df_edit['Region'] == 'Colombia','iso_a3']='COL'
df_edit.loc[df_edit['Region'] == 'India','iso_a3']='IND'
df_edit.loc[df_edit['Region'] == 'Indonesia','iso_a3']='IDN'
df_edit.loc[df_edit['Region'] == 'Japan','iso_a3']='JPN'
df_edit.loc[df_edit['Region'] == 'Mexico','iso_a3']='MEX'
df_edit.loc[df_edit['Region'] == 'Pakistan','iso_a3']='PAK'
df_edit.loc[df_edit['Region'] == 'Russia','iso_a3']='RUS'
df_edit.loc[df_edit['Region'] == 'South Africa','iso_a3']='ZAF'
df_edit.loc[df_edit['Region'] == 'South Korea','iso_a3']='KOR'
df_edit.loc[df_edit['Region'] == 'Taiwan','iso_a3']='TWN'
df_edit.loc[df_edit['Region'] == 'United States','iso_a3']='USA'

# update labels and sort data
df_edit = df_edit.replace('Emissions|GHG Emissions by gas with LULUCF|N2O','Emissions|GHG Emissions by gas with LULUCF|All GHG')
df_edit = df_edit.sort_values(by = ['Region', 'Scenario']).reset_index()

# replace spaces and special characters in column headers with '_" 
df_edit.columns = df_edit.columns.str.replace(' ', '_')
df_edit.columns = df_edit.columns.str.replace('/', '_')
df_edit.columns = df_edit.columns.str.replace('-', '_')

# convert the column names to lowercase
df_edit.columns = [x.lower() for x in df_edit.columns]

# remove index column
df_edit = df_edit.iloc[: , 1:]

# move iso_a3 to the first column
cols = list(df_edit.columns)
cols = [cols[-1]] + cols[:-1]
df_edit = df_edit[cols]

# save processed dataset to csv
processed_data_file = os.path.join(data_dir, 'GCAM_edit.csv')
df_edit.to_csv(processed_data_file, index = False)