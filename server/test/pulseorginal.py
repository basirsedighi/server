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

        if start:
            if int(fps_new)==0:
                myPWM.ChangeDutyCycle(0)
                if i%100==0:
                    print("1")
                    #messagePOST = RestConnect+"?FPS=0"
                    #requests.post(messagePOST)
            elif int(fps_new)!= fps:
                fps = int(fps_new)
                myPWM.ChangeDutyCycle(50)
                myPWM.ChangeFrequency(int(fps))
            elif fps==int(fps_new) and i%100==0:
                #messagePOST = RestConnect+"?FPS="+str(fps)
                #requests.post(messagePOST)
                myPWM.ChangeDutyCycle(50)
                myPWM.ChangeFrequency(int(fps))
                
        
        
        i=i+1
    except Exception as e:

        myPWM.ChangeDutyCycle(50)
        myPWM.ChangeFrequency(5)

GPIO.cleanup()
