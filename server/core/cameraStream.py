
from threading import Thread
import cvb
import uuid


class CameraStream(Thread):
    def __init__(self, camera):
        Thread.__init__(self)
        self.camera = camera
        self.tripId = uuid.uuid4()
        self.lastBufferImage = None
        self.bufferImage = None
        self.bufferImage_f = 100
        self.running = True

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

    def run(self):
        i = 0
        # Generer ny mappe for lagring
        path = "storage/{tripId}"
        while self.running:
            try:

                # get image from camera stream
                image, status = self.camera.get_image()

                # check if status is ok
                if status == cvb.WaitStatus.Ok:

                    # skriv metadata
                    # Lagre bilde

                    # lagre bufferimage for sjekk av operatør
                    if self.bufferImage_f == 100:
                        self.bufferImage = image
                        i = 0

                    i = i+1

                else:
                    raise RuntimeError("timeout during wait"
                                       if status == cvb.WaitStatus.Timeout else"aquisistion aborted")
            except:
                pass

            finally:
                self.camera.abortStream()

    def terminate(self):
        self.running = False

    def getBufferImage(self):

        if self.lastBufferImage is not self.bufferImage:
            self.lastBufferImage = self.bufferImage
        return self.bufferImage
