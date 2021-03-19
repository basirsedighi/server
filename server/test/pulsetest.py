import requests
import json



RestConnect ="http://192.168.0.100:8000/RaspFPS"


while True:

    try:
    
        response = requests.get(RestConnect)
        data = response.json()
        print(data['start'])

    except Exception as e:
        print(e)