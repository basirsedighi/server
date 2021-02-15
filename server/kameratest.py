# CVBpy Example Script
#
# 1. Open the GenICam.vin driver.
# 2. Acquire images.
#
# Requires: -

import os
from os import path
import cvb
from core.camera import Camera
import cv2
import numpy as np
import io
from core.timer import Timer
#from PIL import Image

image_name = 0
image_name2 = 0
list_of_images = []
date = "01.04.2021"
kamera1 = "kamera1"
kamera2 = "kamera2"
camera1 = Camera(0)
camera2 = Camera(1)


camera1.start_stream()
camera2.start_stream()
o = io.BytesIO()

def folderConstructor():
    #   Making a folder for the images
    if not (path.exists('C:/Users/tor_9/Documents/test_jpg/01.04.2021')):        
         os.mkdir("C:/Users/tor_9/Documents/test_jpg/"+date) #   setting up folder for pictures
    else:
        # List all files in a directory using os.listdir
        basepath = 'C:/Users/tor_9/Documents/test_jpg/'+date
        for entry in os.listdir(basepath):
            if os.path.isfile(os.path.join(basepath, entry)):
                list_of_images.append(entry)                
        image_name = len(list_of_images) + 1        

folderConstructor()


while True: 
    timer = Timer()
    timer.start()
    image1,status1 = camera1.get_image()
    image2,status2 = camera2.get_image()
    if status1 == cvb.WaitStatus.Ok:           
        image1.save('C:/Users/tor_9/Documents/test_jpg/' +date+ '/'+kamera1 +str(image_name)+'.jpg')
        
    if status2 == cvb.WaitStatus.Ok:
        image2.save('C:/Users/tor_9/Documents/test_jpg/' +date+ '/'+kamera2 +str(image_name)+'.jpg')
        image_name += 1
        #np_image = cvb.as_array(image1,copy=False)    
        
    # Window name in which image is displayed 
        #window_name = 'image'        
        
    # Using cv2.imshow() method  
    # Displaying the image  
        #cv2.imshow(window_name, np_image) 
        
    #waits for user to press any key  
    #(this is necessary to avoid Python kernel form crashing) 
    #    if cv2.waitKey(1) ==27:
    #        break
  
    #closing all open windows  
    #        cv2.destroyAllWindows() 
    timer.stop()

