from multiprocessing import Process
import requests
import pynmea2, serial, os, time, sys, glob, datetime
from datetime import datetime
import json

class gpsHandler(Process):
    def __init__(self):
        super(gpsHandler,self).__init__()

        self.RestConnect ="http://10.22.182.47:8000/gps"


    
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

                # 'warm up' with reading some input
                            for i in range(10):
                                ser.readline()
                            # try to parse (will throw an exception if input is not valid NMEA)
                            pynmea2.parse(ser.readline().decode('ascii', errors='replace'))

               
  
                            while True:
                                line = ser.readline()

                                if line:
                                    line = str(line)
                                    result = ''
                                    result = self.__trimLine(line)
                                    msg = pynmea2.parse(result)
                                    if msg.sentence_type =="RMC":

                                        #message = self.createMessage(msg)
                                        data = self.createMessage(msg)

                                        x = requests.post(self.RestConnect, data =data,headers={'content-type':'application/json'})

                                        


                                
                                else:
                                    raise Exception("no new lines")
                                    
                                

                    except Exception as e:
                        sys.stderr.write('Error reading serial port %s: %s\n' % (type(e).__name__, e))
                    except KeyboardInterrupt as e:
                        sys.stderr.write('Ctrl-C pressed, exiting log of %s to %s\n' % (port, "jdksj"))

                sys.stderr.write('Scanned all ports, waiting 10 seconds...press Ctrl-C to quit...\n')
                time.sleep(5)
        except KeyboardInterrupt:
            sys.stderr.write('Ctrl-C pressed, exiting port scanner\n')


    def createMessage(self,msg):
        now = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        
        
        message = {"velocity":str(msg.spd_over_grnd),"timeStamp":str(now),"lat":str(msg.lat),"lon":str(msg.lon)}

        data = json.dumps(message)
       
        return data


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
    

    def logfilename(self):
        now = datetime.datetime.now()
        return 'NMEA_%0.4d-%0.2d-%0.2d_%0.2d-%0.2d-%0.2d.nmea' % \
                    (now.year, now.month, now.day,
                    now.hour, now.minute, now.second)



    def __trimLine(self, msg):
        message = ''
        message = msg
        start = message.find('$')
        # -7 removes checksum, -5 if we add a test on the checksum
        end = len(message)-5
        result = ''
        result = message[start:end]
        return result
