from enum import unique
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
    Sectors: All selected
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

# move iso_a3 to the first column and reverse years
cols = ['iso_a3', 'country', 'data_source', 'sector', 'gas', 'unit'] + [str(year) for year in range(1990, 2019)]
df_edit = df_edit[cols]

# subset energy sector
df_ene = df_edit.loc[df_edit['sector'].isin(['Electricity/Heat', 'Transportation', 'Manufacturing/Construction','Fugitive Emissions', 'Building', 'Other Fuel Combustion'])]
df_ene = df_ene.sort_values(["country", "sector"], ascending = (True, True))

# subset table by sectors
df_edit = df_edit.loc[df_edit['sector'].isin(['Agriculture', 'Energy', 'Industrial Processes', 'Land-Use Change and Forestry', 'Total excluding LUCF', 'Total including LUCF', 'Waste'])]
df_edit = df_edit.sort_values(["country", "sector"], ascending = (True, True))

# grouped_df = df_ene.groupby("country").nunique()

# save processed dataset to csv
processed_data_file = os.path.join(data_dir, 'historical_emissions_energy_edit.csv')
df_ene.to_csv(processed_data_file, index = False)

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
df.dropna(inplace = True)

# get unique country list
df_edit = df.loc[:,['ISO','Country']]
df_edit = df_edit.drop_duplicates()

# deal with exceptions
df_edit.loc[df_edit.Country == 'Tonga','ISO'] = 'TON'
df_edit = df_edit[df_edit.Country != 'Russian Federation']

# add links
df_edit['NDC_Overview'] = [f'https://climatewatchdata.org/ndcs/country/{ISO_Code}' for ISO_Code in df_edit['ISO']]
df_edit['NDC_Full'] = [f'https://climatewatchdata.org/ndcs/country/{ISO_Code}/full' for ISO_Code in df_edit['ISO']]
df_edit['Embed_URL'] = [f'https://climatewatchdata.org/embed/countries/{ISO_Code}/ghg-emissions' for ISO_Code in df_edit['ISO']]
df_edit['Embed_Code'] = [f'<iframe src="https://climatewatchdata.org/embed/countries/{ISO_Code}/ghg-emissions" frameborder="0" style="height: 600px; width: 1230px"></iframe>' for ISO_Code in df_edit['ISO']]

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

# clean NDCs
# deal with exceptions
df.loc[df.Country == 'Russian Federation', 'Country'] = 'Russia'

# convert the column names to lowercase
df.columns = [x.lower() for x in df.columns]

# replace all NaN with None
df = df.where((pd.notnull(df)), None)

# convert the data type of the column 'year' to integer
df['year'] = df['year'].astype('int64')

# convert the data type of the numeric columns to float
df['value'] = df['value'].astype('float64')

# save processed dataset to csv
processed_data_file = os.path.join(data_dir, 'NDC_quantification_edit.csv')
df.to_csv(processed_data_file, index = False)

######## Pathway - Climate Action Tracker ########
'''
Download data and save to your data directory
Data can be downloaded at the following link:
https://climateactiontracker.org/countries/
A excel file was downloaded for each country from Climate Action Tracker
'''
# download the data from the source
logger.info('Downloading raw data')
ExcelFilenames = glob.glob(os.path.join(os.path.expanduser("~"), 'Downloads', 'CAT_AssessmentData*.xls'))
ExcelFilenames = ExcelFilenames + glob.glob(os.path.join(os.path.expanduser("~"), 'Downloads', 'CAT_AssessmentData*.xlsx'))

raw_data_files = []
# move this file into your data directory
for file in ExcelFilenames:
    raw_data_file = os.path.join(data_dir, os.path.basename(file))
    shutil.move(file, raw_data_file)
    raw_data_files.append(raw_data_file)

file = raw_data_files[0]
modelled_pathways = pd.DataFrame()
country = []
link = []
iso_a3 = []
# combine all files
for file in raw_data_files:
    data = pd.read_excel(file, sheet_name = 'ModelledPathways')
    country.append(data.iloc[-8, 3])
    link.append('https://climateactiontracker.org/countries/'+ data.iloc[-8, 3].lower().replace(' ','-') + '/')
    data = data.iloc[-4:,1:]
    data.columns = ['code', 'upper_end_of'] + list(range(2015, 2051))
    data['iso_a3'] = file.split('_')[2]
    iso_a3.append(file.split('_')[2])
    modelled_pathways = modelled_pathways.append(data)

modelled_pathways = modelled_pathways.reset_index(drop = True)
modelled_pathways.loc[modelled_pathways.upper_end_of == '1.5°C Paris Agreement compatible', 'code'] = 'Below 1.5C and low overshoot'
modelled_pathways.loc[modelled_pathways.upper_end_of == 'Almost sufficient', 'code'] = '2.0C'
modelled_pathways.loc[modelled_pathways.upper_end_of == 'Insufficient', 'code'] = '3.0C'
modelled_pathways.loc[modelled_pathways.upper_end_of == 'Highly insufficient', 'code'] = '4.0C'

# move iso_a3 to the first column
cols = list(modelled_pathways.columns)
cols = [cols[-1]] + cols[:-1]
modelled_pathways = modelled_pathways[cols]

# save processed dataset to csv
processed_data_file = os.path.join(data_dir, 'modelled_pathways_edit.csv')
modelled_pathways.to_csv(processed_data_file, index = False)

# create CAT links list
modelled_pathways_link = pd.DataFrame(list(zip(iso_a3, country, link)), columns = ['iso_a3', 'country', 'link'])

# fix problematic links
modelled_pathways_link.loc[modelled_pathways_link['iso_a3'] == 'KOR','link'] = 'https://climateactiontracker.org/countries/south-korea/'
modelled_pathways_link.loc[modelled_pathways_link['iso_a3'] == 'ARE','link'] = 'https://climateactiontracker.org/countries/uae/'
modelled_pathways_link.loc[modelled_pathways_link['iso_a3'] == 'BBR','link'] = 'https://climateactiontracker.org/countries/uk/'
modelled_pathways_link.loc[modelled_pathways_link['iso_a3'] == 'EU27','link'] = 'https://climateactiontracker.org/countries/eu/'
modelled_pathways_link.loc[modelled_pathways_link['iso_a3'] == 'RUS','link'] = 'https://climateactiontracker.org/countries/russian-federation/'

# sort by iso_a3
modelled_pathways_link = modelled_pathways_link.sort_values('iso_a3')

# save processed dataset to csv
processed_data_file = os.path.join(data_dir, 'modelled_pathways_link.csv')
modelled_pathways_link.to_csv(processed_data_file, index = False)
