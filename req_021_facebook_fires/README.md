# Fire Data
This file describes the analysis that was done by the Resource Watch team for Facebook to be used to display active fires and burned area for the United States in their newly launched [Climate Science Center](https://www.facebook.com/climatescienceinfo/). The goal of the analysis is to demonstrate burned area from 2002 through 2020 for the United States. 

Check out the Climate Science Center (CSC) for up-to-date information on climate data in your area from trusted sources. And go to [Resource Watch](https://resourcewatch.org/) to explore over 300 datasets covering topics from food, forests, water, oceans, cities, energy, climate, and society. This analysis was originally performed by [Weiqi Zhou](https://www.wri.org/profile/weiqi-zhou) and was QC'd by [Kristine Lister](https://www.wri.org/profile/kristine-lister).

### Data Sources
This analysis was done using the data from [Global Wildfire Information System (GWIS)](https://gwis.jrc.ec.europa.eu/), which provides state level burned area from 2002 to 2019 by landcover. Burned area data for 2020 was added using the fire data from [NASA LP DAAC at the USGS EROS Center](https://lpdaac.usgs.gov/products/mcd64a1v006/) and the administrative areas of the United States from [GADM](https://gadm.org/).

### Methods
The first objective of this analysis is to fetch and subset the state level burned area data for the United States from 2002 through 2019. This analysis was done using the file [Fire_by_LULC.py](https://github.com/resource-watch/blog-analysis/blob/master/req_021_facebook_fires/Fire_by_LULC.py), following the steps:
1. Download the Global Monthly Burned Area data from GWIS.
2. Subset the data to the United States. 
3. Calculate the total burned area for each state.
4. Aggregate annual burned area using monthly burned area data.
5. Export the results as a CSV file.

The second objective of this analysis is to calculate the total burned area for 2020. This analysis was done in ArcGIS Pro, following the steps:
1. Download MODIS Burned Area Monthly Global 500m Tiffs for 2020.
2. Reclassify the monthly Tiffs. Sign pixels with a burn day of year to 1, and sign pixels without a burn day of year to 0.
3. Perform a zonal statistics using the state level shapefile as zone, and count the number of non-zero pixels for each state.
4. Save the results of the zonal statistics as database files (.dbf).
5. Load .dbf files as pandas dataframes.
6. Calculated monthly total burned area for each state using the number of non-zero pixels and the spatial resolution of the Tiffs.
7. Aggregate annual total burned area using monthly total burned area data.
8. Append the 2020 burned area dataframe to the 2002-2019 burned area dataframe.
9. Export the results as a CSV file.

### Final Data
The final data can be viewed in the directory [data](https://github.com/resource-watch/blog-analysis/blob/master/req_021_facebook_fires/data/).
1. [yearly_USA_2020](https://github.com/resource-watch/blog-analysis/blob/master/req_021_facebook_fires/data/yearly_USA_2020.csv)
    - State level burned area data from 2002 to 2020.

### References
- Boschetti, L., Sparks, A., Roy, D.P., Giglio, L., San-Miguel-Ayanz, J., GWIS national and sub-national fire activity data from the NASA MODIS Collection 6 Burned Area Product in support of policy making, carbon inventories and natural resource management, developed under NASA Applied Sciences grant #80NSSC18K0400, Using the NASA Polar Orbiting Fire Product Record to Enhance and Expand the Global Wildfire Information System (GWIS).

- Giglio, L., C. Justice, L. Boschetti, D. Roy. MCD64A1 MODIS/Terra+Aqua Burned Area Monthly L3 Global 500m SIN Grid V006. 2015, distributed by NASA EOSDIS Land Processes DAAC, [https://doi.org/10.5067/MODIS/MCD64A1.006](https://doi.org/10.5067/MODIS/MCD64A1.006).

- Global Administrative Areas (2021). GADM database of Global Administrative Areas, version 3.6. \[online\] URL: [www.gadm.org](www.gadm.org).
