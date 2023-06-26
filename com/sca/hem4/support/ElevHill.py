# -*- coding: utf-8 -*-
"""
Created on Thu May 11 13:43:54 2023

@author: SteveFudge

Computes elevation and hill height of a group of receptor using the USGS 3dep DEM data. This
module uses the p3dep Python library. py3dep is documented here: https://github.com/hyriver/py3dep

"""

import py3dep
import pandas as pd
import numpy as np
import time
from math import ceil
from numpy import sin, cos, arcsin, pi, sqrt, amax, full, arctan, tan, arctan2
from numba import jit
import gc


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
                batch_elev = py3dep.elevation_bycoords(batch, source='tnm')
                elevation_data.extend(batch_elev)
        else:
            batch_elev = py3dep.elevation_bycoords(coords, source='tnm')
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

    # Takes a single receptor coordinate and calculates the max elev that exceeds 10% slope
    @staticmethod
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
        
        """
        Get 90m grid of elevations and the radius to use for hill height capture
        Construct a geometric box centered on the facility center. The box has
        length and width that is 2*initial_radius. Use
        the box to get an xarray of 90m resolution elevation data.
        initial_radius is in km and is the max modeling distance plus 62km which is 10x
        the height of Dinali in km. This is the needed radius to capture Dinali as a
        hill height for any receptor. This is the starting distance.
        """
        initial_radius = max_model_dist + 62
        r_earth = 6371 # radius of earth in km
        lat2 = center_lat  + (initial_radius / r_earth) * (180 / pi)
        lon2 = center_lon + (initial_radius / r_earth) * (180 / pi) / cos(np.deg2rad(center_lat))
        lat1 = center_lat  - (initial_radius / r_earth) * (180 / pi)
        lon1 = center_lon - (initial_radius / r_earth) * (180 / pi) / cos(np.deg2rad(center_lat))
        geo_box = (lon1, lat1, lon2, lat2)
        elev_xarray = py3dep.get_dem(geo_box, 90, crs='epsg:4269')

        elev_df = elev_xarray.to_dataframe()
        # del elev_xarray
        elev_df.reset_index(inplace=True)
        elev_lat = elev_df['y'].to_numpy()
        elev_lon = elev_df['x'].to_numpy()
        elev_elev = elev_df['elevation'].to_numpy()
        elev_arr = np.column_stack((elev_lat, elev_lon, elev_elev))
        # del elev_df, elev_lat, elev_lon, elev_elev
        # gc.collect()

        # Use the max of the 90m grid elevations and the min receptor elevation
        # to compute the horizontal distance (km) needed for a 10% slope to get hill height.
        maxelev = elev_arr.max()
        maxelev_radius = ((maxelev - min_rec_elev) * 0.001 * 10) + 0.1
        
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
    
# start_time = time.time()

# #-------- Get elevations for receptor coordinates -----------------------------
# # receptor_file = r'C:\Git_HEM4\HEM4\census\Census2020_HEM_28Jun22.csv'
# receptor_file = r'C:\Temp\Hill height testing\Test coordinates\Outers_from_08013Western.csv'
# receptor_df = pd.read_csv(receptor_file)
# coords = [(lat, lon) for lat, lon in zip(receptor_df['Longitude'], receptor_df['Latitude'])]

# # Get elevations for batches of 100 receptors
# elevation_data = []
# batch_size = 100
# if len(coords) > 1:
#     for i in range(0, len(coords), batch_size):
#         batch = coords[i:i+batch_size]
#         batch_elev = py3dep.elevation_bycoords(batch, source='tnm')
#         elevation_data.extend(batch_elev)
# else:
#     batch_elev = py3dep.elevation_bycoords(coords, source='tnm')
#     elevation_data.append(batch_elev)
    
# receptor_df['new_elev'] = elevation_data
# print("Time to get new elevs ", time.time()-start_time)


# #-------- Get gridded elevation data for hill heights compuration -----------------

# # Define facility center
# fac_center = [receptor_df['Longitude'].mean(), receptor_df['Latitude'].mean()]

# # First use 90m elevations in large radius around center. The max 90m elevation
# # will be used to determine the required horizontal distance (radius)
# initial_radius = 50+62
# r_earth = 6371
# lat2 = fac_center[1]  + (initial_radius / r_earth) * (180 / pi)
# lon2 = fac_center[0] + (initial_radius / r_earth) * (180 / pi) / cos(np.deg2rad(fac_center[1]))
# lat1 = fac_center[1]  - (initial_radius / r_earth) * (180 / pi)
# lon1 = fac_center[0] - (initial_radius / r_earth) * (180 / pi) / cos(np.deg2rad(fac_center[1]))
# geo_box = (lon1, lat1, lon2, lat2)
# sample_xarray = py3dep.get_dem(geo_box, 90, crs='epsg:4269')

# # Use the min and max 90m elevation to compute horizontal distance (km) needed for a 10% slope
# maxelev = sample_xarray.max().values
# minelev = receptor_df['new_elev'].min()
# maxelev_radius = ((maxelev - minelev) * 0.001 * 10) + 0.1

# # Use the max 90m elev radius to define corners of geo box in which to get gridded 30m elevation data
# # for the entire domain.
# elev_radius = 50 + maxelev_radius
# lat2 = fac_center[1]  + (elev_radius / r_earth) * (180 / pi)
# lon2 = fac_center[0] + (elev_radius / r_earth) * (180 / pi) / cos(np.deg2rad(fac_center[1]))
# lat1 = fac_center[1]  - (elev_radius / r_earth) * (180 / pi)
# lon1 = fac_center[0] - (elev_radius / r_earth) * (180 / pi) / cos(np.deg2rad(fac_center[1]))
# geo_box = (lon1, lat1, lon2, lat2)

# # Get the 30m gridded elevation data
# res=90
# elev_xarray = py3dep.get_dem(geo_box, res, crs='epsg:4269')
# elev_df = elev_xarray.to_dataframe()
# del elev_xarray
# elev_df.reset_index(inplace=True)
# elev_lat = elev_df['y'].to_numpy()
# elev_lon = elev_df['x'].to_numpy()
# elev_elev = elev_df['elevation'].to_numpy()
# stacked = np.column_stack((elev_lat, elev_lon, elev_elev))
# del elev_df, elev_lat, elev_lon, elev_elev
# gc.collect()

# print("--- %s seconds to get gridded elevation data for hill heights ---" % (time.time() - start_time))

# #----------- Compute hill heights at the receptors --------------------

# receptor_df.dropna(subset=['Latitude', 'Longitude'])
# receptor_df.reset_index(inplace=True, drop=True)
# recdf_for_hills = receptor_df.loc[:, ['Latitude', 'Longitude', 'new_elev']]
# receptor_arr = recdf_for_hills.to_numpy()
# final_hill_arr = getHill(receptor_arr, stacked, maxelev_radius)
# receptor_df['newhill'] = final_hill_arr

# print("There are ", len(receptor_arr), " blocks to process")

# receptor_df.to_csv(f"C:\Temp/Hill height testing\Python results/Output_Elev_Hills_08013Western_vincenty_res{res}.csv")
# print("--- %s seconds to completely finish ---" % (time.time() - start_time))

