import cvb
import cv2
import base64
import os,string
from os import path
from datetime import datetime
import math
import uuid
from starlette.websockets import WebSocket, WebSocketDisconnect
import time
import shutil



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
    image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
    image_np = cv2.resize(image_np, (1280, 720))
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


def checkStorageAllDrives():
    available_drives = []


    # for d in string.ascii_uppercase: # Iterating through the english alphabet    
    #     path = '%s:' % d    
    #     if os.path.exists(path): # checks if path exists
    #         available_drives.append(path)  #  append the path from a drive to a list

    nested_storage= {'drives':{} }
    try:
        directory_contents = os.listdir("/media/rekkverk")
        for item in directory_contents:
            available_drives.append("/media/rekkverk/"+str(item))
            
            
            
        


        nested_storage= {'drives':{} } #  Initializing a dictionary

        number= 1 # Variable for 
        for i in available_drives:  #  Iterating through all drives
            
            total, used, free = shutil.disk_usage(i) # Return disk usage statistics about the given path as a named tuple with the attributes total, used and free
            
            dictname = "hd"+ str(number)
            nested_storage['drives'].update ({dictname:{ "name": i,"total": "%d" % (total // (2**30))
            , "used": "%d" % (used // (2**30)), "free": "%d" % (free // (2**30))}})  #  Appends a dictionary containing storage info(harddrive) into a nested dictionary.
            number += 1


        
    except:
        pass

    finally:
        return nested_storage




def most_free_space():
    onedrive={}
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





def getExternalStorage():
    available_drives = []


    for d in string.ascii_uppercase: # Iterating through the english alphabet    
        path = '%s:' % d    
        if os.path.exists(path): # checks if path exists
            available_drives.append(path)  #  append the path from a drive to a list
    

    return available_drives
    

def createFolder():
    
    """Creates a folder at startup in 'bilder' with todays date

    parameter: cvb Image
    """
    date = getDate()

    

        #   Making a folder for the images
    if not path.exists('bilder/'+date):

        os.mkdir('bilder/'+date) 


async def createImageFolder(tripName):
    path = os.path.dirname(os.path.abspath(__file__))
        
    path = fixPath(self.path)

    date = getDate()
    
    if not path.exists(path+'/log/'+str(date)+"/"+str(tripName)):


        os.makedirs(path+'/log/'+str(date)+"/"+str(tripName)) 
    

    bestDrive = most_free_space()
    if bestDrive:
        drive = bestDrive['name']
        print(drive)

        if not path.exists(drive+"/"+"bilder/"+str(date)+"/"+str(tripName)+"/"+"kamera1"):
        
            os.makedirs(drive+"/bilder/"+str(date)+"/"+str(tripName)+"/"+"kamera1")
            
        
        if not path.exists(drive+"/bilder/"+str(date)+"/"+str(tripName)+"/"+"kamera2"):
        
            
            os.makedirs(drive+"/bilder/"+str(date)+"/"+str(tripName)+"/"+"kamera2")
        
        if not path.exists(drive+"/bilder/"+str(date)+"/"+str(tripName)+"/"+"kamera3"):
        
            
            os.makedirs(drive+"/bilder/"+str(date)+"/"+str(tripName)+"/"+"kamera3")

        

   


        return drive
    
    else: return "failed"

def estimateStorageTime(storages,fps):
    # 20 bilder/sek
    # 1 bilde 8000kB

    total = 0
    
    bilder_pr_sek = 20
    bilde_size = 9  # Mb
    
    for storage in storages['drives']:
        
      

        free = int(storages['drives'][storage]["free"])
        if storages['drives'][storage]['name'] == "C:":

            pass
        else:

            total = total + free

        free = free*1000
        seconds_left = free/(bilder_pr_sek*bilde_size)
        minleft = math.floor(seconds_left/60)
        hoursLeft = int(minleft/60)
        minleft = minleft % 60

        storages['drives'][storage]['h'] = hoursLeft
        storages['drives'][storage]['m'] =minleft
    


    storages['total'] = {'free':total,'timeleft':{}}
    free = total*1000
    seconds_left = free/(bilder_pr_sek*bilde_size)
    minleft = math.floor(seconds_left/60)
    hoursLeft = int(minleft/60)
    minleft = minleft % 60

    storages['total'].update({'timeleft':{'h':hoursLeft,'m':minleft}})

    storages['total'].update({'h': hoursLeft})
    storages['total'].update({'m':minleft})





    return storages

def fixPath(path):

    test = path.split("\\")
    if len(test)>1:

        
        newPath = '/'.join(test)
        return newPath
    else:
        
        return path

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



def discoverCameras():

    discover =[]

    try:

        discover = cvb.DeviceFactory.discover_from_root(cvb.DiscoverFlags.IgnoreVins,time_span=200)

        
    
    except Exception as e:
        print(e)
    
    finally:
        return discover
    


    


def discoverCamerasLength():

    discover = cvb.DeviceFactory.discover_from_root(cvb.DiscoverFlags.IgnoreVins)
    

    return len(discover)


