## This file describes the blog analysis that was done for Airports and Sealevel Rise

This calculation was done using Google Earth Engine, a free geospatial analysis system by Google. The code itself can be found [here](https://code.earthengine.google.com/d9c15a9bcd09461d13fe671bc3afff94). While the sytem is free you need to sign up with a Google account, which can be done [here](https://earthengine.google.com/).

The first objective of this analysis is to find airports that are threatened by sealevel rise at 0.5m and 1m level. This analysis involves three steps:

1) find airports with altitude below 0.5m and 1m using the "altitude" field from airport dataset.

2) Create a buffer with a 1000 meter radius around the coordinate for each airport to represent the actual area of the airport. This of course do not represent the real airport sizes, and is likely an underestimation.  

3) Check which of these airports that are below 0.5m elevation or 1m elevation are predicted to have sea water inside the 1000m buffer in their respective sea level rise scenarios. This is done using the Areas Vulnerable to Coastal Flooding & Sea Level Rise (m) on Resource Watch (https://resourcewatch.org/data/explore/Projected-Sea-Level-Rise).

The second objective of the analysis is to find how many airports per continent will be impacted by sealevel rise at 0.5m and 1m level. This analysis is first done by spatially joining a continent shapefile to airports threatened by sealevel rise.   

However, the result includes airports that are closed. We then cleaned up the results by checking if the airport is still in operation through an online search. Also, some airports are not captured by the continent boundary shapefile, we manually added them to the spreadsheet.

Please find the final analysis results in the [Final Results folder](https://github.com/resource-watch/blog-analysis/tree/master/blog_021a_airports_sealevel/final_results).
