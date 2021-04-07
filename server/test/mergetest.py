import csv
from collections import defaultdict
from bisect import bisect_left
import collections

path = "C:/Users/tor_9/Documents/csv/"

#----lists----#

#   image informastion lists:
millispiclist = []
kameranumberlist = []
picnumberlist = []
millisk1list = []

#   gps informastion lists
millisgpslist = []
longlist = []
latlist = []
fixlist = []
speedlist = []

#cleande
cleanmillisgpslist = []
cleanlonglist = []
cleanlatlist = []
cleanfixlist = []
cleanspeedlist = []
#newgps = []
#newcoordinatelist = []
filledgpslist = []
overlappingpointlist = []
expandedlongitudelist = []
expandedlatitudelist = []
#   gps dictionary

#   index lists
calculatedindexlist = []
indexlist = []
closesttimelist = []
testclose = []
dublicateindexlist = []
dublicateindexvaluelist = []
newindexlist = []

#   values for iterating
cleanlength = 0
picrow = 0
gpsrow = 0
indexnumber = 0
k1row = 0
expand = 0


before = None
after = None
#----Functions----#





#  finds the closest time between image list and gps list
#  return list of index
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
#   return 
def calculateindexposition(gpsmillislist, picmillislist):
    for n in gpsmillislist:      
        closesttime, position = take_closest(picmillislist, n)
        if position != 0:
            position -= 1
        indexlist.append(position)    
    return indexlist

#  find and remove dublicates from index list
#   return a list of positions were dublicates were removed
def findandremovedublicates(wholeindexlist):
    for n in range(len(wholeindexlist)-1):    
        points = wholeindexlist[n+1] - wholeindexlist[n]         
        if points == 0:            
            dublicateindexvalue = wholeindexlist[n]
            dublicateindexlist.append(n)
            dublicateindexvaluelist.append(dublicateindexvalue)

    for n in dublicateindexvaluelist:
        wholeindexlist.remove(n)

    return wholeindexlist, dublicateindexlist

#   finds and remove overlapping values from the gps value list
#   return list of coordinates without points overalapping
def findandremovefromlistbyindex(gpslist, dublicateindexlist):
    overlappingpointlist.clear() 
      
    for n in dublicateindexlist: 
             
        overlappingpointlist.append(gpslist[n])
    
    for n in overlappingpointlist:
        gpslist.remove(n)
    
    return gpslist
#  make new gps list with read gps coordinates and calculated gps coordinates 
#  returns a list with read and calculated coordinates 

#   generate gps coordinates between two points
#   return list of the generated coordiantes sorted with the read coordinates
def generatePointsBetween(position1, position2, pointsbetween):
    newgps = []
    #print(position1)
    step = abs(((position2 - position1) / (pointsbetween)))    
    if position1<position2:
        for i in range(1,pointsbetween):
            newgpscoordinate = position1+(step*i)
            newgps.append(newgpscoordinate)
    else:
        for i in range(1,pointsbetween):
            newgpscoordinate = position1-(step*i)
            newgps.append(newgpscoordinate)
    
    return newgps

def makenewcoordinatelist(gpscoordinateslist,calculatedindexlist):
    newcoordinatelist = []
    #  making a list for easier generating of gps coordinates
    
    for n in range(len(calculatedindexlist)-1):
        points = calculatedindexlist[n+1] - calculatedindexlist[n]                 
        generatedcoordinatelist = generatePointsBetween(gpscoordinateslist[n], gpscoordinateslist[n+1], points)
        
        newcoordinatelist.append(gpscoordinateslist[n])
        newcoordinatelist.extend(generatedcoordinatelist)
        if n == len(calculatedindexlist)-2:
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
     
# Open gps csv file and make a csv reader object 
with open(path +'gpstest.csv', newline='') as csvgps:
    gpsreader = csv.reader(csvgps, delimiter=',', quotechar='|')
    for row in gpsreader:
        #  make a list for each column in the csv file
        fixlist.append(row[1])
        speedlist.append(row[2])
        latlist.append(float(row[4]))
        longlist.append(float(row[5]))
        millisgpslist.append(int(row[6])) 



indexlist = calculateindexposition(millisgpslist, millisk1list)


index, dub = findandremovedublicates(indexlist)

