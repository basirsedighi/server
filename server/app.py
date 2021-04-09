import numpy as np
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
# camera = Camera()
# camera.start_stream()
manager = ConnectionManager()
image_freq = 20
gps_freq =0
storage = {}
app = FastAPI()
image_lock = Lock()
camera_1 = Camera(0)
camera_2 = Camera(1)
camera_3 = Camera(4)
gps = gpsHandler()
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
    "http://10.22.182.47:4200",
    "http://10.22.182.47"

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
 

    image_freq = freq





@app.get('/start1')
def startA():

    global camera_1, isRunning1, image_lock, imageQueue, abort,isRunning
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

                elif status == cvb.WaitStatus.Timeout and isRunning1:
                    print("stream 1 timeout")
                    break

                    
                
                
                
                

            except Exception as e :

                print(e)
                pass

    isRunning1=False        
    print("stream 1 stopped: "+str(index))
    camera_1.stopStream()

    return "stream 1 has stopped"
    




@app.get('/start2')
def startB():

    global camera_2, isRunning2, image_lock, imageQueue, abort
    

    
   
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

                elif status == cvb.WaitStatus.Timeout and isRunning2:
                    print("stream 2 timeout")
                    break

                    
                
                

                
            except Exception as e:
                print(e)
                pass

          

    isRunning2=False
    camera_2.stopStream()
    print("stream 2 stopped: "+str(index))

    

    return "stream2 has stopped"
    # start bildetaking

@app.get('/start3')
def startC():

    global camera_3, isRunning3, image_lock, imageQueue, abort
    

    
   
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

                elif status == cvb.WaitStatus.Timeout and isRunning2:
                    print("stream 3 timeout")
                    break

                    
                
                

                
            except Exception as e:
                print(e)
                pass

          

    isRunning3=False
    camera_3.stopStream()
    print("stream 3 stopped: "+str(index))

    

    return "stream2 has stopped"
    # start bildetaking


async def abortStream():
    global camera_1,camera_2, abort,gps,start_Puls,image_freq
    print("stopping stream")
    #toggleGPSControl()
    image_freq = 0

   


    
   
    
    gps.toggleLogging()


async def start_acquisition():
    global isRunning1, isRunning2,camera_1,camera_2,gps,isRunning,abort,image_freq
    print("Starting stream")
    #toggleGPSControl()
    abort=False
    image_freq = 0
    
    
    gps.toggleLogging()
    
    
   
    
def startPulse():
    global image_freq,isRunning1,isRunning2,isRunning3
    

    isRunning1 = True
    isRunning2 = True
    isRunning3 = True

    image_freq = 20



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
    global storage,imagesave

    storages =checkStorageAllDrives()
    
    storageLeft(storages)

    
    payload = estimateStorageTime(storages,10)

    total = payload['total']['free']
    if int(total)<10:
        await abortStream()
        
    

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
        await initCameraA()
        await initCameraB()
        
        config_loaded = True
    except:
        print("config failed")
        cameraStatus ="config_failed"
        status = "Konfig feilet"
        config_loaded = False

    finally:

        await manager.broadcast(json.dumps({"event": "initB", "data": cameraStatus}))
        await manager.broadcast(json.dumps({"event": "initA", "data": cameraStatus}))
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
        

    finally:
      await manager.broadcast(json.dumps({"event":"validerfailed","data":"feeeels"}))
        
        
def gen():
    global camera_1,valider1
    
    while 1:
        try:
            frame, status = camera_1.get_image()
            if status == cvb.WaitStatus.Ok:
                print("generator1")
                frame = np.array(frame)
                frame = cv2.resize(frame, (640, 480))
                _, frame = cv2.imencode('.jpg', frame)

                image = frame.tobytes()

                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')
        
        except Exception as e:
            print(e)



    




def gen1():
    global camera_2,valider2

    while 1:

        try:
            frame, status = camera_2.get_image()
            if status == cvb.WaitStatus.Ok:
                print("generator2")
                frame = np.array(frame)
                frame = cv2.resize(frame, (640, 480))
                _, frame = cv2.imencode('.jpg', frame)

                image = frame.tobytes()

                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')
        except Exception as e:
            print(e)

@app.get('/video_feed1')
async def video_feed1():
    global valider

    
    return StreamingResponse(gen(), media_type="multipart/x-mixed-replace; boundary=frame")
    
    





    


@app.get('/video_feed2')
async def video_feed2():
    global valider
    
    return StreamingResponse(gen1(), media_type="multipart/x-mixed-replace; boundary=frame")
    
   
@app.get('/live')
def live():
    global camera_1
    frame, status = camera_1.get_image()
    if status == cvb.WaitStatus.Ok:

        b64 = cvbImage_b64(frame)

        raw_data = {"event": "snapshot", "data": b64}

        

        return raw_data



@app.websocket("/stream/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    global started,config_loaded,imagesave,gps,drive_in_use,gpsControl,valider1,valider2
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

                if not config_loaded:
                    await loadConfig()
                
                else:


                    await manager.broadcast(json.dumps({"event": "initB", "data": "config_ok"}))
                    await manager.broadcast(json.dumps({"event": "initA", "data": "config_ok"}))
                    await manager.broadcast(json.dumps({"event": "loadConfig", "data": "ok"}))
                



            elif(event == 'start'):
                imagesave.setTripName(str(msg))
                gps.setTripName(str(msg))
                drive_in_use = await createImageFolder(msg)
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
                
                

    except WebSocketDisconnect as e:  # WebSocketDisconnect

        print("[WEBSOCKET] websocket disconnect")

        await manager.disconnect(websocket)

        


@app.on_event("startup")
async def startup():

    # Prime the push notification generator
    print("startup")


@app.on_event("shutdown")
def shutdown_event():
    global imagesave, closeServer

    imagesave.raise_exception()
    imagesave.join()
    gps.join()



if __name__ == "__main__":
    uvicorn.run(app, host="192.168.10.152", port=8000)


    #169.254.108.159
    #192.168.0.100