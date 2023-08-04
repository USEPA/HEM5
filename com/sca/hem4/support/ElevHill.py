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
        
    
    # @staticmethod
    # def getElevGrid(max_model_dist, center_lon, center_lat, min_rec_elev):
    #     """

    #     Parameters
    #     ----------
    #     max_model_dist: Float
    #         Maximum modeling distance of this facility
    #     center_lon : Float
    #         Longitude of center of the receptors.
    #     center_lat : Float
    #         Latitude of center of the receptors.
    #     min_rec_elev : Float
    #         Minimum elevation of the receptors

    #     Returns
    #     -------
    #     elev_xarray : xarray
    #         Grid of 90m resolution elevations around the center coordinate.
    #     radius_to_use : Float
    #         Horizontal distance (km) to use from the receptor distance to capture hill heights.

    #     """

    #     # Construct a geometric box centered on the facility center. The box has
    #     # length and width that is 2*initial_radius. Use
    #     # the box to get an xarray of 90m resolution elevation data.
    #     # initial_radius is in km and is the max modeling distance plus 62km which is 10x
    #     # the height of Dinali in km. This is the needed radius to capture Dinali as a
    #     # hill height for any receptor. This is the starting distance.
    #     initial_radius = max_model_dist + 62
    #     r_earth = 6371 # radius of earth in km
    #     lat2 = fac_center[1]  + (initial_radius / r_earth) * (180 / pi)
    #     lon2 = fac_center[0] + (initial_radius / r_earth) * (180 / pi) / cos(np.deg2rad(fac_center[1]))
    #     lat1 = fac_center[1]  - (initial_radius / r_earth) * (180 / pi)
    #     lon1 = fac_center[0] - (initial_radius / r_earth) * (180 / pi) / cos(np.deg2rad(fac_center[1]))
    #     geo_box = (lon1, lat1, lon2, lat2)
    #     elev_xarray = py3dep.get_dem(geo_box, 90, crs='epsg:4269')

    #     # Use the max of the 90m grid elevations and the min receptor elevation
    #     # to compute the horizontal distance (km) needed for a 10% slope to get hill height.
    #     maxelev = elev_xarray.max().values
    #     radius_to_use = ((maxelev - min_rec_elev) * 0.001 * 10) + 0.1
        
    #     return elev_xarray, radius_to_use

    def getMax_wrapper(self, rec_lat, rec_lon, rec_elev, elev_lat, elev_lon, elev_elev):
        return self.getMax(rec_lat, rec_lon, rec_elev, elev_lat, elev_lon, elev_elev)
    
    
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
        
        # First, use the initial_radius to get 90m elevations around center. The max 90m elevation
        # will be used to determine the required horizontal distance (radius)
        initial_radius = max_model_dist + 62
        r_earth = 6371 # radius of earth in km
        lat2 = center_lat  + (initial_radius / r_earth) * (180 / pi)
        lon2 = center_lon + (initial_radius / r_earth) * (180 / pi) / cos(np.deg2rad(center_lat))
        lat1 = center_lat  - (initial_radius / r_earth) * (180 / pi)
        lon1 = center_lon - (initial_radius / r_earth) * (180 / pi) / cos(np.deg2rad(center_lat))
                
        # Split the overall bounding box into multiple boxes, get data for each box, and concatenate
        lower_left = (lat1, lon1)  # Latitude, Longitude of lower left corner
        upper_right = (lat2, lon2)  # Latitude, Longitude of upper right corner
        threshold_size = .2  # In square degrees, adjust as needed
        split_boxes = ElevHill.split_box(lower_left, upper_right, threshold_size)
        
        box_dfs_90 = []
        elev_df = pd.DataFrame()
        for box in split_boxes:
            geo_box_i = (box[0][1], box[0][0], box[1][1], box[1][0])
            try:
                sample_xarray = py3dep.get_dem(geo_box_i, 90, crs='epsg:4269')
                tempdf = sample_xarray.to_dataframe()
                box_dfs_90.append(tempdf)
                del sample_xarray
            except BaseException as e:
                messagebox.showinfo("Cannot access USGS server", "Your computer was unable to connect to the USGS server to obtain elevation data." \
                                    " This HEM run will stop. Please check your Internet connection and restart this run." \
                                    " (If an Internet connection is not available, you can model without elevations.)" \
                                    " More detail about this error is available in the log.")
                fullStackInfo = traceback.format_exc()
                Logger.logMessage("Cannot access the 90m USGS server needed by the py3dep get_dem function.\n" \
                                  " Aborting this HEM run.\n" \
                                  " Detailed error message: \n\n" + fullStackInfo)                
                raise ValueError("USGS elevation server unavailable")
                            
        elev_df = pd.concat(box_dfs_90, axis=0)
                

        # Use the max of the 90m grid elevations and the min receptor elevation
        # to compute the horizontal distance (km) needed for a 10% slope to get hill height.
        maxelev = elev_df['elevation'].max()
        minelev = np.max(rec_arr[:, 2])
        maxelev_radius = ((maxelev - minelev) * 0.001 * 10) + 0.1

        # Use the max 90m elev radius to define corners of geo box in which to get 
        # gridded 30m elevation data for the entire domain (more refined radius).
        elev_radius = max_model_dist + maxelev_radius
        lat2 = center_lat  + (elev_radius / r_earth) * (180 / pi)
        lon2 = center_lon + (elev_radius / r_earth) * (180 / pi) / cos(np.deg2rad(center_lat))
        lat1 = center_lat  - (elev_radius / r_earth) * (180 / pi)
        lon1 = center_lon - (elev_radius / r_earth) * (180 / pi) / cos(np.deg2rad(center_lat))
                
        # Split the overall bounding box into multiple boxes, get data for each box, and concatenate
        lower_left = (lat1, lon1)  # Latitude, Longitude of lower left corner
        upper_right = (lat2, lon2)  # Latitude, Longitude of upper right corner
        threshold_size = .2  # In square degrees, adjust as needed
        split_boxes = ElevHill.split_box(lower_left, upper_right, threshold_size)

        # Get the 30m gridded elevation data
        box_dfs_30 = []
        elev_df = pd.DataFrame()
        for box in split_boxes:
            geo_box_i = (box[0][1], box[0][0], box[1][1], box[1][0])
            try:
                sample_xarray = py3dep.get_dem(geo_box_i, 30, crs='epsg:4269')
                tempdf = sample_xarray.to_dataframe()
                box_dfs_30.append(tempdf)
                del sample_xarray
            except BaseException as e:
                messagebox.showinfo("Cannot access USGS server", "Your computer was unable to connect to the USGS server to obtain elevation data." \
                                    " This HEM run will stop. Please check your Internet connection and restart this run." \
                                    " (If an Internet connection is not available, you can model without elevations.)" \
                                    " More detail about this error is available in the log.")
                fullStackInfo = traceback.format_exc()
                Logger.logMessage("Cannot access the 30m USGS server needed by the py3dep get_dem function.\n" \
                                  " Aborting this HEM run.\n" \
                                  " Detailed error message: \n\n" + fullStackInfo)                
                raise ValueError("USGS elevation server unavailable")
                            
        elev_df = pd.concat(box_dfs_30, axis=0)
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


