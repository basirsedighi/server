import RPi.GPIO as GPIO
import time
import requests

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
myPWM = GPIO.PWM(18,50)
myPWM.start(10)
fps = 4
i = 0
#RestConnect ="http://10.10.10.62:8090/RaspFPS"

while True:
        
   
    
  
    myPWM.ChangeDutyCycle(50)
    myPWM.ChangeFrequency(int(fps))
        
    
    
    


GPIO.cleanup()
