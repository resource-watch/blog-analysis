import numpy as np
from sklearn.linear_model import LinearRegression
import os
import pandas as pd
import dotenv

# Get script folder
os.chdir(os.path.dirname(os.path.realpath(__file__)))
# Define working folder
data_folder = 'results'
if not os.path.exists(data_folder):
    os.makedirs(data_folder)
os.chdir(data_folder)

# Define years for linear regression
years = np.arange(1901,2020)
# Define state-level metadata columns
meta_list = ['GID_0', 'NAME_0', 'GID_1', 'NAME_1', 'VARNAME_1', 'NL_NAME_1', 'TYPE_1', 'ENGTYPE_1', 'CC_1', 'HASC_1']
# load file name
file_name = 'GPCC_annual_state_level_mean.csv'

# Loop through each state
# Read the data into a pandas dataframe
state_df = pd.read_csv(file_name)
# Subset precipitation data to years
state_precip = state_df[[str(year) for year in years]]
# Subset state-level metadata
state_meta = state_df[meta_list]
# Copy metadata columns as output dataset
out_df = state_meta.copy()
# Calculate mean precipitation of 1901-2000 as baseline
out_df['Baseline'] = state_precip[[str(year) for year in np.arange(1901,2001)]].mean(axis=1)

for i,row in state_precip.iterrows():
    # Get list of values for linear regression
    row_temp_data = row.values

    # Fit linear regression
    model = LinearRegression().fit(years.reshape((-1, 1)), row_temp_data)
    # Save values
    out_df.at[i,'LinReg_1901_2019_Intercept'] = model.intercept_
    out_df.at[i,'LinReg_1901_2019_Slope'] = model.coef_[0]
    out_df.at[i,'LinReg_1901_2019_R_Squared'] = model.score(years.reshape((-1, 1)), row_temp_data)

out_df['RateChange_1901_2019'] = out_df['LinReg_1901_2019_Slope'] * len(years) / out_df['Baseline'] * 100
# Save results
out_df.to_csv(file_name.replace('mean.csv','regression_and_rate_change.csv'), index = False)

# Copy annual precipitation dataset as smooth dataset
state_precip_smooth = state_precip.copy()
# 9-point binomial filter smooth
weight = [1, 8, 28, 56, 70, 56, 28, 8, 1]
# Calculate weighted average
for i in range(state_precip.shape[1]):
    if i>=4 and i<=(state_precip.shape[1]-5):
        temp = state_precip.iloc[:,(i-4):(i+5)]
        state_precip_smooth.iloc[:,i] = (temp*weight).sum(axis=1)/sum(weight)
    elif i<4:
        temp = state_precip.iloc[:,0:(i+5)]
        state_precip_smooth.iloc[:,i] = (temp*weight[(4-i):9]).sum(axis=1)/sum(weight[(4-i):9])
    elif i>(state_precip.shape[1]-5):
        temp = state_precip.iloc[:,(i-4):state_precip.shape[1]]
        state_precip_smooth.iloc[:,i] = (temp*weight[0:4+state_precip.shape[1]-i]).sum(axis = 1)/sum(weight[0:4+state_precip.shape[1]-i])

# Copy metadata columns as output dataset
out_df = state_meta.copy()
# Concat metadata and smooth dataset
out_df = pd.concat([out_df,state_precip_smooth], axis = 1)
# Save results
out_df.to_csv(file_name.replace('.csv','_smooth.csv'), index = False)
