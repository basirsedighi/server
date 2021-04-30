#!/home/rekkverk/server/server/venv/bin/python3
import numpy as np
import sys
from typing import List
import cv2
from fastapi import FastAPI,Request
from starlette.responses import HTMLResponse, StreamingResponse
from starlette.websockets import WebSocket, WebSocketDisconnect
from starlette.concurrency import run_until_first_complete
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.routing import WebSocketRoute
from starlette.exceptions import HTTPException as StarletteHTTPException
from core.cameraStream import CameraStream
import asyncio
from concurrent.futures.process import ProcessPoolExecutor
import shutil
import json
import serial
from core.camera import Camera
import threading
from threading import Lock, Thread
import base64
from time import sleep
import pynmea2
import math
import cvb
import uvicorn
import csv

from core.models import models
import time
from fastapi.middleware.cors import CORSMiddleware
from manager import ConnectionManager
from io import BytesIO
from core.timer import Timer
from core.imageSave import ImageSave
import queue
from gps import Gps
from gps2 import gpsHandler
import os
from os import path
from datetime import datetime
from multiprocessing import Process,Queue,Pool
from pydantic import BaseModel
from core.helpers.helper_server import *
from core.helpers.helper_server import ConnectionManager
from core.models.models import GpsData ,freq
from core.merging import merge
from merging2 import merge2
# camera = Camera()
# camera.start_stream()
manager = ConnectionManager()
image_freq = 20
gps_freq =0
debug = False
storage = {}
app = FastAPI()
image_lock = Lock()
camera_1 = Camera(0)
camera_2 = Camera(1)
camera_3 = Camera(2)

index1 =0
index2 =0
index3 =0


cameras =[camera_1,camera_2,camera_3]
camerasDetected =[]
tempTrip =""

isConfigured =False

stopStream1 = False
stopStream2 = False
stopStream3 = False

gps = gpsHandler(debug)
imageQueue = queue.Queue(maxsize=0)
imageQueue2 = queue.Queue(maxsize=0)
imagesave2=ImageSave(imageQueue2,"saving thread")
imagesave = ImageSave(imageQueue,"saving thread")
config_loaded = False

#temp images to show user
temp_img_1 = None
temp_img_2 =None
temp_img_3 =None

capturing =False
guruMode = False

#g = Gps('C:/Users/norby/Desktop')

imagesave.daemon = True
imagesave2.daemon = True
#imagesave2.start()
imagesave.start()
gpsData ={}
gps.daemon = True
gps.start()
gps_status = {}
valider1 = True
valider2 = True
valider3 = True
abort = False
logging = False
closeServer = False
isRunning1 = False
isRunning2 = False
isRunning3 = False
isRunning = False
start_Puls = False
drive_in_use ="C:"
storageLeft_in_use = 50
gpsControl = True

#manage socket connections
manager = ConnectionManager()

#   Variables and lists for the gps coordinates 
#   lists
longlitudelist = []
latitudelist = []
#   variables
path = 'C:/Users/tor_9/Documents/csv'

#creates new folder for saving imaging
#createFolder()


started = False

class GpsData(BaseModel):
    velocity: str
    timestamp:str
    lat:str
    lon:str
    quality:int



origins = [
    "http://localhost.tiangolo.com",

    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://10.22.182.47:4200",
    "http://10.0.222.1",
    "http://localhost:8000/changeFps",
    


]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.get('/gps')
async def getData():
    global gps_status,gps,gps_freq


    gps_status = gps.getData()

    gps_freq = float(gps_status['velocity'])
   
    return gps_status

