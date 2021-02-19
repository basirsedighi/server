import threading
import queue
import time
import sys
import glob
import socket
import codecs
import csv
import datetime
import serial
import pynmea2
import time
import signal
from collections import namedtuple
Position = namedtuple("Position","lat lon timestamp")


class Gps:
    
    
    connected = False
    log_name_and_path = ""
    status = 0

    def __init__(self, log_path):
        print("connecting...")
        self.status = 0

        try: 
            self.ser = serial.Serial(timeout=5)
            self.ser.baudrate = 9600
            self.ser.port = 'COM5'
            self.ser.open()
            self.__createLogger(log_path)
            print("connected")
            self.status = 1
            self.connected = True
        except serial.SerialException:
            print("did not connect to com port")
            self.connected = False
            time.sleep(2.0)
        except serial.SerialTimeoutException:
            print('trying to reconnect')
            time.sleep(2.0)
        #these are current positions
        self.position = Position(0.0, 0.0, 0.0)
        self.str_position = Position('', '', '')
        
        #these are old positions
        self.old_position = Position(0.0, 0.0, 0.0)
        
        #velocity in kmh
        self.velocity = 0.0
        
    def checkGps(self):
        self.connected = False
        try:
            print("trying to read")
            line = str(self.ser.readline())
            self.connected = True
            print("did read")
            result = ''
            result = self.__trimLine(line)
            print(result)
            self.timestamp = time.time()
            msg = pynmea2.parse(result)
            print(msg)
            if self.__updateFields(msg):
                self.__logData()
                return True
        except serial.SerialTimeoutException as e:
            print('Timeout: {}'.format(e))
            return False
        except serial.SerialException as e:
            print('Device error: {}'.format(e))
            return False
        
        


    def calculatePwm(self, distance):
        result = 1000 / self.__calculateFrequency(distance)
        return result        


    def __trimLine(self, msg):
        message = ''
        message = msg
        start = message.find('$')
        #-7 removes checksum, -5 if we add a test on the checksum
        end = len(message)-5
        result = ''
        result = message[start:end]
        return result

    def __calculateFrequency(self, distance):
        factor = 3.6
        velocityInMs = self.velocity / factor
        result = velocityInMs / distance
        return result

    def __updateFields(self, msg):
        if  msg.sentence_type == 'RMC':
            self.velocity = self.__knotsToKmh(msg.spd_over_grnd)

            #set old positions before updating
            self.old_position = Position(self.position.lat, self.position.lon , self.position.timestamp)
            self.position = Position(msg.lat, msg.lon, time.time())
            
            self.str_position = Position(str(self.position.lat),str(self.position.lon), datetime.datetime.fromtimestamp(self.position.timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'))
            return True
        else:
            return False
            
    def __knotsToKmh(self, knots):
        factor = 1.852
        result = factor * knots
        
        return result

    def __caluclatePositions(self, number):
        lons = []
        lats = []
        timestamps = []
        positions = []
        for i in range(number):
            step_lat = (abs(self.position.lat-self.old_position.lat))/number
            step_lon = (abs(self.position.lon-self.old_position.lon))/number
            step_timestamp = (self.position.timestamp-self.old_position.timestamp)

            lats.append(((step_lat*i) + self.old_position.lat))
            lons.append(((step_lon*i) + self.old_position.lon))
            timestamps.append(((step_timestamp*i) + self.old_position.timestamp))

        for i in range(number):
            positions.append(Position(lats[i], lons[i], timestamps[i]))
        return positions

    def __createLogger(self, path):
        name =  datetime.date.today().strftime("%d_%m_%Y")
        file_name = name + (".csv")
        self.log_name_and_path = path + file_name
        
        with open(self.log_name_and_path, 'w', newline='') as f:
            self.writer = csv.writer(f)
            self.writer.writerow(['Latitude', 'Longitude', 'Timestamp'])

    def __logData(self):
        if ((self.position.timestamp) != (self.old_position.timestamp)):
            with open(self.log_name_and_path, 'a', newline='') as f:
                self.writer = csv.writer(f)
                self.writer.writerow(self.position)
def main():
    #need exceptions in case it would not connect to gps
    while True:
        g = Gps("C:/Users/Michal Leikanger/Desktop/")
        i = 0
        while g.connected:
            try:
                #check fault with serial message
                if g.checkGps():
                    i = i+1
                    #print("updated " + str(i))
            except pynmea2.ParseError:
                print('disconnected from gps')
                g.connected = False
            
        
if __name__ == "__main__":
    main()
        


