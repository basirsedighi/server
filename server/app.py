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
from time import time
from fastapi.middleware.cors import CORSMiddleware
from manager import ConnectionManager
from io import BytesIO
from core.timer import Timer
from core.imageSave import ImageSave
import queue
from gps import Gps


from core.helpers.helper_server import cvbImage_b64


# camera = Camera()
# camera.start_stream()
manager = ConnectionManager()
image_freq = 10
app = FastAPI()
image_lock = Lock()
camera_1 = Camera(1)
camera_2 = Camera(0)
cameraStream_1 = CameraStream(camera_1, Lock)
cameraStream_2 = CameraStream(camera_2, Lock)
imageQueue = queue.Queue()
imagesave = ImageSave(imageQueue)
imagesave.daemon = True
imagesave.start()
valider = False
g = Gps('C:/Users/norby/Desktop')


isRunning1 = True
isRunning2 = True


image_lock = Lock()

gps_connect = 0
started = False


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


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        await websocket.close()
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.get("/")
async def root():
    return {"message": "Hello World"}

# {"status":1,}


@app.get('/gps')
def getData():
    global g

    if g.connected:

        g.checkGps()

        return {"status": g.status, "velocity": g.velocity}


@app.get('discoverDevices')
@app.get('/stop')
async def stop():
    print("stanser bildetaking")
    # stopp bildetaking


@app.get('/start1')
def start():

    global camera_1, isRunning1, image_lock, imageQueue
    i = 0
    timer = Timer("stream1")
    isRunning1 = True
    while isRunning1:
        timer.start()

        image, status = camera_1.get_image()

        if status == cvb.WaitStatus.Ok:
            # image = cvb.as_array(image, copy=False)
            # frame = cv2.resize(image, (640, 480))
            imageQueue.put(image)
            timer.stop()

        else:
            print(status)

        i = i+1

    camera_1.stopStream()

    return "stopped"
    # start bildetaking


@app.get('/start2')
def start():

    global camera_2, isRunning2, image_lock, imageQueue
    timer = Timer("stream2")
    isRunning2 = True
    i = 0
    while isRunning2:
        timer.start()

        image, status = camera_2.get_image()

        if status == cvb.WaitStatus.Ok:

            imageQueue.put(image)

            # image = cvb.as_array(image, copy=False)
            # frame = cv2.resize(image, (640, 480))

            timer.stop()
        # else:

        #     print(status)

        i = i+1

    # closing all open windows

    camera_2.stopStream()

    return "stopped"
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
    path = "C:/Users/norby/Pictures/test"

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

    timeleft = estimateStorageTime(storage)
    payload = {}
    payload['timeleft'] = timeleft
    payload['storage'] = storage

    return payload

# estimate how


def estimateStorageTime(storage):
    # 20 bilder/sek
    # 1 bilde 144kB

    bilder_pr_sek = 20
    bilde_size = 0.144  # Mb

    free = storage["free"]
    seconds_left = free/(bilder_pr_sek*bilde_size)
    minleft = math.floor(seconds_left/60)
    hoursLeft = int(minleft/60)
    minleft = minleft % 60

    return {"h": hoursLeft, "m": minleft}


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


async def stopStream():
    global isRunning1, isRunning2
    print("stopping stream")

    isRunning1 = False
    isRunning2 = False


async def initCameraA():
    global camera_1
    status = "ok"
    try:
        camera_1.init()

    except:
        print("initializing of camera failed")
        status = "failed"
    finally:
        await manager.broadcast(json.dumps({"event": "initA", "data": status}))


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


async def startStreamA():
    global camera_1
    status = "started"
    try:
        camera_1.start_stream()

    except:
        print("initializing of camera failed")
        status = "failed"
    finally:
        await manager.broadcast(json.dumps({"event": "streamA", "data": status}))


async def startStreamB():
    global camera_2
    status = "started"
    try:
        camera_2.start_stream()

    except:
        print("stream failed")
        status = "failed"
    finally:
        await manager.broadcast(json.dumps({"event": "streamB", "data": status}))


async def discoverCameras():

    discover = cvb.DeviceFactory.discover_from_root()
    mock_info = next(
        (info for info in discover if "GenICam.vin" in info.access_token), None)
    if mock_info is None:

        raise RuntimeError("unable to find CVMock.vin")

    print(mock_info.access_token)


async def validate(cam):
    global camera_1, camera_2, valider

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


@app.get('/video_feed1')
def video_feed():
    return StreamingResponse(gen(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.get('/video_feed2')
def video_feed():
    return StreamingResponse(gen(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.websocket("/stream/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    global started
    await manager.connect(websocket)
    await manager.broadcast(json.dumps({"event": "connected"}))
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            event = data['event']
            msg = data['data']

            if(event == "onConnection"):
                await websocket.send_text(json.dumps({"connection": "connected"}))
            elif(event == 'start'):
                start = True

            elif(event == 'stop'):
                started = False
                await stopStream()

                await manager.broadcast(json.dumps({"event": "stopping"}))

            elif(event == "init"):
                await initCameraA()
                await initCameraB()

            elif(event == "stream"):
                await startStreamA()
                await startStreamB()
            elif(event == "validation"):
                await validate(msg)

            elif(event == "start_acquisition"):
                status = start_acquisition()
                await manager.broadcast(json.dumps({"event": "started"}))

    except Exception as e:  # WebSocketDisconnect
        print(e)
        await manager.disconnect(websocket)

        pass


@app.on_event("startup")
async def startup():
    app.state.executor = ProcessPoolExecutor()

    # Prime the push notification generator
    print("startup")


@app.on_event("shutdown")
def shutdown_event():
    global imagesave
    imagesave.stop()
    imagesave.join()
    print("shutdown")