#   Open a csv file and appends coordinates in lists
#   return a list with the latitude coordinates and a list with longitude coordinates
@app.get('/GetCoordinates')
def getgpscoordinates():
    mainlist =[]
    tripnamelist =[]
    date = getDate()
    absolute_path = os.path.dirname(os.path.abspath(__file__))
    #absolute_path = fixPath(absolute_path)
    #print(absolute_path)
    path = absolute_path+"/log/"

    folders= os.listdir(path)
    print(folders)
    try:
        for folder in folders:
            subFolders = os.listdir(absolute_path+"/log/"+folder)
            print(folder)

            for subFolder in subFolders:
                print(subFolder)
                latitudelist = []
                longlitudelist =[]
                
                path1 = path+folder+"/"+subFolder+"/" +'merged.csv'
                print(path1)
                skip = os.path.exists(path1)
                print(skip)
                if skip:

                    with open(path1, newline='') as csvgps:
                        gpsreader = csv.reader(csvgps, delimiter=',', quotechar='|')
                        next(gpsreader)
                        i = next(gpsreader)
                        for row in gpsreader:
                            #  make a list for each column in the csv file
                            
                            latitudelist.append(row[3])
                            longlitudelist.append(row[4])
                        
                        
                        cordlist =list(zip(latitudelist,longlitudelist))
                    tripnamelist.append(subFolder)
                    mainlist.append(cordlist)
    except Exception as e:
        print(e)
        
        
    return {"lists":mainlist,"names":tripnamelist}



    
def log(data):
    global tempTrip

    
    
    date = getDate()
    absolute_path = os.path.dirname(os.path.abspath(__file__))
    fixPath(absolute_path)
    path = absolute_path+"/log/"+date+"/"+tempTrip

# Open gps csv file and make a csv reader object 
    with open(path +'/log.csv','a', newline='') as csvgps:

        fieldnames = ['stream','images']
        writer = csv.DictWriter(csvgps, fieldnames=fieldnames)
    
        writer.writerow({"stream":data['stream'],"images":data['results']['images_ok']})
            








@app.get('/getStates')
async def states():

    states = getStates()



    return states


  


@app.post('/gpserror')
async def data(test):

    return test

@app.get('/RaspFPS')
async def fps():
    global image_freq,start_Puls,gps_freq,gpsControl

    

    if not gpsControl:
        fps = image_freq
    
    else:

        
        fps = gps_freq
        
        

     


    return {'fps':fps,"start":start_Puls}

@app.post('/changeFps')
async def change(freq:freq):
    global image_freq
 

    image_freq = freq.fps

    return {"fps":image_freq}


@app.get('/merge')
def merge():
    global tempTrip
    
    date = getDate()
    absolute_path = os.path.dirname(os.path.abspath(__file__))
    fixPath(absolute_path)
    path = absolute_path+"/log/"+date+"/"+tempTrip

    result = merge2(path)

    payload = {"event":"merging","result":result}
    return payload



def emergencyStop():
    global abort,image_freq,stopStream1,stopStream2,stopStream3,capturing,isConfigured
    toggleGPSControl(False)
    abort =True
    isConfigured = False
    started =False
    capturing =False
    image_freq = 0

    stopStream1 =True
    stopStream2 =True
    stopStream3 =True
    #abort = True

    

@app.get('/start1')
def startA():

    timer =Timer("stream1")

    global camera_1, imagesave, imageQueue, abort,stopStream1,gps,capturing,index1
    index1 = 0
    test  =0
    
    print("started camera 1")
    print(time.time()*1000)
    starttime = 0
    newstamp =0
    clockReset = False
    error = "no ERROR"
    cameraStamp =3
    lastCameraStamp =0
    firstCameraStamp =0
    camera_1.resetClock()
                      
    while True:

        if abort:
            break

       

        
        try:
            
            image, status = camera_1.get_image()

           

            

            if status == cvb.WaitStatus.Ok:
                
                
                    
                
                cameraStamp = int(image.raw_timestamp/1000)
                
                
                
                timeStamp = int(time.time() * 1000)

               




                if capturing:
                    
                   

                    
                    if index1 >0:
                        newstamp =  starttime+ (cameraStamp-firstCameraStamp)
                        
                        
                
                        data = {"image": image, "camera": 1, "index": index1,"timeStamp":timeStamp,"cameraStamp":newstamp}
                        imageQueue.put(data)
                        index1 = index1 +1
                    
                    if index1 ==0:   
                        starttime = timeStamp
                        firstCameraStamp = cameraStamp
                        index1 = index1 +1
                
                
                    
            
                
            
            elif status == cvb.WaitStatus.Abort:
                print("stream 1 abort")
                break

            elif status == cvb.WaitStatus.Timeout and stopStream1:
                print("stream 1 timeout")
                break
            elif status == cvb.WaitStatus.Timeout:
                print("timed out waiting for images")

            else:
                test = test+1
            
               
            # timer.stop()

                
            
            
            
            

        except Exception as e :

            error = str(e)
            emergencyStop()
            pass

   
    stopStream1 =False 
    camera_1.stopStream()

    return {"message": "stream 1 has stopped","images_ok":str(index1),"images":str(test),"error":error}
    




