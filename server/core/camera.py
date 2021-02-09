import cvb
import os


class Camera:

    def __init__(self, port=1):
        self.port = port
        self.image = None
        self.device = cvb.DeviceFactory.open(os.path.join(
            cvb.install_path(), "drivers", "CVMock.vin"), port=self.port)
        self.stream = None

    def start_stream(self):
        self.stream = self.device.stream
        self.stream.start()

    def get_image(self):
        image, status = self.stream.wait()
        return image, status
