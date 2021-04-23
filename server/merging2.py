import os
from core.helpers.helper_server import *
import csv
from core.timer import Timer








def merge2(path):



    status = "good"

    picmilli =[]
    gpsmilli=[]
    latList = []
    longList =[]
    speedList=[]


    timer = Timer("hallo")



    try:
        # Open image csv file and make a csv reader object 
        with open(path +'/images.csv', newline='') as csvpic:
            picreader = csv.reader(csvpic, delimiter=',', quotechar='|')
            for row in picreader:
                #  make a list for each column in the csv file               
                picmilli.append(float(row[3]))
                
                
                    
                    
        
        # Open gps csv file and make a csv reader object 
        with open(path +'/gps.csv', newline='') as csvgps:
            gpsreader = csv.reader(csvgps, delimiter=',', quotechar='|')
            for row in gpsreader:
                #  make a list for each column in the csv file
                gpsmilli.append(float(row[4]))
                latList.append(float(row[5]))
                longList.append(float(row[6]))
                speedList.append(float(row[2]))

            

        test = gpsmilli.copy()

        indexlist=[]
        moveindex =0
        timer.start()

       
        for pic in picmilli:

            diffList=[]
            minvalue =[]
            
            for gps in test:
                diffList.append(abs(gps-pic))
                
                
           
            #test.pop(0)
            min_value = min(diffList)
            minvalue.append(min_value)
            index = diffList.index(min_value)
            # index = moveindex+index
            indexlist.append(index)
            moveindex +=1


        timer.stop()


        print(indexlist)
        
        # Open gps csv file and make a csv reader object 
        with open(path +'/newlist.csv','w', newline='') as csvgps:

            fieldnames = ['index','picmilli', 'gpsmilli',"lat","long","speed"]
            writer = csv.DictWriter(csvgps, fieldnames=fieldnames)
            for i in range(len(picmilli)):
                try:
                    writer.writerow({'index':i,"picmilli":picmilli[i],"gpsmilli":gpsmilli[indexlist[i]],"lat":latList[indexlist[i]],"long":longList[indexlist[i]],"speed":speedList[indexlist[i]]})
                except IndexError:
                    writer.writerow({'index':i,"picmilli":picmilli[i],"gpsmilli":"","lat":"","long":"","speed":""})
            

    except Exception as e:
        print(e)

        status = "error"
    

    finally:
        return status







# date = "2021-04-23"
# tempTrip= "oljhuhu"
# absolute_path = os.path.dirname(os.path.abspath(__file__))
# fixPath(absolute_path)
# path = absolute_path+"/log/"+date+"/"+tempTrip

# result = merge2(path)