from typing import List

from fastapi import FastAPI
from starlette.responses import HTMLResponse
from starlette.websockets import WebSocket, WebSocketDisconnect

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


@app.on_event("startup")
async def startup():
    # Prime the push notification generator
    await notifier.generator.asend(None)


@app.on_event("shutdown")
def shutdown_event():
    print("shutdown")
