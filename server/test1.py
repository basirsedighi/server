import haversine as hs
from haversine import Unit
import math




#distance = hs.haversine(loc1,loc2,unit=Unit.METERS)




# def getDistanceFromLatLonInKm(lat1,lon1,lat2,lon2):
#    dLat = deg2rad(lat2-lat1) 
#    dLon = deg2rad(lon2-lon1)
#    R = 6371 
#    a = math.sin(dLat/2) * math.sin(dLat/2) +math.cos(deg2rad(lat1)) * math.cos(deg2rad(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
    
#    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)); 
#    d = R * c # Distance in kmreturn d;

#    return d


# def deg2rad(deg):
#   return deg * (math.pi/180)


# dis = getDistanceFromLatLonInKm(lat1, lon1, lat2, lon2)

# print(dis*1000)


#markers
markers =[

(62.369605166666666,8.040499),
(62.4363605,	7.857269666666666),
(62.447173,	7.8369230000000005),
(62.463835833333334	,7.819622833333334),
(62.478904666666665,	7.767432333333334),
(62.53934783333333,	7.725357)

]

#ground truth
groundTruth=[
(62.369563166666666	, 8.0402965),
(62.436300333333335,	7.857232),
(62.44713333333333	,7.836808333333334),
(62.4637855,	7.819518),
(62.47882883333333	,7.767362833333333),
(62.53927,	7.725302666666667)



]
for truth,mark in zip(groundTruth,markers):
    distance = hs.haversine(truth,mark,unit=Unit.METERS)
    print(round(distance,2))
