# Resource Watch Blog Analysis Github
#### Purpose
This Github repository was created to document analyses done for calculations done on the [Resource Watch Blog](https://blog.resourcewatch.org/).

#### File Structure
Each analysis should be stored in a single file, named with the Blog ID and a descriptive title for the analysis. This folder should **always** include a README.md file that describes the analysis that was done. If a script (preferably Python) was used for the analysis, that code should also be included as a separate file. The general structure can be summarized as follows:

```
Repository
|
|- Analysis 1 folder = {blog_id}_{descriptive_title}
| |-{blog_id}_{descriptive_title}_analysis.py # optional, script used for analysis
| |-README.md # file describing the analysis
| +-...
|
|-Analysis 2 folder
| +-...
|
+-...
```

#### Contents of README.md
If the analysis was done in Excel, and functions used should be clearly described. If it was done in Carto, any SQL statements should be included as code snippets. For analyses that were done in Google Earth Engine (GEE), a link to the GEE script should be included, AND the code should be included in the README.md file as a code snippet for users who do not have access to Google Earth Engine.

If the analysis was done using a script that has been uploaded to Github, the readme should still be included and describe the general steps that were taken - which datasets were used, what years do they represent, how were they combined, what calculations were done, etc.


#### Contents of script, if included
If a script was used for the analysis, the code should be uploaded to this Github. This code should be thoroughly commented so that readers unfamiliar with the coding language can still follow the process.

All codes should be written using open-source tools and programming languages. Tools and modules that require a subscription should be avoided (e.g., ArcGIS).

A few general rules should be followed when creating these scripts to make it easy for users to get working and reproduce results on their own computer. These steps are described, below:
- Create a directory to store your code and do your analysis using the naming convention described above. All data inputs or analysis outputs should go into this folder. Define that directory at the beginning of each script using the following line of code (with {blog_id} and {descriptive_title} replaced by the appropriate values):
```
dir = os.getenv(BLOG_DIR)+'{blog_id}_{descriptive_title}/'
```
- Pull any input data directly from source or Resource Watch API in the script. Avoid downloading data manually to your computer to avoid confusion about where the user should find the data.
- As you pull each new dataset, briefly describe the dataset, the source, and explain how you will use it.
- Make sure units are clearly defined in any output tables.
- Save all results that were cited in the blog to a csv file in the directory defined at the beginning of the script.
