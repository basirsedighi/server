import cvb
import cv2
import base64
import os
from os import path
from datetime import datetime
import math
import uuid
from starlette.websockets import WebSocket, WebSocketDisconnect
import time


class ConnectionManager:
    """class that handles the socket connections

    
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        try:
            await websocket.accept()
            self.active_connections.append(websocket)

        except Exception as e:
            print(e)

    async def disconnect(self, websocket: WebSocket):
        # await websocket.close()
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

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


def getTimeStamp():

    now = time.time()

    timenow = datetime.today().strftime('%H:%M:%S')
    milliseconds = '%03d' % int((now - int(now)) * 1000)
    return str(timenow) +":"+ str(milliseconds)


def createFolder():
    
    """Creates a folder at startup in 'bilder' with todays date

    parameter: cvb Image
    """
    date = getDate()

        #   Making a folder for the images
    if not path.exists('bilder/'+date):

        os.mkdir('bilder/'+date) 


async def createImageFolder(tripName):
   
    date = getDate()
    
    if not path.exists("bilder/"+str(date)+"/"+str(tripName)+"/"+"kamera1"):
       
        os.makedirs("bilder/"+str(date)+"/"+str(tripName)+"/"+"kamera1")
        
    
    if not path.exists("bilder/"+str(date)+"/"+str(tripName)+"/"+"kamera2"):
    
        
        os.makedirs("bilder/"+str(date)+"/"+str(tripName)+"/"+"kamera2")

    

    if not path.exists('log/'+str(date)):


        os.makedirs('log/'+str(date)) 


def estimateStorageTime(storage):
    # 20 bilder/sek
    # 1 bilde 8000kB

    bilder_pr_sek = 20
    bilde_size = 9  # Mb

    free = storage["free"]
    seconds_left = free/(bilder_pr_sek*bilde_size)
    minleft = math.floor(seconds_left/60)
    hoursLeft = int(minleft/60)
    minleft = minleft % 60

    return {"h": hoursLeft, "m": minleft}

def getDate():

    return datetime.today().strftime('%Y-%m-%d')



def uniqueID():

    return uuid.uuid4() 



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



async def discoverCameras():

    discover = cvb.DeviceFactory.discover_from_root()
    mock_info = next(
        (info for info in discover if "GenICam.vin" in info.access_token), None)
    if mock_info is None:

        raise RuntimeError("unable to find CVMock.vin")

    print(mock_info.access_token)


