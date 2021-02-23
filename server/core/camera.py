import cvb
import os


class Camera:

    def __init__(self, port=0):
        self.port = port
        self.image = None
        self.device = None
        self.stream = None

    def init(self):
        self.device = cvb.DeviceFactory.open(os.path.join(
            cvb.install_path(), "drivers", "GenICam.vin"), port=self.port)

        self.stream = self.device.stream

    def start_stream(self):

        self.stream.start()

    def get_image(self):

        image, status = self.stream.wait()
        return image, status

    def abortStream(self):
        self.stream.abort()
        self.device = None
        self.stream = None

    def stopStream(self):
        self.stream.stop()

    def getPort(self):
        return self.port

    def terminate(self):
        self.device.close()

    def getSnapShot(self):
        image, status = self.stream.wait()
        return image, status
