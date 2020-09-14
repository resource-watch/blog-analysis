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

#Define years for linear regression
years = np.arange(1950,2020)
years_1970 = np.arange(1970,2020)

for country_file in country_file_list:
    country_df = pd.read_csv(country_file)
    
    #Separate attribute columns and data
    attribute_columns = [x for x in list(country_df) if x not in map(str, years)]
    out_df = country_df.copy()[attribute_columns]
    
    #Get temperature columns and data
    temperature_columns = [x for x in list(country_df) if x in map(str, years)]
    temperature_data = country_df[temperature_columns]
    
    
    for i,row in temperature_data.iterrows():
        #Calculate change in average temperature over different time period lengths
        change = np.mean(row[[str(x) for x in np.arange(2009,2020)]])-np.mean(row[[str(x) for x in np.arange(1950,1971)]])
        
        out_df.at[i,'Change_2009_2019-1950_1970'] = change
        

        #Get list of values for linear regression
        row_temp_data = row.values
        #Fit linear regression
        model = LinearRegression().fit(years.reshape((-1, 1)), row_temp_data)
        #Save values
        out_df.at[i,'LinReg_1950_2019_Intercept'] = model.intercept_
        out_df.at[i,'LinReg_1950_2019_Slope'] = model.coef_[0]
        out_df.at[i,'LinReg_1950_2019_R_Squared'] = model.score(years.reshape((-1, 1)), row_temp_data)

        #Get list of values for linear regression
        row_temp_data = row[map(str, years_1970)].values
        #Fit linear regression
        model = LinearRegression().fit(years_1970.reshape((-1, 1)), row_temp_data)
        #Save values
        out_df.at[i,'LinReg_1970_2019_Intercept'] = model.intercept_
        out_df.at[i,'LinReg_1970_2019_Slope'] = model.coef_[0]
        out_df.at[i,'LinReg_1970_2019_R_Squared'] = model.score(years_1970.reshape((-1, 1)), row_temp_data)
    
    #Save results
    out_df.to_csv(country_file.replace('annual','regression_and_change'),index=False)