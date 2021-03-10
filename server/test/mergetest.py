import csv
path = "C:/Users/tor_9/Documents/csv/"
pictime = []
gpstime = []
with open(path +'pictest.csv', newline='') as csvpic:
    picreader = csv.reader(csvpic, delimiter=',', quotechar='|')
    for row in picreader:
        pictime.append(row[3])
#print(pictime)
with open(path +'gpstest.csv', newline='') as csvgps:
    gpsreader = csv.reader(csvgps, delimiter=',', quotechar='|')
    for row in gpsreader:
        gpstime.append(row[3])

for i in pictime:
    x = i.split(":")
    print (x)

