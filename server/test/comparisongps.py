import csv
picnumber = []
mergelat = []
mergelong = []

excactlat = []
excactlong = []


with open(path +'merge.csv', newline='') as csvpic:
    picreader = csv.reader(csvpic, delimiter=',', quotechar='|')
    for row in picreader:   
        picnumber.append(row[])  
        mergelat.append(row[])
        mergelong.append(row[])          
        



with open(path +'exactcord.csv', newline='') as csvpic:
    picreader = csv.reader(csvpic, delimiter=',', quotechar='|')
    for row in picreader:
        
        