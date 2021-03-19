import csv
from collections import defaultdict
from bisect import bisect_left
import collections

path = "C:/Users/tor_9/Documents/csv/"
#image informastion lists:
millispiclist = []
kameranumberlist = []
picnumberlist = []
millisk1list = []

#gps informastion lists:
millisgpslist = []
longlist = []
latlist = []
fixlist = []
speedlist = []

picrow = 0
gpsrow = 0
indexnumber = 0
skipfirst = False
indexlist = []
closesttimelist = []
testclose = []

newgps = []
#test
lst = [3.64, 5.2, 8, 8.5, 9.35, 9.42]
k= 9.36


totaldic = {"number":[],"kamera":[], "picmillis":[], "gpsmillis":[],"fix":[],"speed":[],"long":[],"lat":[]}
gpsdict = {"gpsmillis":[],"fix":[],"speed":[],"long":[],"lat":[]}
# Python code t get difference of two lists
# Using set()

def generatePointsBetween(p1, p2, nb_points):
    """"Return a list of nb_points equally spaced points
    between p1 and p2"""
    # If we have 8 intermediate points, we have 8+1=9 spaces
    # between p1 and p2
    
    step = abs(((p2 - p1) / (nb_points)))
    print (step)
    if p1<p2:
        for i in range(1,nb_points):
            newgpscoordinate = p1+(step*i)
            newgps.append(newgpscoordinate)
    else:
        for i in range(1,nb_points):
            newgpscoordinate = p1-(step*i)
            newgps.append(newgpscoordinate)
    
    return newgps



def closest(myList, value): 
      
    return myList[min(range(len(myList)), key = lambda i: abs(int(myList[i])-int(value)))] 

def take_closest(myList, myNumber):
    """
    Assumes myList is sorted. Returns closest value to myNumber.

    If two numbers are equally close, return the smallest number.
    """
    pos = bisect_left(myList, myNumber)
    
    if pos == 0:
        return myList[0], pos       
    if pos == len(myList):
        return myList[-1], pos        
    before = myList[pos - 1]
    after = myList[pos]
    if abs(int(after) - int(myNumber)) < abs(int(myNumber) - int(before)):      
        return after, pos
    else:        
        return before, pos

#  compare time from pic list and gps list
def findindextoclosestgpsmatch(gpsmillislist, picmillislist):
    for n in gpsmillislist:      
        closesttime, position = take_closest(picmillislist, n)
        if position != 0:
            position -= 1
        indexlist.append(position)    
    return indexlist

#  make new gps list with read gps coordinates and calculated gps coordinates 
#  returns a list with read and calculated coordinates 
def makenewgpscoordinatelist(gpscoordinateslist,indexlist):
    #  making a list for easier generating of gps coordinates 
    for n in range(len(indexlist)-1):    
        points = indexlist[n+1] - indexlist[n]         
        if points != 0:
            generatedcoordinatelist = generatePointsBetween(gpscoordinateslist[n], gpscoordinateslist[n+1])
            newcoordinatelist.append(gpscoordinateslist[n])
            newcoordinatelist.extend(generatedcoordinatelist)
            newcoordinatelist.append(gpscoordinateslist[n+1])
    return newcoordinatelist
    


# Open image csv file and make a csv reader object 
with open(path +'pictest.csv', newline='') as csvpic:
    picreader = csv.reader(csvpic, delimiter=',', quotechar='|')
    for row in picreader:
        #  make a list for each column in the csv file
        picnumberlist.append(row[0])
        kameranumberlist.append(row[2])
        millispiclist.append(int(row[3]))
        if row[2] == '1':
            millisk1list.append(int(row[3]))
        
print(millisk1list[0])
# Open gps csv file and make a csv reader object 
with open(path +'gpstest.csv', newline='') as csvgps:
    gpsreader = csv.reader(csvgps, delimiter=',', quotechar='|')
    for row in gpsreader:
        #  make a list for each column in the csv file
        fixlist.append(row[1])
        speedlist.append(row[2])
        longlist.append(float(row[4]))
        latlist.append(float(row[5]))
        millisgpslist.append(int(row[6])) 


indexlist = findindextoclosestgpsmatch(millisgpslist, millisk1list)


# for n in millisgpslist:      
#     closesttime, position = take_closest(millisk1list, n)
#     diff = closesttime-n
#     if position != 0:
#         position -= 1
    #print('diff: '+str(diff)+' ,picindex: '+ str(position)+' ,gpsindex: '+ str(millisgpslist.index(n)) )
    #indexlist.append(position)
    #print(closesttime-n)
#print(indexlist)
counter = 0


#  making a list for easier generating of gps coordinates 
# for n in range(len(indexlist)-1):    
#     new = str(indexlist[n])+'-'+str(indexlist[n+1])
#     indexlistcombined.append(new)




#print(len(indexlist))
#print(indexlist)
indextest = 0
#print(len(indexlist))
row= 0
k1row = 0
with open(path+ 'k1time.csv','w', newline='') as k1test:
    fieldnames = ['picmillis', 'gpsmillis']
    k1writer = csv.DictWriter(k1test, fieldnames=fieldnames) 
    for n in millisk1list:   
        if indexlist[indexnumber] == k1row: 
            k1writer.writerow({'picmillis': n, 'gpsmillis': millisgpslist[row]})
            row += 1
            indexnumber +=1
            k1row += 1
        else:
            k1writer.writerow({'picmillis': n, 'gpsmillis': ''})
            k1row += 1

with open(path+ 'test.csv','w', newline='') as csvtest:
     
    fieldnames = ['picnumber','kamera', 'picmillis', 'gpsmillis','testmillis','diff','long', 'lat','fix','speed']
    testwriter = csv.DictWriter(csvtest, fieldnames=fieldnames)    
    for n in millispiclist:  
        
        if indexlist[indexnumber] == picrow: 
            #print(str(indexlist[indexnumber])+'--'+str(picrow))                      
            before = indexlist[indexnumber]
            indexnumber += 1    
            after = indexlist[indexnumber]
            millis = millisgpslist[gpsrow]
            
            
            if before == after:
                indexnumber +=1                            
                test = millisgpslist[gpsrow]
                gpsrow += 1
                diff = abs(int(millis) - int(test))
            else:
                test = ''
                diff = ''
            
            testwriter.writerow({'picnumber':picnumberlist[picrow],'kamera':kameranumberlist[picrow] ,'picmillis':n,
             'gpsmillis':millis,'testmillis': test,'diff':diff , 'long': longlist[gpsrow], 'lat': latlist[gpsrow],
              'fix':fixlist[gpsrow], 'speed': speedlist[gpsrow]})
            gpsrow += 1
        else:
            testwriter.writerow({'picnumber':picnumberlist[picrow],'kamera':kameranumberlist[picrow] ,'picmillis': n, 'gpsmillis': '', 'long': '', 'lat': ''})        
        #print('pic: '+str(picrow))
        picrow +=1
        


#for n in millisgpslist:  
#     x = min(millispiclist, key=lambda x:abs(x-int(n)))  
#     print(x)








    
    



    

 

