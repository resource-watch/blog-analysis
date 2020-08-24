'''
This code calculates the average monthly temperature from January 1948 through May 2020 using the GHCN CAMS Gridded 2m Temperature (Land) dataset (https://psl.noaa.gov/data/gridded/data.ghcncams.html)
Given a list of country and state boundaries (with associated shapefiles taken as subsets from GADM (https://gadm.org/index.html)) the code loops through all months of available data
and calculates the regional mean of the monthly temperature for each feature (which represent states and countries) and saves the results as a CSV.
'''
import rasterio as rio
import geopandas as gpd
import rasterstats as rstats
import os
import numpy as np
import glob

#Define file format for netCDF files
nc_fo = 'NETCDF:"{}":air'
#Define folder to export results to
out_folder = 'Results'
#Define folder to read country boundaries from
shape_file_folder = 'CountryShapes'
#Define list of country and state boundaries to calculate average temperature
shape_file_list = ['FRA_adm0','FRA_adm1','DEU_adm0','DEU_adm1','GBR_adm0','GBR_adm1','USA_adm0','USA_adm1','USA_adm0_contiguous']

#Load in all netCDF files for 1948 through 2020
file_list = glob.glob('MonthlyNetCDF/*.nc')
#List them in chronological order
file_list.sort()

#Loop through country and state boundaries
for shape_file in shape_file_list:
    #Print name to track progress
    print(shape_file)
    #Read shapefile
    shp_df = gpd.read_file(os.path.join(shape_file_folder,shape_file,'{}.shp'.format(shape_file)))
    #Define CSV to export to
    out_file = os.path.join(out_folder,'{}_monthly.csv'.format(shape_file))

    #Loop through shapefile rows, which for the country files is only one row for the entire country, and for the state files a separate row for each state
    for i,row in shp_df.iterrows():
        #Loop through months of climate data
        for file_name in file_list:
            #Define column name from netCDF file name (year and month)
            column_name = os.path.basename(file_name).split('.')[0]
            #Calculate average temperature for given month in the state or country
            result = rstats.zonal_stats(row['geometry'], nc_fo.format(file_name), stats="mean")
            result = [x.get('mean') for x in result][0]
            #If the result=None, this means no pixel had their center fall into the region (this can happen for small regions like the District of Columbia or Berlin)
            #Therefore we change the calculation to include all pixels that touched the polygon
            if result==None:
                result = rstats.zonal_stats(row['geometry'], nc_fo.format(file_name), stats="mean",all_touched=True)
                result = [x.get('mean') for x in result][0]
            #Convert temperature from Kelvin to Celsius
            try:
                result = result-273.15
            #This fails if the temperature=None
            except:
                result = None
            #Save result to shapefile
            shp_df.at[i,column_name] = result
    #Drop geometry column from shapefile which is not needed for the CSV and save memory
    shp_df = shp_df.drop(columns=['geometry'])
    #Export to CSV
    shp_df.to_csv(out_file,index=False)