@app.get('/start2')
def startB():

    global camera_2, isRunning, imageQueue, abort,stopStream2,capturing,index2
    
    timer = Timer("stream2")
    
    error = "no error"
    index2 = 0
    test =0
    print("started camera 2") 
    print(time.time()*1000) 
    
    
    while True:
        if abort:
            break

        

        
          
        try:
            image, status = camera_2.get_image()

        

          

            if status == cvb.WaitStatus.Ok:
                

                if capturing:

                    data = {"image": image, "camera": 2, "index": index2,"timeStamp":"","cameraStamp":""}

                    imageQueue.put(data)
                    index2 = index2 +1
            
            elif status == cvb.WaitStatus.Abort:
                print("stream 2 abort")
                break

            elif status == cvb.WaitStatus.Timeout and stopStream2:
                print("stream 2 timeout")
                break
            elif status == cvb.WaitStatus.Timeout:
                print("timed out waiting for images")
            
            else:
                test =test+1
            

            

                
            
            

            
        except Exception as e:
            error = str(e)
            emergencyStop()
            pass

          

    

    stopStream2 =False
    camera_2.stopStream()
    

    

    return {"message": "stream 2 has stopped","images_ok":str(index2),"images":str(test),"error":error}
    # start bildetaking

@app.get('/start3')
def startC():

    global camera_3, isRunning, imageQueue, abort,stopStream3,capturing,camerasDetected,index3
    

    error ="no error"
    timer = Timer("stream3")
    index3 = 0
    test =0
    print("started camera 3") 
    print(time.time()*1000) 
    
    if len(camerasDetected) >2:
        while True:
            if abort:
                break

        

            
            # timer.start()
            try:
                image, status = camera_3.get_image()

            

                

                if status == cvb.WaitStatus.Ok:
                    #timeStamp = int(time.time() * 1000)
                    
                    if capturing:
                        data = {"image": image, "camera": 3, "index": index3,"timeStamp":"","cameraStamp":""}

                        imageQueue.put(data)
                        index3 = index3 +1
                
                elif status == cvb.WaitStatus.Abort :
                    print("stream 3 abort")
                    break

                elif status == cvb.WaitStatus.Timeout and stopStream3:
                    print("stream 3 timeout")
                    break
                
                elif status == cvb.WaitStatus.Timeout:
                    print("timed out waiting for images")
                
                else:
                    test = test+1
                

                # timer.stop()

                    
                
                

                
            except Exception as e:
                error = str(e)
                emergencyStop()
                pass

          

 
        stopStream3 =False
        camera_3.stopStream()
    

    

    return {"message": "stream 3 has stopped","images_ok":str(index3),"images":str(test),"error":error}
    # start bildetaking


async def abortStream():
    """Stops all the streams

    By setting the pulse hz to zero 
    then the capturing times out


"""
    global gps,start_Puls,image_freq,gpsControl,stopStream1,stopStream2,stopStream3,isConfigured
    print("stopping stream")

    toggleGPSControl(False)
    isConfigured = False
    image_freq = 0
    stopStream1 =True
    stopStream2 =True
    stopStream3 =True
    
   


