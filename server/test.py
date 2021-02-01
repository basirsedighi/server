#!/usr/bin/env python3
import threading
import asyncio
import websockets
import time
import signal
import sys
sys.path.append('.')


stopFlag = False


class GPSWorker (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.data = 0
        self.lastData = 0
        self.inc = 0

    # Simulate GPS data
    def run(self):
        while not stopFlag:
            self.data = self.inc
            self.inc += 1
            time.sleep(1)

    def get(self):
        if self.lastData is not self.data:
            self.lastData = self.data
            return self.data


class IMUWorker (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.data = 0
        self.lastData = 0
        self.inc = 0

    # Simulate IMU data
    def run(self):
        while not stopFlag:
            self.data = self.inc
            self.inc += 1
            time.sleep(0.04)

    def get(self):
        if self.lastData is not self.data:
            self.lastData = self.data
            return self.data


class MSGWorker (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.connected = set()

    def run(self):
        while not stopFlag:
            data = gpsWorker.get()
            if data:
                self.sendData('{"GPS": "%s"}' % data)

            data = imuWorker.get()
            if data:
                self.sendData('{"IMU": "%s"}' % data)

            time.sleep(0.04)

    async def handler(self, websocket, path):
        self.connected.add(websocket)
        try:
            await websocket.recv()
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.connected.remove(websocket)

    def sendData(self, data):
        for websocket in self.connected.copy():
            print("Sending data: %s" % data)
            coro = websocket.send(data)
            future = asyncio.run_coroutine_threadsafe(coro, loop)


if __name__ == "__main__":
    print('aeroPi server')
    gpsWorker = GPSWorker()
    imuWorker = IMUWorker()
    msgWorker = MSGWorker()

    try:
        gpsWorker.start()
        imuWorker.start()
        msgWorker.start()

        ws_server = websockets.serve(msgWorker.handler, '0.0.0.0', 8000)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(ws_server)
        loop.run_forever()
    except KeyboardInterrupt:
        stopFlag = True
        print("Exiting program...")
