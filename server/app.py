import numpy as np
from typing import List
import cv2
from fastapi import FastAPI
from starlette.responses import HTMLResponse, StreamingResponse
from starlette.websockets import WebSocket, WebSocketDisconnect
from starlette.concurrency import run_until_first_complete
from starlette.routing import WebSocketRoute
from core.cameraStream import CameraStream

import shutil
import json
import serial
import queue
from core.gps import Gps
from core.camera import Camera
import time
import pynmea2
import math
import cvb
from core.models import models
from time import time
from fastapi.middleware.cors import CORSMiddleware
from manager import ConnectionManager

# camera = Camera()
# camera.start_stream()
manager = ConnectionManager()
image_freq = 10
app = FastAPI()
camera_1 = Camera(0)
camera_2 = Camera(1)

gps_connect = 0
started = False


# gps = Gps(gpsQueue)
# gps.start()
serial = serial.Serial('COM8', 9600, timeout=0)


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:4200"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get('gpsStatus')
async def gpsStatus():
    global gps_connect

    return gps_connect

# {"status":1,}


@app.get('/gps')
async def getData():

    while(True):
        try:

            for i in range(10):
                line = serial.readline()

            line = pynmea2.parse(
                serial.readline().decode('ascii', errors='replace'))

            msg = line

            return msg
        except pynmea2.nmea.ParseError as e:
            print(e)


@app.get('/stop')
async def stop():
    print("starter bildetaking")
    # stopp bildetaking


@app.get('/start')
async def start():
    print("stanser bildetaking")

    return "starting"
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
    path = "C:/Users/norby"

    # Get the disk usage statistics
    # about the given path
    stat = shutil.disk_usage(path)

    a, b, c = stat

    # byte to  Gigabyte
    total = math.floor(a*(10 ** -6))
    used = math.floor(b *
                      (10 ** -6))

    free = math.floor(c*(10 ** -6))

    storage = {"total": total, "used": used, "free": free}

    estimateStorageTime(storage)
    return storage

# estimate how


def estimateStorageTime(storage):
    # 20 bilder/sek
    # 1 bilde 5Mb

    bilder_pr_sek = 20
    bilde_size = 5  # mb

    free = storage["free"]
    seconds_left = free/(bilder_pr_sek*bilde_size)


def gen():
    global camera
    while True:
        frame, status = camera.get_image()
        if status == cvb.WaitStatus.Ok:
            frame = np.array(frame)
            frame = cv2.resize(frame, (640, 480))
            _, frame = cv2.imencode('.jpg', frame)

            image = frame.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')


async def startStream():
    global camera_1, camera_2

    camera_stream = CameraStream(camera_1)
    cameraStatus = camera_stream.init()
    await manager.broadcast(json.dumps({"event": "cameraStatus", "data": cameraStatus}))

    cameraStatus = camera_stream.startStream()
    await manager.broadcast(json.dumps({"event": "cameraStatus", "data": cameraStatus}))


@app.get('/video_feed')
def video_feed():
    return StreamingResponse(gen(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.get('/video_feed2')
def video_feed():
    return StreamingResponse(gen(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.websocket("/stream/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    global started
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            event = data['event']

            if(event == 'onConnection'):
                await manager.broadcast(json.dumps({"event": "connected"}))
                if(started):
                    await manager.broadcast(json.dumps({"event": "starting"}))

            elif(event == 'start'):
                started = True

                await manager.broadcast(json.dumps({"event": "starting"}))
                await startStream()

            elif(event == 'stop'):
                started = False
                await manager.broadcast(json.dumps({"event": "stopping"}))

            # data = json.dumps(data)
            # await websocket.send_text(data)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(json.dumps({"event": "disconnect{client_id}"}))


@app.on_event("startup")
async def startup():

    print("startup")


@app.on_event("shutdown")
def shutdown_event():
    print("shutdown")
