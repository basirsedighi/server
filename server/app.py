import numpy as np
from typing import List
import cv2
from fastapi import FastAPI
from starlette.responses import HTMLResponse, StreamingResponse
from starlette.websockets import WebSocket, WebSocketDisconnect
from starlette.concurrency import run_until_first_complete
from starlette.routing import WebSocketRoute
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
from core.models.models import GpsData 
# camera = Camera()
# camera.start_stream()
manager = ConnectionManager()
image_freq = 10
app = FastAPI()
image_lock = Lock()
camera_1 = Camera(1)
camera_2 = Camera(0)
gps = gpsHandler()
imageQueue = queue.Queue()
imagesave = ImageSave(imageQueue,"saving thread")
config_loaded = False

#g = Gps('C:/Users/norby/Desktop')

imagesave.daemon = True
imagesave.start()
gpsData ={}
gps.daemon = True
gps.start()
gps_status = {}
valider = False
abort = False
logging = False
closeServer = False
isRunning1 = False
isRunning2 = False

#manage socket connections
manager = ConnectionManager()

#creates new folder for saving imaging
createFolder()


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












@app.get('/gps')
async def getData():
    global gps_status,gps


    data = gps.getData()
    print(data)
    return data



@app.post('/gpsPost')
async def getData(test:GpsData):
    global gps_status,logging

    gps_status = test

    #print(gps_status)
    if(logging):

        

        print("logging")

    
    return test


@app.post('/gpserror')
async def data(test):

    return test

@app.get('/RaspFPS')
async def fps():


    return 1



@app.get('/start1')
def startA():

    global camera_1, isRunning1, image_lock, imageQueue, abort
    i = 0
    
    #camera_1.start_stream()
    while isRunning1:

        if abort:
            break

        if isRunning1:

            image, status = camera_1.get_image()

            timeStamp = getTimeStamp()

            if status == cvb.WaitStatus.Ok:
                data = {"image": image, "camera": 1, "index": i,"timeStamp":timeStamp}
                imageQueue.put(data)

            i = i+1

    camera_1.stopStream()

    return "stream 1 has stopped"
    




@app.get('/start2')
def startB():

    global camera_2, isRunning2, image_lock, imageQueue, abort
    

    
    i = 0

    #camera_2.start_stream()
    while isRunning2:
        if abort:
            break

        

        if isRunning2:

            

            image, status = camera_2.get_image()

            timeStamp = getTimeStamp()

            if status == cvb.WaitStatus.Ok:

                data = {"image": image, "camera": 2, "index": i,"timeStamp":timeStamp}

                imageQueue.put(data)

            i = i+1

    # closing all open windows

    camera_2.stopStream()

    return "stream2 has stopped"
    # start bildetaking






@app.get('imagefreq')
async def getfreq():
    global image_freq
    return image_freq
# change imagefreq from Gui


@app.post('/changeimagefreq/')
async def change_image_freq(freq: models.freq):
    global image_freq

    image_freq = freq.freq

    return image_freq


@app.get('/storage')
async def getStorage():

    # Path
    

    # Get the disk usage statistics
    # about the given path
    stat = shutil.disk_usage("/")

    a, b, c = stat

    # byte to  Gigabyte
    total = math.floor(a*(10 ** -6))
    used = math.floor(b *
                      (10 ** -6))

    free = math.floor(c*(10 ** -6))

    storage = {"total": total, "used": used, "free": free}

    timeleft = estimateStorageTime(storage)
    payload = {}
    payload['timeleft'] = timeleft
    payload['storage'] = storage

    return payload

# estimate hows






def gen():
    global camera_1, valider
    if valider:
        frame, status = camera_1.get_image()
        if status == cvb.WaitStatus.Ok:
            frame = np.array(frame)
            frame = cv2.resize(frame, (640, 480))
            _, frame = cv2.imencode('.jpg', frame)

            image = frame.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')


async def abortStream():
    global isRunning1, isRunning2, abort,gps
    print("stopping stream")
    abort = not abort

    isRunning1 = not isRunning1
    isRunning2 = not isRunning2
    gps.toggleLogging()



async def start_acquisition():
    global isRunning1, isRunning2,camera_1,camera_2,gps
    print("Starting stream")

    gps.toggleLogging()

    camera_1.start_stream()
    camera_2.start_stream()

    isRunning1 = not isRunning1
    isRunning2 = not isRunning2


async def initCameraA():
    global camera_1, abort
    if abort:
        abort = False
    status = "ok"
    try:
        camera_1.init()

    except:
        print("initializing of camera failed")
        status = "failed"
    finally:
        await manager.broadcast(json.dumps({"event": "initA", "data": status}))


async def loadConfig():
    global camera_1,camera_2,config_loaded
    status="Konfig vellykket"
    try:
        camera_1.loadConfig()
        camera_2.loadConfig()
        
        config_loaded = True
    except:
        print("config failed")
        status = "Konfig feilet"
        config_loaded = False

    finally:

        
        
        await manager.broadcast(json.dumps({"event": "loadConfig", "data": status}))

 

async def initCameraB():
    global camera_2
    status = "ok"
    try:
        camera_2.init()

    except:
        print("initializing of camera failed")
        status = "failed"
    finally:
        await manager.broadcast(json.dumps({"event": "initB", "data": status}))











async def validate(cam):
    global camera_1, camera_2, valider

    camera = None
    if cam == 'A':
        camera = camera_1

    else:
        camera = camera_2

    frame, status = camera.getSnapShot()
    if status == cvb.WaitStatus.Ok:

        b64 = cvbImage_b64(frame)

        raw_data = {"event": "snapshot", "data": b64}

        data = json.dumps(raw_data)

        await manager.broadcast(data)


@app.get('/video_feed1')
def video_feed():
    return StreamingResponse(gen(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.get('/video_feed2')
def video_feed():
    return StreamingResponse(gen(), media_type="multipart/x-mixed-replace; boundary=frame")



@app.websocket("/stream/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    global started,config_loaded,imagesave,gps
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

                    await manager.broadcast(json.dumps({"event": "loadConfig", "data": "ok"}))
                



            elif(event == 'start'):
                imagesave.setTripName(str(msg))
                gps.setTripName(str(msg))
                await createImageFolder(msg)
                await manager.broadcast(json.dumps({"event": "starting"}))
                await start_acquisition()
                
                

                

            elif(event == 'stop'):
                started = False
                await abortStream()

                await manager.broadcast(json.dumps({"event": "stopping"}))

            elif(event == "init"):
                await initCameraA()
                await initCameraB()

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
