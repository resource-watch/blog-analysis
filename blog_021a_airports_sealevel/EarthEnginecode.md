```
// The objective of this analysis is to find airports that would be threatened by 0.5m of sea level rise
// and those that would be affected by and 1m of sea level rise.

// This analysis involves four steps:
// 1) Find airports at an altitude below 0.5 meters and those at an altitude below 1 meter using the "altitude" 
//    field from the Airports dataset on Resource Watch:
//    https://resourcewatch.org/data/explore/com002-Airports_replacement
// 2) The Airports dataset represents each airport as a single point, defined by a pair of coordinates. In order
//    to better represent the area covered by each airport, a buffer with a radius of 1000 meters was created 
//    around the point representing each airport. This buffered area is a conservative approximation and likely 
//    underestimates the actual size of the airports.  
// 3) Check which of the airports that are below an altitude of 0.5 meters are predicted to have seawater inside 
//    the 1000 meter buffer. Do the same for the airports with an altitude below 1 meter. The area covered by 
//    seawater was represented by the Areas Vulnerable to Coastal Flooding & Sea Level Rise (m) dataset on 
//    Resource Watch: https://resourcewatch.org/data/explore/Projected-Sea-Level-Rise
// 4) The Airports dataset includes some airports that have closed since the dataset was produced. To improve the 
//    accuracy of the results, each airport that was affected by one of the sea level rise sceniarios (0.5 meters 
//    or 1 meter sea level rise) was manually checked to ensure it was still in operation. This was 
//    done through an online search.


// Import the sea level rise data

// The sea level rise dataset comes from Climate Central. It identifies areas vulnerable to coastal 
// flooding and sea level rise. Learn more about the dataset on Resource Watch: 
// https://resourcewatch.org/data/explore/Projected-Sea-Level-Rise

var sealevel = ee.Image("");
// Note: the sea level rise image location has been removed from this code.
// If you would like access to this dataset, please contact Climate Central: 
// https://sealevel.climatecentral.org/

// There are 10 bands that each correspond to different sea level rise scenarios.

// select the band that corresponds to sea level rise of 0.5 meters (m)
// band 1 (b1) represents the 0.5m scenario
var sealevel_05m = sealevel.select('b1');

// display sea level rise 0.5m on the map
Map.addLayer(sealevel_05m,
           {bands :["b1"],palette : ['000080'], opacity:0.5},
           "Sea Level Rise, 0.5 m", false);
           
// select the band that corresponds to sea level rise of 1 meter (m)
// band 2 (b2) represents the 1m scenario
var sealevel_1m = sealevel.select('b2');

// display sea level rise 1m on the map
Map.addLayer(sealevel_1m,
           {bands :["b2"],palette : ['000080'], opacity:0.5},
           "Sea Level Rise, 1m", false);


// Import airports data

// This dataset is released by OpenFlights in 2017 and has global coverage of airports.
// Learn more about the dataset on Resource Watch: https://resourcewatch.org/data/explore/Airports

var airports = ee.FeatureCollection("users/resourcewatch/com_002_airports_edit");

// Select airports with altitude below 0.5m. The airport altitude is reported in feet,
// so we will look for airports with an altitude below 1.64042 feet (0.5m * 3.38084ft/m).
var airports_b05m = airports.filter(ee.Filter.lt('altitude',1.64042))
print(airports_b05m) //169 airports are below an altitutde of 0.5m

// Visualize airports below altitude 0.5m
Map.addLayer(airports_b05m, {color : 'ffff00'}, 'Airports altitude below 0.5m (yellow)', false)

// The airport dataset lists airports as single points. To better account for airport size, this
// analysis buffers an area with 1000 meter radius around each airport point and assumes those buffered
// circles are the area covered by the airport. While the choice of 1000 meters is arbitrary, it is on the
// more conservative spectrum in estimating airport sizes. It is important to note though, that for
// airports along the coasts, a larger radius is less desirable because there is a greater chance that
// the buffered airports will extend into the sea.

// Create function to buffer airports by 1000m
function PointBufferingALGORITHM1( AnyGivenPointFEATURE )
      {return AnyGivenPointFEATURE.buffer(1000);
      }

// Get the scale for the sea level rise dataset, which we will use in later functions
var scale = sealevel_05m.projection().nominalScale().getInfo()

// Write a function that checks if airports are affected by sea level rise of 0.5m
function checkIfAffected_05m( airport ) {
 // Check if there are any 0.5m sea level rise pixels within the airport buffered area
 var affected = sealevel_05m.reduceRegion({
   reducer: ee.Reducer.anyNonZero(),
   geometry: airport.geometry(),
   scale: scale}) ;

 // Set the 'affected' parameter with the result (0 or 1)
 // Airports being affected will return values of 1
 var new_feature = airport.set('affected', affected.get('b1'))
 return new_feature;
 }


// Buffer airports with altitude below 0.5m
var airports_b05m_buffer_1000 = airports_b05m.map(PointBufferingALGORITHM1);

// Map our function over buffered airports below 0.5m altitude to see which were affected by 0.5m sea level rise
var altitudeb05m_buffer_1000_affected_05m = airports_b05m_buffer_1000.map(checkIfAffected_05m)

// Find the airports below 0.5 altitude that were affected by 0.5m sea level rise
var airports_05m_risk_altitude = altitudeb05m_buffer_1000_affected_05m.filterMetadata('affected', 'equals', 1);

// Filter out seaplanes
// Seaplanes are a type of amphibious aircraft that are able to take off and land on water.
// We filtered out airports that directly cater to seaplanes because many of these airports sit on
// bodies of water and are automatically triggered as at risk.
var airports_05m_risk_altitude = airports_05m_risk_altitude.filterMetadata('name', 'not_contains', 'Sea');

// Create a list of the names of the airports that were affected by this scenario
// The element number of this list indicates how many airports currently below sea level 0.5m will be affected
// by sea level rise 0.5m
var list_05m = ee.List(airports_05m_risk_altitude.aggregate_array('name'))
print("Airports Threatened by sea level Rise 0.5m ", list_05m)
// This shows that 48 airports will be affected by 0.5m of sea level rise.

// Visualize these airports
Map.addLayer(airports_05m_risk_altitude, {color : 'ff0000'}, 'Airports threatened by sea level rise, 0.5m')

// Export results
Export.table.toDrive({
 collection: airports_05m_risk_altitude,
 description: 'Airports_05m_altitude_threaten',
 fileFormat: 'CSV'
});

// Now we will repeat the analysis to see which airports would be affected by 1m of sea level rise,
// instead of 0.5m sea level rise.
// Select airports with altitude below 1m. The airport altitude is reported in feet,
// so we will look for airports with an altitude below 3.38084 feet (1m * 3.38084ft/m).
var airports_b1m = airports.filter(ee.Filter.lt('altitude',3.38084))

// Visualize airports below altitude 1m
Map.addLayer(airports_b1m, {color : 'ffff00'}, 'Airports altitude below 1m (yellow)', false)

// Buffer airports below 1m altitude
var airports_b1m_buffer_1000 = airports_b1m.map(PointBufferingALGORITHM1);

function checkIfAffected_1m( airport ) {
 // Check if there are any 1m sea level rise pixels within the airport buffered area
 var affected = sealevel_1m.reduceRegion({
   reducer: ee.Reducer.anyNonZero(),
   geometry: airport.geometry(),
   scale: scale}) ;

 // Set the 'affected' parameter with the result (0 or 1)
 // Airports being affected will return values of 1
 var new_feature = airport.set('affected', affected.get('b2'))
 return new_feature;
 }

// Map our function over buffered airports below 1m altitude to see which were affected by 1m sea level rise
var altitudeb1m_buffer_1000_affected_1m = airports_b1m_buffer_1000.map(checkIfAffected_1m)

// Find the airports below 1m altitude that were affected by 1m sea level rise
var airports_1m_risk_altitude = altitudeb1m_buffer_1000_affected_1m.filterMetadata('affected', 'equals', 1)

// Filter out seaplanes
var airports_1m_risk_altitude = airports_1m_risk_altitude.filterMetadata('name', 'not_contains', 'Sea');

// Create a list of the names of the airports that were affected by this scenario
var list_1m = ee.List(airports_1m_risk_altitude.aggregate_array('name'))
print("Airports Threatened by sea level Rise 1m ", list_1m)
// This shows that 85 airports will be affected

// Visualize these airports
Map.addLayer(airports_1m_risk_altitude, {color : 'ff0000'}, 'airports threatened by sea level rise, 1m')

// Export results
Export.table.toDrive({
 collection: airports_1m_risk_altitude,
 description: 'Airports_1m_altitude_threaten',
 fileFormat: 'CSV'
});

// The Airports dataset includes some airports that have closed since the dataset was produced. To improve the 
// accuracy of the results, each airport that was affected by one of the sea level rise scenarios (0.5 meters 
// or 1 meter sea level rise) was manually checked to ensure it was still in operation. This was done by 
// checking the airports in the output results file (Airports_1m_altitude_threaten.csv) through an online search.

// Analysis by continent
// This part of the analysis aims to determine how many airports that were affected by sea level rise came
// from each continent.

// The first step is to manually assign a continent to each affected airport in the results files:
// Airports_1m_altitude_threaten.csv and Airports_05m_altitude_threaten.csv
// The continent assigned to each affected airport can be viewed in the results files uploaded to Github:
// https://github.com/resource-watch/blog-analysis/tree/master/blog_021a_airports_sealevel/Final%20Results

// Using the assigned continents, the number of airports that were affected by 0.5 and 1m sea level rise for 
// each continent were then counted in Excel.
```
