
import os
from os import path
from threading import Thread
import cvb
import uuid
import datetime
from core.timer import Timer
import time


class CameraStream():
    def __init__(self, camera, lock):

        self.camera = camera
        self.lock = lock
        self.tripId = uuid.uuid4()
        self.lastBufferImage = None
        self.bufferImage = None
        self.bufferImage_f = 100
        self.running = True
        self.port = camera.getPort()
        self.baseUrl = "C:/Users/norby/Pictures/test/"
        self.date = "02.08.1993"
        self.image_name = 1
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
        i = 0
        self.running = True
        # self.folderConstructor()
        timer = Timer()
        # Generer ny mappe for lagring
        path = "storage/{tripId}"

        while self.running:
            try:

                # get image from camera stream
                self.lock.acquire()
                image, status = self.camera.get_image()
                self.lock.release()
                # time.sleep(0.5)

                # check if status is ok
                if status == cvb.WaitStatus.Ok:

                    # # skriv metadata
                    # # Lagre bilde
                    image.save(self.baseUrl + self.date + '/'+'kamera'+str(self.port) +
                               str(self.image_name)+'.jpg')

                    self.image_name += 1

                    # lagre bufferimage for sjekk av operatør
                    if self.bufferImage_f == 100:
                        self.bufferImage = image
                        i = 0

                    i = i+1

                else:
                    print("failed")
            except RuntimeError as e:
                self.running = False
                print(e)

        self.camera.abortStream()
        print("stopped")

        return "stopped"

    def terminate(self):
        self.running = False

    def getBufferImage(self):

        if self.lastBufferImage is not self.bufferImage:
            self.lastBufferImage = self.bufferImage
        return self.bufferImage

    def folderConstructor(self):
        #   Making a folder for the images
        if not (path.exists(self.baseUrl + self.date)):
            # setting up folder for pictures
            os.mkdir(self.baseUrl+self.date)
        else:
            # List all files in a directory using os.listdir
            basepath = self.baseUrl+self.date
            for entry in os.listdir(basepath):
                if os.path.isfile(os.path.join(basepath, entry)):
                    self.list_of_images.append(entry)
            self.image_name = len(self.list_of_images) + 1
