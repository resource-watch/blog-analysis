## This file describes the blog analysis that was done for Airports and Sealevel Rise

This calculation was done using Google Earth Engine, a free geospatial analysis system by Google. The code itself can be found [here](https://code.earthengine.google.com/91a8b8e1441a64e0a11f9a0b8eb1c632). While the sytem is free you need to sign up with a Google account, which can be done [here](https://earthengine.google.com/). 

The code is shown below:
```
// import sealevel rise image
// The sealevel rise dataset comes from Climate Central. It identifies areas vulnerable to coastal flooding and sealevel rise
// learn more the dataset here: https://resourcewatch.org/data/explore/Projected-Sea-Level-Rise

var sealevel = sealevel

// examine sealevel data

// there are 10 bands each correspond to different sea level rise scenarios.

print(sealevel)

// select sea level rise 1m  

var sealevel_1m = sealevel.select('b2');  // band 2 represents 1m scenario.

// display sealevel rise 1m on the map  

Map.addLayer(sealevel_1m,  

            {bands :["b2"],palette : ['000080'], opacity:0.5},

            "Sea Level Rise, 1m", false);


// select sea level rise 0.5 m  

var sealevel_05m = sealevel.select('b1'); // b1 represents 0.5 m scenario.

// display sealevel rise 1m on the map  

Map.addLayer(sealevel_05m,  

            {bands :["b1"],palette : ['000080'], opacity:0.5},

            "Sea Level Rise, 0.5 m", false);

// begin analysis
// the objective of this analysis is to find airports that are threatened by sealevel rise at 0.5m and 1m level.
// this analysis involves three steps:
// 1) find airports with altitude below 0.5m and 1m using the "altitude" field from airport dataset.

// 2) check- Create a buffer with a 1000 meter radius around the coordinate for each airport to represent the actual area of the airport. This of course do not represent the real airport sizes, and is likely an understimation.  

// 3) Check which of these airports that are below 0.5m elevation or 1m elevation are prediced to have sea water inside the 1000m buffer in their respective sea level rise scenarios. This is done using the Areas Vulnerable to Coastal Flooding & Sea Level Rise (m) on Resource Watch (https://resourcewatch.org/data/explore/Projected-Sea-Level-Rise).

// examine airports data
// this dataset is released by OpenFlights in 2017 and has a global coverage of airports
// learn more about the dataset on Resource Watch: https://resourcewatch.org/data/explore/Airports
// note that since there are more than 5000 airports, the entire dataset cannot be printed for examination together.
// instead, we can examine the first 10 airports to understand dataset fields
print(airports.limit(10))

// Select airports with altitude below 0.5m. The airport altitude is reported in feet, so we will look for airports with an altitude below 1.64042 feet (0.5m * 3.38084ft/m)"


var airports_b05m = airports.filter(ee.Filter.lt('altitude',1.64042))

print(airports_b05m) //169 airports are below 0.5 m

//Uncomment the next line by removing the // at the beggining to visualize airports below altitude 0.5m

//Map.addLayer(airports_b05m, {color : 'ffff00'}, 'Airports altitude below 0.5m (yellow)')


// The airport dataset lists airports as single points. To better account for airport size, this analysis buffers a 1000 meter radius around each airport point and assumes those buffered circles are an airport's size. While the choice of 1000 meters is arbitrary and on the more conservative spectrum in estimating airport sizes. It is important to note though, for airports along the coasts, a larger radius is less desirable because there is a greater chance that the buffered airports will extend into the sea.



function PointBufferingALGORITHM1( AnyGivenPointFEATURE )

       {  return AnyGivenPointFEATURE.buffer( 1000);

       }


// get the scale for sealevel rise  

var scale = sealevel_05m.projection().nominalScale().getInfo()



// write a function that checks if airports are being effected by sealevel rise , 0.5m
function checkIfAffected_05m( airport ) {

  // check if there are any 0.5 m sea level rise pixels within the airport buffered area

  var affected = sealevel_05m.reduceRegion({

    reducer: ee.Reducer.anyNonZero(),

    geometry: airport.geometry(),

    scale: scale}) ;

  // set the 'affected' parameter with the result (0 or 1)

  var new_feature = airport.set('affected', affected.get('b1')) // airports being affected will return values of 1  

  return new_feature;

  }


// buffer airports with altitude below 0.5m

var airports_b05m_buffer_1000 = airports_b05m.map( PointBufferingALGORITHM1 );

// map our function over buffered airports below 0.5m altitude to see which were affected by 0.5m sea level rise

var altitudeb05m_buffer_1000_affected_05m = airports_b05m_buffer_1000.map(checkIfAffected_05m)

//find the airports below 0.5 altitude that were affected by 0.5m sea level rise

var airports_05m_risk_altitude = altitudeb05m_buffer_1000_affected_05m.filterMetadata('affected', 'equals', 1);

// filter out seaplanes //note - can you explain this a little more? Describe what a sea plane is and why you are filtering them out.
var airports_05m_risk_altitude = airports_05m_risk_altitude.filterMetadata('name', 'not_contains', 'Sea');

// convert feature collection to a list
var airports_05m_risk_altitude_list = airports_05m_risk_altitude.toList(altitudeb05m_buffer_1000_affected_05m.size());

print(airports_05m_risk_altitude_list)// the element number of this list indicates 48 airports currently below sealevel 0.5m will be affected by sealevel rise 0.5m

// print only airport names in a list
var list_05m = ee.List(airports_05m_risk_altitude.aggregate_array('name'))

print(list_05m, "Airports Threatened by Sealevel Rise 0.5m ")

Map.addLayer(airports_05m_risk_altitude, {color : 'ff0000'}, 'airports threatened by sealevel rise, 0.5m')

// export result

Export.table.toDrive({

  collection: airports_05m_risk_altitude,

  description: 'Airports_05m_altitude_threaten',

  fileFormat: 'CSV'

});
// Now we will repeat the analysis to see which airports would be affected by 1m of sea level rise, instead of 0.5m sea level rise
// select airports with altitude below 1m  

var airports_b1m = airports.filter(ee.Filter.lt('altitude',3.38084))

//Uncomment the next line by removing the // at the beggining to visualize airports below altitude 0.5m

//Map.addLayer(airports_b1m, {color : 'ffff00'}, 'Airports altitude below 1m (yellow)')

// buffer airports below 1m altitude

var airports_b1m_buffer_1000 = airports_b1m.map( PointBufferingALGORITHM1 );

function checkIfAffected_1m( airport ) {

  // check if there are any 1m sea level rise pixels within the airport buffered area

  var affected = sealevel_1m.reduceRegion({

    reducer: ee.Reducer.anyNonZero(),

    geometry: airport.geometry(),

    scale: scale}) ;

  // set the 'affected' parameter with the result (0 or 1)

  var new_feature = airport.set('affected', affected.get('b2')) // airports being affected will return values of 1  

  return new_feature;

  }


// map our function over buffered airports below 1m altitude to see which were affected by 1m sea level rise

var altitudeb1m_buffer_1000_affected_1m = airports_b1m_buffer_1000.map(checkIfAffected_1m)

//find the airports below 1m altitude that were affected by 1m sea level rise

var airports_1m_risk_altitude = altitudeb1m_buffer_1000_affected_1m.filterMetadata('affected', 'equals', 1)

// filter out seaplanes. check -, Seaplanes, a type of amphibious aircraft, are able to take off and land on water. We filter out airports that directly cater to seaplanes because many of these airports sit on bodies of water and are automatically triggered as at risk.
var airports_1m_risk_altitude = airports_1m_risk_altitude.filterMetadata('name', 'not_contains', 'Sea');

var airports_1m_risk_altitude_list = airports_1m_risk_altitude.toList(altitudeb1m_buffer_1000_affected_1m.size());

print(airports_1m_risk_altitude_list)// the element number of this list indicates 85 airports currently below sealevel 1m will be affected by sealevel rise 1 m

// print only airport names in a list
var list_1m = ee.List(airports_1m_risk_altitude.aggregate_array('name'))

print(list_1m, "Airports Threatened by Sealevel Rise 1m ")

Map.addLayer(airports_1m_risk_altitude, {color : 'ff0000'}, 'airports threatened by sealevel rise, 1m')



// export result

Export.table.toDrive({

  collection: airports_1m_risk_altitude,

  description: 'Airports_1m_altitude_threaten',

  fileFormat: 'CSV'

});


// find how many airports at 0.5 m and 1m case are threatened for each continent

// import continents dataset. See metadata here:  https://www.arcgis.com/home/item.html?id=a3cb207855b348a297ab85261743351d

var allcontinents = ee.Feature(continents);

print(allcontinents, "Continents")//examine the continents


// create variables for each continent  

// South America  

var SouthAmerica = continents.filterMetadata('CONTINENT', 'equals', 'South America');

// Africa  

var Africa = continents.filterMetadata('CONTINENT', 'equals','Africa');  

// Europe  

var Europe = continents.filterMetadata('CONTINENT', 'equals', 'Europe');  

// Asia  

var Asia = continents.filterMetadata('CONTINENT', 'equals', 'Asia');  

// Australia  

var Australia = continents.filterMetadata('CONTINENT', 'equals', 'Australia');  

// Oceania  

var Oceania = continents.filterMetadata('CONTINENT','equals', 'Oceania');  

// North America  

var NorthAmerica = continents.filterMetadata('CONTINENT', 'equals', 'North America');  

// Antarctica  

var Antarctica = continents.filterMetadata('CONTINENT', 'equals', "Antarctica");  



// spatial join airports at risk with continent //check -   a spatial join find places where the features in one collection intersect those in another. In this case, we find where airports intersect with each continent

var spatialFilter = ee.Filter.intersects({

    leftField :'.geo',

    rightField : '.geo',

    maxError:1

});



// define a save all join  //check -  a save all join returns a join that pairs each element from the first collection with a group of matching elements from the second collection.

var saveAllJoin = ee.Join.saveAll ({

    matchesKey:'airportspercontinent'

});

// Apply the join  


// find the number of airports at risk per continent  

// South America  


// 1m  

var  airports_1m_SouthAmerica_altitude = saveAllJoin.apply (airports_1m_risk_altitude, SouthAmerica, spatialFilter);

print('Airports affected in South America, 1m', airports_1m_SouthAmerica_altitude.size())

airports_1m_SouthAmerica_altitude = airports_1m_SouthAmerica_altitude.set('Continent', "South America")


//0.5 m  

var airports_05m_SouthAmerica_altitude = saveAllJoin.apply (airports_05m_risk_altitude, SouthAmerica, spatialFilter);

print('Airports affected in South America, 0.5m',airports_05m_SouthAmerica_altitude.size())
// Africa  

// 1m  

var airports_1m_Africa_altitude = saveAllJoin.apply (airports_1m_risk_altitude, Africa, spatialFilter);

print('Airports affected in Africa, 1m', airports_1m_Africa_altitude.size())

// 0.5m  

var airports_05m_Africa_altitude = saveAllJoin.apply (airports_05m_risk_altitude, Africa, spatialFilter);

print('Airports affected in Africa, 0.5m',airports_05m_Africa_altitude.size())

// Europe  

// 2m  


// 1m  

var airports_1m_Europe_altitude = saveAllJoin.apply (airports_1m_risk_altitude, Europe, spatialFilter);

print('Airports affected in Europe, 1m',airports_1m_Europe_altitude.size())

// 0.5 m  

var airports_05m_Europe_altitude = saveAllJoin.apply (airports_05m_risk_altitude, Europe, spatialFilter);

print('Airports affected in Europe, 0.5m',airports_05m_Europe_altitude.size())  

// Asia  


// 1m  

var airports_1m_Asia_altitude= saveAllJoin.apply (airports_1m_risk_altitude, Asia, spatialFilter);

print('Airports affected in Asia, 1m',airports_1m_Asia_altitude.size())  

// 0.5m  

var airports_05m_Asia_altitude= saveAllJoin.apply (airports_05m_risk_altitude, Asia, spatialFilter);

print('Airports affected in Asia, 0.5m',airports_05m_Asia_altitude.size())  



// Australia  



// 1m  

var airports_1m_Australia_altitude= saveAllJoin.apply (airports_1m_risk_altitude, Australia, spatialFilter);

print('Airports affected in Australia, 1m', airports_1m_Australia_altitude.size())  

// 0.5 m  

var airports_05m_Australia_altitude= saveAllJoin.apply (airports_05m_risk_altitude, Australia, spatialFilter);

print('Airports affected in Australia, 0.5m',airports_05m_Australia_altitude.size())   



// Oceania  



// 1m  

var airports_1m_Oceania_altitude= saveAllJoin.apply (airports_1m_risk_altitude, Oceania, spatialFilter);

print('Airports affected in Oceania, 1 m',airports_1m_Oceania_altitude.size())  

// 0.5m  

var airports_05m_Oceania_altitude= saveAllJoin.apply (airports_05m_risk_altitude, Oceania, spatialFilter);

print('Airports affected in Oceania, 0.5 m',airports_05m_Oceania_altitude.size())  



// North America  



// 1m  

var airports_1m_NorthAmerica_altitude= saveAllJoin.apply (airports_1m_risk_altitude, NorthAmerica, spatialFilter);

print('Airports affected in North America, 1 m',airports_1m_NorthAmerica_altitude.size())  

// 0.5m  

var airports_05m_NorthAmerica_altitude= saveAllJoin.apply (airports_05m_risk_altitude, NorthAmerica, spatialFilter);

print('Airports affected in North America, 0.5 m',airports_05m_NorthAmerica_altitude.size())



// Antarctica


// 1m  

var airports_1m_Antarctica_altitude =  saveAllJoin.apply (airports_1m_risk_altitude, Antarctica, spatialFilter);

print('Airports affected in Antarctica, 1 m' ,airports_1m_Antarctica_altitude.size())  

// 0.5 m  

var airports_05m_Antarctica_altitude =  saveAllJoin.apply (airports_05m_risk_altitude, Antarctica, spatialFilter);

print('Airports affected in Antarctica, 0.5m' ,airports_05m_Antarctica_altitude.size())  



```
