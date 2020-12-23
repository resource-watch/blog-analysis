'''
This code downloads the temperature data for our analysis from NOAA. The source of the temperature data is the GHCN CAMS Gridded 2m Temperature (Land) (https://psl.noaa.gov/data/gridded/data.ghcncams.html)
The original NetCDF file contains monthly average temperature at 0.5 degree resolution in degrees Kelvin from January 1948 through May 2020.
The original NetCDF had longitude ranging from 0 to 360 degrees, which must be shifted to -180 to 180 degrees in order to match our country boundary polygons.

The package CDO was used to shift the NetCDF longitude and calculate annual temperatures, 
instructions on how to dowload the package can be found here https://www.unidata.ucar.edu/software/netcdf/workshops/most-recent/third_party/CDO.html
'''
# Import necessary libraries
import subprocess
import os
import urllib.request
import os

#Create data directory
data_dir = 'data'
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

#Switch to data directory
os.chdir(data_dir)
    
# Define URL to download data
url = 'ftp://ftp.cdc.noaa.gov/Datasets/ghcncams/air.mon.mean.nc'
file_name = 'air.mon.mean.nc'

# Download data
urllib.request.urlretrieve(url, file_name)

# Define command to shift longitude range
cmd = ('cdo sellonlatbox,-180,180,-90,90 air.mon.mean.nc air.mon.mean.centered.nc')
# Run command
subprocess.check_output(cmd,shell=True)

# Define command to calculate annual temperatures from monthly temperatures
cmd = ('cdo yearmean air.mon.mean.centered.nc air.annual.mean.nc')
# Run command
subprocess.check_output(cmd,shell=True)

#Create folder to save annual NetCDF files to
if not os.path.exists('AnnualNetCDF'):
    os.makedirs('AnnualNetCDF')

# Define NetCDF name
in_netcdf = 'air.annual.mean.nc'

#Define years to separate netcdf for
years = np.arange(1950,2020)

#Loop through years
for year in years:
    #define command to separate netcdf by one year
    cmd = ('cdo -selyear,{} air.annual.mean.nc AnnualNetCDF/{}.nc'.format(year,year))
    subprocess.check_output(cmd,shell=True)