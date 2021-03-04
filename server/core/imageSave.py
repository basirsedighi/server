from threading import Thread
import queue
from datetime import datetime
from core.timer import Timer
import os
from os import path
from datetime import datetime
import cvb
import ctypes


class ImageSave(Thread):
    def __init__(self, queue,name):
        Thread.__init__(self)
        self.tripName = "first"
        self.queue = queue
        self.isRunning = True
        self.name = name 

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

                    # image.save(
                    #     "bilder/"+str(date)+"/"+str(self.tripName)+"/kamera"+str(camera)+"/"+str(index)+'.jpeg')
                    try:
                        
                         image.save(
                        "bilder/"+str(date)+"/"+str(self.tripName)+"/kamera"+str(camera)+"/"+str(index)+'.bmp')
                    
                    except Exception:
                        
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


    
    def raise_exception(self):
        thread_id = self.get_id() 
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 
              ctypes.py_object(SystemExit)) 
        if res > 1: 
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0) 
            print('Exception raise failure') 
    

    def get_id(self): 

        # returns id of the respective thread 
        if hasattr(self, '_thread_id'): 
            return self._thread_id 
        for id, thread in threading._active.items(): 
            if thread is self: 
                return id