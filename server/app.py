import numpy as np
from typing import List
import cv2
from fastapi import FastAPI
from starlette.responses import HTMLResponse, StreamingResponse
from starlette.websockets import WebSocket, WebSocketDisconnect
import json
import serial
import queue
from core.gps import Gps
from core.camera import Camera
import time
import pynmea2
import cvb
from time import time
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()


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
    print("starter bildetaking")
    # stopp bildetaking


@app.get('/start')
async def start():
    print("stanser bildetaking")
    # start bildetaking


@app.get('/storage/')
async def getData():
    return "datas"


def gen():
    while True:
        frame, status = camera.get_image()
        if status == cvb.WaitStatus.Ok:
            frame = np.array(frame)
            _, frame = cv2.imencode('.jpg', frame)

            image = frame.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')


@app.get('/video_feed')
def video_feed():
    return StreamingResponse(gen(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.websocket("/ws/{socket}")
async def websocket_endpoint(websocket: WebSocket, socket: str):
    global gpsQueue

    await manager.connect(websocket)
    await websocket.send_text(json.dumps({"connection": "connected"}))

    try:

        while True:

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

    # Prime the push notification generator
    print("startup")


@app.on_event("shutdown")
def shutdown_event():
    print("shutdown")
