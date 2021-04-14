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
tempTrip =""

stopStream1 = False
stopStream2 = False
stopStream3 = False

gps = gpsHandler(debug)
imageQueue = queue.Queue()
imagesave = ImageSave(imageQueue,"saving thread")
config_loaded = False

#temp images to show user
temp_img_1 = None
temp_img_2 =None
temp_img_3 =None

#g = Gps('C:/Users/norby/Desktop')

imagesave.daemon = True
imagesave.start()
gpsData ={}
gps.daemon = True
gps.start()
gps_status = {}
valider1 = True
valider2 = True
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
gpsControl = False

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


app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")

    


origins = [
    "http://localhost.tiangolo.com",

    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:4200",
    "http://localhost:8000",
    "http://10.22.182.47:4200",
    "http://10.22.182.47",
    "http://localhost:8000/changeFps",


]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    return RedirectResponse("/")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})


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
    date = getDate()
    absolute_path = os.path.dirname(os.path.abspath(__file__))
    path = absolute_path+"/log/"

    folders= os.listdir(path)

    for folder in folders:
        subFolders = os.listdir(absolute_path+"/log/"+folder)
        print(folder)

        for subFolder in subFolders:
            print(subFolder)
            latitudelist = []
            longlitudelist =[]

            with open(path+folder+"/"+subFolder+"/" +'gps.csv', newline='') as csvgps:
                gpsreader = csv.reader(csvgps, delimiter=',', quotechar='|')
                for row in gpsreader:
                    #  make a list for each column in the csv file
                    latitudelist.append(row[4])
                    longlitudelist.append(row[5])
                
                cordlist = [latitudelist,longlitudelist]
            
            mainlist.append(cordlist)
        
    return {"list":mainlist}



    
        

    
  


@app.post('/gpserror')
async def data(test):

    return test

@app.get('/RaspFPS')
async def fps():
    global image_freq,start_Puls,gps_freq,gpsControl

    

    if not gpsControl:
        fps = image_freq
    
    else:

        if gps_freq >2:
            fps = gps_freq
        
        else: fps =0

     


    return {'fps':fps,"start":start_Puls}

@app.post('/changeFps')
async def change(freq:freq):
    global image_freq
 

    image_freq = freq.fps

    return {"fps":image_freq}





@app.get('/start1')
def startA():

    global camera_1, isRunning1, imagesave, imageQueue, abort,isRunning,stopStream1,gps
    index = 0
    test  =0
    
    print("started camera 1")
    print(time.time()*1000)
    while True:

        if abort:
            break

       
        if isRunning1:    
        
            try:

                image, status = camera_1.get_image()

                

                if status == cvb.WaitStatus.Ok:
                    timeStamp = int(time.time() * 1000) #getTimeStamp()
                
                    data = {"image": image, "camera": 1, "index": index,"timeStamp":timeStamp}
                    imageQueue.put(data)
                    index = index +1
                
                elif status == cvb.WaitStatus.Abort:
                    print("stream 1 abort")
                    break

                elif status == cvb.WaitStatus.Timeout and stopStream1:
                    print("stream 1 timeout")
                    break

                    
                
                
                
                

            except Exception as e :

                print(e)
                pass

    isRunning1=False
    stopStream1 =False 
    gps.toggleLogging(False)
          
    print("stream 1 stopped: "+str(index))
    camera_1.stopStream()

    return {"message": "stream 1 has stopped"}
    




@app.get('/start2')
def startB():

    global camera_2, isRunning2, image_lock, imageQueue, abort,stopStream2
    

    
   
    index = 0
    test =0
    print("started camera 2") 
    print(time.time()*1000) 
    
    
    while True:
        if abort:
            break

        if isRunning2:

        
   
            try:
                image, status = camera_2.get_image()

            

                #getTimeStamp()

                if status == cvb.WaitStatus.Ok:
                    timeStamp = int(time.time() * 1000)

                    data = {"image": image, "camera": 2, "index": index,"timeStamp":timeStamp}

                    imageQueue.put(data)
                    index = index +1
                
                elif status == cvb.WaitStatus.Abort :
                    print("stream 2 abort")
                    break

                elif status == cvb.WaitStatus.Timeout and stopStream2:
                    print("stream 2 timeout")
                    break

                    
                
                

                
            except Exception as e:
                print(e)
                pass

          

    isRunning2=False
    stopStream2 =False
    camera_2.stopStream()
    print("stream 2 stopped: "+str(index))

    

    return {"message": "stream 2 has stopped"}
    # start bildetaking

