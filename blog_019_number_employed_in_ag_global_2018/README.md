## Employment in Agriculture Analysis
This file describes the analysis that was done for the blog "**[Map of the Month: How Many People Work in Agriculture?](https://blog.resourcewatch.org/2019/05/30/map-of-the-month-how-many-people-work-in-agriculture/)**," posted on the [Resource Watch blog](https://blog.resourcewatch.org/).

This analysis uses World Bank data to determine an estimate of how many people were working in agriculture globally in 2018. This was done with the following steps:

1) Estimate the number of people who were employed in 2018. This was done by pulling in data on the total labor force, which is the people who have a job or people who are looking for a job, and the unemployment rate, which is percent of labor force looking for a job. The total labor force was multiplied by (1 - unemployment rate) to determine how many people were employed.
    - This calculation was done using the [Unemployment Rate](https://resourcewatch.org/data/explore/com036-Unemployment-Percent) dataset on [Resource Watch](https://resourcewatch.org/) and the [Labor force, total](https://data.worldbank.org/indicator/sl.tlf.totl.in) dataset from the World Bank.
2) Of the people who were employed, determine how many worked in agriculture. This was estimated by multiplying the number of people who were employed by the percent employment in agriculture.
    - This calculation was done using the [Employment in Agriculture](https://resourcewatch.org/data/explore/soc074-Employment_in_agriculture) dataset on [Resource Watch](https://resourcewatch.org/).

Please see the [Python script](https://github.com/resource-watch/blog-analysis/blob/master/blog_019_number_employed_in_ag_global_2018/blog_019_number_employed_in_ag_global_2018_analysis.py) for the full analysis.

###### Note: This dataset analysis was done by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).