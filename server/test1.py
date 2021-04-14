import os
from datetime import datetime
def getDate():

    return datetime.today().strftime('%Y-%m-%d')

date = getDate()

path = os.path.dirname(os.path.abspath(__file__))

directory_contents = os.listdir(path+"/log/"+date+"/test123")


