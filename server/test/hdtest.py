import os, string
#https://stackoverflow.com/questions/827371/is-there-a-way-to-list-all-the-available-drive-letters-in-python/827397?fbclid=IwAR2UlZclP6t0B6KD5Y6B4w3NdfigJDTZcwWHLKCuS0kqorrTCwhsSiRIJcA

available_drives = []
print()
for d in string.ascii_uppercase:    
    path = '%s:' % d   
    print('%s:' % d) 
    if os.path.exists(path):
        available_drives.append(path)
print(available_drives)