@app.get('/start3')
def startC():

    global camera_3, isRunning3, image_lock, imageQueue, abort,stopStream3
    

    
   
    index = 0
    test =0
    print("started camera 2") 
    print(time.time()*1000) 
    
    
    while True:
        if abort:
            break

        if isRunning3:

        
   
            try:
                image, status = camera_3.get_image()

            

                #getTimeStamp()

                if status == cvb.WaitStatus.Ok:
                    timeStamp = int(time.time() * 1000)

                    data = {"image": image, "camera": 3, "index": index,"timeStamp":timeStamp}

                    imageQueue.put(data)
                    index = index +1
                
                elif status == cvb.WaitStatus.Abort :
                    print("stream 3 abort")
                    break

                elif status == cvb.WaitStatus.Timeout and stopStream3:
                    print("stream 3 timeout")
                    break

                    
                
                

                
            except Exception as e:
                print(e)
                pass

          

    isRunning3=False
    stopStream3 =False
    camera_3.stopStream()
    print("stream 3 stopped: "+str(index))

    

    return {"message": "stream 3 has stopped"}
    # start bildetaking


async def abortStream():
    global camera_1,camera_2, abort,gps,start_Puls,image_freq,gpsControl,stopStream1,stopStream2,stopStream3
    print("stopping stream")
    toggleGPSControl(False)
    gps.toggleLogging(False)

    
    image_freq = 0

    stopStream1 =True
    stopStream2 =True
    stopStream3 =True
    #abort = True
   


async def start_acquisition():
    global isRunning1, isRunning2,camera_1,camera_2,gps,isRunning,abort,image_freq
    print("Starting stream")
    #toggleGPSControl(True)
    abort=False
    image_freq = 0
    
    
   
    
    
   
    
def startPulse():
    global image_freq,isRunning1,isRunning2,isRunning3,started,gps
    
    gps.toggleLogging(True)
    isRunning1 = True
    isRunning2 = True
    isRunning3 = True
    started = True


    image_freq = 20

def pause():
    global isRunning1,isRunning2,isRunning3,gps,image_freq
    gps.toggleLogging(False)
    toggleGPSControl(False)
    image_freq =0
    # isRunning1 = False
    # isRunning2 = False
    # isRunning3 = False
    


# def resume():
#     isRunning1 = True
#     isRunning2 = True
#     isRunning3 = True



@app.post('/changeimagefreq/')
async def change_image_freq(freq:freq):
    global image_freq

    image_freq = freq

    return image_freq


def toggleGPSControl(value):
    global gpsControl

    gpsControl =  value


@app.get('/storage')
async def getStorage():
    global storage,imagesave,started

    storages =checkStorageAllDrives()
    
    storageLeft(storages)

    
    payload = estimateStorageTime(storages,10)

    total = payload['total']['free']
    if int(total)<10 and started:
        #await abortStream()
        pass
        
    

    return payload

# estimate hows

def storageLeft(storages):
    global drive_in_use,imagesave,storageLeft_in_use

    drives = storages['drives']

    for i in drives:
        drive = drives[i]

        if(drive['name'] == drive_in_use):

            storageLeft_in_use = int(drive['free'])
            imagesave.setStorageLeft(int(drive['free']))
            
   


async def initCameraA():
    global camera_1, abort
    if abort:
        abort = False
    status = "ok"
    try:
        camera_1.init()
       
        
        if not camera_1.isRunning():
            
            camera_1.start_stream()


    except:
        print("initializing of cmera failed")
        status = "failed"
    finally:
        
        await manager.broadcast(json.dumps({"event": "initA", "data": status}))





async def loadConfig():
    global camera_1,camera_2,config_loaded
    status="Konfig vellykket"
    cameraStatus = "config_ok"
    try:
        camera_1.loadConfig()
        camera_2.loadConfig()
       
        
        config_loaded = True
    except:
        print("config failed")
        cameraStatus ="config_failed"
        status = "Konfig feilet"
        config_loaded = False

    finally:

        
        await manager.broadcast(json.dumps({"event": "loadConfig", "data": status}))

 

