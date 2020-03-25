import csv
import pickle
import sys

state = 'MA'

if len(sys.argv) > 1:
    state = sys.argv[1]

hospital_filename = 'output/' + state + '_hospital_geo_locations'
university_filename = 'output/' + state + '_university_geo_locations'
output_file_name = 'output/' + state + '_pairwise_distances.csv'

# Load dictionaries
hospital_dictionary_file = open(hospital_filename + '.pkl','rb')
hospital_dictionary = pickle.load(hospital_dictionary_file)
hospital_dictionary_file.close()

school_dictionary_file = open(university_filename + '.pkl','rb')
school_dictionary = pickle.load(school_dictionary_file)
school_dictionary_file.close()

with open(output_file_name) as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    print("Source, SourceLong, SourceLat, Destination, DestLong, DestLat, Driving Distance (m), Driving Time (s)")
    for row in reader:
        university_key = int(row[0])
        hospital_key = int(row[3])
        print(school_dictionary[university_key] + "," + row[1] + "," + row[2] + "," + hospital_dictionary[hospital_key] + "," + row[4] + "," + row[5] + "," + row[6] + "," + row[7])
        

