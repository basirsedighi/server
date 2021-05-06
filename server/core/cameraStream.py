
import os
from os import path
from threading import Thread
import cvb
import uuid
import datetime
from core.timer import Timer
import time


class CameraStream(Thread):
    def __init__(self, camera, queue,name,capturing):
        Thread.__init__(self)
        self.daemon =True
        self.camera = camera
        self.imageQueue = queue
        self.name=name
        self.tripId = ""
        self.lastBufferImage = None
        self.bufferImage = None
        self.bufferImage_f = 100
        self.capturing = capturing
        self.port = camera.getPort()
        self.image_name = 0
        self.list_of_images = []
        self.isInit = False
        self.streamStopped=False

    def init(self):
        

        

        self.camera.init()
        

    def start_stream(self):
        
        
        self.camera.start_stream()

       
    


    def startCapturing(self):
        self.capturing =True
    

    def stopCapturing(self):
        self.capturing =False
    

    def resetIndex(self):
        self.image_name =0
    
    def setInit(self):
        self.isInit = True
    
    def stopstream(self):
        self.streamStopped = True

    def run(self):
        global capturing


        while True:
            if  self.isInit:
                break
      
        
        while True:
            
            
            try:

                image, status = self.camera.get_image()

            

                

                if status == cvb.WaitStatus.Ok:

                    cameraStamp = int(image.raw_timestamp/1000)
                    timeStamp = int(time.time() * 1000)

                    
                    if self.capturing:
                        if self.image_name >0 :
                            newstamp =  starttime+ (cameraStamp-firstCameraStamp)

                            data = {"image": image, "camera":self.name, "index": self.image_name,"timeStamp":timeStamp,"cameraStamp":newstamp}

                            self.imageQueue.put(data)
                            self.image_name = self.image_name +1
                            print(self.image_name)
                        
                        if self.image_name ==0:
                            print("reset")   
                            starttime = timeStamp
                            firstCameraStamp = cameraStamp
                            self.image_name = self.image_name +1
                    
                    

                
                
                elif status == cvb.WaitStatus.Abort :
                    print("stream 2 abort")
                    
                    

               
                    
                elif status == cvb.WaitStatus.Timeout and self.streamStopped:
                    print("stopped")
                    print(self.image_name)
            
        
        

        
            except Exception as e:
                print(e)
                pass
            

        self.camera.stopStream()
        

    def stop(self):
        self.running = False

    def getBufferImage(self):

        if self.lastBufferImage is not self.bufferImage:
            self.lastBufferImage = self.bufferImage
        return self.bufferImage

    def reset(self):
        self.image_name = 0


    def getDevice(self):
       return self.camera.getDevice()
    
    def isRunning(self):
        return self.camera.isRunning()