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
from threading import Lock
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

from core.helpers.helper_server import cvbImage_b64

# camera = Camera()
# camera.start_stream()
manager = ConnectionManager()
image_freq = 10
app = FastAPI()
image_lock = Lock()
camera_1 = Camera(1)
camera_2 = Camera(0)
valider = False


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

    def disconnect(self, websocket: WebSocket):
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
async def getData():
    return "hallo"


@app.get('discoverDevices')
@app.get('/stop')
async def stop():
    print("stanser bildetaking")
    # stopp bildetaking


@app.get('/start1')
def start():

    global camera_1, camera_stream_1, isRunning1, image_lock
    camera_1.start_stream()

    isRunning1 = True
    while isRunning1:

        image, status = camera_1.get_image()

        if status == cvb.WaitStatus.Ok:
            image = cvb.as_array(image, copy=True)
            frame = cv2.resize(image, (640, 480))
            cv2.imshow("fddsf", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):

                break

        else:
            print(status)

    cv2.destroyAllWindows()

    camera_1.stopStream()

    return "starting"
    # start bildetaking


@app.get('/start2')
def start():

    global camera_2, isRunning2, image_lock

    camera_2.start_stream()
    isRunning2 = True
    while isRunning2:

        image, status = camera_2.get_image()

        if status == cvb.WaitStatus.Ok:
            image = cvb.as_array(image, copy=True)
            frame = cv2.resize(image, (640, 480))

            cv2.imshow("fdsf", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        else:

            print(status)

    # closing all open windows
    cv2.destroyAllWindows()

    camera_2.stopStream()

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
    # 1 bilde 144kB

    bilder_pr_sek = 20
    bilde_size = 0.144  # Mb

    free = storage["free"]
    seconds_left = free/(bilder_pr_sek*bilde_size)

    return seconds_left


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
    global camera_1, camera_2

    camera_1.stopStream()
    camera_2.stopStream()


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


async def validate():
    global camera_1, valider

    frame, status = camera_1.get_image()

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
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            event = data['event']

            if(event == "onConnection"):
                await websocket.send_text(json.dumps({"connection": "connected"}))
            elif(event == 'start'):
                start = True

                await manager.broadcast(json.dumps({"event": "starting"}))

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
                await validate()

        # data = json.dumps(data)
        # print(data)
        # await websocket.send_text(data)

    except (WebSocketDisconnect) as e:

        manager.disconnect(websocket)

        pass


@app.on_event("startup")
async def startup():
    app.state.executor = ProcessPoolExecutor()

    # Prime the push notification generator
    print("startup")


@app.on_event("shutdown")
def shutdown_event():
    print("shutdown")
