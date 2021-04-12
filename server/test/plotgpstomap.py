import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cv2
    
path = "C:/Users/tor_9/Documents/csv/"
header_list = ['picmillis', 'gpsmillis','readlat', 'readlong', 'extendedlat','extendedlong']
df = pd.read_csv(path+'k1time.csv', names = header_list)

BBox = (df.extendedlong.min(),   df.extendedlong.max(),      
         df.extendedlat.min(), df.extendedlat.max())

ruh_m = plt.imread(path+'map.png')

fig, ax = plt.subplots(figsize = (8,7))

ax.scatter(df.extendedlong, df.extendedlat, zorder=1, alpha= 0.2, c='b', s=10)

ax.set_title('Plotting Spatial Data on Riyadh Map')
ax.set_xlim(BBox[0],BBox[1])
ax.set_ylim(BBox[2],BBox[3])

ax.imshow(ruh_m, zorder=0, extent = BBox, aspect= 'equal')