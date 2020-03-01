# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 09:51:23 2020

@author: MMORRIS
"""

# Find the nearest meteorology station

import numpy as np
import pandas as pd
from geopy.distance import lonlat, distance

def find_met(ylat, xlon):
    with open("resources//metlib_aermod.xlsx", "rb") as metfile:
        met_st = pd.read_excel(metfile
                      , names=('surfcity','surffile','surfwban','surfyear','surflat',
                         'surflon','uacity','uawban','ualat','ualon','elev','anemhgt','commkey',
                         'comment','desc','upperfile'))
            
    # create numpy arrays
    lat = met_st['surflat'].values
    lon = met_st['surflon'].values    
    
    dist = np.ones(len(lat))
    
    facility = (xlon, ylat)
    for i in np.arange(len(lon)):
        station = (lon[i], lat[i])
        dist[i] = distance(lonlat(*facility), lonlat(*station)).meters
    
    index = np.where(dist==dist.min())[0][0]

    distance2fac = dist[index]
    surf_file = met_st['surffile'][index]
    upper_file = met_st['upperfile'][index]
    # Note: remove white space from surfcity and uacity, Aermod will not allow spaces in the city name
    surfdata_str = str(met_st['surfwban'][index]) + " " + str(met_st['surfyear'][index]) + " " + str(met_st['surfcity'][index]).replace(" ","")
    uairdata_str = str(met_st['uawban'][index]) + " " + str(met_st['surfyear'][index]) + " " + str(met_st['uacity'][index]).replace(" ","")
    prof_base = str(met_st['elev'][index])
    
    return surf_file, upper_file, surfdata_str, uairdata_str, prof_base, distance2fac