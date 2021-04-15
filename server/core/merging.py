import csv
from collections import defaultdict
from bisect import bisect_left
import collections


#---start for variables and lists for merging csv---#

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

#   Modified coordinate list
modyfiedlatlist = []
modyfiedlonglist = []

closesttimelist = []
accelereation = []
#newgps = []
#newcoordinatelist = []
filledgpslist = []
overlappingpointlist = []
expandedlongitudelist = []
expandedlatitudelist = []

expandedmodifiedlongitudelist = []
expandedmodifiedlatitudelist = []
#   gps dictionary

#   index lists
calculatedindexlist = []
indexlist = []
closesttimelist = []
testclose = []
dublicateindexlist = []
dublicateindexvaluelist = []
newindexlist = []

timedifferencelist = []
#   values for iterating
cleanlength = 0
picrow = 0
gpsrow = 0
indexnumber = 0
k1row = 0
expand = 0


before = None
after = None

#---end for variables and lists for merging csv---#


#------------------------------------------#

#----start of functions for csv merging----#

#------------------------------------------#

#----end of functions for csv merging----#
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
    testlist = []
    for n in gpsmillislist:      
        closesttime, position = take_closest(picmillislist, n)
        if position != 0:
            position -= 1
        testlist.append(closesttime)
        indexlist.append(position) 
      
    return indexlist, closesttimelist

#  find and remove dublicates from index list
#   TO DO: velge duplicate som er nærmest pictime
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
def findandremovefromlistbyindex(valuelist, dublicateindexlist):
     
    for n in dublicateindexlist:               
        del valuelist[n]
        i = 1
        

    
    return valuelist
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

#   get time difference between picture taken and coordinate read
#   return time difference list
def gettimedifference(gpstimelist, pictimelist, indextimelist):
    i = 0
    
    timediff = [] 
    for n in indextimelist:
        diff = gpstimelist[i] - pictimelist[n]
        timediff.append(diff)
        i += 1
        
    
    return timediff



#   get constant acceleration for each read gps coordinate
#   return a list of acceleration
def getaccelerationlist(gpsspeedlist, gpstimelist):
    
    accelerationlist = []
    for n in range(len(gpsspeedlist)-1):           
        acceleration = (float(gpsspeedlist[n+1]) - float(gpsspeedlist[n])) / (float(gpstimelist[n+1]) - float(gpstimelist[n]))
        #print(n)
        #print(str(gpsspeedlist[n+1])+' - '+str(gpsspeedlist[n])+' / '+str(gpstimelist[n+1])+' - '+str(gpstimelist[n]))
        #print('acc: '+str(acceleration)+' diff: '+str(n))
        accelerationlist.append(acceleration)
    return accelerationlist
        


#   modifies coordinates based on time difference between picture taken and coordinate read,
#   speed, and constant acceleration
#   return list of modified coordinates
def modifycoordinatesbasedontimedifference(timedifflist, coordiantelist, speed, accelerationlist):
    print(len(timedifflist))
    print(len(coordiantelist))
    print(len(accelerationlist))
    shiftedcoord = []
    i = 0
    for n in range(len(coordiantelist)-1):
        time = float(timedifflist[n]/1000) # ms til sekunder
        #print(time)


        if timedifflist[n] < 0:
            shifted = coordiantelist[n] + speed[n] * abs(time) + (accelerationlist[n] * (time**2))/2
        elif timedifflist[n] > 0:
            shifted = coordiantelist[n] + speed[n] * abs(time) - (accelerationlist[n] * (time**2))/2
        print(shifted)
        print(coordiantelist[n])
        shiftedcoord.append(shifted)



#   Calculate coordinates between to points based on speed, time and acceleration 
#   x = x0 + v0*t + 0.5*at^2
#   return list with read and calculated coordinates
def gengpspoints(position1, position2, speed1, speed2, time1, time2, pointsbetween):

    acceleration = (speed1 - speed2) / (position1 - position2)  #   finds constant acceleration 
    timestep = (time1 - time2)/pointsbetween


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
    
#----------------------------------------#

#----end of functions for csv merging----#

#----------------------------------------#


#-------------------------------------------#

#---beginning of program for csv merging---# 

