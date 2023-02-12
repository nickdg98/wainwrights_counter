import math

import pandas as pd
import polyline

class Summit:
    def __init__(self, lat: int, long: int, name: str) -> None:
        self.lat = lat
        self.long = long
        self.name = name
        
df = pd.read_csv('wainwrights.csv')
wainwrights = list(map(lambda x: Summit(name=x[1], lat=x[2], long=x[3]), df.values.tolist()))

def distance(c1, c2) -> float:
    # cx is of form (lat, long)
    c = math.pi/180
    og = 6371 * c * math.sqrt(abs(c1[0]-c2[0])**2 + abs(c1[1]-c2[1])**2)
    return og

def get_summits_on_polyline(code) -> list:
    # list of wainwright summits that a given polyline route had gone through
    distances = []
    closests = []
    summits = []
    if code:
        coords = polyline.decode(code)
        for coord in coords:
            closest = 50
            for summit in wainwrights:
                d = distance(coord, (summit.lat, summit.long))
                if d < 0.05 and summit.name not in summits:
                    summits.append(summit.name)
                closest = min(d,closest)
                distances.append(d)
            closests.append(closest)
    return summits
