import numpy as np
from sklearn.linear_model import LinearRegression
import os
import pandas as pd


# Define working folder
out_folder = 'Results'
os.chdir(out_folder)

# Define countries and states to loop over
country_file_list = ['FRA_adm0_annual.csv','DEU_adm0_annual.csv','GBR_adm0_annual.csv',
                        'USA_adm0_annual.csv','USA_adm0_contiguous_annual.csv','USA_adm1_annual.csv',
                        'GBR_adm1_annual.csv','DEU_adm1_annual.csv','FRA_adm1_annual.csv']

years = np.arange(1950,2020)
years_1970 = np.arange(1970,2020)

for country_file in country_file_list:
    country_df = pd.read_csv(country_file)
    
    attribute_columns = [x for x in list(country_df) if x not in map(str, years)]
    out_df = country_df.copy()[attribute_columns]
    
    temperature_columns = [x for x in list(country_df) if x in map(str, years)]
    temperature_data = country_df[temperature_columns]
    
    
    for i,row in temperature_data.iterrows():
        #1950 - 2019 change
        change = row['2019'] - row['1950']
        out_df.at[i,'Change_1950_2019'] = change
        
        row_temp_data = row.values
        
        model = LinearRegression().fit(years.reshape((-1, 1)), row_temp_data)
        
        out_df.at[i,'LinReg_1950_2019_Intercept'] = model.intercept_        
        out_df.at[i,'LinReg_1950_2019_Slope'] = model.coef_[0]
        out_df.at[i,'LinReg_1950_2019_R_Squared'] = model.score(years.reshape((-1, 1)), row_temp_data)
        
        
        #1970 - 2019 change
        change = row['2019'] - row['1970']
        out_df.at[i,'Change_1970_2019'] = change
        
        row_temp_data = row[map(str, years_1970)].values
        
        model = LinearRegression().fit(years_1970.reshape((-1, 1)), row_temp_data)
        
        out_df.at[i,'LinReg_1970_2019_Intercept'] = model.intercept_        
        out_df.at[i,'LinReg_1970_2019_Slope'] = model.coef_[0]
        out_df.at[i,'LinReg_1970_2019_R_Squared'] = model.score(years_1970.reshape((-1, 1)), row_temp_data)
        
    out_df.to_csv(country_file.replace('annual','annual_regression'),index=False)