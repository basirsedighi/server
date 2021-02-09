import threading
import serial
import queue
import time
import pynmea2


class Gps(threading.Thread):

    def __init__(self, queue):

        # calling parent class constructor
        threading.Thread.__init__(self)
        self.queue = queue
        self.serial = serial.Serial('COM8', 9600, timeout=0)

    def run(self):

        while(True):

            for i in range(10):
                line = self.serial.readline()
                line = pynmea2.parse(
                    self.serial.readline().decode('ascii', errors='replace'))
            time.sleep(2)
            self.queue.put(line)

    def getData():
        return data
