#include "osrm/match_parameters.hpp"
#include "osrm/nearest_parameters.hpp"
#include "osrm/route_parameters.hpp"
#include "osrm/table_parameters.hpp"
#include "osrm/trip_parameters.hpp"
#include "osrm/coordinate.hpp"
#include "osrm/engine_config.hpp"
#include "osrm/json_container.hpp"

#include "osrm/osrm.hpp"
#include "osrm/status.hpp"

#include <exception>
#include <iostream>
#include <string>
#include <utility>

#include <chrono>
#include <cstdlib>

/* Usage: ./route_distances [map.osrm] [binary_data_1] [binary_data_1_count]  [binary_data_2] [binary_data_2_count]*/

typedef struct{
    double id; /* ID for subunit */
    double longitude;
    double latitude;
}unitData;

/* All-purpose function to write data to file */
static void overwrite_data_to_file(void *data, const char *fileName, size_t numBytes){
    FILE *f=fopen(fileName,"w");
    fwrite(data,1,numBytes,f);
    fclose(f);
}

/* All-purpose function to read data from file */
static void *get_file_data(const char *fileName){
    
    FILE *f = fopen(fileName,"r");
    size_t fsize;
    fseek(f,0L,SEEK_END);
    fsize = ftell(f);
    fseek(f,0L,SEEK_SET);
    void *data = malloc(fsize);
    fread(data,1,fsize,f);
    fclose(f);
    return data;
}


int main(int argc, const char *argv[])
{
    
    if (argc < 4)
    {
        std::cerr << "Usage: " << argv[0] << " [map.osrm] [list1_data] [list1_count] [list2_data] [list2_count]\n";
        return EXIT_FAILURE;
    }
    
    /* Read in the block data */
    unitData *sourceData = (unitData*)get_file_data(argv[2]);
    unitData *destinationData = (unitData*)get_file_data(argv[4]);

    int numberOfSourceUnits = atoi(argv[3]);
    int numberOfDestinationUnits = atoi(argv[5]);

    /* Initialize output holder */
    double *output = (double *)calloc(numberOfSourceUnits*numberOfDestinationUnits,sizeof(double));
    
    /* Adapted from OSRM sample code */
    using namespace osrm;
    
    osrm::engine::EngineConfig config;
    
    config.storage_config = {argv[1]};
    config.use_shared_memory = false;
    
    /* From OSRM sample code:
     // We support two routing speed up techniques:
     // - Contraction Hierarchies (CH): requires extract+contract pre-processing
     // - Multi-Level Dijkstra (MLD): requires extract+partition+customize pre-processing */
    
    // config.algorithm = EngineConfig::Algorithm::CH; 
    config.algorithm = osrm::engine::EngineConfig::Algorithm::MLD;
    
    const osrm::OSRM osrm{config};
    
    for(int source = 0; source < numberOfSourceUnits; source++){
        for(int dest = 0; dest < numberOfDestinationUnits; dest++){
            RouteParameters params;
            
            params.coordinates.push_back({util::FloatLongitude{sourceData[source].longitude}, util::FloatLatitude{sourceData[source].latitude}});
            params.coordinates.push_back({util::FloatLongitude{destinationData[dest].longitude}, util::FloatLatitude{destinationData[dest].latitude}});
            
            // Response is in JSON format
            engine::api::ResultT result = json::Object();
            
            // Execute routing request, this does the heavy lifting
            const auto status = osrm.Route(params, result);
            
            auto &json_result = result.get<json::Object>();
            if (status == Status::Ok)
            {
                auto &routes = json_result.values["routes"].get<json::Array>();
                
                // Let's just use the first route
                auto &route = routes.values.at(0).get<json::Object>();
                const auto distance = route.values["distance"].get<json::Number>().value;
                const auto duration = route.values["duration"].get<json::Number>().value;
                
                // Warn users if extract does not contain the default coordinates from above
                if (distance == 0 || duration == 0)
                {
                    // Uncomment to debug. Distance or duration will be zero if source = dest, or if you're outside the map.
                    /* std::cout << "Note: distance or duration is zero. "; */
                }

                std::cout << std::to_string((int)sourceData[source].id) << ",";
                std::cout << sourceData[source].longitude << ",";
                std::cout << sourceData[source].latitude  << ",";
                std::cout << std::to_string((int)destinationData[dest].id) << ",";
                std::cout << destinationData[dest].longitude << ",";
                std::cout << destinationData[dest].latitude << ",";
                
                std::cout << distance << ",";
                std::cout << duration << std::endl;
            }
            else if (status == Status::Error)
            {
                const auto code = json_result.values["code"].get<json::String>().value;
                const auto message = json_result.values["message"].get<json::String>().value;
                
            }
        }
        
    }
    
    return 0;
    
}

