import cvb
import cv2
import base64
import os
from os import path
from datetime import datetime
import uuid

def cvbImage_b64(frame):
    """Return a b64 string

    parameter: cvb Image
    """

    image_np = cvb.as_array(frame, copy=False)
    # image_rot = cv2.cv2.ROTATE_90_CLOCKWISE
    image_np = cv2.resize(image_np, (640, 480))
    _, frame = cv2.imencode('.jpg', image_np)
    im_bytes = frame.tobytes()
    im_b64 = base64.b64encode(im_bytes)
    base64_string = im_b64.decode('utf-8')

    return base64_string

def getDate():

    return datetime.today().strftime('%Y-%m-%d')

def createFolder():
    date = getDate()

        #   Making a folder for the images
    if not path.exists('bilder/'+date):

        os.mkdir('bilder/'+date) 

def uniqueID():

    return uuid.uuid4() 


def createImageFolder():
    date = getDate()

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