async def initCameraB():
    global camera_2
    status = "ok"

    try:
        camera_2.init()
        if not camera_2.isRunning():

            camera_2.start_stream()
       

    except:
        print("initializing of camera failed")
        status = "failed"
    finally:
        await manager.broadcast(json.dumps({"event": "initB", "data": status}))
        

async def initCameraC():
    global camera_3
    status = "ok"

    try:
        camera_3.init()
        if not camera_3.isRunning():

            camera_3.start_stream()
       

    except:
        print("initializing of camera failed")
        status = "failed"
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
        

   
        
def gen():
    global camera_1,valider1
    
    while 1:

        if valider1:
            try:
                frame, status = camera_1.get_image()
                if status == cvb.WaitStatus.Ok:
                    frame = np.array(frame)
                    frame = cv2.resize(frame, (640, 480))
                    _, frame = cv2.imencode('.jpg', frame)

                    image = frame.tobytes()

                    yield (b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')
            
            except Exception as e:
                print(e)
        
        else:
            break



    




def gen1():
    global camera_2,valider2

    while 1:

        if valider2:

            try:
                frame, status = camera_2.get_image()
                if status == cvb.WaitStatus.Ok:
                    frame = np.array(frame)
                    frame = cv2.resize(frame, (640, 480))
                    _, frame = cv2.imencode('.jpg', frame)

                    image = frame.tobytes()

                    yield (b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')
            except Exception as e:
                print(e)
        else:
            break

@app.get('/video_feed1')
def video_feed1():
    global valider

    
    return StreamingResponse(gen(), media_type="multipart/x-mixed-replace; boundary=frame")
    
    





    


@app.get('/video_feed2')
def video_feed2():
    global valider
    
    return StreamingResponse(gen1(), media_type="multipart/x-mixed-replace; boundary=frame")
    


def videofeed():
    global camera_1
    
    frame, status = camera_1.get_image()
    if status == cvb.WaitStatus.Ok:

        b64 = cvbImage_b64(frame)

        raw_data = {"event": "snapshot", "data": b64}

        yield raw_data



def merge_CSV_files():
    global tempTrip
    date = getDate()
    absolute_path = os.path.dirname(os.path.abspath(__file__))
    path = absolute_path+"/log/"+date+"/"+tempTrip
    merge(path)



   
    
    
    


def startfps():
    global image_freq

    image_freq = 5




@app.websocket("/stream/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    global started,config_loaded,imagesave,gps,drive_in_use,gpsControl,valider1,valider2,tempTrip
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
                states = getStates()
                

        
            elif(event == "loadConfig"):

                if not config_loaded:
                    # await loadConfig()
                    await initCameraA()
                    await initCameraB()
                   
                
                else:


                    await manager.broadcast(json.dumps({"event": "initB", "data": "config_ok"}))
                    await manager.broadcast(json.dumps({"event": "initA", "data": "config_ok"}))
                    await manager.broadcast(json.dumps({"event": "loadConfig", "data": "ok"}))
                



            elif(event == 'start'):
                tempTrip = str(msg)
                imagesave.setTripName(str(msg))
                gps.setTripName(str(msg))
                drive_in_use = await createImageFolder(msg)
                if drive_in_use =="failed":
                    await manager.broadcast(json.dumps({"event": "error","data":"no drives"}))

                
                imagesave.setDrive(drive_in_use)
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
                await initCameraB()
                #await initCameraC()
                

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
                valider2 =msg
            
            elif(event == "debug"):
                gps.setDebug(msg)

            
            elif(event == "pause"):
                pause()
            
            elif(event =="merge"):
                startfps()
                await initCameraA()
                await initCameraB()
                   
                merge_CSV_files()


                
                

    except WebSocketDisconnect as e:  # WebSocketDisconnect

        print("[WEBSOCKET] websocket disconnect")

        await manager.disconnect(websocket)

        


@app.on_event("startup")
async def startup():
    print("[startup] loading config")
    # await loadConfig()
    


@app.on_event("shutdown")
def shutdown_event():
    global imagesave, closeServer,gps

    print("shutting down server")

    imagesave.raise_exception()
    gps.raise_exception()
    imagesave.join()
    gps.join()
    os.system('sudo kill -9 `sudo lsof -t -i:8000')



def main(arg):
   

    uvicorn.run(app, host="192.168.10.153", port=8000)


if __name__ == "__main__":
  
    main(debug)
    


    #169.254.108.159
    #192.168.0.100