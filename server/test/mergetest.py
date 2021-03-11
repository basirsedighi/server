import csv
path = "C:/Users/tor_9/Documents/csv/"
pictime = []
gpstime = []
# Python code t get difference of two lists
# Using set()
def Diff(li1, li2):
    return (list(list(set(li1)-set(li2)) + list(set(li2)-set(li1))))

with open(path +'pictest.csv', newline='') as csvpic:
    picreader = csv.reader(csvpic, delimiter=',', quotechar='|')
    for row in picreader:
        pictime.append(row[3])
#print(pictime)
with open(path +'gpstest.csv', newline='') as csvgps:
    gpsreader = csv.reader(csvgps, delimiter=',', quotechar='|')
    for row in gpsreader:
        gpstime.append(row[3])

lastpictime = pictime[-1].split(':')
lastpictime = list(map(int, lastpictime))


for i in gpstime:
        x = i.split(":")         
        x = list(map(int, x))  
        print(len(Diff(lastpictime, x)))
        print(Diff(lastpictime, x))
        print(lastpictime)
        print(x)
        #if len(temp) >= 3:
        #    print(lastpictime)
        #    print(x)

#del gpstime[:]
#    print(len(gpstime))


if len(gpstime) > len(pictime):
    del gpstime[len(pictime):]
    print(len(gpstime))
#while True:
    
    



    

 

