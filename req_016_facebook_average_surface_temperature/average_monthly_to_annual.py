'''
This code takes results on monthly average temperature in a state or country and averages the monthly values to annual
'''
# Import libraries
import pandas as pd
import os
import numpy as np
import glob

# Define working folder
out_folder = 'Results'
os.chdir(out_folder)

# Define countries and states to loop over
country_list = ['DEU_adm0','DEU_adm1','FRA_adm0','FRA_adm1','GBR_adm0','GBR_adm1','USA_adm0','USA_adm1','USA_adm0_contiguous']
# Define CSV names for monthly (input) data and annual (output) data
monthly_file_name = '{}_monthly.csv'
annual_file_name = '{}_annual.csv'

# Loop through countries and states in list
for country in country_list:
    # Define output file
    output_file = annual_file_name.format(country)
    # Load in monthly data
    monthly_data = pd.read_csv(monthly_file_name.format(country))
    
    # Find attribute columns that don't represent monthly data
    columns_to_keep = [x for x in list(monthly_data) if '-' not in x]
    # Save these attribute columns for the output
    out_data = monthly_data.copy()[columns_to_keep]
    # Define years to average over [1950,2019]
    years = np.arange(1950,2020)
    
    # Loop through years to average
    for year in years:
        # Find columns that represent monthly average temperature in that year
        month_columns = [x for x in list(monthly_data) if str(year) in x]
        # Subset data by those columns
        year_data_by_month = monthly_data[month_columns]
        # Take average across these columns to average monthly data to annual data
        out_data[str(year)] = year_data_by_month.mean(axis=1)
    # Save results 
    out_data.to_csv(output_file,index=False)