import csv
from collections import defaultdict
from bisect import bisect_left
import collections
import os


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
test = []
dublicateindexlist = []
dublicateindexvaluelist = []
newindexlist = []

timedifferencelist = []



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
    #fix so pic log can star before gps log
        

    indexlist.clear()
    testlist = [0]
    #before = gpsmillislist[0] 
    for n in picmillislist:      
        closesttime, position = take_closest(gpsmillislist, n)
        #if position != 0:
        #    position -= 1
        diff = n - closesttime
        before = position
        
        
        #print('diff= '+str(closesttime)+' - '+str(n))
        #print('index: '+str(gpsmillislist.index(n)) +' pos:'+str(position)+' indexgps: '+str(picmillislist.index(closesttime))+' diff: '+ str(diff))
        closesttimelist.append(diff)
        #print(gpsmillislist.index(closesttime))
        indexlist.append(gpsmillislist.index(closesttime)) 
        after = position
        
        #if position < 100:
        #   print('pos:'+str(position)+' timediff: '+str(diff))
        
    #print(indexlist)
    #print(closesttimelist)
    return indexlist, closesttimelist 





#  find and remove dublicates from index list
#   TO DO: velge duplicate som er nærmest pictime
#   return a list of positions were dublicates were removed
def findandremovedublicates(wholeindexlist, closesttimelists):
    
    for n in range(len(wholeindexlist)-1):    
        points = wholeindexlist[n+1] - wholeindexlist[n]         
        if points == 0:
                     
            dublicateindexvalue = wholeindexlist[n]
            dublicateindexlist.append(n)
            dublicateindexvaluelist.append(dublicateindexvalue)

    for n in dublicateindexvaluelist:
        wholeindexlist.remove(n)
    
    return wholeindexlist, dublicateindexlist

# trenger en indexliste
def finddublicates(testlist):
    
    #[20,30,-50,40, -20,40,24,32 ,43 ,24,-25,62 ,6,-24,52,12 ,51,-100,23]
    
    sameindexlist = []
    picmillisindexlist = []
    last = 0
    indexcounter = 0
    
    for n in range(len(testlist)-1):        
        points = testlist[n+1] - testlist[n]
                
        if points == 0:
            indexcounter += 1
        elif points != 0:
            picmillisindexlist.append(testlist[n])
            sameindexlist.append(last)
            sameindexlist.append(indexcounter)
            
            
            
            indexcounter += 1
            last = indexcounter
    sameindexlist.append(last)
    sameindexlist.append(indexcounter)
      
    
    
     
       
    print('samindex')
    print(sameindexlist)

    print(picmillisindexlist)
    # add return picmillisindexlist
    return sameindexlist 

    #difflist = [20,30,-50,40, -20,40,24,32 ,43 ,24,-25,62 ,6,-24,52,12 ,51,-100,23]
    # til :  [[20,30,-50,40], [-20,40,24,32] ,[43] ,[24,-25,62] ,[6,-24,52,12] ,[51,-100,23]]
    # [0, 3, 4, 7, 8, 8, 9, 11, 12, 15, 16, 18]
def orginisedifflist(unorganizeddifflist, dubindex):
    
    #dubindex = [0, 3, 4, 7, 8, 8, 9, 11, 12, 15, 16, 18]
    print('unorg')
    print(dubindex)
    newlist = []
    templist = []
    skip = False
    trueskip = True
    print('test')
    print()
    for n in range(len(dubindex)-1):
        if skip == False:
            print('n: '+str(dubindex[n])+' n+1: '+str(dubindex[n+1]))
            templist = unorganizeddifflist[int(dubindex[n]):int(dubindex[n+1]+1)]
            # if dubindex[n] != dubindex[n+1]:
            #     templist = unorganizeddifflist[int(dubindex[n]):int(dubindex[n+1]+1)]
            # else: 
            #     templist = unorganizeddifflist[n]
            #print(templist)
            newlist.append(templist) 
        if skip == True:
            skip = False              
        else: 
            skip = True
     #templist.clear()
                   
              
        
    print('orginisedifflist') 
    print('newlist')
    print(newlist)
    return newlist

