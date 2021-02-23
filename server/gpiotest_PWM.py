import RPi.GPIO as GPIO
import time
import requests

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
myPWM = GPIO.PWM(18,50)
myPWM.start(10)
fps = None
i = 0
#RestConnect ="http://10.10.10.62:8090/RaspFPS"

while True:
    
    #response = requests.get(RestConnect).text
    #print(response)
    response = "15"
    if int(response)==0:
        myPWM.ChangeDutyCycle(0)
        if i%100==0:
            #messagePOST = RestConnect+"?FPS=0"
            #requests.post(messagePOST)
    elif int(response)!= fps:
        fps = int(response)
        myPWM.ChangeDutyCycle(50)
        myPWM.ChangeFrequency(int(fps))
    elif fps==int(response) and i%100==0:
        #messagePOST = RestConnect+"?FPS="+str(fps)
        #requests.post(messagePOST)
        myPWM.ChangeDutyCycle(50)
        myPWM.ChangeFrequency(int(fps))
        
    
    
    i=i+1


GPIO.cleanup()
