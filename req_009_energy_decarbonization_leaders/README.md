## Energy Decarbonization Analysis
This file describes the analysis that was done for the blog "**6 Lessons on Energy Decarbonization from Countries Leading the Way**," posted on [Insights](https://www.wri.org/blog) and [TheCityFix](https://thecityfix.com/).

This analysis involves two calculations:
1) **The national electricity consumption as portion of total primary energy consumption**
    - This was done using the [Electricity Consumption](https://resourcewatch.org/data/explore/ene034-Electricity-Consumption) and [Energy Consumption](https://resourcewatch.org/data/explore/ene033-Energy-Consumption_1) datasets on [Resource Watch](https://resourcewatch.org/).
    - Each country's electricity consumption was divided by its total energy consumption for each year that data was available.
    - This calculation can be found in the "Electricity Consumption per Total Energy Consumption" section of the [Python script](https://github.com/resource-watch/blog-analysis/blob/master/req_009_energy_decarbonization_leaders/req_009_energy_decarbonization_leaders_analysis.py).

2) **The national rate of improvement in energy intensity**
    - This was done with the [Energy Intensity](https://resourcewatch.org/data/explore/2c444596-2be3-4786-bdfc-24010f99b21e) dataset on [Resource Watch](https://resourcewatch.org/).
    - For each year of data, every country's annual rate of change in energy intensity was calculated.
    - This calculation can be found in the "Annual Rate of Change for Energy Intensity" section of the [Python script](https://github.com/resource-watch/blog-analysis/blob/master/req_009_energy_decarbonization_leaders/req_009_energy_decarbonization_leaders_analysis.py).

Please see the [Python script](https://github.com/resource-watch/blog-analysis/blob/master/req_009_energy_decarbonization_leaders/req_009_energy_decarbonization_leaders_analysis.py) for the full analysis.

###### Note: This dataset analysis was done by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).