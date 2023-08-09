# -*- coding: utf-8 -*-
"""
Created on Thu May 11 13:43:54 2023

@author: SteveFudge

Computes elevation and hill height of a group of receptor using the USGS 3dep DEM data. This
module uses the p3dep Python library. py3dep is documented here: https://github.com/hyriver/py3dep

"""

import py3dep
import numpy as np
import pandas as pd
from numpy import sin, cos, arcsin, pi, sqrt, amax
from numba import jit
import gc
from com.sca.hem4.log.Logger import Logger
import traceback
from tkinter import messagebox
import time


class ElevHill:
    """
    A utility class with functions for acquiring elevations and computing hill
    heights.
    """
    
    @staticmethod
    def getElev(coords):
        """
        Using USGS 10m resolution DEM data, get elevations for a list of coordinates
        where the coordinates are a list of tuples organized as (longitude, latitude).
        """
        # Get elevations for batches of 100 coordinates
        elevation_data = []
        batch_size = 100
        if len(coords) > 1:
            for i in range(0, len(coords), batch_size):
                batch = coords[i:i+batch_size]
                
                try:
                    batch_elev = py3dep.elevation_bycoords(batch, source='tep')
                except BaseException as e:
                    messagebox.showinfo("Cannot access USGS server", "Your computer was unable to connect to the USGS server to obtain elevation data." \
                                        " This HEM run will stop. Please check your Internet connection and restart this run." \
                                        " (If an Internet connection is not available, you can model without elevations.)" \
                                        " More detail about this error is available in the log.")
                    fullStackInfo = traceback.format_exc()
                    Logger.logMessage("Cannot access the USGS server needed by the py3dep elevation_bycoords function.\n" \
                                      " Aborting this HEM run.\n" \
                                      " Detailed error message: \n\n" + fullStackInfo)                        
                    raise ValueError("USGS elevation server unavailable")
                else:
                    elevation_data.extend(batch_elev)
        else:
            try:
                batch_elev = py3dep.elevation_bycoords(coords, source='tnm')
            except BaseException as e:
                messagebox.showinfo("Cannot access USGS server", "Your computer was unable to connect to the USGS server to obtain elevation data." \
                                    " This HEM run will stop. Please check your Internet connection and restart this run." \
                                    " (If an Internet connection is not available, you can model without elevations.)" \
                                    " More detail about this error is available in the log.")
                fullStackInfo = traceback.format_exc()
                Logger.logMessage("Cannot access the USGS server needed by the py3dep elevation_bycoords function.\n" \
                                  " Aborting this HEM run.\n" \
                                  " Detailed error message: \n\n" + fullStackInfo)                
                raise ValueError("USGS elevation server unavailable")
            else:
                elevation_data.append(batch_elev)

        elev_rounded = [round(e) for e in elevation_data]
        
        return elev_rounded
        
        
    # Takes a single receptor coordinate and calculates the max elev that exceeds 10% slope
    @staticmethod
    @jit(nopython=True, parallel=True)
    def getMax(rec_lat, rec_lon, rec_elev, elev_lat, elev_lon, elev_elev):
        hill = 0
        dist = (2 * arcsin(sqrt(sin(pi/180*(elev_lat-rec_lat)/2)**2 + 
                cos(pi/180*(rec_lat)) * cos(pi/180*(elev_lat)) * 
                sin(pi/180*(elev_lon-rec_lon)/2)**2)) * 6371000)
        IT = (elev_elev - rec_elev) - dist * 0.1
        mystack = np.column_stack((IT,elev_elev))
        mask = mystack[:, 0] >= 0
        temp = mystack[mask,:]
        if temp.size > 0:
            hill = round(amax(temp[:,1]))
        return hill
    
    @staticmethod
    def split_box(lower_left, upper_right, threshold_size):
        """
        Recursively split the bounding box into smaller boxes until the size is less than the threshold,
        maintaining the aspect ratio.
        :param lower_left: Tuple (latitude, longitude) representing the lower left corner of the bounding box.
        :param upper_right: Tuple (latitude, longitude) representing the upper right corner of the bounding box.
        :param threshold_size: The maximum area for a bounding box.
        :return: A list of tuples, where each tuple contains the lower left and upper right coordinates of a smaller box.
        """
        boxes = []
        stack = [(lower_left, upper_right)]

        while stack:
            lower_left, upper_right = stack.pop()

            width = upper_right[1] - lower_left[1]
            height = upper_right[0] - lower_left[0]
            aspect_ratio = width / height

            # Check if the box size is less than the threshold
            if width * height <= threshold_size:
                boxes.append((lower_left, upper_right))
            else:
                mid_latitude = (lower_left[0] + upper_right[0]) / 2
                mid_longitude = (lower_left[1] + upper_right[1]) / 2

                # Split the box into two halves along the longer side while maintaining aspect ratio
                if aspect_ratio > 1:
                    split_point1 = (lower_left[0], mid_longitude)
                    split_point2 = (upper_right[0], mid_longitude)
                else:
                    split_point1 = (mid_latitude, lower_left[1])
                    split_point2 = (mid_latitude, upper_right[1])

                # Add the two smaller boxes to the stack for further splitting
                stack.append((lower_left, split_point2))
                stack.append((split_point1, upper_right))

        return boxes

    # Takes a receptor coordinate array and returns an array of calculated hill height scales
    @staticmethod
    def getHill(rec_arr, max_model_dist, center_lon, center_lat, min_rec_elev):
        """
        Parameters
        ----------
        rec_arr : 3-dimensional array
            Array of receptor coordinates and their elevation organized as
            (lat,lon,elev).
        max_model_dist : Float
            Maximum HEM modeling distance in km (usually 50km)
        center_lon : Float
            Longitude of center of the receptors.
        center_lat : Float
            Latitude of center of the receptors.
        min_rec_elev : Float
            Minimum elevation of the receptors

        Returns
        -------
        hill_arr : 1-dim array
            Hill heights (m) of each input receptor.
        """
        
        # Query the 30m DEM server for all elevations within a geo box where the radius is
        # based on the max HEM modeling distance plus 62km to potentially account dor Denali
        # at a 10% slope.
        initial_radius = max_model_dist + 62
        r_earth = 6371 # radius of earth in km
        lat2 = center_lat  + (initial_radius / r_earth) * (180 / pi)
        lon2 = center_lon + (initial_radius / r_earth) * (180 / pi) / cos(np.deg2rad(center_lat))
        lat1 = center_lat  - (initial_radius / r_earth) * (180 / pi)
        lon1 = center_lon - (initial_radius / r_earth) * (180 / pi) / cos(np.deg2rad(center_lat))
        geo_box = (lon1, lat1, lon2, lat2)
        
        try:
            xarray = py3dep.get_dem(geo_box, 30, crs='epsg:4269')
            elev_df = xarray.to_dataframe()
        except BaseException as e:
            messagebox.showinfo("Cannot access 30m USGS server", "Your computer was unable to connect to the USGS server to obtain elevation data." \
                                " This HEM run will stop. Please check your Internet connection and restart this run." \
                                " (If an Internet connection is not available, you can model without elevations.)" \
                                " More detail about this error is available in the log.")
            fullStackInfo = traceback.format_exc()
            Logger.logMessage("Cannot access the 30m USGS server needed by the py3dep get_dem function.\n" \
                              " Aborting this HEM run.\n" \
                              " Detailed error message: \n\n" + fullStackInfo)                
            raise ValueError("USGS elevation server unavailable")

        # Use the max of the 90m grid elevations and the min receptor elevation
        # to compute the horizontal distance (km) needed for a 10% slope to get hill height.
        maxelev = xarray.max().values
        minelev = np.max(rec_arr[:, 2])
        maxelev_radius = ((maxelev - minelev) * 0.001 * 10) + 0.1
                            
        elev_df.reset_index(inplace=True)
        elev_lat = elev_df['y'].to_numpy()
        elev_lon = elev_df['x'].to_numpy()
        elev_elev = elev_df['elevation'].to_numpy()
        elev_arr = np.column_stack((elev_lat, elev_lon, elev_elev))
        del elev_df, elev_lat, elev_lon, elev_elev
        gc.collect()
        
        # Process each receptor        
        hill_arr = np.empty((rec_arr.shape[0],))  # Create an empty NumPy array
        for i in range(rec_arr.shape[0]):
            row = rec_arr[i]
            lat = row[0]
            lon = row[1]
            elev = row[2]
            
            # Limit elevation data near the receptor of interest (km)
            lat2 = lat  + (maxelev_radius / r_earth) * (180 / pi)
            lon2 = lon + (maxelev_radius / r_earth) * (180 / pi) / cos(np.deg2rad(lat))
            lat1 = lat  - (maxelev_radius / r_earth) * (180 / pi)
            lon1 = lon - (maxelev_radius / r_earth) * (180 / pi) / cos(np.deg2rad(lat))
            latcon = ((elev_arr[:, 0] >= lat1) &  (elev_arr[:, 0] <= lat2))
            loncon = ((elev_arr[:, 1] >= lon1) &  (elev_arr[:, 1] <= lon2))
            elevcon = (elev_arr[:, 2] > elev)
            elev_filter = elev_arr[latcon & loncon & elevcon]
            elev_lat = elev_filter[:,0]
            elev_lon = elev_filter[:,1]
            elev_elev = elev_filter[:,2]
            
            rec_elev = np.full((elev_elev.size,), elev)
            rec_lat = np.full((elev_lat.size,), lat)
            rec_lon = np.full((elev_lon.size,), lon)
            Hillht = ElevHill.getMax(rec_lat, rec_lon, rec_elev, elev_lat, elev_lon, elev_elev)
            hill_arr[i] = max(Hillht, elev)
            
        return hill_arr


