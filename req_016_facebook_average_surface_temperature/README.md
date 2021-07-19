# Average Annual Temperature for Select Countries and Global Scale
This file describes analysis that was done by the Resource Watch team for Facebook to be used to display increased temperatures for select countries in their newly launched [Climate Science Information Center](https://www.facebook.com/hubs/climate_science_information_center). Check out the Climate Science Information Center (CSIC) for up to date information on climate data in your area from trusted sources. And go to [Resource Watch](https://resourcewatch.org/) to explore over 300 datasets covering topics from food, forests, water, oceans, cities, energy, climate, and society. This analysis was originally performed by [Kristine Lister](https://www.wri.org/profile/kristine-lister) and was QC'd by Taufiq Rashid.

This analysis was done using the [GHCN CAMS Gridded 2m Temperature (Land)](https://psl.noaa.gov/data/gridded/data.ghcncams.html) dataset, 
which provides monthly average surface temperature measured 2 meters above surface level in degrees Celsius from January 1948 through June 2021 at 0.5 × 0.5 degree 
resolution and was created by the Climate Prediction Center at the National Centers for Environmental Prediction of the National Oceanic and Atmospheric Administation ([NCEP](https://www.ncep.noaa.gov/)).

The GHCN CAMS dataset is created by interpolating measurements from combination two large individual data sets of station observations collected from the 
Global Historical Climatology Network version 2 and the Climate Anomaly Monitoring System (GHCN + CAMS).

The goal of this analysis is to calculate the average monthly and annual tempe
1. Upload annual temperature data to Google Earth Engine and calculate the average annual surface temperature using the file [Calculate_Annual_Temperature.py](https://github.com/resource-watch/blog-analysis/blob/master/req_016_facebook_average_surface_temperature/Calculate_Annual_Temperature.py)
2. Calculate a linear regression through time and change from 1950-1970 average to 2009-2020 average [regression_and_change.py](https://github.com/resource-watch/blog-analysis/blob/master/req_016_facebook_average_surface_temperature/regression_and_change.py)

Note for the global analysis, constraints from Earth Engine on the complexity of shapes did not allow us to clip the temperature data to land boundaries. Therefore for the global average, the Resource Watch team calculated the average value of the available temperature data, which does cover some non-land coastal areas. 

The results of this analysis can be viewed in the directory [results](https://github.com/resource-watch/blog-analysis/tree/master/req_016_facebook_average_surface_temperature/results) where all temperature values are given in degrees Celsius.

The citations for the GHCN CAMS dataset are below
- GHCN Gridded V2 data provided by the NOAA/OAR/ESRL PSL, Boulder, Colorado, USA, from their Web site at https://psl.noaa.gov/ 
- Fan, Y., and H. van den Dool (2008), A global monthly land surface air temperature analysis for 1948-present, J. Geophys. Res., 113, D01103, [doi:10.1029/2007JD008470](doi:10.1029/2007JD008470).
