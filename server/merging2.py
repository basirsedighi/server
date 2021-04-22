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

                

        test = gpsmilli.copy()

        indexlist=[]
        moveindex =0
        timer.start()

        print(len(gpsmilli))
        print(len(picmilli))
        for pic in picmilli:

            diffList=[]
            minvalue =[]
            
            for gps in test:
                diffList.append(abs(gps-pic))
                
                
            
            test.pop(0)
            min_value = min(diffList)
            minvalue.append(min_value)
            index = diffList.index(min_value)
            index = moveindex+index
            indexlist.append(index)
            moveindex +=1


        timer.stop()




        # Open gps csv file and make a csv reader object 
        with open(path +'/newlist.csv','w', newline='') as csvgps:

            fieldnames = ['picmilli', 'gpsmilli',"lat","long"]
            writer = csv.DictWriter(csvgps, fieldnames=fieldnames)
            for i in range(len(picmilli)):
                writer.writerow({"picmilli":picmilli[i],"gpsmilli":gpsmilli[indexlist[i]],"lat":latList[indexlist[i]],"long":longList[indexlist[i]]})
            

    except Exception as e:

        status = "error"
    

    finally:
        return status





