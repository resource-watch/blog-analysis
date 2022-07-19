# Air Quality Data
This file describes the analysis that was done by the Resource Watch team for Facebook to be used to display global air quality data in their newly launched [Climate Science Center](https://www.facebook.com/climatescienceinfo/). The goal of the analysis is to demonstrate state-level air quality for the current day and 5-day forecast. 

Check out the Climate Science Center (CSC) for up-to-date information on climate data in your area from trusted sources. And go to [Resource Watch](https://resourcewatch.org/) to explore over 300 datasets covering topics from food, forests, water, oceans, cities, energy, climate, and society. This analysis was originally performed by [Weiqi Zhou](https://www.wri.org/profile/weiqi-zhou) and was QC'd by [Kristine Lister](https://www.wri.org/profile/kristine-lister).

### Data Sources
This analysis was done using the data from [Goddard Earth Observing System Composition Forecast (GEOS-CF)](https://gmao.gsfc.nasa.gov/weather_prediction/GEOS-CF/), which provides near real-time distributions of atmospheric composition. State-level daily zonal analysis was produced using the administrative area data from [GADM](https://gadm.org/). 

### Methods
This dataset is provided by the source as netcdf files, with one file for each hour of the day. Inside each netcdf file, the nitrogen dioxide data can be found in the 'NO2' variable of the netcdf file, the ozone data in 'O3', and the fine particulate matter data in 'PM25_RH35_GCC'. The first objective of this analysis is to combine the hourly pollutants data into daily files. This analysis was done using the file [Air_Quality.py](https://github.com/resource-watch/blog-analysis/blob/master/req_022_facebook_air_quality/Air_Quality.py), following the steps:
1. Fetch the hourly netcdf files using the URLs.
2. Convert the netcdf files to tif files.
3. Hourly tif files are combined into daily files by calculating a specific metric for each variable.
4. For both nitrogen dioxide and PM2.5, a daily average is calculated, and for ozone, the daily maximum value is calculated.
5. The units for ozone and nitrogen dioxide are converted from mol/mol to parts per billion (ppb)
6. The original source units are kept for fine particulate matter.
7. Export the daily files as tif files.

The second objective of this analysis is to calculate the daily average/maximum value at state-level, following the steps:
1. Download the state-level shape file from GADM.
2. Calculate the state-level average for nitrogen dioxide and PM2.5, and state-level maximum for ozone.
3. Export the results as a CSV file.

### References
- Knowland, K.E., C.A. Keller, and R. Lucchesi. 2019. File Specification for GEOS-CF Products. GMAO Office Note no. 17 (Version 1.0). [https://gmao.gsfc.nasa.gov/pubs/office_notes.php](https://gmao.gsfc.nasa.gov/pubs/office_notes.php)
- Global Administrative Areas (2021). GADM database of Global Administrative Areas, version 3.6. \[online\] URL: [www.gadm.org](www.gadm.org).
