# coding: utf-8


import logging
import time
from enum import Enum
from typing import Any, Dict, List, Optional

from fastapi import Body, FastAPI, HTTPException
from pydantic import BaseModel
from starlette.endpoints import WebSocketEndpoint
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import FileResponse
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.websockets import WebSocket


app = FastAPI()  # pylint: disable=invalid-name
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_headers=["*"], allow_methods=["*"]
)
app.debug = True

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print('connected')
    while True:

        data = await websocket.receive_text()
        print(data)
        await websocket.send_text(f"Message text was: {data}")
