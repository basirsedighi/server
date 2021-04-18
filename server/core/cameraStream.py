
import os
from os import path
from threading import Thread
import cvb
import uuid
import datetime
from core.timer import Timer
import time


class CameraStream():
    def __init__(self, camera, queue):

        self.camera = camera
        self.imageQueue = queue
        self.tripId = ""
        self.lastBufferImage = None
        self.bufferImage = None
        self.bufferImage_f = 100
        self.running = True
        self.port = camera.getPort()
        self.image_name = 0
        self.list_of_images = []

    def init(self):
        status = "camera ok"

        try:

            self.camera.init()
        except:
            print("initializing of camera failed")
            status = "camera not ok"
        finally:
            return status

    def startStream(self):
        status = "stream ok"
        try:
            self.camera.start_stream()

        except:
            print("stream failed")
            status = "stream failed"

        finally:
            return status

    def stream(self):
      

        while True:
            if running:
                try:

                    image, status = camera.get_image()

                

                    #getTimeStamp()

                    if status == cvb.WaitStatus.Ok:
                        timeStamp = int(time.time() * 1000)
                        print(image.raw_timestamp)

                        data = {"image": image, "camera": 1, "index": self.image_name,"timeStamp":timeStamp}

                        self.imageQueue.put(data)
                        self.image_name = self.image_name +1
                    
                    elif status == cvb.WaitStatus.Abort :
                        print("stream 2 abort")
                        break

                    elif status == cvb.WaitStatus.Timeout and stopStream2:
                        print("stream 2 timeout")
                        break

                
            
            

            
                except Exception as e:
                    print(e)
                    pass
               

        self.camera.abortStream()
        print("stopped")

        return "stopped"

    def terminate(self):
        self.running = False

    def getBufferImage(self):

        if self.lastBufferImage is not self.bufferImage:
            self.lastBufferImage = self.bufferImage
        return self.bufferImage

    def reset(self):
        self.image_name = 0
