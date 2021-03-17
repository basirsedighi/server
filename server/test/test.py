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