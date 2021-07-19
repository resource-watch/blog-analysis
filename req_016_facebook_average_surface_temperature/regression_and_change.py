import numpy as np
from sklearn.linear_model import LinearRegression
import os
import pandas as pd
import statsmodels.api as sm


# Define working folder
out_folder = 'results'
if not os.path.exists(out_folder):
    os.makedirs(out_folder)
os.chdir(out_folder)

# Define countries and states to loop over
file_list = ['Average_Temperature_Country_Level.csv','Average_Temperature_State_Level.csv','Average_Temperature_Global_Level.csv']

#Define years for linear regression
years = np.arange(1950,2021)
years_1970 = np.arange(1970,2021)

for file_name in file_list:
    country_df = pd.read_csv(file_name)
    
    if 'Global' in file_name:
        country_df['Region'] = 'Global'
    
    #Separate attribute columns and data
    attribute_columns = [x for x in list(country_df) if x not in map(str, years)]
    attribute_columns = [x for x in attribute_columns if x not in ['system:index','.geo']]
    out_df = country_df.copy()[attribute_columns]
    
    #Get temperature columns and data
    temperature_columns = [x for x in list(country_df) if x in map(str, years)]
    temperature_columns.sort()
    temperature_data = country_df[temperature_columns]
    
    #Reorder columns and resave CSV
    select_columns = attribute_columns+temperature_columns
    select_columns = [x for x in select_columns if x not in ['system:index','.geo']]
    country_df = country_df[select_columns]
    country_df.to_csv(file_name,index=False)
    
    for i,row in temperature_data.iterrows():
        #Check if data is available for all years
        if ~row.isnull().all():
        
            #Calculate change in average temperature over different time period lengths
            change = np.mean(row[[str(x) for x in np.arange(2009,2021)]])-np.mean(row[[str(x) for x in np.arange(1950,1971)]])
        
            out_df.at[i,'Change_2009_2020-1950_1970'] = change
        
        
            #Get list of values for linear regression
            row_temp_data = row.values

            #Fit linear regression
            model = LinearRegression().fit(years.reshape((-1, 1)), row_temp_data)
            #Save values
            out_df.at[i,'LinReg_1950_2020_Intercept'] = model.intercept_
            out_df.at[i,'LinReg_1950_2020_Slope'] = model.coef_[0]
            out_df.at[i,'LinReg_1950_2020_R_Squared'] = model.score(years.reshape((-1, 1)), row_temp_data)
            
            #Get p-value
            statsmodel = sm.OLS(row_temp_data,years)
            fii = statsmodel.fit()
            p_values = fii.summary2().tables[1]['P>|t|']
            out_df.at[i,'LinReg_1950_2020_P_Value'] = p_values.values[0]

            #Get list of values for linear regression
            row_temp_data = row[map(str, years_1970)].values
            #Fit linear regression
            model = LinearRegression().fit(years_1970.reshape((-1, 1)), row_temp_data)
            #Save values
            out_df.at[i,'LinReg_1970_2020_Intercept'] = model.intercept_
            out_df.at[i,'LinReg_1970_2020_Slope'] = model.coef_[0]
            out_df.at[i,'LinReg_1970_2020_R_Squared'] = model.score(years_1970.reshape((-1, 1)), row_temp_data)
            
            #Get p-value
            statsmodel = sm.OLS(row_temp_data,years_1970)
            fii = statsmodel.fit()
            p_values = fii.summary2().tables[1]['P>|t|']
            out_df.at[i,'LinReg_1970_2020_P_Value'] = p_values.values[0]
            
        #if data is not available for all years, save values as Null
        else:
            out_df.at[i,'Change_2009_2020-1950_1970'] = None
            out_df.at[i,'LinReg_1950_2020_Intercept'] = None
            out_df.at[i,'LinReg_1950_2020_Slope'] = None
            out_df.at[i,'LinReg_1950_2020_R_Squared'] = None
            out_df.at[i,'LinReg_1950_2020_P_Value'] = None
            out_df.at[i,'LinReg_1970_2020_Intercept'] = None
            out_df.at[i,'LinReg_1970_2020_Slope'] = None
            out_df.at[i,'LinReg_1970_2020_R_Squared'] = None
            out_df.at[i,'LinReg_1970_2020_P_Value'] = None
            
    
    #Save results
    out_df.to_csv(file_name.replace('.csv','_regression_and_change.csv'),index=False)