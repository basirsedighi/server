import cvb
import os


class Camera:

    def __init__(self, port=0):
        self.port = port
        self.image = None
        self.device = None
        self.stream = None
        self.config_path ="core/config/conf.gcs"
        self.tempimg = None
        


    def loadConfig(self):
        

        self.device = cvb.DeviceFactory.open(os.path.join(
            cvb.install_path(), "drivers", "GenICam.vin"), port=self.port)


        self.device_node_map = self.device.node_maps["Device"]
        self.device_node_map.load_settings(file_name=self.config_path)



    def init(self):

        try:
            self.device = cvb.DeviceFactory.open(os.path.join(
                cvb.install_path(), "drivers", "GenICam.vin"), port=self.port)


            # self.device_node_map = self.device.node_maps["Device"]
            # self.device_node_map.load_settings(file_name=self.config_path)

            self.stream = self.device.stream
            self.stream.start()
        
        except Exception as e:
            print(e)
    

    def init2(self,device):

        try:
           
            self.device = device
            test =self.device.read_property(cvb.DiscoveryProperties.UsbPortPath )

            print(test)
       

            self.stream = self.device.stream
            self.stream.start()
    
        except Exception as e:

            print(e)

            

    def start_stream(self):

        self.stream.start()

    def get_image(self):

        image, status = self.stream.wait_for(8000)
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
        image, status = self.stream.get_snapshot()
        return image, status

    def isRunning(self):
        return self.stream.is_running