async def start_acquisition():
    """ starts gps logging and turns on GPS control


    """
    global abort,image_freq
    print("Starting stream")
    toggleGPSControl(True)
    gps.toggleLogging(True)
    
    
    abort=False
    image_freq = 0
    
    
   
    
    
   
    
def startPulse():
    """
    starts the image capturing
    """
    global image_freq,started,gps,capturing
    
    toggleGPSControl(True)
    gps.toggleLogging(True)
    started = True
    capturing = True


def pause():
    """Pauses the image capturing

    """
    global gps,image_freq,capturing
    gps.toggleLogging(False)
    toggleGPSControl(False)
    capturing = False
    image_freq =0


@app.post('/changeimagefreq/')
async def change_image_freq(freq:freq):
    global image_freq

    image_freq = freq

    return image_freq


def toggleGPSControl(value):
    global gpsControl

    gpsControl =  value


@app.get('/capturing')
async def getCapturing():
    global index1,index2,index3


    return {"camera1":index1,"camera2":index2,"camera3":index3}


@app.get('/storage')
async def getStorage():
    global storage,started

    storages =checkStorageAllDrives()
    
    storageLeft(storages)

    
    payload = estimateStorageTime(storages,10)

    total = payload['total']['free']
    if int(total)<10 and started:
        emergencyStop()
        await manager.broadcast(json.dumps({"event":"storage","data":"empty"}))
        
        
    

    return payload

# estimate hows

def storageLeft(storages):
    global drive_in_use,imagesave,imagesave2,storageLeft_in_use

    drives = storages['drives']

    for i in drives:
        drive = drives[i]

        if(drive['name'] == drive_in_use):

            storageLeft_in_use = int(drive['free'])
            imagesave.setStorageLeft(int(drive['free']))
            #imagesave2.setStorageLeft(int(drive['free']))
            
   


async def initCameraA():
    global camera_1, abort,cameras,camerasDetected
    if abort:
        abort = False
    status = "ok"


    try:
        #camera_1.init()
    
        if camera_1.getDevice() is not None:

            if not camera_1.isRunning():
                
                camera_1.start_stream()
        
        else:

            if len(camerasDetected)>0:
                print("camera 1 init")
                camera_1.init()

        config_loaded = True

    except Exception as e:
        print(e)
        print("initializing of camera 1 failed")
        status = "failed"
    finally:
        
        await manager.broadcast(json.dumps({"event": "initA", "data": status}))





async def loadConfig():
    global camera_1,camera_2,config_loaded,cameras,camerasDetected
    status="Konfig vellykket"
    cameraStatus = "config_ok"
    try:
        camerasDiscovered = await discoverCameras()
        i =0
        for device in camerasDiscovered:
            cameras[i].init()


            i=i+1
       
       
        
        config_loaded = True
    except:
        print("config failed")
        cameraStatus ="config_failed"
        status = "Konfig feilet"
        config_loaded = False

    finally:

        
        await manager.broadcast(json.dumps({"event": "loadConfig", "data": status}))

 

async def initCameraB():
    global camera_2,cameras,camerasDetected
    status = "ok"
   

    try:
        #camera_2.init()
        if camera_2.getDevice() is not None: 
            if not camera_2.isRunning():

                camera_2.start_stream()
        
        else:

            if len(camerasDetected)>1:
                print("camera 2 init")
                camera_2.init()
        
        
    

    except Exception as e:
        print(e)
        print("initializing of camera 2 failed")
        status = "failed"
    finally:
        
        await manager.broadcast(json.dumps({"event": "initB", "data": status}))
        
def index_in_list(a_list, index):
        test = index < len(a_list)
        return test

async def initCameraC():
    global camera_3,config_loaded,camerasDetected
    status = "ok"
    
    
    
    
        
    try:

        
        #camera_3.init()
        if camera_3.getDevice() is not None:
            
            

            if not camera_3.isRunning():

                camera_3.start_stream()
        
        else:
            
           if len(camerasDetected)>2:
                print("camera 3 init")
                camera_3.init()
            
        
        
    

    except Exception as e:
        print("initializing of camera 3 failed")
        status = "failed"
        print(e)
    finally:
        
        
        await manager.broadcast(json.dumps({"event": "initC", "data": status}))








