## Airports Affected by Sea Level Rise Analysis

This file describes the analysis that was done for the blog "[Runways Underwater: Map Show Where Rising Seas Threaten 80 Airports Around the World](https://blog.resourcewatch.org/2020/02/05/runways-underwater-maps-show-where-rising-seas-threaten-80-airports-around-the-world/)," posted on the [Resource Watch blog](https://blog.resourcewatch.org/).

The first objective of this analysis was to find airports that would be threatened if sea levels were to rise 0.5 meters, as well as those that would be threatened if they rose 1 meter. This analysis involves three steps:

1) Find airports at an altitude below 0.5 meters and those at an altitude below 1 meter using the "altitude" field from the [Airports](https://resourcewatch.org/data/explore/com002-Airports_replacement) dataset on [Resource Watch](https://resourcewatch.org/).
2) The Airports dataset represents each airport as a single point, defined by a pair of coordinates. In order to better represent the area covered by each airport, a buffer with a radius of 1000 meters was created around the point representing each airport. This buffered area is a conservative approximation and likely underestimates the actual size of the airports.  
3) Check which of the airports that are below an altitude of 0.5 meters are predicted to have sea water inside the 1000 meter buffer. Do the same for the airports with an altitude below 1 meter. The area covered by seawater was represented by the [Areas Vulnerable to Coastal Flooding & Sea Level Rise (m)](https://resourcewatch.org/data/explore/Projected-Sea-Level-Rise) dataset on [Resource Watch](https://resourcewatch.org/).
4) Airports for seaplanes were removed from the results. Seaplanes are a type of amphibious aircraft that are able to take off and land on water. Airports that directly cater to seaplanes were removed because many of these airports sit on bodies of water and are automatically flagged as at risk.
5) The Airports dataset includes some airports that have closed since the dataset was produced. To improve the accuracy of the results, each airport that was affected by one of the sea level rise sceniarios (0.5 meters or 1 meter sea level rise) was manually checked to ensure it was still in operation. This was done through an online search.

The second objective of the analysis was to determine which continent would be most impacted by sea level rise, based on how many affected airports were found on each continent. This analysis was done for both the 0.5 meters and 1 meter sea level rise scenarios. For each sea level rise scenario, the affected airports were manually assigned to a continent. The affected airports were then summed by continent in Excel.

This analysis was done using Google Earth Engine, a free geospatial analysis system by Google. While the system is free, you need to sign up with a Google account in order to use it, which can be done [here](https://earthengine.google.com/).

If you have a Google Earth Engine account, the code used for the analysis can be viewed [in Google Earth Engine](https://code.earthengine.google.com/5b7bd8baed8d29cb46f787afaeef41eb). If you do not have an account, you can still view a copy of the code [here](https://github.com/resource-watch/blog-analysis/blob/master/blog_021_airports_affected_by_sea_level_rise/EarthEnginecode.md).

You can find the results of this analysis in the [Final Results folder](https://github.com/resource-watch/blog-analysis/blob/master/blog_021_airports_affected_by_sea_level_rise/Final%20Results).

###### Note: This dataset analysis was done by [Tina Huang](https://www.wri.org/profile/tina-huang), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
