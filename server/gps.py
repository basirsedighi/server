import threading
import queue
import time
import sys
import glob
import socket
import codecs
import serial
import pynmea2
from collections import namedtuple
Position = namedtuple("Position","lat lon timestamp")
class Gps:

    ser = serial.Serial()

    def __init__(self):
        print("object created")
        self.ser.baudrate = 9600
        self.ser.port = 'COM5'
        self.ser.open()

        #these are current positions
        self.position = Position(1000.0, 500.0, 100)

        #these are old positions
        self.old_position = Position(0.0, 0.0, 0)

        #velocity in kmh
        self.velocity = 0.0
        
    def checkGps(self):
        try:
            line = str(self.ser.readline())
            result = ''
            result = self.__trimLine(line)
            self.timestamp = time.time()
            msg = pynmea2.parse(result)
            self.__updateFields(msg)
        except serial.SerialException as e:
            print('Device error: {}'.format(e))
        except pynmea2.ParseError as e:
            print('Parse error: {}'.format(e))
        

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
            self.old_position.lat = self.position.lat
            self.old_position.lon = self.position.lon
            self.old_position.timestamp = self.position.timestamp

            self.position.lat = msg.lat
            self.position.lon = msg.lon
            self.position.timestamp = time.time()
            
        

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

def main():
    #need exceptions in case it would not connect to gps
    g = Gps()
    """
    while True:
        #check fault with serial message
        g.checkGps()

        print("vel: " + str(g.velocity))
        print("lat: " + str(g.lat))
        print("lon: " + str(g.lon))
        
     """ 
if __name__ == "__main__":
    main()
        

