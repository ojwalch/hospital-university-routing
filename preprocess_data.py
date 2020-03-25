import shapefile
import sys

import pickle
import csv
import pandas as pd
from array import array

def state_abbreviation_to_map_name(state):
    state_dictionary = {'AK': 'Alaska','AL': 'Alabama','AR': 'Arkansas','AS': 'American Samoa','AZ': 'Arizona','CA': 'California','CO': 'Colorado','CT': 'Connecticut','DC': 'District of Columbia','DE': 'Delaware','FL': 'Florida','GA': 'Georgia','GU': 'Guam','HI': 'Hawaii','IA': 'Iowa','ID': 'Idaho','IL': 'Illinois','IN': 'Indiana','KS': 'Kansas','KY': 'Kentucky','LA': 'Louisiana','MA': 'Massachusetts','MD': 'Maryland','ME': 'Maine','MI': 'Michigan','MN': 'Minnesota','MO': 'Missouri','MP': 'Northern Mariana Islands','MS': 'Mississippi','MT': 'Montana','NA': 'National','NC': 'North Carolina','ND': 'North Dakota','NE': 'Nebraska','NH': 'New Hampshire','NJ': 'New Jersey','NM': 'New Mexico','NV': 'Nevada','NY': 'New York','OH': 'Ohio','OK': 'Oklahoma','OR': 'Oregon','PA': 'Pennsylvania','PR': 'Puerto Rico','RI': 'Rhode Island','SC': 'South Carolina','SD': 'South Dakota','TN': 'Tennessee','TX': 'Texas','UT': 'Utah','VA': 'Virginia','VI': 'Virgin Islands','VT': 'Vermont','WA': 'Washington','WI': 'Wisconsin','WV': 'West Virginia','WY': 'Wyoming'}
    return (state_dictionary[state].lower()).replace(' ','-')


def read_data(filename, state):
    data = []
    shapefile_data = shapefile.Reader(filename)

    for entry in shapefile_data.shapeRecords():
        name = entry.record[2]
        name = name.replace(',', '')  # Remove commas in names to avoid messing with the final CSV
        entry_state = entry.record[5]
        latitude = entry.record[15]
        longitude = entry.record[16]
        if entry_state == state:
            data.append({'name': name, 'latitude': latitude, 'longitude': longitude})

    df = pd.DataFrame(data)
    # print(df)

    return df


def generate_dictionary_and_binary(df, filename):
    unit_data = []
    id_to_name = {}

    for index, row in df.iterrows():
        id_to_name[index] = row['name']
        unit_data.append(index)
        unit_data.append(row['longitude'])
        unit_data.append(row['latitude'])

    output_file = open(filename, 'wb')
    float_array = array('d', unit_data)
    float_array.tofile(output_file)
    output_file.close()
    return id_to_name


state = 'MA'

if len(sys.argv) > 1:
    state = sys.argv[1]

hospital_input_file = 'data/Hospitals/Hospitals.shp'
university_input_file = 'data/Colleges_and_Universities/Colleges_and_Universities.shp'
output_file_name = 'output/' + state + '_pairwise_distances'

df_hospitals = read_data(hospital_input_file, state)
df_schools = read_data(university_input_file, state)

hospital_filename = 'output/' + state + '_hospital_geo_locations'
university_filename = 'output/' + state + '_university_geo_locations'

hospital_dictionary = generate_dictionary_and_binary(df_hospitals,hospital_filename)
school_dictionary = generate_dictionary_and_binary(df_schools,university_filename)

hospital_count = df_hospitals.shape[0]
school_count = df_schools.shape[0]

print('\nTo run the pairwise routing: \n')

print('./route-distances/build/route-distances state-osm/' + state_abbreviation_to_map_name(state) + '-latest.osrm ' + university_filename + ' ' + str(school_count) + ' ' + hospital_filename + ' ' + str(hospital_count) + ' > ' + output_file_name + '.csv')

print('\nTo map the integer IDs to string names: \n')

print('python3 postprocess_data.py ' + state + ' > ' + output_file_name + '_with_names.csv\n\n')

hospital_dictionary_file = open(hospital_filename + '.pkl','wb')
pickle.dump(hospital_dictionary, hospital_dictionary_file)
hospital_dictionary_file.close()

school_dictionary_file = open(university_filename + '.pkl','wb')
pickle.dump(school_dictionary, school_dictionary_file)
school_dictionary_file.close()

