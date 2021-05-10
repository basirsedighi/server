import serial
import pynmea2
from math import pi, cos, sin, acos
import datetime
import time
import os 
os.system('sudo chmod a+rw /dev/ttyUSB2')

class GPS:
    '''doc'''

    def __init__(self, serial_port='/dev/ttyUSB2', baudrate=115200):
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.lat, self.lon = 0.0, 0.0
        self.speed_kph = 0.0
        self.last_lon, self.last_lat, self.last_timestamp = 0.0, 0.0, datetime.time()
        self.gps = None
        self.gps_active = False 
        

    def send(self, cmd):
        # self.gps.write_line(cmd)
        try :
            self.gps.write(cmd.encode())
        except:
            print('Not Connected To GPS')
            self.gps.close()
        
        time.sleep(3)
        
        num = self.gps.inWaiting()
        # try:
        #     print(self.gps.read(num).decode())
        # except:
        #     print(self.gps.read(num))
        print(self.gps.read(num))

    def connect(self):
        '''doc'''
        try:
            self.gps = serial.Serial(self.serial_port, baudrate=self.baudrate)
            self.gps.timeout = 30
        except serial.serialutil.SerialException:
            print('\nERROR: Either, GPS is not or you dont have permission to read...\nPlease write: sudo chmod a+rw /dev/ttyUSB0 in the terminal and try again.\n')
    
    def poll(self):
        '''doc'''
        lat, lon, timestamp = 0.0, 0.0, 0.0
        if self.gps is None: return
        data = self.gps.readline().decode()
        message = data[0:6]
        if (message == '$GPRMC'):
            parts = data.split(',')
            if parts[2]=="V":
                self.gps_active = False
                self.speed_kph=0
                return None
            elif parts[2]=="A":
                self.gps_active = True
                self.speed_kph = 1.852 * float(parts[7])
        if(message=='$GPGGA'):
            y = pynmea2.parse(data)
            if y.gps_qual>=1:
                self.lat = y.latitude
                self.lon = y.longitude
            print('{0} {1} {2}'.format(y.gps_qual, self.lat, self.lon))
    
    def initGPS(self):
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
        self.send('SetNMEAOutput, Stream7, COM3, GSV+GSA, sec1\r\n')
        self.send('SetNMEAOutput, Stream8, COM3, GGA+VTG+RMC, sec1\r\n')
#Example of usage
if __name__ == "__main__":
    n = 0
    gps = GPS()
    gps.connect()
    #gps.initGPS()
    time.sleep(5)
    i = 0
    while 1:
        gps.poll()
        i+=1
        if i==1000:
            break
    gps.gps.close()

