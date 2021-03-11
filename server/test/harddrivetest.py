import shutil
import os, string


nested_storage= { }  #  Initializing a dictionary
nested_storage["hd1"] = {} # Initializing a nested dictionary
number= 1 # Variable for 
available_drives = []


#https://stackoverflow.com/questions/827371/is-there-a-way-to-list-all-the-available-drive-letters-in-python/827397?fbclid=IwAR2UlZclP6t0B6KD5Y6B4w3NdfigJDTZcwWHLKCuS0kqorrTCwhsSiRIJcA
for d in string.ascii_uppercase: # Iterating through the english alphabet    
    path = '%s:' % d    
    if os.path.exists(path): # checks if path exists
        available_drives.append(path)  #  append the path from a drive to a list
print(available_drives)

for i in available_drives:  #  Iterating through all drives
    
    total, used, free = shutil.disk_usage(i) # Return disk usage statistics about the given path as a named tuple with the attributes total, used and free
    
    dictname = "hd"+ str(number)
    nested_storage[dictname] = {"name": i,"total": "%d" % (total // (2**30))
    , "used": "%d" % (used // (2**30)), "free": "%d" % (free // (2**30))}  #  Appends a dictionary containing storage info(harddrive) into a nested dictionary.
    
    number += 1

print(nested_storage)