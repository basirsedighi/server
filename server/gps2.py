from multiprocessing import Process
from threading import Thread
import requests
import pynmea2, serial, os, time, sys, glob, datetime
from datetime import datetime
import json
import enum
import io
import os
import csv
os.system('sudo chmod a+rw /dev/ttyUSB2')
os.system('sudo chmod a+rw /dev/ttyUSB1')
os.system('sudo chmod a+rw /dev/ttyUSB0')

class GPS_QUALITY(enum.Enum):
   BEST = 3
   GOOD = 2
   LOW = 1
   BAD = 0

class Error(Exception):
    """Base class for other exceptions"""
    pass

class InitGPS(Error):
    """Raised when initilizing start to break loop"""
    pass

class gpsHandler(Thread):
    def __init__(self,debug):
        Thread.__init__(self)
        self.debug = debug
        self.message  ={"quality":0,"satelites":0,"velocity":0,"timestamp":"","gpsTime":"","lat":"","lon":"","new":False,"pc":""}
        self.data = {"quality":0,"satelites":0,"velocity":0,"timestamp":"","gpsTime":"","lat":"","lon":"","new":False,"pc":""}
        self.logging = False
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.tripName =""
        self.date = self.getDate()
        self.serial = None
        self.init = False
        self.connected = False
        self.initStarted = False

    
    def run(self):



        try:
            while True:
                ports = self.scan_ports()
                if len(ports) == 0:
                    if self.debug:
                        sys.stderr.write('No ports found, waiting 5 seconds...press Ctrl-C to quit...\n')
                    time.sleep(5)
                    continue

                for port in ports:
                # try to open serial port
                    if self.debug:
                        sys.stderr.write('Trying port %s\n' % port)
                    try:
                # try to read a line of data from the serial port and parse
                        with serial.Serial(port, 115200, timeout=10) as ser:

                            self.serial = ser
                            self.read = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
                              #sends commands to gps
                            if self.init:
                                self.initGPS()
                                self.init = False
                # 'warm up' with reading some input
                            for i in range(10):
                                data = ser.readline()
                                #print(data)
                            # try to parse (will throw an exception if input is not valid NMEA)
                           
                            pynmea2.parse(ser.readline().decode('ascii', errors='replace'))

                          
                            self.connected = True
                            while True:
                                
                                
                                if self.init:
                                    raise InitGPS
                                line = self.read.readline()
                                #.decode('ascii', errors='replace')
                                

                                if not line=="":
                                    
                                    line = self.__trimLine(line)
                                    #print(line)
                                    try:

                                        msg = pynmea2.parse(line)
                                        #print(msg)
                                    except:
                                        pass
                                    
                                    
                                     
                                    message = self.createMessage(msg)
                                    if message =="no_data":
                                        pass
                                    else:
                                                                            
                                        self.data = message
                                        
                                    

                                        if(self.logging and self.data['new'] ==True):
                                            path= self.path+"/log"+"/"+self.date +"/"+self.tripName+"/"+"gps"+".csv"
                                            write_header = not os.path.exists(path)
                                            with open(path,'a',newline='')as csvfile:
                                

                                                fieldnames = ['tripname','quality', 'velocity', "timestamp","time milli","lat","lon","satelites","pc"]
                                                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                                                if write_header:
                                                    writer.writeheader()
                                                
                                                row = ({'tripname':self.tripName,'quality':self.data['quality'],'velocity':self.data['velocity'],"timestamp":self.data['timestamp'],"time milli":self.data['gpsTime'],"lat":self.data['lat'],"lon":self.data['lon'],"satelites":self.data['satelites'],"pc":self.data["pc"]})
                                                writer.writerow(row)

                                       
                                    
                                    
                                  

                                        


                                
                                else:
                                    raise Exception("no new lines")
                                    
                                

                    except Exception as e:
                        if self.debug: sys.stderr.write('Error reading serial port %s: %s\n' % (type(e).__name__, e))
                        self.data = {"quality":0,"velocity":0,"timestamp":"","gpsTime":"","lat":"","lon":""}
                    except KeyboardInterrupt as e:
                        pass
                        sys.stderr.write('Ctrl-C pressed, exiting log of %s to %s\n' % (port, "jdksj"))

                    except InitGPS:
                        print("Initilizing the GPS")
                        break
                if self.debug: sys.stderr.write('Scanned all ports, waiting 5 seconds...\n')
                self.data = {"quality":0,"velocity":0,"timestamp":"","gpsTime":"","lat":"","lon":""}
                time.sleep(3)
                self.connected = False
        except KeyboardInterrupt:
            self.serial.close()
            self.read.close()
            #sys.stderr.write('Ctrl-C pressed, exiting port scanner\n')

    def getData(self):

        return self.data
    
    def setTripName(self,tripName):
        self.tripName = tripName
    
    def getDate(self):

        return datetime.today().strftime('%Y-%m-%d')
    

    def setDebug(self,value):
        print(value)

        self.debug = value

    def convertDatetime(self,dt):
        now = datetime.now()
        x = datetime(now.year, now.month, now.day,now.hour,dt.minute,dt.second,dt.microsecond)

        timestamp = datetime.timestamp(x)
        

        return int(timestamp*1000)

    
    def isConnected(self):
        return self.connected
    
    def getTimeStamp(self):

        now = time.time()

        timenow = datetime.today().strftime('%H:%M:%S')
        milliseconds = '%03d' % int((now - int(now)) * 1000)
        return str(timenow) +":"+ str(milliseconds)

    def createMessage(self,msg):
        now = self.getTimeStamp()
        milliseconds = int(time.time() * 1000)
        fix_quality = 0
        hdop = 5
        velocity = 0
        gpstime = ""
        gpstimes = ""
        

        
        if(msg.sentence_type =="RMC"):
            update = False
            if self.debug:

                print("RMC received")
                print(msg.timestamp)
           
            if msg.status =="A":
                velocity = self.__knotsToKmh(msg.spd_over_grnd)
                velocity = self.__kmhToMs(velocity)
                gpstime = msg.timestamp
                update =True
                
                gpstimes = self.convertDatetime(gpstime)
           
        
            self.message.update({"velocity":str(velocity),"timestamp":str(gpstime),"gpsTime":str(gpstimes),"lat":str(msg.latitude),"lon":str(msg.longitude),"new":update,"pc":str(now)})
            return self.message
        

       


        if(msg.sentence_type=="GGA"):
            if self.debug:

                print("GGA received")
                print(msg)

           
            satelites = msg.num_sats
            fix_quality = int(msg.gps_qual)

            try:
                hdop = float(msg.horizontal_dil)
            except:
                pass
            
        
            quality = self.getGpsQuality(fix_quality,hdop)
            
            self.message.update({"quality":int(quality),"satelites":satelites,"new":False})
            return self.message   

            

        

        return "no_data"

    def getGpsQuality(self,fixQuality, hdop):
        gpsQuality = GPS_QUALITY.BAD.value
        if (fixQuality and hdop > 0):
            if (fixQuality == 4):
                gpsQuality = GPS_QUALITY.BEST.value
            elif ((fixQuality == 5 and hdop < 2) or hdop <= 1):
                gpsQuality = GPS_QUALITY.GOOD.value
            else:

                gpsQuality = GPS_QUALITY.LOW.value
        
    
        return gpsQuality
    

    def toggleLogging(self,value):
        
        self.logging = value

    def send(self, cmd):
        # self.gps.write_line(cmd)
        try :
            self.serial.write(cmd.encode())
        except:
            sys.stderr.write('Not Connected To GPS')
            #self.serial.close()
        
        time.sleep(3)
        
        num = self.serial.inWaiting()
        # try:
        #     print(self.gps.read(num).decode())
        # except:
        #     print(self.gps.read(num))
        recieved = self.serial.read(num)
        if self.debug:
            try:
                print(recieved.decode('utf-8'))
            except Exception:
                pass
        
        

    

    def startInit(self):

        self.init =True

        
    def initGPS(self):
        self.initStarted =True
        self.send('SetNMEAOutput, Stream1+Stream2+Stream7+Stream8, none, none, off\r\n')
        self.send('SetGPIOFunctionality, GP1, Output, none, LevelLow\r\n')
        self.send('SetGPIOFunctionality, GP2, Output, none, LevelHigh\r\n')
        self.send('SetGPIOFunctionality, GP3, Output, none, LevelHigh\r\n')
        self.send('setDataInOut, COM1,DC1,DC2\r\n')
        self.send('setDataInOut, COM3,DC2,DC1\r\n')
        self.send('#PSPO,1\n')
        self.send('SSSSSSSSSS\r\n')
        self.send('setDataInOut, COM1, CMD, SBF+NMEA\r\n')
        self.send('SSSSSSSSSS\r\n')
        self.send('SetSBFOutput,Stream1+Stream2+Stream3+Stream4+Stream5,none,none,off\r\n')
        self.send('setPVTMode, Rover, all\r\n')
        self.send('sem,+PVT,10\r\n')
        self.send('setDataInOut, COM1, CMD, SBF\r\n')
        self.send('setGeoidUndulation, auto\r\n')
        self.send('setSmoothingInterval,all,100,1\r\n')
        self.send('setRAIMLevels,on,-4,-4,-3\r\n')
        self.send('setPVTMode, Rover, all\r\n')
        self.send('setFixReliability, RTK, 0.2, 4.40\r\n')
        self.send('setDiffCorrUsage,,,auto,0\r\n')
        self.send('setDataInOut, COM2, RTCMv3, SBF+NMEA\r\n')
        self.send('setDataInOut, COM2,DC1,DC2\r\n')
        self.send('setDataInOut, COM3,DC2,DC1\r\n')
        self.send('+++\r\n')
        self.send('AT\r\n')
        self.send('+++\r\n')
        self.send('AT\r\n')
        self.send('+++\r\n')
        self.send('ATE1\r\n')
        self.send('AT+MGEER=2\r\n')
        self.send('AT+CMEE=2\r\n')
        self.send('AT+CBST?\r\n')
        self.send('AT+CPIN?\r\n')
        self.send('AT+CSQ\r\n')
        self.send('AT+MIPCALL?\r\n')
        self.send('AT+MIPCALL=1,"telenor","",""\r\n')
        self.send('AT+MIPOPEN?\r\n')
        self.send('AT+MIPODM=1,1200,"159.162.103.14",2101,0\r\n')
        self.send('GET /CPOSHREF HTTP/1.0\r\n')
        self.send('User-Agent: NTRIP Altus\r\n')
        self.send('Authorization: Basic NTgwMDAwNzEzNTMzOkdKRVJERTEzMDU=\r\n')
        self.send('Accept: */*\r\n')
        self.send('Connection: close\r\n')
        self.send('\r\n')
        self.send('\r\n')
        self.send('SSSSSSSSSS\r\n')
        self.send('setDataInOut, COM3, CMD, SBF+NMEA\r\n')
        self.send('setDataInOut, COM2, RTCMv3, SBF+NMEA\r\n')
        self.send('SetNMEAOutput, Stream1, COM2, GGA, sec1\r\n')
        self.send('SetNMEAOutput, Stream8, COM3, GGA+VTG+RMC, msec100\r\n')
        
        self.initStarted = False
    


    #https://fishandwhistle.net/post/2016/using-pyserial-pynmea2-and-raspberry-pi-to-log-nmea-output/
    def scan_ports(self):

        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(6)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            patterns = ('/dev/tty[A-Za-z]*', '/dev/ttyUSB*')
            ports = [glob.glob(pattern) for pattern in patterns]
            ports = [item for sublist in ports for item in sublist]  # flatten
        elif sys.platform.startswith('darwin'):
            patterns = ('/dev/*serial*', '/dev/ttyUSB*', '/dev/ttyS*')
            ports = [glob.glob(pattern) for pattern in patterns]
            ports = [item for sublist in ports for item in sublist]  # flatten
        else:
            raise EnvironmentError('Unsupported platform')
        return ports
    

    

    

    def __calculateFrequency(self, distance):

        factor = 3.6
        velocityInMs = self.velocity / factor
        result = velocityInMs / distance
        return result

    def __knotsToKmh(self, knots):
        factor = 1.852
        result = factor * knots
        return result



    def __kmhToMs(self,speedKmh):

        return speedKmh/3.6



    def setClock(self,time):
        
        gpsutc = time.year+time.month+time.day+(time.second) + (time.microsecond)

        os.system('sudo date -u ???set="%s"' % gpsutc)
    
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

    def __trimLine(self, msg):
        message = ''
        message = msg
        start = message.find('$')
        # -7 removes checksum, -5 if we add a test on the checksum
        end = len(message)-5
        result = ''
        result = message[start:end]
        return result
