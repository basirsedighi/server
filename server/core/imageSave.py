from threading import Thread
import queue
from datetime import datetime
from core.timer import Timer
import os
from multiprocessing import Process
from os import path
from datetime import datetime
import cvb
import ctypes
import csv
import json
from core.helpers.helper_server import most_free_space
import cv2
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

def SaveImagesListToFolder(List):
        print(List[0])
        cv2.imwrite(List[0],List[1])

class ImageSave(Process):
    def __init__(self, imageQueue,name):
        Process.__init__(self)
        self.args = imageQueue
        self.daemon = True
        self.tripName = "BASIR4"
        print(self.args)
        self.isRunning = False
        self.name = name
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.path = self.fixPath(self.path)
        self.saving = False
        self.date = self.getDate()
        self.drive = '/media/rekkverk/b073e905-9aee-4b54-bee7-c86cf0d6dde6'

        self.storageLeft = 50
        self.data = None
        

        self.queue = self.args





    def fixPath(self,path):

            test = path.split("\\")
            if len(test)>1:

                test.pop()
                newPath = '/'.join(test)
                return newPath
            else:
                path = path.split("/")
                path.pop()
                path = '/'.join(path)

                
                return path
    def run(self):
               
        ImageList = []
        date = self.getDate()

        try:
            while True:
                
                try:
                    if self.args.poll(3):
                        data = self.args.recv()
                    else:
                        #print (f"No data available after {3} seconds...")
                        continue
                    
                except Exception as e:
                    print(e)
                    

                try : 
                    if data:
                        self.saving = True

                    else:
                        self.saving =False
                    #print('True')
                except Exception as e:
                    print(e)
                    self.saving = False


                
                
                
                if self.saving:
                    #print(self.data)
                    
                    #data = self.dataList
                    image = data['image']
                    camera = data['camera']
                    index =  data['index']
                    timestamp =  data['timeStamp']
                    cameraStamp = data['cameraStamp']

                    
                    try:

                        if self.storageLeft < 5:
                            newDrive = most_free_space()
                            self.drive = newDrive['name']
                        
                        try:
                            #ArrayImage = cvb.as_array(image, copy=False)
                            path = self.drive+"/"+"bilder/"+str(date)+"/"+str(self.tripName)+"/kamera"+str(camera)+"/"+str(index)+'.jpg'
                            ImageList.append([path,image])
                            if len(ImageList)%128==0:
                                with ThreadPoolExecutor() as executors:
                                    executors.map(SaveImagesListToFolder, ImageList)
                                
                                ImageList=[]

                            #print(str(index))

                            
                            
                            #image.save
                        except Exception as e:
                            print(e)
                            pass
                        if False:

                            path = self.path+"/log"+"/"+self.date+"/"+self.tripName+"/"+"images"+".csv"
                            write_header = not os.path.exists(path)
                            with open(path,'a',newline='')as csvfile:
                                

                                fieldnames = ['index', 'tripname', "camera","pc_time","camera_time"]
                                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                                if write_header:
                                    writer.writeheader()
                                
                                row = ({'index':index,'tripname':self.tripName,"camera":camera,"pc_time":timestamp,"camera_time":cameraStamp})
                                writer.writerow(row)

                    except Exception as e:


                        print("[SAVING THREAD  ERROR]"% (type(e).__name__, e))
                        
                        
                    # finally:
                    #     self.queue.task_done()
                            

                    
        except Exception as e:
            print(e)
            pass
           

        return "Stopped"

    def stop(self):

        self.isRunning = False
    
    def setDrive(self,drive):

        self.drive = drive


    def getDate(self):

        return datetime.today().strftime('%Y-%m-%d')
    

    def setStorageLeft(self,storage):

        self.storageLeft = storage
        


    def saveImages(self):
        self.saving = True

    def getTimeStamp(self,now):

        

        timenow = datetime.today().strftime('%H:%M:%S')
        milliseconds = '%03d' % int((now - int(now)))
        return str(timenow) +":"+ str(milliseconds)

    def createFolder(self):
        date = self.getDate()

            #   Making a folder for the images
        if not path.exists('log/'+date):

            os.mkdir('log/'+date) 
    
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

