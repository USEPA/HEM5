# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 12:57:56 2017

@author: sfudge
"""

import math
import numpy as np
import pandas as pd

#import pandas as pd
#import warnings
#warnings.simplefilter("error", pd.core.common.SettingWithCopyWarning)
from support.UTM import UTM


def center(sourcelocs, utmz):
      
    # Fill up lists of x and y coordinates of all source vertices    
    vertx_l = []
    verty_l = []
    for index, row in sourcelocs.iterrows():
        
        vertx_l.append(row["utme"])
        verty_l.append(row["utmn"])
        
        # If this is an area source, add the other 3 corners to vertex list
        if row["source_type"].upper() == "A":
            angle_rad = math.radians(row["angle"])
            utme1 = row["utme"] + row["lengthx"] * math.cos(angle_rad)
            utmn1 = row["utmn"] - row["lengthx"] * math.sin(angle_rad)
            utme2 = (row["utme"] + (row["lengthx"] * math.cos(angle_rad)) +
                    (row["lengthy"] * math.sin(angle_rad)))
            utmn2 = (row["utmn"] + (row["lengthy"] * math.cos(angle_rad)) -
                     (row["lengthx"] * math.sin(angle_rad)))
            utme3 = row["utme"] + row["lengthy"] * math.sin(angle_rad)
            utmn3 = row["utmn"] + row["lengthy"] * math.cos(angle_rad)
            vertx_l.append(utme1)
            vertx_l.append(utme2)
            vertx_l.append(utme3)
            verty_l.append(utmn1)
            verty_l.append(utmn2)
            verty_l.append(utmn3)
            
        # If this is a volume source, then add the vertices of it
        if row["source_type"].upper() == "V":
            utme1 = row["utme"] + row["lengthx"] * math.sqrt(2)/2
            utmn1 = row["utmn"] - row["lengthy"] * math.sqrt(2)/2
            utme2 = row["utme"] + row["lengthx"] * math.sqrt(2)/2
            utmn2 = row["utmn"] + row["lengthy"] * math.sqrt(2)/2
            utme3 = row["utme"] - row["lengthx"] * math.sqrt(2)/2
            utmn3 = row["utmn"] + row["lengthy"] * math.sqrt(2)/2
            vertx_l.append(utme1)
            vertx_l.append(utme2)
            vertx_l.append(utme3)
            verty_l.append(utmn1)
            verty_l.append(utmn2)
            verty_l.append(utmn3)
    
        # If line or buoyant line source, add second vertex
        if row["source_type"].upper() == "N" or row["source_type"].upper() == "B":
            vertx_l.append(row["utme_x2"])
            verty_l.append(row["utmn_y2"])
            
#            if row["location_type"].upper() == "L":
#                utme2, utmn2, utmz = ll2utm.ll2utm(row["y2"], row["x2"],0,0)
#            else:
#                utme2 = row["lon"]
#                utmn2 = row["lat"]
#            vertx_l.append(utme2)
#            verty_l.append(utmn2)
#        
        # If a polygon source, read the polygon vertex file
        
    # Find the two vertices that are the farthest apart
    # Also find the corners of the modeling domain
    
    vertx_a = np.unique(np.array(vertx_l))
    verty_a = np.unique(np.array(verty_l))
   
    max_dist = 0
    max_x = min_x = vertx_a[0]
    max_y = min_y = verty_a[0]
    
    if len(vertx_a) > 1: #more than one source
        for i in range(0, len(vertx_a)-1):
            for j in range(0, len(verty_a)-1):
                dist = (vertx_a[i] - vertx_a[i+1])**2 + (verty_a[j] - verty_a[j+1])**2
                if dist > max_dist:
                    max_x = max(max_x,vertx_a[i+1])
                    max_y = max(max_y,verty_a[i+1])
                    min_x = min(min_x,vertx_a[i+1])
                    min_y = min(min_y,verty_a[i+1])
                    max_dist = math.sqrt(dist)
                    xmax1 = vertx_a[i]
                    ymax1 = verty_a[i]
                    xmax2 = vertx_a[i+1]
                    ymax2 = verty_a[i+1]
    
        # Calculate the center of the facility in utm coordinates
        cenx = (xmax1 + xmax2) / 2
        ceny = (ymax1 + ymax2) / 2
    
        # Compute the lat/lon of the center
        sceny = pd.Series([ceny])
        scenx = pd.Series([cenx])
        sutmz = pd.Series([utmz])
        acenlat, acenlon = UTM.utm2ll(sceny, scenx, sutmz)
    
        cenlon = acenlon[0]
        cenlat = acenlat[0]
        
    else: #single source
        
       # Calculate the center of the facility in utm coordinates
        cenx = max_x
        ceny = max_y
    
        # Compute the lat/lon of the center
        sceny = pd.Series([ceny])
        scenx = pd.Series([cenx])
        sutmz = pd.Series([utmz])
        acenlat, acenlon = UTM.utm2ll(sceny, scenx, sutmz)
    
        cenlon = acenlon[0]
        cenlat = acenlat[0]    
    
    return cenx, ceny, cenlon, cenlat, max_dist, vertx_a, verty_a