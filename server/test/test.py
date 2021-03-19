<<<<<<< HEAD
import string
import os
import shutil


def getExternalStorage():
    available_drives = []


    for d in string.ascii_uppercase: # Iterating through the english alphabet    
        path = '%s:' % d    
        if os.path.exists(path): # checks if path exists
            available_drives.append(path)  #  append the path from a drive to a list
    

    return available_drives


def checkStorageAllDrives():
    available_drives = []


    for d in string.ascii_uppercase: # Iterating through the english alphabet    
        path = '%s:' % d    
        if os.path.exists(path): # checks if path exists
            available_drives.append(path)  #  append the path from a drive to a list


    nested_storage= {'drives':{} } #  Initializing a dictionary

    number= 1 # Variable for 
    for i in available_drives:  #  Iterating through all drives
        
        total, used, free = shutil.disk_usage(i) # Return disk usage statistics about the given path as a named tuple with the attributes total, used and free
        
        dictname = "hd"+ str(number)
        nested_storage['drives'].update ({dictname:{ "name": i,"total": "%d" % (total // (2**30))
        , "used": "%d" % (used // (2**30)), "free": "%d" % (free // (2**30))}})  #  Appends a dictionary containing storage info(harddrive) into a nested dictionary.
        number += 1


    return nested_storage

def most_free_space():
    useableDrives = {}
    drives = checkStorageAllDrives()
    drives = drives['drives']


    for drive in drives:

        hd = drives[drive]

        if(hd['name']=='C:'):
            pass

        else:
            useableDrives.update({hd['name']:hd})
            onedrive = hd
    bestDrive ={}
    if len(useableDrives)> 1:
        
    

       
        for drive in useableDrives:
            drive1 = useableDrives[drive]
            free = drive1['free']
            for drives in useableDrives:
                drive2 = useableDrives[drives]
                compare = int(drive2['free'])
                if int(free) > compare:
                    bestDrive = drive1
                
                elif int(free)< compare:
                    bestDrive = drive2
    
    else:

        bestDrive = onedrive

            
            
        

    
    return bestDrive

    

   



        

        


most_free_space()
=======
from bisect import bisect_left

def take_closest(myList, myNumber):
    """
    Assumes myList is sorted. Returns closest value to myNumber.

    If two numbers are equally close, return the smallest number.
    """
    pos = bisect_left(myList, myNumber)
    if pos == 0:
        return myList[0]
    if pos == len(myList):
        return myList[-1]
    before = myList[pos - 1]
    after = myList[pos]
    if after - myNumber < myNumber - before:
       return after
    else:
       return before

for n in 

#x = take_closest(lst,k)
#print(x)      
#print([item for item, count in collections.Counter(millispiclist).items() if count > 1])   

#print([item for item, count in collections.Counter(millisk1list).items() if count > 1])
>>>>>>> gpsgen
