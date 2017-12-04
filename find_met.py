# -*- coding: utf-8 -*-
"""
Created on Thu Jun  8 14:28:29 2017

@author: jbaker
"""

# Find the nearest meteorology station

import numpy as np
import pandas as pd
from math import cos, radians

def find_met(ylat, xlon):

    met_st = pd.read_excel(open("resources/metlib_aermod.xlsx", "rb")
                  , names=('surfcity','surffile','surfwban','surfyear','surflat',
                     'surflon','uacity','uawban','ualat','ualon','elev','anemhgt','commkey',
                     'comment','desc','usdist2fac','surfdist2f','upperfile'))
       
    
    # Incorporating census block center; if I remember correctly, there is only one census block passed each time
    # if len(lat) == 1:
#        lat = census block center (and then extract that value)
#        lon = census block center (and then extract that value)
#    else:
    
    # create numpy arrays
    lat = met_st['surflat'].values
    lon = met_st['surflon'].values    
    
    dist = np.ones(len(lat))
    
    for i in np.arange(len(lon)):
         dist[i] = np.sqrt((ylat-lat[i])**2+((xlon+lon[i])*cos(radians(ylat)))**2)*60*2*3*12/39.37
    index = np.where(dist==dist.min())[0][0]

    surf_file = met_st['surffile'][index]
    upper_file = met_st['upperfile'][index]
    surfdata_str = str(met_st['surfwban'][index]) + " " + str(met_st['surfyear'][index]) + " " + str(met_st['surfcity'][index])
    uairdata_str = str(met_st['uawban'][index]) + " " + str(met_st['surfyear'][index]) + " " + str(met_st['uacity'][index])
    prof_base = str(met_st['elev'][index])
        
    return surf_file, upper_file, surfdata_str, uairdata_str, prof_base