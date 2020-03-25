# What this is

This code uses Python3 and C++ to map routes between universities and hospitals. 


# Pre-processing the data (Python wrapper)

The file `preprocess_data.py` loads hospital and university geolocation data from the U.S. Department of Homeland Security and saves two binary files containing numeric IDs and their latitudes and longitudes, to be provided as input to a C++ executable (compiled below). It also saves two dictionaries mapping numeric IDs to the hospital/university names.

To run it, execute:

`python3 preprocess_data.py [state abbreviation here]`; e.g.: 

`python3 preprocess_data.py NY`

If no state is provided, MA is used by default.

At the end of execution, `preprocess_data.py` prints a command that can be used once the C++ executable is compiled, run from the main folder.


# OSRM Routing 
## Installing OSRM

These instructions are for Mac, with [Homebrew](https://brew.sh) installed, using Terminal. 

1. Install dependencies with Homebrew:

`brew install boost git cmake libzip libstxxl libxml2 lua tbb ccache`
`brew install GDAL`

2. Clone the [osrm-backend repo](https://github.com/Project-OSRM/osrm-backend): 

`git clone https://github.com/Project-OSRM/osrm-backend.git`

3. Build the backend by running the following commands: 

`cd osrm-backend`
`mkdir build`
`cd build`
`cmake ../ -DENABLE_MASON=0`
`make` 

## Getting the data

The list of U.S. mapping files is available [here](http://download.geofabrik.de/north-america/us.html). This README assumes these files are downloaded and extracted to the `/state-osm` folder. 

To download the state you want, use `wget`, e.g.:

`wget http://download.geofabrik.de/north-america/us/new-york-latest.osm.pbf`

There are two ways of processing the data, depending on the type of routing you want to do. The C++ file associated with this project currently uses Multi-Level Dijkstra (MLD). You prepare the osm.pbf file for MLD routing by calling `osrm-extract`, then `osrm-partition`, then `osrm-customize`.

Calling `osrm-extract` requires a profile; e.g. car. Relevant profiles are located in the `/profiles` directory inside `osrm-backend`. You can provide the profile with the `-p` flag. Below is an example of the extraction, partition, and customize steps:  

`osrm-extract new-york-latest.osm.pbf -p ../osrm-backend/profiles/car.lua`
`osrm-partition new-york-latest.osrm`
`osrm-customize new-york-latest.osrm`


The alternative method of routing is Contraction Hierarchies. For this, preprocesssing involves calling `osrm-extract` and `osrm-contract`; e.g. 

`osrm-extract new-york-latest.osm.pbf -p ../osrm-backend/profiles/car.lua`
`osrm-contract new-york-latest.osrm`

This is not currently used in the C++ code, though you can implement it by uncommenting
`config.algorithm = EngineConfig::Algorithm::CH;`

## Running C++ routing code

The C++ code to interface with the `.osrm` files extracted in the previous step is in the `/route-distances folder`. To compile it, navigate to the folder and run the following commands: 

`mkdir build`
`cd build`
`cmake ..`
`make`

This generates the `route-distances` executable in the build folder. The arguments to the executable are

`./route-distances [map file.osrm] [source binary data file] [number of sources] [destination binary data file] [number of destinations]`

A line of code to call the executable is produced by `preprocess_data.py`. 

The executable prints pairwise driving distances with the following format: 

`Source Index, Source Longitude, Source Latitude, Destination Index, Destination Longitude, Desination Latitude, Driving distance (meters), Driving time (seconds)`

You can pipe it to a csv file by appending ` > output_file.csv`; e.g. 

`./route-distances/build/route-distances state-osm/new-york-latest.osrm output/university_geo_locations 277 output/hospital_geo_locations 464 > output/NY_pairwise_distances.csv`


# Post-processing (Python executable)

The C++ assigns numeric IDs to the geolocations it works with. To replace the numeric IDs with their string names, run `postprocess_data.py`. As with `preprocess_data.py`, the script takes one argument, the state abbreviation, and uses Massachusetts as default. The output again prints to the screen, but you can pipe it to a file as below: 

`python3 postprocess_data.py NY > output/NY_pairwise_distances_with_names.csv`

# Data

- [College  and University Shapefiles](https://hifld-geoplatform.opendata.arcgis.com/datasets/colleges-and-universities/data)

- [Hospital Shapefiles](https://hifld-geoplatform.opendata.arcgis.com/datasets/6ac5e325468c4cb9b905f1728d6fbf0f_0)

- [US OSRM files](http://download.geofabrik.de/north-america/us.html)
