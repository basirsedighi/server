from threading import Thread
import queue
from datetime import datetime

import quick_queue
from quick_queue.quick_queue import QQueue
from core.timer import Timer
import os
from multiprocessing import Process, Pipe, Queue
from os import path
from datetime import datetime
import cvb
import ctypes
import csv
import json
from core.helpers.helper_server import most_free_space
import cv2
from PIL import Image
import concurrent
from concurrent.futures import ThreadPoolExecutor
import time
import sys


def SaveImagesListToFolder(List):
         # #print(self.data)
        try:
            
            data = List
            date = "2021-05-10"
            drive = '/media/rekkverk/b073e905-9aee-4b54-bee7-c86cf0d6dde6'
            image = data['image']
            camera = data['camera']
            index =  data['index']
            timestamp =  data['timeStamp']
            cameraStamp = data['cameraStamp']
            path = os.path.join(drive,'bilder',date,'BASIR4',f'kamera{camera}',str(index)+'.jpg')
            #print(path)
            cv2.imwrite(path,image)
        except Exception as e:
            print(f'Thread dead because of {sys.exc_info()[0]}{sys.exc_info()[1]}')


def pickFromQueue(queue):
    frame = queue.get()
    return frame

def pickMoreFromQueue(queue):
    idx = 0
    frames = []

    while not idx == 4:
        frames.append(queue.get())
        idx += 1

    return frames


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
        dataList = None
        ImageList = []
        date = self.getDate()

        try:
            while True:
                
                if self.args.full():
                    print("Queue Full")

                try:
                    
                    
                    
                    #datalist = [self.args.get(),self.args.get(),self.args.get(),self.args.get(),self.args.get(),self.args.get(),self.args.get(),self.args.get(),self.args.get(),self.args.get(),self.args.get(),self.args.get(),self.args.get()]
                    if not self.args.empty():
                        
                        # datalist  = [self.args.poll for _ in range(24)]
                        dataList = []
                        maxworkers = 32
                        
                        with ThreadPoolExecutor(max_workers=maxworkers) as executors:
                                
                               futures = {executors.submit(pickMoreFromQueue, self.args): frame for frame in range(maxworkers)}
                               for future in concurrent.futures.as_completed(futures):
                                   startThread = time.time()
                                   #url = futures[future]
                                   try:
                                        data = future.result()
                                        #print(data)
                                        dataList = [*dataList, *data]
                                        endThread = time.time()
                                        print(f'Getting 4 images took {-startThread+endThread}')
                                        #dataList.append(*data)
                                   except Exception as exc:
                                        print('%r generated an exception: %s' % (exc))
                                   else:
                                        pass
                                        #print('%r page is %d bytes' % (url, len(data)))

                        
                        
                        if self.args.full():
                            print('imfull')
                        
                        
                                          
                        
                except Exception as e:
                    print(f'Cant get from bucket because {e}')    
                
                        
                    
                except Exception as e:
                    print(e)
                    

                try : 
                    #print(datalist)
                    if dataList:
                        self.saving = True

                    else:
                        self.saving =False
                    #print('True')
                except Exception as e:
                    print(e)
                    self.saving = False


                
                
                
                if self.saving:
                    try :
                        start = time.time()
                        print(f'Lenght of Datalist {len(dataList)}')
                        with ThreadPoolExecutor(max_workers=32) as executors:
                                 executors.map(SaveImagesListToFolder, dataList)
                        
                    
                        end = time.time()
                        print(f'saving 128 images took {end-start}s ')
                    # #print(self.data)
                    
                    # #data = self.dataList
                    # image = data['image']
                    # camera = data['camera']
                    # index =  data['index']
                    # timestamp =  data['timeStamp']
                    # cameraStamp = data['cameraStamp']

                    
                    # try:

                    #     if self.storageLeft < 5:
                    #         newDrive = most_free_space()
                    #         self.drive = newDrive['name']
                        
                    #     try:
                    #         #ArrayImage = cvb.as_array(image, copy=False)
                    #         path = self.drive+"/"+"bilder/"+str(date)+"/"+str(self.tripName)+"/kamera"+str(camera)+"/"+str(index)+'.jpg'
                    #         ImageList.append([path,image])
                    #         if len(ImageList)%128==0:
                                
                                
                                # ImageList=[]

                            #print(str(index))

                            
                            
                        #     #image.save
                        # except Exception as e:
                        #     print(e)
                            # pass
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

    def new_method(self):
        return True

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

