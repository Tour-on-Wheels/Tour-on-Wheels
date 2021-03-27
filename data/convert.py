# Python program to convert
# JSON file to CSV
  
  
import json
import csv
  
  
# Opening JSON file and loading the data
# into the variable data
with open('archive/trains.json') as json_file:
    data = json.load(json_file)

data = data['features']

dat = []
for element in data:
	del element['geometry']
	del element['type']
	dat.append(element['properties'])

file = open("trains.csv", 'w')

for k in dat[0]:
	file.write(k+",")

file.write("\n")
for k in dat:
	for j in k:
		file.write(str(k[j])+",")
	file.write("\n")

file.close()