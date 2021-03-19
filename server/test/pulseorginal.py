import RPi.GPIO as GPIO
import time
import requests

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
myPWM = GPIO.PWM(18,50)
myPWM.start(10)




fps = None
i = 0
RestConnect ="http://192.168.0.100:8000/RaspFPS"

while True:

    try:
    
        response = requests.get(RestConnect)
        data = response.json()
        fps_new = data['fps']
        start = data['start']
        print(start)

        if start:
            myPWM.ChangeDutyCycle(50)
            myPWM.ChangeFrequency(fps_new)

        else:
            myPWM.ChangeDutyCycle(0)

        
        
        i=i+1
    except Exception as e:
        print(e)
        myPWM.ChangeDutyCycle(0)
        

GPIO.cleanup()