def findclosestdublicate(orginiseddifflist):
    #difflist = [[20,30,-50,40], [-20,40,24,32] ,[43] ,[24,-25,62] ,[6,-24,52,12] ,[51,-100,23]]
    
    absolutedifflist = []
    finalindex = []
    counter = 0
    print(orginiseddifflist)
    for n in orginiseddifflist:
        
        print('___________________')
        absolutedifflist = list(map(abs, n))
        print(absolutedifflist)
        closest = min(absolutedifflist)
        
        bestindex = absolutedifflist.index(closest)
        print(closest)
        finalindex.append(bestindex+counter)
        print('counter:'+str(counter)+' bestindex:'+str(bestindex)+' index: '+str(bestindex+counter))
        print('len: '+str(len(n)))
        print('___________________')
        counter += len(n)
        
    print('findclosestdublicate')
    print('finalindex')
    print(finalindex)
    return finalindex

def removedub(diffylist, keeplist):
    #[[20,30,-50,40], [-20,40,24,32] ,[43] ,[24,-25,62] ,[6,-24,52,12] ,[51,-100,23]]
    #[20,-20,43,24,6,23]
    #keeplist = [0, 4, 8, 9, 12, 18]
    #diffylist = [20,30,-50,40, -20,40,24,32 ,43 ,24,-25,62 ,6,-24,52,12 ,51,-100,23, 50, 60]
    k = 0
    removedublist = []
    
    for n in range(len(diffylist)):
        removedublist.append(n)
    
    keeplist.reverse()
    print(len(keeplist))
    print(len(removedublist))
    for n in keeplist:
        print(n)
        print(removedublist[n])
        del removedublist[n]
    keeplist.reverse()  
    
    
    print('removedub')
    print(removedublist)
    print(keeplist)
    return removedublist, keeplist
   
            
def choosefromindex(valuelist1, wantindex):
    preflist = []
    for n in wantindex:
        preflist.append(valuelist1[n])

    return preflist
    
#   finds and remove overlapping values from the gps value list
#   return list of coordinates without points overalapping
def removefromlistbyindex(valuelist, dublicateindexlist):
    
    for n in dublicateindexlist:               
        del valuelist[n]
     

    
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
def gettimedifference(gpstimelist, pictimelist):    
    timediff = [] 
    for n in range(len(gpstimelist)-1):
        diff = gpstimelist[n] - pictimelist[n]
        timediff.append(diff)
        
        
    
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
def modifycoordinatesbasedontimedifference(timedifflist, coordiantelist, speed, accelerationlist, gpsmillismodified, gpsmillis):
    #print(len(timedifflist))
    #print(len(coordiantelist))
    #print(len(accelerationlist))
    shiftedcoord = []
    print(len(coordiantelist))
    print(len(speed))
    print(len(accelerationlist))
    i = 0
    for n in range(len(coordiantelist)-1):
        time = float(timedifflist[n]/1000) # ms til sekunder
        #print(time)
        tempmillis = gpsmillismodified[n]
        tempindex = gpsmillis.index(tempmillis)
        if tempindex >= len(accelerationlist):
            tempindex = len(accelerationlist)-1
        
        print('-------')
        print(tempindex)
        print(accelerationlist[tempindex])

        if timedifflist[n] < 0:
            shifted = coordiantelist[n] + speed[n] * abs(time) + (accelerationlist[tempindex] * (time**2))/2
        elif timedifflist[n] > 0:
            shifted = coordiantelist[n] + speed[n] * abs(time) - (accelerationlist[tempindex] * (time**2))/2
        #print(shifted)
        #print(coordiantelist[n])
        shiftedcoord.append(shifted)
    return shiftedcoord



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
def makecleanlist(valuelist, keeplist):
    newlist = []
    for n in keeplist:
        newlist.append(valuelist[n])
    return newlist

