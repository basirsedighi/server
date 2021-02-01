from typing import List

from fastapi import FastAPI
from starlette.responses import HTMLResponse
from starlette.websockets import WebSocket, WebSocketDisconnect
import json
import queue
from core.gps import Gps
import time
app = FastAPI()

gpsQueue = queue.Queue()

# gps = Gps(gpsQueue)
# gps.start()


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


@app.get('/data/')
async def getData():
    return "datas"


@app.get('/storage/')
async def getData():
    return "datas"


def start():
    # start kamera thread


@app.websocket("/ws/{socket}")
async def websocket_endpoint(websocket: WebSocket, socket: str):
    global gpsQueue

    await manager.connect(websocket)

    try:

        while True:
            try:

                data = await websocket.receive_text()
                #data = gpsQueue.get_nowait()
                #data = json.dumps(data)
                # print(data)
                # await websocket.send_text(data)

            except queue.Empty as e:

                pass
            finally:

                manager.disconnect(websocket)

    except (WebSocketDisconnect) as e:

        pass


@app.on_event("startup")
async def startup():

    # Prime the push notification generator
    print("startup")


@app.on_event("shutdown")
def shutdown_event():
    print("shutdown")
