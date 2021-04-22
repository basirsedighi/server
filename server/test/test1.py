import os










absolute_path = os.path.dirname(os.path.abspath(__file__))
path = absolute_path+"/log/"+date+"/"+tempTrip



# Open image csv file and make a csv reader object 
with open(path +'/images.csv', newline='') as csvpic:
    picreader = csv.reader(csvpic, delimiter=',', quotechar='|')
    for row in picreader:
        #  make a list for each column in the csv file
        picnumberlist.append(row[0])                
        millisk1list.append(float(row[3]))
        
        
            
            
    
# Open gps csv file and make a csv reader object 
with open(path +'/gps.csv', newline='') as csvgps:
    gpsreader = csv.reader(csvgps, delimiter=',', quotechar='|')
    for row in gpsreader:
        #  make a list for each column in the csv file
        fixlist.append(row[1])
        speedlist.append(float(row[2]))
        millisgpslist.append(float(row[4])) 
        latlist.append(float(row[5]))
        longlist.append(float(row[6]))
        