def makevelocitylist(cordinates, gpsmillis):
    calculatedvelocity = []
    for n in range(len(cordinates)-1):
        speed = (cordinates[n]-cordinates[n+1])/(gpsmillis[n+1]-gpsmillis[n])
        calculatedvelocity.append(speed)
    return calculatedvelocity

#----------------------------------------#

#----end of functions for csv merging----#

#----------------------------------------#


#-------------------------------------------#

#---beginning of program for csv merging---# 

#-------------------------------------------#
def merge(path):
    #   values for iterating
    cleanlength = 0
    picrow = 0
    gpsrow = 0  

    k1row = 0
    expand = 0
    testlist = [[20,30,-50,40], [-20,40,24,32] ,[43] ,[24,-2,62] ,[6,-24,52,12] ,[51,-100,23]]
    print('_________-test______________')
    #print(findclosestdublicate(testlist))
    try:
        # Open image csv file and make a csv reader object 
        with open(path +'/images.csv', newline='') as csvpic:
            picreader = csv.reader(csvpic, delimiter=',', quotechar='|')
            for row in picreader:
                #  make a list for each column in the csv file
                picnumberlist.append(row[0])                
                millisk1list.append(int(row[3]))
                
     
                    
            
        # Open gps csv file and make a csv reader object 
        with open(path +'/gps.csv', newline='') as csvgps:
            gpsreader = csv.reader(csvgps, delimiter=',', quotechar='|')
            for row in gpsreader:
                #  make a list for each column in the csv file
                fixlist.append(row[1])
                speedlist.append(float(row[2]))
                millisgpslist.append(int(row[4])) 
                latlist.append(float(row[5]))
                longlist.append(float(row[6]))

    #for testing
    
    except Exception as e:
        print(e)
    #testlist = [0,0,0,0,1,1,1,1,2,3,3,3,4,4,4,4,5,5,5,5]
    #unorganizeddifflist = [20,30,-50,40, -20,40,24,32 ,43 ,24,-25,62 ,6,-24,52,12 ,51,-100,23,50]
    #finddublicates(testlist)
    # del picnumberlist[20:-1]            
    # del millisk1list[20:-1]
    # del fixlist[190:-1]
    # del fixlist[0:115]
    # del speedlist[190:-1]
    # del speedlist[0:115]
    # del millisgpslist[190:-1]
    # del millisgpslist[0:115]
    # del latlist[190:-1]
    # del latlist[0:115]
    # del longlist[190:-1]
    # del longlist[0:115]
    print(len(longlist))
    print(millisgpslist[0])
    print(millisgpslist[-1])
    
    print('millispic: '+ str(len(millisk1list)))
    print('lat: '+ str(len(latlist)))
    
    matchinglatitudelist = []
    matchinglongitudelist = []
    matchingspeedlist = []
    matchinggpsmillislist = []
    matchingaccelereation = []
    latvelocitylist = []
    longvelocitylist = []
    lataccelereationlist = []
    longaccelereationlist = []
    #print(millisgpslist)
    indexlist, closesttimelist = calculateindexposition(millisgpslist, millisk1list)
    
    
    matchinggpsmillislist = choosefromindex(millisgpslist,indexlist)
    matchinglatitudelist = choosefromindex(latlist,indexlist)
    matchinglongitudelist = choosefromindex(longlist,indexlist)
    matchingspeedlist = choosefromindex(speedlist,indexlist)
    
    latvelocitylist = makevelocitylist(latlist, millisgpslist)
    longvelocitylist = makevelocitylist(longlist, millisgpslist)

    lataccelereationlist = getaccelerationlist(latvelocitylist, millisgpslist)
    longaccelereationlist = getaccelerationlist(longvelocitylist, millisgpslist)

    accelereation = getaccelerationlist(longvelocitylist, millisgpslist)
    print(len(accelereation))

    #matchingaccelereation = choosefromindex(accelereation, indexlist)

    timedifferencelist = gettimedifference(matchinggpsmillislist, millisk1list)

    #   Modifies latitude and longitude list
    modyfiedlatlist = modifycoordinatesbasedontimedifference(timedifferencelist, matchinglatitudelist, latvelocitylist, lataccelereationlist, matchinggpsmillislist, millisgpslist)
    modyfiedlonglist = modifycoordinatesbasedontimedifference(timedifferencelist, matchinglongitudelist, longvelocitylist, longaccelereationlist, matchinggpsmillislist, millisgpslist)

    
    with open(path+ '/mergedfucktest.csv','w', newline='') as test1:
        fieldnames = ['picmillis','gpsmillis','latitude','longitude', 'modyfiedlat', 'modyfiedlong']
        writer = csv.DictWriter(test1, fieldnames=fieldnames) 
        
        for n in range(len(millisk1list)-1):
            
            writer.writerow({'picmillis': millisk1list[n],'gpsmillis':matchinggpsmillislist[n], 
            'latitude':matchinglatitudelist[n],'longitude':matchinglongitudelist[n],
            'modyfiedlat': modyfiedlatlist[n], 'modyfiedlong': modyfiedlonglist[n]})#'readlat':cleanlatlist[n], 'readlong':cleanlonglist[n]})

    with open(path+ '/mapping.csv','w', newline='') as test2:
        fieldnames = ['lat','lng']
        writer1 = csv.DictWriter(test2, fieldnames=fieldnames) 
        writer1.writeheader()
        for n in range(200):            
            writer1.writerow({'lat':matchinglatitudelist[n],'lng':matchinglongitudelist[n]})#'readlat':cleanlatlist[n], 'readlong':cleanlonglist[n]})

    with open(path+ '/mappingmoved.csv','w', newline='') as test3:
        fieldnames = ['lat','lng']
        writer2 = csv.DictWriter(test3, fieldnames=fieldnames) 
        writer2.writeheader()
        for n in range(200):            
            writer2.writerow({'lat':modyfiedlatlist[n],'lng':modyfiedlonglist[n]})#'readlat':cleanlatlist[n], 'readlong':cleanlonglist[n]})

    #print('---------------------------------')
    #print(indexlist)
    #print('indexlist: '+str(len(indexlist)))
    #finddublicates(indexlist)
    
    # dub, index = removedub(closesttimelist, findclosestdublicate(orginisedifflist(closesttimelist, finddublicates(indexlist))))
    # print('sub: '+str(len(dub)))
    # print('index: '+str(len(index)))
    # print(dub)
    # print(index)
    #print('indexlist len: '+str(len(indexlist)))
    #index, dub = findandremovedublicates(indexlist, closesttimelist)
    #print('index: '+str(len(index)))
    #print('dub: '+str(dub))
    # dub.reverse()   #   reversing the dublicate list, resulting removing from top of list.
    # i = 0
    # print(millisgpslist[0])
    # for n in index:
    #     print('Diff: '+str(millisgpslist[n]-millisk1list[i]))
    #     i=+1
    #   Removing dublicates from lists
    

    # cleanlatlist = removefromlistbyindex(latlist, dub)
    # cleanlonglist = removefromlistbyindex(longlist, dub)
    # cleanmillisgpslist = removefromlistbyindex(millisgpslist, dub)
    # cleanspeedlist = removefromlistbyindex(speedlist, dub)
    # cleanfixlist = removefromlistbyindex(fixlist, dub)
    # timedifferencelist = removefromlistbyindex(closesttimelist, dub)
    # print(testindexlist)
    # print(len(testindexlist))
    
    
    #test = makecleanlist(millisgpslist, index)
    # print('timediff')
    # print(timedifferencelist)
    #timedifferencelist = gettimedifference(cleanmillisgpslist, millisk1list, index)
    
    #   Modifies cleaned latitude and longitude list
    # modyfiedlatlist = modifycoordinatesbasedontimedifference(timedifferencelist, cleanlatlist,cleanspeedlist, accelereation)
    # modyfiedlonglist = modifycoordinatesbasedontimedifference(timedifferencelist, cleanlonglist,cleanspeedlist, accelereation)

    #   Expand cleaned latitude and longitude list
    # expandedlatitudelist = makenewcoordinatelist(cleanlatlist, index)
    # expandedlongitudelist = makenewcoordinatelist(cleanlonglist, index)

    #   Expand modified latitude and longitude list
    # expandedmodifiedlatitudelist = makenewcoordinatelist(cleanlatlist, index)
    # expandedmodifiedlongitudelist = makenewcoordinatelist(cleanlonglist, index)
    # print(testindex)
    # print('picmillis: '+ str(len(millisk1list)))
    # print('gpsmillis: '+ str(len(test)))
    # print('exlat: '+ str(len(expandedlatitudelist)))
    # print('exlong: '+ str(len(expandedlongitudelist)))
    # print('cleanminllis'+ str(len(millisgpslist)))
    
    
    # with open(path+ '/mergedfuck.csv','w', newline='') as k1test:
    #     fieldnames = ['picmillis', 'gpsmillis','readlat', 'readlong', 'extendedlat','extendedlong', 'extendedmodifiedlat','extendedmodifiedlong']
    #     k1writer = csv.DictWriter(k1test, fieldnames=fieldnames) 
    #     indexnumber =0
        
    #     for n in millisk1list: 
    #         #print('index: '+str(indexlist[indexnumber])+' ,k1row: '+str(k1row)+' gpsrow: '+str(gpsrow)+' lenght: '+str(len(cleanlatlist)))
    #         # print ('indexnumber'+ str(indexnumber))
    #         # print(len(index))
    #         # print('index[indexnumber]'+ str(index[indexnumber]))
    #         if not(indexnumber >= len(testindex)):            
    #             if testindex[indexnumber] == k1row and gpsrow <= (len(cleanlatlist)-1): 
    #                 print(cleanmillisgpslist[gpsrow])
    #                 # k1writer.writerow({'gpsmillis': cleanmillisgpslist[gpsrow],'readlat':cleanlatlist[gpsrow],
    #                 # 'readlong':cleanlonglist[gpsrow], 'picmillis': n, 'extendedlat':expandedlatitudelist[expand],
    #                 # 'extendedlong':expandedlongitudelist[expand], 'extendedmodifiedlat':expandedmodifiedlatitudelist[expand]
    #                 # , 'extendedmodifiedlong':expandedmodifiedlongitudelist[expand]})
    #                 k1writer.writerow({'gpsmillis': millisgpslist[gpsrow],'readlat':cleanlatlist[gpsrow],
    #                 'readlong':cleanlonglist[gpsrow], 'picmillis': n})
    #                 gpsrow += 1            
    #                 indexnumber +=1
    #                 expand += 1
    #             elif k1row < len(expandedlatitudelist):
    #                 # k1writer.writerow({'picmillis': n, 'extendedlat':expandedlatitudelist[expand],
    #                 # 'extendedlong':expandedlongitudelist[expand], 'extendedmodifiedlat':expandedmodifiedlatitudelist[expand]
    #                 # , 'extendedmodifiedlong':expandedmodifiedlongitudelist[expand]})
    #                 k1writer.writerow({'picmillis': n })
    #                 expand += 1
    #             else:
    #                 k1writer.writerow({'picmillis': n})
    #             k1row += 1
    #         else:
    #             # k1writer.writerow({'picmillis': n, 'extendedlat':expandedlatitudelist[expand-1],
    #             # 'extendedlong':expandedlongitudelist[expand-1], 'extendedmodifiedlat':expandedmodifiedlatitudelist[expand-1]
    #             # , 'extendedmodifiedlong':expandedmodifiedlongitudelist[expand-1]})
    #             k1writer.writerow({'picmillis': n})
    
    
                
#-------------------------------------------#

#---end of program for csv merging---# 

#-------------------------------------------#

  
date ="2021-04-20"
tempTrip= "bachelorvol2.2.3utenpuse"
absolute_path = os.path.dirname(os.path.abspath(__file__))
path = absolute_path+"/log/"+date+"/"+tempTrip      
print(path)
pathtb = "C:/Users/tor_9/Documents/csv"
merge(pathtb)