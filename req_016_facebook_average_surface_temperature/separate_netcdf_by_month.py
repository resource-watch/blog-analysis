'''
This code takes a single netCDF file that contains monthly average temperature at 0.5 degree resolution in degrees Kelvin from January 1948 through May 2020
and separates the data into individual netCDF's that contain a single month's average temperature.
This allows the individual monthly netCDF's to be used in the raster_stats module to calculate the average monthly temperature in a given polygon.
The source of the temperature data is the GHCN CAMS Gridded 2m Temperature (Land) (https://psl.noaa.gov/data/gridded/data.ghcncams.html)
and the original netCDF was downloaded from ftp://ftp.cdc.noaa.gov/Datasets/ghcncams/air.mon.mean.nc

A transformation was performed from the original downloaded file to change the longitude bounds from [0,360] to [-180,180] using the CDO software (https://www.unidata.ucar.edu/software/netcdf/workshops/most-recent/third_party/CDO.html)
The command was:
cdo sellonlatbox,-180,180,-90,90 air.mon.mean.nc air.mon.mean.centered.nc
'''

import netCDF4 as nc
import numpy as np
from rasterstats import zonal_stats
import os
from datetime import date, timedelta


# Define NetCDF name
nc_fo = 'air.mon.mean.centered.nc'
# Read NetCDF of monthly climate data in Kelvin
ncin = nc.Dataset(nc_fo, 'r', format='NETCDF4')
 
# Read in time, latitude, and longitude variables
tin = ncin.variables['time']
latitude = ncin.variables['lat']
longitude = ncin.variables['lon']
nlat = len(latitude)
nlon = len(longitude)

# Read in climate data
vin = ncin.variables['air']

# Define list of time-steps read from the NetCDF which is in units of "Hours since 1800-01-01"
time_values = tin[:].tolist()

# Loop through the time steps
for i, time in enumerate(time_values):
    # Convert the original units ("hours since 1800-01-01") to a year-month-day format
    hours = time
    start = date(1800,1,1)
    delta = timedelta(hours=hours)
    offset = start + delta

    # Define output netCDF file
    out_file_name = 'MonthlyNetCDF/{}.nc'.format(str(offset))
    
    #Open a netCDF file to write
    ncout = nc.Dataset(out_file_name, 'w', format='NETCDF4')
    # define axis size
    ncout.createDimension('time', None)  # unlimited
    ncout.createDimension('lat', nlat)
    ncout.createDimension('lon', nlon)
    
    # create time axis
    time = ncout.createVariable('time', np.dtype('double').char, ('time',))
    time.long_name = 'time'
    time.units = 'hours since 1800-01-01 00:00:00'
    time.calendar = 'standard'
    time.axis = 'T'

    # create latitude axis
    lat = ncout.createVariable('lat', np.dtype('double').char, ('lat'))
    lat.standard_name = 'latitude'
    lat.long_name = 'latitude'
    lat.units = 'degrees_north'
    lat.axis = 'Y'

    # create longitude axis
    lon = ncout.createVariable('lon', np.dtype('double').char, ('lon'))
    lon.standard_name = 'longitude'
    lon.long_name = 'longitude'
    lon.units = 'degrees_east'
    lon.axis = 'X'

    # create variable array
    vout = ncout.createVariable('air', np.dtype('double').char, ('time', 'lat', 'lon'),fill_value=-9.96921e+36)
    vout.long_name = 'Monthly mean of surface temperature'
    vout.units = 'K'

    # copy axis from original dataset
    time[:] = tin[i]
    lon[:] = longitude[:]
    lat[:] = latitude[:]

    # Select value at the given time step to export
    vout[0,:,:] = vin[i,:,:]
    vout = vout[0,:,:]

    # close files
    ncout.close()
    
# close file
ncin.close()