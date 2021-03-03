from threading import Thread
import queue
from datetime import datetime
from core.timer import Timer
import os
from os import path
from datetime import datetime
import cvb


class ImageSave(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.tripName = "first"
        self.queue = queue
        self.isRunning = True

    def run(self):
        
        
        date = self.getDate()
        timer = Timer("thread loop")
        try:
            while True:

                if not self.isRunning:
                    break
                if self.queue.empty():
                    pass
                else:

                    data = self.queue.get()

                    image = data['image']
                    camera = data['camera']
                    index = data['index']

                    image.save(
                        "bilder/"+str(date)+"/"+str(self.tripName)+"/kamera"+str(camera)+"/"+str(index)+'.jpeg')
                    try:
                        
                         image.save(
                        "bilder/"+str(date)+"/"+str(self.tripName)+"/kamera"+str(camera)+"/"+str(index)+'.jpeg')
                    
                    except:
                        print("error")
                        pass
                    finally:
                        self.queue.task_done()

                    
        except Exception as e:

            print("[saving thread]:  "+e)
            pass
           

        return "Stopped"

    def stop(self):

        self.isRunning = False
    

    def getDate(self):

        return datetime.today().strftime('%Y-%m-%d')
    

    def createFolder(self):
        date = self.getDate()

            #   Making a folder for the images
        if not path.exists('bilder/'+date):

            os.mkdir('bilder/'+date) 
    
    def setTripName(self,name):

        self.tripName = name
