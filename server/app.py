import numpy as np
from typing import List
import cv2
from fastapi import FastAPI
from starlette.responses import HTMLResponse, StreamingResponse
from starlette.websockets import WebSocket, WebSocketDisconnect
from starlette.concurrency import run_until_first_complete
from starlette.routing import WebSocketRoute


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
from manager import ConnectionManager


manager = ConnectionManager()
app = FastAPI()

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


@app.websocket("/stream/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    global started
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            event = data['event']
            print(event)

            if(event == 'onConnection'):
                await manager.broadcast(json.dumps({"event": "connected"}))
                if(started):
                    await manager.broadcast(json.dumps({"event": "starting"}))

            elif(event == 'start'):
                started = True
                await manager.broadcast(json.dumps({"event": "starting"}))

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
