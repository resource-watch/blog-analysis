'''
This script uses World Bank data to determine an estimate of how many people
were working in agriculture globally in 2018.

Definitions of each input dataset were copied from the World Bank website and summarized
into a one-line summary of what the data represent. Please see the data source provided
for each dataset for more details or to download the data.
'''

import pandas as pd
import math

# first, set the directory that you are working in by filling in the empty quotes below
# example: dir = '/home/employment_in_ag'
dir = ''

# create a new sub-directory within your specified dir called 'data'
# download and unzip the following World Bank Group datasets and put them in the
# 'data' sub-directory

'''
1) Labor force, total:

World Bank definition: Labor force comprises people ages 15 and older who supply labor for the production 
of goods and services during a specified period. It includes people who are currently 
employed and people who are unemployed but seeking work as well as first-time job-seekers.
Not everyone who works is included, however. Unpaid workers, family workers, and students
are often omitted, and some countries do not count members of the armed forces. 
Labor force size tends to vary during the year as seasonal workers enter and leave.

Summary: Labor force = people who have a job or people who are looking for a job
data source: https://data.worldbank.org/indicator/sl.tlf.totl.in

------------------------------------------------------------------------------------------

2) Unemployment, total (% of total labor force) (modeled ILO estimate):

World Bank definition: Unemployment refers to the share of the labor force that is without work but available
for and seeking employment.

Summary: Unemployment = percent of labor force looking for a job
data source: https://data.worldbank.org/indicator/SL.UEM.TOTL.ZS

------------------------------------------------------------------------------------------

3) Employment in agriculture (% of total employment) (modeled ILO estimate):

World Bank definition: Employment is defined as persons of working age who were engaged in any activity 
to produce goods or provide services for pay or profit, whether at work during the 
reference period or not at work due to temporary absence from a job, or to working-time 
arrangement. The agriculture sector consists of activities in agriculture, hunting, 
forestry and fishing, in accordance with division 1 (ISIC 2) or categories A-B (ISIC 3) 
or category A (ISIC 4).

Summary: Employment in agriculture = percent of people who have a job in agriculture
data source: https://data.worldbank.org/indicator/sl.agr.empl.zs

'''

# ----ANALYSIS----

# First, we will find the number of people who have a job.
# We can estimate that value as follows:
# Number of people employed = Number of people in labor force * (1-unemployment)

# Locate and read in the data on the number of people in the labor force
file_loc = dir+'data/API_SL.TLF.TOTL.IN_DS2_en_csv_v2_10580635/API_SL.TLF.TOTL.IN_DS2_en_csv_v2_10580635.csv'
labor_force = pd.read_csv(file_loc, skiprows=[0,1,2,3])
# Filter out the data that represents the whole world in 2018
labor_force_wld2018 = labor_force[labor_force['Country Name']=='World']['2018'].values[0]

# Locate and read in the percent of the labor for that is unemployed
file_loc = dir+'data/API_SL.UEM.TOTL.ZS_DS2_en_csv_v2_10576601/API_SL.UEM.TOTL.ZS_DS2_en_csv_v2_10576601.csv'
unemployment_p = pd.read_csv(file_loc, skiprows=[0,1,2,3])
# Filter out the data that represents the whole world in 2018
unemployment_p_wld2018 = unemployment_p[unemployment_p['Country Name']=='World']['2018'].values[0]

# Calculate the number of people who are employed:
n_employed_wld2018 = labor_force_wld2018*(1 - unemployment_p_wld2018/100)

# Now, we want to figure out how many of the people who are employed are working in agriculture
# We can estimate that value as follows:
# Number employed in agriculture = Number of people employed * Percent employment in agriculture

# Locate and read in the data on the percent of people employed in agriculture
file_loc = dir+'data/API_SL.AGR.EMPL.ZS_DS2_en_csv_v2_10576798/API_SL.AGR.EMPL.ZS_DS2_en_csv_v2_10576798.csv'
employment_in_ag_p = pd.read_csv(file_loc, skiprows=[0,1,2,3])
# Filter out the data that represents the whole world in 2018
employment_in_ag_p_wld2018 = employment_in_ag_p[employment_in_ag_p['Country Name']=='World']['2018'].values[0]

# Calculate the number of people who are employed in agriculture:
n_employed_in_ag_wld2018 = n_employed_wld2018*(employment_in_ag_p_wld2018/100)

# Print result:
print('Number of people employed globally in agriculture in 2018 (estimated): {:,}'.format(math.trunc(round(n_employed_in_ag_wld2018))))