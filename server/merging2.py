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
    qualityList=[]
    picIndex =[]


    timer = Timer("hallo")



    try:
        # Open image csv file and make a csv reader object 
        with open(path +'/images.csv', newline='') as csvpic:
            picreader = csv.reader(csvpic, delimiter=',', quotechar='|')
            next(picreader)
            for row in picreader:
                #  make a list for each column in the csv file               
                picmilli.append(float(row[4]))
                picIndex.append(int(row[0]))
                
                
                    
                    
        
        # Open gps csv file and make a csv reader object 
        with open(path +'/gps.csv', newline='') as csvgps:
            gpsreader = csv.reader(csvgps, delimiter=',', quotechar='|')
            next(gpsreader)
            i =0
            for row in gpsreader:
                #  make a list for each column in the csv file
                try:
                    gpsmilli.append(float(row[4]))
                    latList.append(row[5])
                    longList.append(row[6])
                    speedList.append(row[2])
                    qualityList.append((row[1]))
                except Exception:
                    pass
                   

                i+=1

            

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


        
        print("writing")
        # Open gps csv file and make a csv reader object 
        with open(path +'/merged.csv','w', newline='') as csvgps:

            fieldnames = ['index','Image milli', 'gps milli',"lat","long","speed","Quality"]
            writer = csv.DictWriter(csvgps, fieldnames=fieldnames)
            writer.writeheader()
            for i in range(len(picmilli)):
                try:
                    writer.writerow({'index':picIndex[i],"Image milli":picmilli[i],"gps milli":gpsmilli[indexlist[i]],"lat":latList[indexlist[i]],"long":longList[indexlist[i]],"speed":speedList[indexlist[i]],"Quality":qualityList[indexlist[i]]})
                except IndexError:
                    writer.writerow({'index':picIndex[i],"Image milli":picmilli[i],"gps milli":"","lat":"","long":"","speed":"","Quality":""})
            

    except Exception as e:
        print(e)

        status = "error"
    

    finally:
        return status





# absolute_path = os.path.dirname(os.path.abspath(__file__))
# absolute_path = fixPath(absolute_path)
    
# path = absolute_path+"/log/"+"2021-04-20/bachelorvol2.2.3utenpuse"

# merge2(path)