async def validate(cam):
    global camera_1, camera_2
    try:
        
        camera = None
        if cam == 'A':
            camera = camera_1

        else:
            camera = camera_2
    
        frame, status = camera.get_image()
        if status == cvb.WaitStatus.Ok:

            

            b64 = cvbImage_b64(frame)

            raw_data = {"event": "snapshot", "data": b64}

            data = json.dumps(raw_data)
            await manager.broadcast(data)
    except Exception as e:
        print(e)
        

@app.get('/stopFeed')
async def stoplive():
    global valider1

    valider1 = False

    
        
def gen():
    global camera_1,valider1
    
    while 1:

        if valider1:
            try:
                frame, status = camera_1.get_image()
                if status == cvb.WaitStatus.Ok:
                    frame = np.array(frame)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = cv2.resize(frame, (640, 480))
                    _, frame = cv2.imencode('.jpg', frame)

                    image = frame.tobytes()

                    yield (b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')
                
                
                    
            
            except Exception as e:
                pass
               
        
        


    




def gen1():
    global camera_2,valider1

    while 1:

        if valider1:

            try:
                frame, status = camera_2.get_image()
                if status == cvb.WaitStatus.Ok:
                    frame = np.array(frame)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = cv2.resize(frame, (640, 480))
                    _, frame = cv2.imencode('.jpg', frame)

                    image = frame.tobytes()

                    yield (b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')
                
                
            except Exception as e:
                pass
       

def gen2():
    global camera_3,valider1

    while 1:

        if valider1:

            

            try:
                frame, status = camera_3.get_image()
                if status == cvb.WaitStatus.Ok:
                    frame = np.array(frame)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = cv2.resize(frame, (640, 480))
                    _, frame = cv2.imencode('.jpg', frame)

                    image = frame.tobytes()

                    yield (b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')
                
                
            except Exception as e:
                pass
        

@app.get('/video_feed1')
def video_feed1():
    global valider

    
    return StreamingResponse(gen(), media_type="multipart/x-mixed-replace; boundary=frame")
    
    





    


@app.get('/video_feed2')
def video_feed2():
    global valider
    
    return StreamingResponse(gen1(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.get('/video_feed3')
def video_feed3():
    global valider
    
    return StreamingResponse(gen2(), media_type="multipart/x-mixed-replace; boundary=frame")
    


def videofeed():
    global camera_1
    
    frame, status = camera_1.get_image()
    if status == cvb.WaitStatus.Ok:

        b64 = cvbImage_b64(frame)

        raw_data = {"event": "snapshot", "data": b64}

        yield raw_data



def resett():
    global tempTrip,gps,isConfigured,started
    isConfigured= False
    started = False
    gps.toggleLogging(False)
    
  



def initGPS():
    global gps
    gps.startInit()

    
    
def getImages():
    global index1,index2,index3

    return {"camera1":index1,"camera2":index2,"camera3":index3}


def startfps():
    global image_freq,capturing,isRunning,isConfigured,gpsControl

    toggleGPSControl(False)
    capturing = False
    image_freq = 5


   



def getStates():
    global capturing,config_loaded,started,isConfigured,gpsControl,guruMode,debug
    return {"capturing":capturing,"init_ok":config_loaded,"running":started,"isConfigured":isConfigured,"gpsControl":gpsControl,"guruMode":guruMode,"debug":debug}


@app.websocket("/stream/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    global started,config_loaded,imagesave,isConfigured,imagesave2,gps,drive_in_use,gpsControl,valider1,valider2,tempTrip,cameras,guruMode,debug
    await manager.connect(websocket)
    await websocket.send_text(json.dumps({"event": "connected", "data": "connected to server"}))
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            event = data['event']
            msg = data['data']
            print(event)

            

            if(event == "onConnection"):

                await manager.broadcast(json.dumps({"connection": "connected"}))
                
                

        
            elif(event == "loadConfig"):
                
               
                    
                    #print(len( await discoverCameras()))
                    await initCameraA()
                    print("A")
                    await initCameraB()
                    print("B")
                    await initCameraC()
                    print("C")
                
                
                   
                



            elif(event == 'start'):

                isConfigured = True
                tempTrip = str(msg)
                imagesave.setTripName(str(msg))
                #imagesave2.setTripName(str(msg))
                gps.setTripName(str(msg))
                drive_in_use = await createImageFolder(msg)
                print(drive_in_use)
                if drive_in_use =="failed":
                    await manager.broadcast(json.dumps({"event": "error","data":"no drives"}))

                
                imagesave.setDrive(drive_in_use)
                #imagesave2.setDrive(drive_in_use)
                await start_acquisition()
                await manager.broadcast(json.dumps({"event": "starting"}))
            
                
                

                
            elif(event =="pulse"):
                
                startPulse()
            elif(event == 'stop'):
                started = False
                await abortStream()

                await manager.broadcast(json.dumps({"event": "stopping"}))

            elif(event == "init"):

                
                await initCameraA()
                print("A")
                await initCameraB()
                print("B")
                await initCameraC()
                print("C")
                

            elif(event == "stream"):
                await startStreamA()
                await startStreamB()
            elif(event == "validation"):
                await validate(msg)
            
            elif(event =="gps"):
                print(msg)

            elif(event == "start_acquisition"):
                status = start_acquisition()
            
            elif(event == "create_trip"):
                await createImageFolder(data)
                await manager.broadcast(json.dumps({"event":"folderCreated"}))
            
            elif(event == "toggleGps"):
                toggleGPSControl(msg)
            
            elif(event == "live"):
                valider1 = msg
                
            
            elif(event == "debug"):
                gps.setDebug(msg)
                debug= msg
            
            elif(event=="search"):

                n =discoverCamerasLength()
                message = json.dumps({"event":"search","data":n})
                await manager.send_personal_message(message, websocket)
                
            
            elif(event == "guru"):
                guruMode = msg

            elif(event=="initGPS"):
                initGPS()
            
            elif(event == "pause"):
                pause()
            
            elif(event =="reset"):
                startfps() 
                resett()

                images = getImages()

                await manager.broadcast(json.dumps({"event":"stopped","data":images}))
                states = getStates()
                await manager.broadcast(json.dumps({"event":"states","data":states}))
            
            elif (event =="emergency"):
                emergencyStop()
            
            elif(event=="log"):
                log(msg)
            
            elif(event=="states"):

                states = getStates()

                await manager.broadcast(json.dumps({"event":"states","data":states}))


                
                

    except (WebSocketDisconnect,RuntimeError) as e:  # WebSocketDisconnect

        print("[WEBSOCKET] websocket disconnect")

        await manager.disconnect(websocket)

        


@app.on_event("startup")
async def startup():
    global camera_1,camera_2,camera_3,cameras,camerasDetected
    print("[startup] init cameras")
    detected =  discoverCamerasLength()
    i =0
    
    
    print("Cameras:"+ str(detected))
    for device in range(int(detected)):
        camerasDetected.append(str(i))
        
        

        i=i+1

    

    if cameras ==0:
        print("Just :" +str(cameras)+"--cameras was connected")
        raise Exception("CONNECT ALL CAMERAS")
       
    
        
    


@app.on_event("shutdown")
def shutdown_event(): 
    global imagesave,imagesave2 ,closeServer,gps

    print("shutting down server")

    imagesave.raise_exception()
    gps.raise_exception()
    imagesave.join()
    gps.join()
    



def main(arg):
   

    uvicorn.run(app, host="localhost", port=8000,log_level="info")


if __name__ == "__main__":
  
    main(debug)
    

    # isi 192.168.10.153
    #169.254.108.159
    #192.168.0.100