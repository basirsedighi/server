import csv
from collections import defaultdict

path = "C:/Users/tor_9/Documents/csv/"
millispiclist = []
millisgpslist = []
longlist = []
latlist = []
# Python code t get difference of two lists
# Using set()

with open(path +'pictest.csv', newline='') as csvpic:
    picreader = csv.reader(csvpic, delimiter=',', quotechar='|')
    for row in picreader:
        millispiclist(row[3])


with open(path +'gpstest.csv', newline='') as csvgps:
    gpsreader = csv.reader(csvgps, delimiter=',', quotechar='|')
    for row in gpsreader:
        millisgpslist(row[3])
        longlist(row[4])
        latlist(row[5])





print(lastpictime)
#lastpictime = list(map(int, lastpictime))


for i in gpstime:
        x = i.split(":")  
        x.reverse()       
        x = list(map(int, x))  
        # print(len(Diff(lastpictime, x)))
        # print(Diff(lastpictime, x))
        # print(lastpictime)
        # print(x)
        #if len(temp) >= 3:
        #    print(lastpictime)
        #    print(x)

#del gpstime[:]
#    print(len(gpstime))


if len(gpstime) > len(pictime):
    del gpstime[len(pictime):]
    print(len(gpstime))
#while True:
    
    



    

 

