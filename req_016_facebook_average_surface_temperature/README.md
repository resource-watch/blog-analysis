# Average Annual Precipitation for Select Countries and States
This file describes analysis that was done by the Resource Watch team for Facebook to be used to display annual precipitation for select countries in their newly launched [Climate Science Information Center](https://www.facebook.com/hubs/climate_science_information_center). The goal of the analysis is to demonstrate trends in total precipitation at the state and national level for select countries from 1901 through 2019. 

Check out the Climate Science Information Center (CSIC) for up to date information on climate data in your area from trusted sources. And go to [Resource Watch](https://resourcewatch.org/) to explore over 300 datasets covering topics from food, forests, water, oceans, cities, energy, climate, and society. This analysis was originally performed by [Weiqi Zhou](https://www.wri.org/profile/weiqi-zhou) and was QC'd by [Kristine Lister](https://www.wri.org/profile/kristine-lister).

### Data Sources
This analysis was done using the [Global Precipitation Climatology Centre (GPCC)](https://www.dwd.de/EN/ourservices/gpcc/gpcc.html) dataset, 
which provides monthly land-surface precipitation from rain-gauges built on GTS-based and historical data from January 1891 through December 2019 at 0.25 × 0.25 degree resolution. The Global Precipitation Climatology Centre (GPCC) is operated by [Deutscher Wetterdienst (DWD)](https://www.dwd.de/EN/Home/home_node.html) under the auspices of the [World Meteorological Organization (WMO)](https://public.wmo.int/en)

The GPCC Full Data Monthly Version 2020 for the period 1891 to 2019 based on quality-controlled data from all stations in GPCC's data base available at the month of regard with a maximum number of more than 53,000 stations in 1986/1987. This product is optimized for best spatial coverage and use for water budget studies. 

### Methods
The first objective of this analysis is to calculate the average annual precipitation in numerous countries at the national and state/provincial level from 1891 through 2019. This analysis was done using the file [Calculate_Annual_Precipitation.py](https://github.com/resource-watch/blog-analysis/blob/master/req_019_facebook_total_precipitation/Calculate_Annual_Precipitation.py), following the steps:
1. Download the precipitation data from GPCC. 
2. Convert the netCDF files to GeoTIFF files.
3. Aggregate annual total precipitation data using monthly precipitation data.
4. Upload proccessed annual precipitation data to Google Earth Engine.
5. Calculate national and state/provincial level mean annual precipitation.
6. Export the results as CSV files.

The second objective of this analysis is to calculate the rate of precipitation change 1901-2019 at the state/provincial level. *This objective followed the method of the [U.S. and Global Mean Temperature and Precipitation indicator (Exhibit 8)](https://cfpub.epa.gov/roe/indicator.cfm?i=89#8).* This analysis was done using the file [Regression_Rate_Change_and_Smooth.py ](https://github.com/resource-watch/blog-analysis/blob/master/req_019_facebook_total_precipitation/Regression_Rate_Change_and_Smooth.py), following the steps:
1. Calculate the slope of each precipitation trend from annual precipitation (in millimeters) by fiting an ordinary least-squares regression.
2. Multiplie the slope by the length of the entire period of record to get total change in millimeters. 
3. Convert the total change to percent change, using average precipitation during the standard baseline period (1901-2000) as the denominator.
4. Export the results as CSV files.


The third objective of this analysis is to calculate a smooth precipitation time series from 1901 to 2019 at the state/provincial level. *This objective followed the smooth trend method of the [U.S. and Global Mean Temperature and Precipitation indicator (Exhibit 7)](https://cfpub.epa.gov/roe/indicator.cfm?i=89#7).* This analysis was done using the file [Regression_Rate_Change_and_Smooth.py ](https://github.com/resource-watch/blog-analysis/blob/master/req_019_facebook_total_precipitation/Regression_Rate_Change_and_Smooth.py). The smoothed precipitation time series was created using a 9-point binomial filter where 4 years on each side of a given value are averaged with decreasing weights further from the center year ([Aubury and Luk, 1995](www.doc.ic.ac.uk/~wl/papers/bf95.pdf)).

### Results
The results of this analysis can be viewed in the directory [results](https://github.com/resource-watch/blog-analysis/tree/master/req_019_facebook_total_precipitation/results) where all precipitation values are given in millimeter.
- The original country level data was named: GPCC_annual_country_\{*country ISO code*\}.csv
- The original state/provincial level data was named: GPCC_annual_state_\{*country ISO code*\}.csv
- The state/provincial level regression and rate change result was named: GPCC_annual_country_\{*country ISO code*\}\_regression_and_rate_change.csv
- The state/provincial level smoothed data was named: GPCC_annual_country_\{*country ISO code*\}\_smooth.csv

### References
- Schneider, Udo; Becker, Andreas; Finger, Peter; Rustemeier, Elke; Ziese, Markus. (2020). GPCC Full Data Monthly Product Version 2020 at 0.25°: Monthly Land-Surface Precipitation from Rain-Gauges built on GTS-based and Historical Data. DOI: [10.5676/DWD_GPCC/FD_M_V2020_025](10.5676/DWD_GPCC/FD_M_V2020_025)

- Environmental Protection Agency (EPA). (2021). Report on the Environment. U.S. and Global Mean Temperature and Precipitation. Retrieved from [https://cfpub.epa.gov/roe/indicator.cfm?i=89](https://cfpub.epa.gov/roe/indicator.cfm?i=89)