#-------------------------------------------#
def merge(path):
    try:
        # Open image csv file and make a csv reader object 
        with open(path +'/images.csv', newline='') as csvpic:
            picreader = csv.reader(csvpic, delimiter=',', quotechar='|')
            for row in picreader:
                #  make a list for each column in the csv file
                #picnumberlist.append(row[0])
                #kameranumberlist.append(row[2])
                #millispiclist.append(float(row[3]))
                
                if row[2] == '1.00' or row[2] == '1':
                    picnumberlist.append(row[0])
                    kameranumberlist.append(row[2])
                    millisk1list.append(float(row[3]))
                    
            
        # Open gps csv file and make a csv reader object 
        with open(path +'/gps.csv', newline='') as csvgps:
            gpsreader = csv.reader(csvgps, delimiter=',', quotechar='|')
            for row in gpsreader:
                #  make a list for each column in the csv file
                fixlist.append(row[1])
                speedlist.append(float(row[2]))
                latlist.append(float(row[4]))
                longlist.append(float(row[5]))
                millisgpslist.append(float(row[6])) 
    
    except Exception as e:
        print(e)


    print('millis: '+ str(len(millisk1list)))
    print('lat: '+ str(len(latlist)))
    #print(millisgpslist)
    indexlist, closesttimelist = calculateindexposition(millisgpslist, millisk1list)

    for n in range(100):
        print(closesttimelist[n])

    print('indexlist len: '+str(len(indexlist)))
    index, dub = findandremovedublicates(indexlist)
    print('index: '+str(len(index)))
    print('dub: '+str(dub))
    dub.reverse()   #   reversing the dublicate list, resulting removing from top of list.

    #   Removing dublicates from lists
    cleanlatlist = findandremovefromlistbyindex(latlist, dub)
    cleanlonglist = findandremovefromlistbyindex(longlist, dub)
    cleanmillisgpslist = findandremovefromlistbyindex(millisgpslist, dub)
    cleanspeedlist = findandremovefromlistbyindex(speedlist, dub)
    cleanfixlist = findandremovefromlistbyindex(fixlist, dub)

    timedifferencelist = gettimedifference(cleanmillisgpslist, millisk1list, index)

    accelereation = getaccelerationlist(cleanspeedlist, cleanmillisgpslist)

    #   Modifies cleaned latitude and longitude list
    modyfiedlatlist = modifycoordinatesbasedontimedifference(timedifferencelist, cleanlatlist,cleanspeedlist, accelereation)
    modyfiedlonglist = modifycoordinatesbasedontimedifference(timedifferencelist, cleanlonglist,cleanspeedlist, accelereation)

    #   Expand cleaned latitude and longitude list
    expandedlatitudelist = makenewcoordinatelist(cleanlatlist, index)
    expandedlongitudelist = makenewcoordinatelist(cleanlonglist, index)

    #   Expand modified latitude and longitude list
    expandedmodifiedlatitudelist = makenewcoordinatelist(cleanlatlist, index)
    expandedmodifiedlongitudelist = makenewcoordinatelist(cleanlonglist, index)

    print('exmodlong: '+ str(len(expandedmodifiedlongitudelist)))
    print('exmodlat: '+ str(len(expandedmodifiedlatitudelist)))
    print('exlat: '+ str(len(expandedlatitudelist)))
    print('exlong: '+ str(len(expandedlongitudelist)))


    with open(path+ 'merged.csv','w', newline='') as k1test:
        fieldnames = ['picmillis', 'gpsmillis','readlat', 'readlong', 'extendedlat','extendedlong', 'extendedmodifiedlat','extendedmodifiedlong']
        k1writer = csv.DictWriter(k1test, fieldnames=fieldnames) 
        
        for n in millisk1list: 
            #print('index: '+str(indexlist[indexnumber])+' ,k1row: '+str(k1row)+' gpsrow: '+str(gpsrow)+' lenght: '+str(len(cleanlatlist)))
            # print ('indexnumber'+ str(indexnumber))
            # print(len(index))
            # print('index[indexnumber]'+ str(index[indexnumber]))
            if not(indexnumber >= len(indexlist)):            
                if index[indexnumber] == k1row and gpsrow <= (len(cleanlatlist)-1): 
                    
                    k1writer.writerow({'gpsmillis': cleanmillisgpslist[gpsrow],'readlat':cleanlatlist[gpsrow],
                    'readlong':cleanlonglist[gpsrow], 'picmillis': n, 'extendedlat':expandedlatitudelist[expand],
                    'extendedlong':expandedlongitudelist[expand], 'extendedmodifiedlat':expandedmodifiedlatitudelist[expand]
                    , 'extendedmodifiedlong':expandedmodifiedlongitudelist[expand]})
                    gpsrow += 1            
                    indexnumber +=1
                    expand += 1
                elif k1row < len(expandedlatitudelist):
                    k1writer.writerow({'picmillis': n, 'extendedlat':expandedlatitudelist[expand],
                    'extendedlong':expandedlongitudelist[expand], 'extendedmodifiedlat':expandedmodifiedlatitudelist[expand]
                    , 'extendedmodifiedlong':expandedmodifiedlongitudelist[expand]})
                    expand += 1
                else:
                    k1writer.writerow({'picmillis': n})
                k1row += 1
            else:
                k1writer.writerow({'picmillis': n, 'extendedlat':expandedlatitudelist[expand-1],
                'extendedlong':expandedlongitudelist[expand-1], 'extendedmodifiedlat':expandedmodifiedlatitudelist[expand-1]
                , 'extendedmodifiedlong':expandedmodifiedlongitudelist[expand-1]})
                
#-------------------------------------------#

#---end of program for csv merging---# 

#-------------------------------------------#

  

        

