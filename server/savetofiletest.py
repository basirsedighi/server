import os
from os import path

date = "01.04.2021"
number_of_images = []
if not (path.exists('C:/Users/tor_9/Documents/test_jpg/'+date)):        
        os.mkdir("C:/Users/tor_9/Documents/test_jpg/"+date) #   setting up folder for pictures
else:
    # List all files in a directory using os.listdir
    basepath = 'C:/Users/tor_9/Documents/test_jpg/'+date
    for entry in os.listdir(basepath):
        if os.path.isfile(os.path.join(basepath, entry)):
            number_of_images.append(entry)
            #print(entry.replace(".jpg", ""))
print(len(number_of_images))