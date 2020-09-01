'''
This code converts results in Kelvin to Celsius and reformats the file structure
'''
# Import libraries
import pandas as pd
import os
import numpy as np
import glob

# Define working folder
out_folder = 'IntermediateResults'
os.chdir(out_folder)

# Define countries and states to loop over
country_file_list = ['adm0_kelvin.csv','USA_adm1_kelvin.csv','GBR_adm1_kelvin.csv','DEU_adm1_kelvin.csv','FRA_adm1_kelvin.csv']
                
columns_to_remove = ['system:index','.geo']

# Define years to average over [1950,2019]
years = np.arange(1948,2021)


# Loop through countries and states in list
for country_file in country_file_list:
    # Define output file
    output_file = country_file.replace('kelvin','monthly')
    
    #Read in data
    monthly_data = pd.read_csv(country_file)
    
    # Remove extra columns from Google Earth Engine
    columns_to_keep = [x for x in list(monthly_data) if x not in columns_to_remove]
    monthly_data = monthly_data[columns_to_keep]
    
    # Select attribute columns
    attribute_columns = [x for x in list(monthly_data) if 'b1' not in x]
    # Save these attribute columns for the output
    out_data = monthly_data.copy()[attribute_columns]
    
    #Get list of data columns (Earth Engine adds a '_b1' to data columns)
    month_columns = [x for x in list(monthly_data) if 'b1' in x]
    
    #Convert all average monthly measurements from Kelvin to Celsius
    monthly_data[month_columns] = monthly_data[month_columns] - 273.15
    
    #Reformat average monthly measurement columns to nicer format
    new_month_columns = [x.replace('_b1','') for x in month_columns]
    new_month_columns = [x.replace('_','-') for x in new_month_columns]
    monthly_data = monthly_data.rename(columns=dict(zip(month_columns,new_month_columns)))
    
    #Merge attribute columns and measurement results
    out_data = pd.concat([out_data,monthly_data],axis=1)
    
    #If the file is the national level results, export one row to a CSV and rename to 'File Name' in attribute
    #This is to especially to split out the all of USA and contiguous USA results into separate files so they won't be confused
    if 'adm0' in country_file:
        #Loop through rows
        for i,row in out_data.iterrows():
            #Define output file name
            output_file = '{}_monthly.csv'.format(row['File Name'].values[0])
            #Reformat shape and export
            row = row.to_frame().transpose()
            row.to_csv(output_file,index=False)
    #Otherwise save results
    else:
        # Save results
        out_data.to_csv(output_file,index=False)