#  Test
#print(len(index))
#print(len(latlist))
#print(len(longlist))
#print('latlist: '+str(len(latlist)))
cleanlatlist = findandremovefromlistbyindex(latlist, dub)
cleanlonglist = findandremovefromlistbyindex(longlist, dub)
cleanmillisgpslist = findandremovefromlistbyindex(millisgpslist, dub)
cleanspeedlist = findandremovefromlistbyindex(speedlist, dub)
cleanfixlist = findandremovefromlistbyindex(fixlist, dub)

#print('clean: '+str(len(cleanlatlist)))
#print('latlist: '+str(len(latlist)))
#print(cleanlatlist)
#print('#################latitude################')
expandedlatitudelist = makenewcoordinatelist(cleanlatlist, index)

# print('#################longitude################')
expandedlongitudelist = makenewcoordinatelist(cleanlonglist, index)

# print('explat: '+str(len(expandedlatitudelist)))

# print('explong: '+str(len(expandedlongitudelist)))
#print(expandedlongitudelist)
#print(len(millisk1list))


# print('test:' '\n')
# print('k1: '+str(len(millisk1list)))


with open(path+ 'k1time.csv','w', newline='') as k1test:
    fieldnames = ['picmillis', 'gpsmillis','readlat', 'readlong', 'extendedlat','extendedlong']
    k1writer = csv.DictWriter(k1test, fieldnames=fieldnames) 
    print(len(cleanlatlist))
    print(len(expandedlongitudelist))
    for n in millisk1list: 
        #print('index: '+str(indexlist[indexnumber])+' ,k1row: '+str(k1row)+' gpsrow: '+str(gpsrow)+' lenght: '+str(len(cleanlatlist)))
        # print ('indexnumber'+ str(indexnumber))
        # print(len(index))
        # print('index[indexnumber]'+ str(index[indexnumber]))
        if not(indexnumber >= len(indexlist)):            
            if index[indexnumber] == k1row and gpsrow <= (len(cleanlatlist)-1): 
                #print(gpsrow)
                k1writer.writerow({'gpsmillis': cleanmillisgpslist[gpsrow],'readlat':cleanlatlist[gpsrow],
                 'readlong':cleanlonglist[gpsrow], 'picmillis': n, 'extendedlat':expandedlatitudelist[expand],
                'extendedlong':expandedlongitudelist[expand]})
                gpsrow += 1            
                indexnumber +=1
                expand += 1
            elif k1row < len(expandedlatitudelist):
                k1writer.writerow({'picmillis': n, 'extendedlat':expandedlatitudelist[expand],
                'extendedlong':expandedlongitudelist[expand]})
                expand += 1
            else:
                k1writer.writerow({'picmillis': n})
            k1row += 1
        else:
            k1writer.writerow({'picmillis': n, 'extendedlat':expandedlatitudelist[expand-1],
            'extendedlong':expandedlongitudelist[expand-1]})
            


  

        

# with open(path+ 'test.csv','w', newline='') as csvtest:
     
#     fieldnames = ['picnumber','kamera', 'picmillis', 'gpsmillis','testmillis','diff','long', 'lat','fix','speed']
#     testwriter = csv.DictWriter(csvtest, fieldnames=fieldnames)    
#     for n in millispiclist:  
            
            
#             if before == after:
#                 indexnumber +=1                            
#                 test = millisgpslist[gpsrow]
#                 gpsrow += 1
#                 diff = abs(int(millis) - int(test))
#             else:
#                 test = ''
#                 diff = ''
            
#             testwriter.writerow({'picnumber':picnumberlist[picrow],'kamera':kameranumberlist[picrow] ,'picmillis':n,
#              'gpsmillis':millis,'testmillis': test,'diff':diff , 'long': longlist[gpsrow], 'lat': latlist[gpsrow],
#               'fix':fixlist[gpsrow], 'speed': speedlist[gpsrow]})
#             gpsrow += 1
#         else:
#             testwriter.writerow({'picnumber':picnumberlist[picrow],'kamera':kameranumberlist[picrow] ,'picmillis': n, 'gpsmillis': '', 'long': '', 'lat': ''})        
#         #print('pic: '+str(picrow))
#         picrow +=1
        


#for n in millisgpslist:  
#     x = min(millispiclist, key=lambda x:abs(x-int(n)))  
#     print(x)


# for n in millisgpslist:      
#     closesttime, position = take_closest(millisk1list, n)
#     diff = closesttime-n
#     if position != 0:
#         position -= 1
    #print('diff: '+str(diff)+' ,picindex: '+ str(position)+' ,gpsindex: '+ str(millisgpslist.index(n)) )
    #indexlist.append(position)
    #print(closesttime-n)
#print(indexlist)





    
    



    

 

