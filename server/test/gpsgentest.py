location1lat = 62.47218
location1long = 6.23619
location1speed = 20
location1time = 1482222882760.0
location2lat = 64.47218
location2long = 8.23619
location2speed = 20
location2time = 1482222883760.0

difference = []
difference2 = []

deltaLat = location2lat - location1lat
deltaLon = location2long - location1long
# remove this line if you don't have measured speed:
deltaSpeed =  location2speed - location1speed

# 4 points needs to be filled: 5
# 12.05.22.000 - 12.05.21.000 = 1 second
# step=elapec time / points to be filled + 1
step = 1 * 1000 / 4; # 1 second in millis 

t = location1time

while (t < location2time): 
  t+= step
  # t0_1 shall run from 0.0 to (nearly) 1.0 in that loop
  t0_1 = (t - location1time) / (location2time - location1time)
  latInter = location1lat + deltaLat  * t0_1
  lonInter = location1long + deltaLon  * t0_1
  # remove the line below if you dont have speed
  speedInter = location1speed + deltaSpeed  * t0_1
  #Location interPolLocation = new Location(latInter, lonInter, speedInter)
  print(latInter, lonInter, speedInter)
  # add interPolLocation to list or plot.
  


