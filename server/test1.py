import os
from core.merging import merge


date ="2021-04-20"
tempTrip= "bachelorvol2.2.3utenpuse"
absolute_path = os.path.dirname(os.path.abspath(__file__))
path = absolute_path+"/log/"+date+"/"+tempTrip      

merge(path)