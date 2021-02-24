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
Position = namedtuple("Position", "lat lon timestamp")


class Gps:

    connected = False
    log_name_and_path = ""
    # status is to indicate the quality of the gps signal on the screen
    #   0:  is not connected to the gps at all:                             status red
    #   1:  connected to the gps, has not received fix available from gps:  status red
    #   2:  has received fix available, HDOP is below threshold:            status yellow
    #   3:  HDOP is above threshold:                                        status green

    status = 0

    def __init__(self, log_path):
        self.status = 0
        try:
            self.ser = serial.Serial(timeout=10)
            self.ser.baudrate = 9600
            self.ser.port = 'COM6'
            self.__createLogger(log_path)
            self.ser.open()
            self.status = 1
            self.connected = True
        except serial.SerialException:
            self.status = 0
            self.connected = False
        except serial.SerialTimeoutException:
            self.status = 0
        #these are current positions
        self.position = Position(0.0, 0.0, 0.0)
        self.str_position = Position('', '', '')

        # these are old positions
        self.old_position = Position(0.0, 0.0, 0.0)

        #velocity in kmh
        self.velocity = 0.0
    def reconnect(self):
        self.ser.close()
        try:
            self.ser.open()
            self.status = 1
            self.connected = True
        except serial.SerialException:
            self.status = 0
            self.connected = False
        except serial.SerialTimeoutException:
            self.status = 0

    def checkGps(self):
        self.connected = False
        try:
            line = str(self.ser.readline())

            self.connected = True
            result = ''
            result = self.__trimLine(line)
            self.timestamp = time.time()
            msg = pynmea2.parse(result)
            if self.__updateFields(msg):
                self.__logData()
                return True
            elif self.__checkConnection(msg):
                return True
            else:
                return False
        except serial.SerialTimeoutException as e:
            #print('Timeout: {}'.format(e))
            self.status = 0
            return False
        except serial.SerialException as e:
            #print('Device error: {}'.format(e))
            self.status = 0
            return False
        except pynmea2.ParseError:
            self.connected = False
            self.status = 0
            return False

    def calculatePwm(self, distance):
        result = 1000 / self.__calculateFrequency(distance)
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

    def __calculateFrequency(self, distance):
        factor = 3.6
        velocityInMs = self.velocity / factor
        result = velocityInMs / distance
        return result

    def __updateFields(self, msg):
        if msg.sentence_type == 'RMC':
            self.velocity = self.__knotsToKmh(msg.spd_over_grnd)

            # set old positions before updating
            self.old_position = Position(
                self.position.lat, self.position.lon, self.position.timestamp)
            self.position = Position(msg.lat, msg.lon, time.time())

            self.str_position = Position(str(self.position.lat), str(self.position.lon), datetime.datetime.fromtimestamp(
                self.position.timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'))
            return True
        else:
            return False

    def __checkConnection(self, msg):
        if msg.sentence_type == 'GSA':
            if msg.mode_fix_type != 1:
                self.status = 2
                try:
                    if float(msg.hdop) < 5.0:
                        self.status = 3
                except ValueError:
                    return False
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
            step_timestamp = (self.position.timestamp -
                              self.old_position.timestamp)

            lats.append(((step_lat*i) + self.old_position.lat))
            lons.append(((step_lon*i) + self.old_position.lon))
            timestamps.append(
                ((step_timestamp*i) + self.old_position.timestamp))

        for i in range(number):
            positions.append(Position(lats[i], lons[i], timestamps[i]))
        return positions

    def __createLogger(self, path):
        name = datetime.date.today().strftime("%d_%m_%Y")
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
    g = Gps("C:/Users/Michal Leikanger/Desktop/")
    while True:
        print(g.status)
        if g.connected:
            g.checkGps()
        else:
            g.reconnect()
                    
if __name__ == "__main__":
    main()
        


if __name__ == "__main__":
    main()
