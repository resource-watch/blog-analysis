# Greenhouse Gas Emissions Data
This file describes the analysis that was done by the Resource Watch team for Facebook to be used to display Greenhouse Gas (GHG) emissions for select countries in their newly launched [Climate Science Information Center](https://www.facebook.com/hubs/climate_science_information_center). The goal of the analysis is to demonstrate historical GHG emissions from 1990 through 2018, and Nationally Determined Contributions (NDCs) for select countries. 

Check out the Climate Science Information Center (CSIC) for up-to-date information on climate data in your area from trusted sources. And go to [Resource Watch](https://resourcewatch.org/) to explore over 300 datasets covering topics from food, forests, water, oceans, cities, energy, climate, and society. This analysis was originally performed by [Weiqi Zhou](https://www.wri.org/profile/weiqi-zhou) and was QC'd by [Kristine Lister](https://www.wri.org/profile/kristine-lister).

### Data Sources
This analysis was done using the data on [Climate Watch](https://www.climatewatchdata.org) dataset, which provides historical GHG emissions data from 1990 to 2018 for 193 countries and 2 regions (World and European Union), and NDCs for 161 countries.

### Data
The final data can be viewed in the directory [data](https://github.com/resource-watch/blog-analysis/blob/master/req_020_facebook_ghg_emissions/data/).
1. [Historical GHG Emissions Data](https://github.com/resource-watch/blog-analysis/blob/master/req_020_facebook_ghg_emissions/data/historical_emissions_edit.csv)
    - Historical GHG emissions data from 1990 to 2018 for 193 countries and 2 regions (World and European Union). 
    - Emissions have 7 different sectors: Agriculture, Energy, Industrial Processes, Land-Use Change and Forestry, Total excluding LUCF, Total including LUCF, Waste.
    - Agriculture + Energy + Industrial Processes + Waste = Total excluding LUCF
    - Total excluding LUCF + Land-Use Change and Forestry = Total including LUCF
    - Cook Islands and Niue don't have data for 'Industrial Processes'.
2. [NDC Links](https://github.com/resource-watch/blog-analysis/blob/master/req_020_facebook_ghg_emissions/data/NDC_links_edit.csv)
    - Links to the country's NDC overview page, full NDC page, embed URL, and embed code.
    - The embed URL for countries that have historical emissions data but don't have NDCs can be got from: https://climatewatchdata.org/embed/countries/{*country ISO code*\}/ghg-emissions
3. [NDCs Data](https://github.com/resource-watch/blog-analysis/blob/master/req_020_facebook_ghg_emissions/data/NDC_quantification_edit.csv)
    - The Paris Agreement requests each country to outline and communicate their post-2020 climate actions, known as their NDCs.
    - This dataset has NDCs for 161 countries.
    - There is a 'range' (bool) column in the data. The 'range' is Yes when the country submitted a reduction range. For example, the USA committed a '50% to 52% reduction by 2030 compared to 2005', then for 2030, the USA has two values (one for 50% and one for 52%) and the 'range' column is Yes.

### References
- Climate Watch. 2020. Washington, DC: World Resources Institute. Available online at: [https://www.climatewatchdata.org](https://www.climatewatchdata.org).