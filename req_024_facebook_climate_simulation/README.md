# NASA Earth Exchange Global Daily Downscaled Projections (NEX-GDDP) Data
This file describes the analysis done by the Resource Watch team for Facebook to be used in displaying Representative Concentration Pathways (RCP) in their newly launched [Climate Science Center](https://www.facebook.com/climatescienceinfo/). RCPs are hypothetical models that predict how various concentrations of greenhouse gases in the atmosphere will change due to future human activities. The goal of this analysis is to demonstrate two RCPs with differing levels of future concentrations: 4.5 (moderate levels of greenhouse gases) and 8.5 (very high levels of greenhouse gases).

Check out the Climate Science Center (CSC) for up-to-date information on climate data in your area from trusted sources. And go to [Resource Watch](https://resourcewatch.org/) to explore over 300 datasets covering topics from food, forests, water, oceans, cities, energy, climate, and society. This analysis was originally performed by [Avra Saslow](https://www.wri.org/profile/avra-saslow) and was QC'd by [Kristine Lister](https://www.wri.org/profile/kristine-lister).

### Data Sources
This analysis was done using the data from the [NASA Earth Exchange Global Daily Downscaled Projections (NEX-GDDP) dataset](https://www.nccs.nasa.gov/services/data-collections/land-based-products/nex-gddp), which provides four global models that predict change in greenhouse gases. The administrative global area is from [GADM](https://gadm.org/). 

### Methods
The objective of this analysis is to gather raster image files for each RCP, and determine the mean value over country and state regions. This is done with the following steps:

1. Fetch NEX-GDDP zipfile.
2. Gather administrative area gpkg file from GADM, and extract country and state regions (GADM levels 0 and 1). 
2. Aggregate mean 4.5 RCP for state/country regions.
3. Aggregate mean 8.5 RCP for state/country regions.
4. Export the results as a CSV file.


### Final Data
The final data can be viewed in the data directory. 
1. NEX_GDDP_45_countries.csv
    - Country level mean value for RCP 4.5 
2. NEX_GDDP_85_countries.csv
    - Country level mean value for RCP 8.5 
3. NEX_GDDP_45_states.csv
   - State level mean value for RCP 4.5 
4. NEX_GDDP_85_states.csv
    - State level mean value for RCP 8.5 



### References
- Gassert, F., E. Cornejo, and E. Nilson. 2021. “Making Climate Data Accessible: Methods for Producing NEX-GDDP and LOCA Downscaled Climate Indicators” Technical Note. Washington, DC: World Resources Institute. Available online at https://www.wri.org/research/making-climate-data-accessible. www.resourcewatch.org.

- Global Administrative Areas (2021). GADM database of Global Administrative Areas, version 3.6. \[online\] URL: [www.gadm.org](www.gadm.org).
