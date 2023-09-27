import math

def haversine(pt1, pt2):
    lat1, lon1 = pt1
    lat2, lon2 = pt2
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    radius = 6371.0
    distance = radius * c
    
    return distance*1000

import numpy as np
coords = np.loadtxt('coords/ground_corners.txt',delimiter=',')[:,:2]

print(haversine(coords[0],coords[1]))
print(haversine(coords[1],coords[2]))
print(haversine(coords[2],coords[3]))
print(haversine(coords[3],coords[0]))