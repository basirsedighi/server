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

class GPS_QUALITY(enum.Enum):
   BEST = 3
   GOOD = 2
   LOW = 1
   BAD = 0

class gpsHandler(Thread):
    def __init__(self):
        Thread.__init__(self)

        self.GpsDataUrl ="http://localhost:8000/gpsPost"
        self.message  ={"quality":0,"velocity":0,"timestamp":"","lat":"","lon":""}
        self.data = {"quality":0,"velocity":0,"timestamp":"","lat":"","lon":""}
        self.logging = False
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.tripName =""
        self.date = self.getDate()
    
    def run(self):



        try:
            while True:
                ports = self.scan_ports()
                if len(ports) == 0:
                    sys.stderr.write('No ports found, waiting 10 seconds...press Ctrl-C to quit...\n')
                    time.sleep(10)
                    continue

                for port in ports:
                # try to open serial port
                    sys.stderr.write('Trying port %s\n' % port)
                    try:
                # try to read a line of data from the serial port and parse
                        with serial.Serial(port, 4800, timeout=1) as ser:

                            sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

                # 'warm up' with reading some input
                            for i in range(10):
                                sio.readline()
                            # try to parse (will throw an exception if input is not valid NMEA)
                            pynmea2.parse(ser.readline().decode('ascii', errors='replace'))

               
  
                            while True:
                                
                                
                                
                                line = sio.readline()
                                

                                if not line=="":
                                    
                                    line = self.__trimLine(line)
                                    try:

                                        msg = pynmea2.parse(line)
                                    except:
                                        pass
                                    
                                    
                                     
                                    message = self.createMessage(msg)
                                    if message =="no_data":
                                        pass
                                    else:
                                                                            
                                        self.data = message

                                    if(self.logging):
                                        with open(self.path+"/log"+"/"+self.date +"/"+self.tripName+"_gps"+".csv",'a',newline='')as csvfile:
                            

                                            fieldnames = ['tripname','quality', 'velocity', "timestamp","lat","lon"]
                                            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                                            
                                            row = ({'tripname':self.tripName,'quality':self.data['quality'],'velocity':self.data['velocity'],"timestamp":self.data['timestamp'],"lat":self.data['lat'],"lon":self.data['lon']})
                                            writer.writerow(row)

                                       
                                    
                                    
                                   # x = requests.post(self.GpsDataUrl, data =data,headers={'content-type':'application/json'})

                                        


                                
                                else:
                                    raise Exception("no new lines")
                                    
                                

                    except Exception as e:
                        sys.stderr.write('Error reading serial port %s: %s\n' % (type(e).__name__, e))
                        self.data = {"quality":0,"velocity":0,"timestamp":"","lat":"","lon":""}
                    except KeyboardInterrupt as e:
                        sys.stderr.write('Ctrl-C pressed, exiting log of %s to %s\n' % (port, "jdksj"))

                sys.stderr.write('Scanned all ports, waiting 10 seconds...press Ctrl-C to quit...\n')
                self.data = {"quality":0,"velocity":0,"timestamp":"","lat":"","lon":""}
                time.sleep(5)
        except KeyboardInterrupt:
            sys.stderr.write('Ctrl-C pressed, exiting port scanner\n')

    def getData(self):

        return self.data
    
    def setTripName(self,tripName):
        self.tripName = tripName
    
    def getDate(self):

        return datetime.today().strftime('%Y-%m-%d')
    def getTimeStamp(self):

        now = time.time_ns()

        timenow = datetime.today().strftime('%H:%M:%S')
        milliseconds = '%03d' % int((now - int(now)) * 1000)
        return str(timenow) +":"+ str(milliseconds)

    def createMessage(self,msg):
        now = self.getTimeStamp()
        fix_quality = 0
        hdop = 5
        
        self.message.update({"timestamp":str(now)})
        if(msg.sentence_type =="RMC"):

            velocity = self.__knotsToKmh(msg.spd_over_grnd)
        
            self.message.update({"velocity":str(velocity),"timestamp":str(now),"lat":str(msg.latitude),"lon":str(msg.longitude)})
            return self.message 
        
        if msg.sentence_type =="VTG":

            velocity = msg.spd_over_grnd_kmph
            self.message.update({"timestamp":str(now),"velocity":str(velocity)})
            return self.message 


        if(msg.sentence_type=="GGA"):

           
            
            fix_quality = int(msg.gps_qual)

            try:
                hdop = float(msg.horizontal_dil)
            except:
                pass
            
        
            quality = self.getGpsQuality(fix_quality,hdop)
            
            self.message.update({"quality":int(quality),"timestamp":str(now),"lat":str(msg.latitude),"lon":str(msg.longitude)})
            return self.message   

        

        if(msg.sentence_type=="GLL"):
            
            
            self.message.update({"timestamp":str(now),"lat":str(msg.latitude),"lon":str(msg.longitude)})
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
    

    def toggleLogging(self):
        self.logging = not self.logging

    
    
  
    def scan_ports(self):

        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(10)]
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



    def __trimLine(self, msg):
        message = ''
        message = msg
        start = message.find('$')
        # -7 removes checksum, -5 if we add a test on the checksum
        end = len(message)-5
        result = ''
        result = message[start:end]
        return result
