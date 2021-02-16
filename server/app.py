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
camera_stream_1 = None
camera_stream_2 = None


camera = Camera()
camera.start_stream()

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


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(self.active_connections)

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

    while(True):
        msg = []

        for i in range(10):
            line = serial.readline()
            line = pynmea2.parse(
                serial.readline().decode('ascii', errors='replace'))
            msg.append(line)

        return msg


@app.get('/stop')
async def stop():
    print("stanser bildetaking")
    # stopp bildetaking


@app.get('/start')
def start():
    global camera_1, camera_stream_1, camera_2, camera_stream_2

    print("starter bildetaking")

    camera_stream_1 = CameraStream(camera_1)
    cameraStatus = camera_stream_1.init()

    cameraStatus = camera_stream_1.startStream()
    camera_stream_1.setDaemon(True)

    camera_stream_2 = CameraStream(camera_2)
    cameraStatus = camera_stream_2.init()
    cameraStatus = camera_stream_2.startStream()
    camera_stream_2.setDaemon(True)

    if cameraStatus == "stream ok":

        camera_stream_1.start()
        camera_stream_2.start()

        camera_stream_1.join()
        camera_stream_2.join()

        # with app.state.executor as pool:
        #     # wait result

        #     result = pool.map(camera_stream_1.run())
        #     print(result)

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


def startStream1():

    global camera_1, camera_stream_1

    camera_stream_1 = CameraStream(camera_1)
    cameraStatus = camera_stream_1.init()

    cameraStatus = camera_stream_1.startStream()

    if cameraStatus == "stream ok":
        camera_stream_1.run()


async def startStream2():
    global camera_2, camera_stream_2

    camera_stream_2 = CameraStream(camera_2)
    cameraStatus = camera_stream_2.init()
    await manager.broadcast(json.dumps({"event": "cameraStatus2", "data": cameraStatus}))

    cameraStatus = camera_stream_2.startStream()
    await manager.broadcast(json.dumps({"event": "cameraStatus2", "data": cameraStatus}))

    if cameraStatus == "stream ok":

        camera_stream_2.run()


async def stopStream():
    global camera_stream_1, camera_stream_2

    camera_stream_1.terminate()
    camera_stream_2.terminate()


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

    await manager.connect(websocket)
    await websocket.send_text(json.dumps({"connection": "connected"}))

            elif(event == 'start'):
                start = True

                await manager.broadcast(json.dumps({"event": "starting"}))

            elif(event == 'stop'):
                started = False
                await stopStream()

                await manager.broadcast(json.dumps({"event": "stopping"}))

            data = await websocket.receive_text()
            print(data)
            # data = gpsQueue.get_nowait()
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
