# Indicator Report for GCBR
This file describes analysis that was done by the Resource Watch team for the Gouritz Cluster Biosphere Reserve (GCBR) to test using Resource Watch for Dashboards to study environmental indicators in GCBR's management units. Several indicators were analyzed, described below:

1. Monthly average NDVI from the [MODIS MOD13Q1.061 Terra Vegetation Indices 16-Day](https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD13Q1) dataset
2. Monthly average Leaf Area Index and FAPAR from the [NOAA AVHRR LAI FAPAR](https://developers.google.com/earth-engine/datasets/catalog/NOAA_CDR_AVHRR_LAI_FAPAR_V5) dataset
3. Monthly average rainfall from the [CHIRPS pentad (5-day) precipitation](https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHG_CHIRPS_PENTAD) dataset
4. Annual average temperature from the [NOAA's GHCN CAMS temperature](https://psl.noaa.gov/data/gridded/data.ghcncams.html)
5. Monthly total burn area from the [MCD64A1.061 MODIS Burned Area Monthly Global 500m](https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD64A1) dataset
6. Monthly total fire brightness from the [FIRMS: Fire Information for Resource Management System](https://developers.google.com/earth-engine/datasets/catalog/FIRMS) dataset
7. Surface water dynamics from the [JRC Global Surface Water](https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_GlobalSurfaceWater) dataset
8. Land cover compisition from the [South Africa National Land Cover](https://egis.environment.gov.za/sa_national_land_cover_datasets) dataset



### Methods
This analysis was performed using Google Earth Engine's Python API and is available in this [Jupyter notebook](https://github.com/resource-watch/blog-analysis/tree/master/req_024_gcbr_indicator_report/GCBR_Indicator_Report.ipynb).

### Results
The results of this analysis can be viewed in the directory [results](https://github.com/resource-watch/blog-analysis/tree/master/req_024_gcbr_indicator_report/results).

### References
- Didan, K. (2021). MODIS/Terra Vegetation Indices 16-Day L3 Global 250m SIN Grid V061. NASA EOSDIS Land Processes Distributed Active Archive Center. [doi:10.5067/MODIS/MOD13Q1.061](https://doi.org/10.5067/MODIS/MOD13Q1.061).
- Fan, Y., and H. van den Dool (2008), A global monthly land surface air temperature analysis for 1948-present, J. Geophys. Res., 113, D01103, [doi:10.1029/2007JD008470](https://doi.org/10.1029/2007JD008470).
- Funk, Chris, Pete Peterson, Martin Landsfeld, Diego Pedreros, James Verdin, Shraddhanand Shukla, Gregory Husak, James Rowland, Laura Harrison, Andrew Hoell & Joel Michaelsen. "The climate hazards infrared precipitation with stations-a new environmental record for monitoring extremes". Scientific Data 2, 150066. [doi:10.1038/sdata.2015.66](https://doi.org/10.1038/sdata.2015.66)
- GHCN Gridded V2 data provided by the NOAA/OAR/ESRL PSL, Boulder, Colorado, USA, from their Web site at https://psl.noaa.gov/ 
- Giglio, L., Justice, C., Boschetti, L., Roy, D. (2021). MODIS/Terra+Aqua Burned Area Monthly L3 Global 500m SIN Grid V061. NASA EOSDIS Land Processes Distributed Active Archive Center. [doi:10.5067/MODIS/MCD64A1.061](https://doi.org/10.5067/MODIS/MCD64A1.061)
- Jean-Francois Pekel, Andrew Cottam, Noel Gorelick, Alan S. Belward, High-resolution mapping of global surface water and its long-term changes. Nature 540, 418-422 (2016). [doi:10.1038/nature20584](https://doi.org/10.1038/nature20584)
- Martin Claverie, Eric Vermote, and NOAA CDR Program (2014): NOAA Climate Data Record (CDR) of Leaf Area Index (LAI) and Fraction of Absorbed Photosynthetically Active Radiation (FAPAR), Version 4. NOAA National Climatic Data Center. [doi:10.7289/V5M043BX](https://doi.org/10.7289/V5M043BX)
- MODIS Collection 6 NRT Hotspot / Active Fire Detections MCD14DL. Available on-line https://earthdata.nasa.gov/firms. [doi:10.5067/FIRMS/MODIS/MCD14DL.NRT.006](https://doi.org/10.5067/FIRMS/MODIS/MCD14DL.NRT.006)




