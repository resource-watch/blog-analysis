# Average Monthly and Annual Temperature for France, Germany, the United Kingdom, and the United States from 1950 through 2019
This file describes analysis that was done by the Resource Watch team for Facebook to be used to display increased temperatures in the four countries listed above.

This analysis was done using the [GHCN CAMS Gridded 2m Temperature (Land)](https://psl.noaa.gov/data/gridded/data.ghcncams.html) dataset, 
which provides monthly average surface temperature measured 2 meters above surface level in degrees Celsius from January 1948 through May 2020 at 0.5 × 0.5 degree 
resolution and was created by the Climate Prediction Center at the National Centers for Environmental Prediction of the National Oceanic and Atmospheric Administation ([NCEP](https://www.ncep.noaa.gov/)).

The GHCN CAMS dataset is created by interpolating measurements from combination two large individual data sets of station observations collected from the 
Global Historical Climatology Network version 2 and the Climate Anomaly Monitoring System (GHCN + CAMS).

The goal of this analysis is to calculate the average monthly and annual temperatures in four countries (France, Germany, the United Kingdom, and the United States)
at the national and state/provincial level from 1950 through 2019. This analysis was done in five steps:
1. Download the tempearture data from NCEP using [download_temperature_data_and_shift.py](https://github.com/resource-watch/blog-analysis/blob/master/req_016_facebook_average_surface_temperature/download_temperature_data_and_shift.py)
2. Download country bounds from GADM using [download_country_and_state_boundaries.py](https://github.com/resource-watch/blog-analysis/blob/master/req_016_facebook_average_surface_temperature/download_country_and_state_boundaries.py)
3. Separate a combined NetCDF of the monthly temperature data into individual monthly data [separate_netcdf_by_month.py](https://github.com/resource-watch/blog-analysis/blob/master/req_016_facebook_average_surface_temperature/separate_netcdf_by_month.py)
4. Savea separate file for the contiguous United States using QGIS, described in the file [separate_contiguous_united_states.txt](https://github.com/resource-watch/blog-analysis/blob/master/req_016_facebook_average_surface_temperature/separate_contiguous_united_states.txt)
5. Calculate the average monthly surface temperature using the file [calculate_average_monthly_temperature.py](https://github.com/resource-watch/blog-analysis/blob/master/req_016_facebook_average_surface_temperature/calculate_average_monthly_temperature.py)
6. Average monthly results to annual using the file [average_monthly_to_annual.py](https://github.com/resource-watch/blog-analysis/blob/master/req_016_facebook_average_surface_temperature/average_monthly_to_annual.py)

The results of this analysis can be viewed in the directory [Results](https://github.com/resource-watch/blog-analysis/tree/master/req_016_facebook_average_surface_temperature/Results) where all temperature values are given in degrees Celsius.

The citations for the GHCN CAMS dataset are below
- GHCN Gridded V2 data provided by the NOAA/OAR/ESRL PSL, Boulder, Colorado, USA, from their Web site at https://psl.noaa.gov/ 
- Fan, Y., and H. van den Dool (2008), A global monthly land surface air temperature analysis for 1948-present, J. Geophys. Res., 113, D01103, doi:10.1029/2007JD008470.
