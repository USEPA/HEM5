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
from itertools import product
import polars as pl

import requests
from rasterio.io import MemoryFile
import multiprocessing

from scipy.interpolate import griddata
from scipy.spatial import KDTree

import socket
from datetime import datetime
import requests
import glob, os

import time
import concurrent.futures
import threading


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

        # Confirm that an Internet connection is available. If there is not, then keep
        # checking every minute indefinitely. Report progress to the log.
        gotInternet = ElevHill.isInternet()
        if gotInternet == False:
            while not gotInternet:
                currtime = datetime.now().strftime("%H:%M:%S")
                message = "No Internet connection to retrieve elevations. Will try again in 1 minute. \n" \
                          + "Click Exit to stop this loop. \n" \
                          + "Current time is: " + currtime + "\n"
                Logger.logMessage(message)
                time.sleep(60)
                gotInternet = ElevHill.isInternet()
            Logger.logMessage("Internet connection has returned. Will retrieve elevations.\n")
 
        outer_loop_condition = True
        while outer_loop_condition:

            # Get elevations for batches of 100 coordinates
            intloop = False
            elevation_data = []
            batch_size = 100
            for i in range(0, len(coords), batch_size):
                batch = coords[i:i+batch_size]
                
                try:
                    # first try to use 10m elevation data
                    batch_elev = py3dep.elevation_bycoords(batch, source='tep')
                except BaseException as e:
                    # tep did not work. Now try tnm.
                    try:
                        batch_elev = py3dep.elevation_bycoords(batch, source='tnm')
                    except BaseException as e:
                        # tnm failed too. See if there is Internet.
                        gotInternet = ElevHill.isInternet()
                        if gotInternet == False:
                            # No Internet. Keep checking until there is.
                            while not gotInternet:
                                gotInternet = ElevHill.isInternet()
                                if gotInternet == False:
                                    currtime = datetime.now().strftime("%H:%M:%S")
                                    message = "No Internet connection to retrieve elevations. Will try again in 1 minute. \n" \
                                              + "Click Exit to stop this loop. \n" \
                                              + "Current time is: " + currtime + "\n"
                                    Logger.logMessage(message)
                                    time.sleep(60)
                            # Internet has returned. Clear cache, break for loop, and start over.
                            Logger.logMessage("Internet connection has returned. Will retrieve elevations.\n")
                            intloop = True
                            files = glob.glob('./cache/*')
                            for f in files:
                                os.remove(f) 
                            break
                        else:
                            # There is Internet, the py3dep server must be down.
                            raise ValueError("USGS elevation server unavailable")
                else:
                    # make sure all elevs are not -999999. That means elevs not available.
                    if len(coords) > 1:
                        if all(x == -999999 for x in batch_elev):
                            raise ValueError("USGS elevation data not available")
                        else:
                            elevation_data.extend(batch_elev)
                    else:
                        if batch_elev == -999999:
                            raise ValueError("USGS elevation data not available")
                        else:
                            elevation_data.append(batch_elev)
            
            if intloop == False:
                outer_loop_condition = False  # successfully got elevations

        elev_rounded = [round(e) for e in elevation_data]
        
        # Replace any -99999 elecations with 0. These are over water.
        elev_rounded_positive = [0 if i == -999999 else i for i in elev_rounded]
        
        return elev_rounded_positive
        
        
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
    
    
    # Takes a usgs url, gets a tif file, and creates and returns a dataframe of lat, lon, and elevations
    @staticmethod
    def getTIF(filenum, stop_event, url, max_model_dist, center_lon, center_lat, min_rec_elev):

        if stop_event.is_set():
            # Stop this thread
             return
                        
        # Make a GET request to download the TIFF file              
        try:
                            
            response = requests.get(url, timeout=8)
                        
        except requests.exceptions.ConnectionError as e:
            
            # Signal that a failure occurred
            stop_event.set()

            gotInternet = ElevHill.isInternet()
            if gotInternet == False:
                raise ValueError("No Internet")
            else:
                # There is Internet, the py3dep server must be down.
                raise ValueError("USGS elevation server unavailable")

        # Has the calling program stopped all threads?
        if stop_event.is_set():
            return
            
        # Read the TIFF file into memory
        with MemoryFile(response.content) as memfile:
            with memfile.open() as dataset:
                # Read the elevation data
                elevation_data = dataset.read(1)
                
                # Create arrays for latitude and longitude
                latitudes, longitudes = np.meshgrid(
                    np.array([dataset.xy(row, 0)[1] for row in range(dataset.height)]),
                    np.array([dataset.xy(0, col)[0] for col in range(dataset.width)]),
                    indexing='ij'
                )

                # Convert the elevation data and coordinates to a DataFrame
                data = {
                    'latitude': latitudes.flatten(),
                    'longitude': longitudes.flatten(),
                    'elevation': elevation_data.flatten()
                }
                df = pd.DataFrame(data)
                df.dropna(inplace=True)
                
                # Compute a hill height horizontal distance (run) using the max elev 
                # in this Tiff and the minimum receptor elevation. Add 50km to this distance
                # to compute a hill height radius for this Tiff. Construct a lat/lon box
                # from this radius and filter the Tiff based on the box. This will potentially
                # remove Tiffs that are too far away or do not contain any elevations that meet
                # the requirement of being a hill height.
                r_earth = 6371 # radius of earth in km
                maxelev = df['elevation'].max()
                maxelev_radius = 50 + ((maxelev - min_rec_elev) * 0.001 * 10)                
                lat2 = center_lat  + (maxelev_radius / r_earth) * (180 / pi)
                lon2 = center_lon + (maxelev_radius / r_earth) * (180 / pi) / cos(np.deg2rad(center_lat))
                lat1 = center_lat  - (maxelev_radius / r_earth) * (180 / pi)
                lon1 = center_lon - (maxelev_radius / r_earth) * (180 / pi) / cos(np.deg2rad(center_lat))
                df2 = df.loc[df['latitude'].between(lat1, lat2) & df['longitude'].between(lon1, lon2)].copy()
                                
                return df
                                
        

    # Takes a receptor coordinate array and returns an array of calculated hill height scales
    @staticmethod
    def getHill(rec_arr, max_model_dist, center_lon, center_lat, model):
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
        model : Class
            Model class used to hold 30m elevation dataframe for this facility

        Returns
        -------
        hill_arr : 1-dim array
            Hill heights (m) of each input receptor.
        """
 
        # Confirm that an Internet connection is available. If there is not, then keep
        # checking every minute indefinitely. Report progress to the log.
        gotInternet = False
        while not gotInternet:
            gotInternet = ElevHill.isInternet()
            if gotInternet == False:
                currtime = datetime.now().strftime("%H:%M:%S")
                message = "No Internet connection to retrieve elevations. Will try again in 1 minute. \n" \
                          + "Click Exit to stop this loop. \n" \
                          + "Current time is: " + currtime + "\n"
                Logger.logMessage(message)
                time.sleep(60)


        # Query the 30m DEM server for all elevations within a geo box where the radius is
        # based on the max HEM modeling distance plus 62km to potentially account for Denali
        # at a 10% slope.
        initial_radius = max_model_dist + 62
        r_earth = 6371 # radius of earth in km
        lat2 = center_lat  + (initial_radius / r_earth) * (180 / pi)
        lon2 = center_lon + (initial_radius / r_earth) * (180 / pi) / cos(np.deg2rad(center_lat))
        lat1 = center_lat  - (initial_radius / r_earth) * (180 / pi)
        lon1 = center_lon - (initial_radius / r_earth) * (180 / pi) / cos(np.deg2rad(center_lat))
        geo_box = (lon1, lat1, lon2, lat2)

        # Determine the minimum receptor elevation
        min_rec_elev = np.min(rec_arr[:, 2])
        
               
        try:                
            # ---------- Use TIF files ----------------------------------
                            
            # Use the overall bounding box to determine which 1-degree tifs to request
            lats = np.arange(np.ceil(lat1), np.ceil(lat2) + 1).tolist()
            lons = np.arange(np.floor(lon1), np.ceil(lon2)).tolist()
            lats = [str(int(num)) for num in lats]
            lons = [f'{abs(int(num)):03}' for num in lons]
            urls = [] 
            
            # Generate the urls needed to request tifs
            for y in lats:
                for x in lons:
                    url = f'https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1/TIFF/current/n{y}w{x}/USGS_1_n{y}w{x}.tif'
                    urls.append(url)
            
            # Generate the arguments for the threads
            max_mod_dist_list = [max_model_dist] * len(urls)
            cenlon_list = [center_lon] * len(urls)
            cenlat_list = [center_lat] * len(urls)
            min_rec_elev_list = [min_rec_elev] * len(urls)
                           
            # Use ThreadPoolExecutor to multithread the function
            workers = multiprocessing.cpu_count()
            elevframes = []

            #------ New way of calling getTIF ----------------
            # Create an event used to stop running tasks
            event = threading.Event()
            elevframes = ElevHill.run_executor(event, ElevHill.getTIF, workers, urls, max_mod_dist_list, cenlon_list, cenlat_list, min_rec_elev_list)
                    
            grid30_df = pd.concat(elevframes)

            
            # # Original code for calling getTIF
            # with ThreadPoolExecutor(max_workers=workers) as executor:
            #     for df in executor.map(ElevHill.getTIF, urls, max_mod_dist_list, cenlon_list, cenlat_list, min_rec_elev_list):
            #         if df is not None and not df.empty:
            #             elevframes.append(df)
            #     grid30_df = pd.concat(elevframes)

                
        except BaseException as e:

            message = "Unable to get TIFF files from the USGS that are needed to compute hill heights.\n" \
                      + "Will attempt to get elevations from the USGS API. This will be a slower process. \n" 
            Logger.logMessage(message)
            
            outer_loop_condition = True
            while outer_loop_condition:

                try:
                    #-------------- Use py3dep method ---------------------------
                                            
                    xarray = py3dep.get_dem(geo_box, 30, crs='epsg:4269')
                    grid30_df = xarray.to_dataframe()
                    grid30_df.reset_index(inplace=True)
                    grid30_df.rename(columns={'x':'longitude', 'y':'latitude'}, inplace=True)
                    outer_loop_condition = False  # Success
                    
                except BaseException as e:

                    gotInternet = ElevHill.isInternet()
                    if gotInternet == False:
                        # No Internet. Keep checking until there is.
                        while not gotInternet:
                            gotInternet = ElevHill.isInternet()
                            if gotInternet == False:
                                currtime = datetime.now().strftime("%H:%M:%S")
                                message = "No Internet connection to retrieve elevations. Will try again in 1 minute. \n" \
                                          + "Click Exit to stop this loop. \n" \
                                          + "Current time is: " + currtime + "\n"
                                Logger.logMessage(message)
                                time.sleep(60)
                        # Internet has returned. Start over.
                        Logger.logMessage("Internet connection has returned. Will retrieve elevations.\n")
                        outer_loop_condition = True
                    else:
                        # There is Internet, the py3dep server must be down.
                        raise ValueError("USGS elevation server unavailable")
    
                
                 
        # Create a numpy elevation array from the 30m dataframe
        grid30_lat = grid30_df['latitude'].to_numpy()
        grid30_lon = grid30_df['longitude'].to_numpy()
        grid30_elev = grid30_df['elevation'].to_numpy()
        grid30_arr = np.column_stack((grid30_lat, grid30_lon, grid30_elev))
                        
        # Use the max of the 30m grid elevations and the min receptor elevation
        # to compute the horizontal distance (km) needed for a 10% slope to get hill height.
        maxelev = np.nanmax(grid30_elev)
        maxelev_radius = ((maxelev - min_rec_elev) * 0.001 * 10)

        # clean up
        del grid30_lat, grid30_lon, grid30_elev
        gc.collect()

        # Now shrink the elev array using a real radius
        real_radius = max_model_dist + maxelev_radius
        lat2 = center_lat  + (real_radius / r_earth) * (180 / pi)
        lon2 = center_lon + (real_radius / r_earth) * (180 / pi) / cos(np.deg2rad(center_lat))
        lat1 = center_lat  - (real_radius / r_earth) * (180 / pi)
        lon1 = center_lon - (real_radius / r_earth) * (180 / pi) / cos(np.deg2rad(center_lat))
        # Old way ----------------------------------------------------------
        # latcon = ((grid30_arr[:, 0] >= lat1) &  (grid30_arr[:, 0] <= lat2))
        # loncon = ((grid30_arr[:, 1] >= lon1) &  (grid30_arr[:, 1] <= lon2))
        # elevcon = (grid30_arr[:, 2] > min_rec_elev)
        # new way ----------------------------------------------------------
        latcon = np.logical_and(grid30_arr[:, 0] >= lat1, grid30_arr[:, 0] <= lat2)
        loncon = np.logical_and(grid30_arr[:, 1] >= lon1, grid30_arr[:, 1] <= lon2)
        elevcon = (grid30_arr[:, 2] >= min_rec_elev)

        grid_arr = grid30_arr[latcon & loncon & elevcon]
                
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

            # old way ----------------------------------------------------------
            # latcon = ((grid_arr[:, 0] >= lat1) &  (grid_arr[:, 0] <= lat2))
            # loncon = ((grid_arr[:, 1] >= lon1) &  (grid_arr[:, 1] <= lon2))
            # elevcon = (grid_arr[:, 2] > elev)

            # new way ----------------------------------------------------------
            latcon = np.logical_and(grid_arr[:, 0] >= lat1, grid_arr[:, 0] <= lat2)
            loncon = np.logical_and(grid_arr[:, 1] >= lon1, grid_arr[:, 1] <= lon2)
            elevcon = (grid_arr[:, 2] >= elev)

            elev_filter = grid_arr[latcon & loncon & elevcon]
            elev_lat = elev_filter[:,0]
            elev_lon = elev_filter[:,1]
            elev_elev = elev_filter[:,2]
            
            rec_elev = np.full((elev_elev.size,), elev)
            rec_lat = np.full((elev_lat.size,), lat)
            rec_lon = np.full((elev_lon.size,), lon)
            Hillht = ElevHill.getMax(rec_lat, rec_lon, rec_elev, elev_lat, elev_lon, elev_elev)
            hill_arr[i] = max(Hillht, elev)
            
        return hill_arr


    @staticmethod
    def offline_ElevHill(known_coords, known_values, coords_needing_help):
        """
        Purpose
        -------
        This function is used to compute elevations (m) or hill heights when the "offline" 
        elevation option is selected. Elevations or hill heights for a list of coordinates 
        are computed by interpolating across a set of known elevations/hills extracted from the 
        Census or Alternate Receptors for this facility.
        
        Parameters
        ----------
        known_coords : 2-dimensional numpy array
            Array of known elevation coordinates organized as (lon,lat).
        known_value : 1-dimensional numpy array
            Elevations for the coordinates in known_elev_coords
        coords_needing_help : 2-dimensional numpy array
            Array of coordinates that need elevation or hill height. Organized as (lon,lat).

        Returns
        -------
        linear_vals : 1-dim array
            Elevation (m) or hill height (m) of each coords_needing_help coordinate.
        """

        linear_vals = griddata(known_coords, known_values, coords_needing_help, method='linear')

        # There will be NaN interpolated values if the desired points fall outside the convex hull 
        missing = np.isnan(linear_vals)
        
        # Use nearest-neighbor interpolation for missing points
        if missing.any():
            tree = KDTree(known_coords)  # Build KDTree with known points
            _, indices = tree.query(coords_needing_help[missing])  # Find nearest neighbors for missing points
            nearest_vals = known_values[indices]  # Get elevations for nearest neighbors
        
            # Combine results
            linear_vals[missing] = nearest_vals  # Replace NaNs with nearest-neighbor values
        
        # Round the values to integers
        linear_vals_rounded = [round(e) for e in linear_vals]
        
        return linear_vals_rounded
    

    @staticmethod
    def internet(host="8.8.8.8", port=53, timeout=10):
        """
        Purpose
        -------
        Determines if there is an active Internet connection.
        
        Host: 8.8.8.8 (google-public-dns-a.google.com)
        OpenPort: 53/tcp
        Service: domain (DNS/TCP)
        """
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except socket.error as ex:
            return False
        
        
    @staticmethod
    def isInternet(url="http://www.google.com/", timeout=5):
        """
        Purpose
        -------
        Determines if there is an active Internet connection.
        
        Host: 8.8.8.8 (google-public-dns-a.google.com)
        OpenPort: 53/tcp
        Service: domain (DNS/TCP)
        """
        try:
            requests.head(url, timeout=timeout)
            return True
        except requests.ConnectionError:
            return False
        except requests.Timeout:
            return False
 

    @staticmethod
    def getHill_onerec(rec_lon, rec_lat, rec_elev):
        """
        Purpose
        -------
        This function is used to compute the hill height of a single point. The
        py3dep API is used to acquire elevations.
        
        Parameters
        ----------
        rec_lon : Longitude of point
        rec_lat : Latitude of point
        rec_elev : Elevation (m) of point

        Returns
        -------
        Hill height (m) of point
        """
        
        # Query the 30m DEM server for all elevations within a geo box where the radius is
        # based on the max HEM modeling distance plus 62km to potentially account for Denali
        # at a 10% slope.
        initial_radius = 45
        r_earth = 6371 # radius of earth in km
        lat2 = rec_lat  + (initial_radius / r_earth) * (180 / pi)
        lon2 = rec_lon + (initial_radius / r_earth) * (180 / pi) / cos(np.deg2rad(rec_lat))
        lat1 = rec_lat  - (initial_radius / r_earth) * (180 / pi)
        lon1 = rec_lon - (initial_radius / r_earth) * (180 / pi) / cos(np.deg2rad(rec_lat))
        geo_box = (lon1, lat1, lon2, lat2)
                    
        try:
            #-------------- Use py3dep method ---------------------------
                            
            xarray = py3dep.get_dem(geo_box, 30, crs='epsg:4269')
            grid30_df = xarray.to_dataframe()
            grid30_df.reset_index(inplace=True)
            grid30_df.rename(columns={'x':'longitude', 'y':'latitude'}, inplace=True)
        
        except BaseException as e:
            #--------- py3dep method failed ---------------------------
                                
            return None
                     
        # Create a numpy elevation array from the 30m dataframe
        grid30_lat = grid30_df['latitude'].to_numpy()
        grid30_lon = grid30_df['longitude'].to_numpy()
        grid30_elev = grid30_df['elevation'].to_numpy()
        grid30_arr = np.column_stack((grid30_lat, grid30_lon, grid30_elev))
                        
        # Use the max of the 30m grid elevations and the receptor elevation
        # to compute the horizontal distance (km) needed for a 10% slope to get hill height.
        maxelev = grid30_elev.max()
        maxelev_radius = ((maxelev - rec_elev) * 0.001 * 10) + 1
            
        # Now shrink the elev array using a real radius
        real_radius = maxelev_radius
        lat2 = rec_lat  + (real_radius / r_earth) * (180 / pi)
        lon2 = rec_lon + (real_radius / r_earth) * (180 / pi) / cos(np.deg2rad(rec_lat))
        lat1 = rec_lat  - (real_radius / r_earth) * (180 / pi)
        lon1 = rec_lon - (real_radius / r_earth) * (180 / pi) / cos(np.deg2rad(rec_lat))
        latcon = ((grid30_arr[:, 0] >= lat1) &  (grid30_arr[:, 0] <= lat2))
        loncon = ((grid30_arr[:, 1] >= lon1) &  (grid30_arr[:, 1] <= lon2))
        elevcon = (grid30_arr[:, 2] > rec_elev)
        grid_arr = grid30_arr[latcon & loncon & elevcon]                       
        elev_lat = grid_arr[:,0]
        elev_lon = grid_arr[:,1]
        elev_elev = grid_arr[:,2]
    
        rec_elev_arr = np.full((elev_elev.size,), rec_elev)
        rec_lat_arr = np.full((elev_lat.size,), rec_lat)
        rec_lon_arr = np.full((elev_lon.size,), rec_lon)
        
        Hillht = ElevHill.getMax(rec_lat_arr, rec_lon_arr, rec_elev_arr, elev_lat, elev_lon, elev_elev)
        hill_height = max(Hillht, rec_elev)
        
        return hill_height
    

    @staticmethod
    def run_executor(event, target, workers, *args):
        
        event.clear() # Clear the event for the new run
        
        try:
        
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                # args is a tuple of lists. The target can only accept one element from each list.
                zipped_elements = zip(*args)
                # for item in zipped_elements:
                futures = [executor.submit(target, index, event, *item) for index,item in enumerate(zipped_elements)]
                
                result_list = []
    
                # Iterate over completed futures
                for future in concurrent.futures.as_completed(futures):
                    # print([f._state for f in futures])
    
                    try:
                        # Retrieving the result here will re-raise the exception from the task.
                        result = future.result()
                        result_list.append(result)
                        
                    except Exception as e:
                        # Signal other tasks to stop. Task should have already set this, but in case...
                        event.set()
                        # Manually shut down the executor, cancelling pending futures in the queue.
                        # Note: this will not stop already running tasks.
                        executor.shutdown(wait=False, cancel_futures=True) 
    
                        if ElevHill.isInternet() == False:
                            # start loop checking for internet every minute on the minute
                            ElevHill.keep_trying()
                            
                            # Internet has returned. Start the executor again.
                            event.clear()
                            raise ValueError('Restart') # Exits loop and 'with' block
                        else:
                            # The internet is up. This is a different problem. Raise it.
                            raise(e)
    
           
            return result_list
        
        except BaseException as e:
            
            if str(e) == 'Restart':
                # Call this function again recursively
                return ElevHill.run_executor(event, target, workers, *args)
            else:
                raise(e)
                                                


    @staticmethod
    def keep_trying():
        # No Internet. Keep checking until there is.
        gotInternet = False
        while not gotInternet:
            gotInternet = ElevHill.isInternet()
            if gotInternet == False:
                currtime = datetime.now().strftime("%H:%M:%S")
                message = "No Internet connection to retrieve elevations. Will try again in 1 minute. \n" \
                          + "Click Exit to stop this loop. \n" \
                          + "Current time is: " + currtime + "\n"
                Logger.logMessage(message)
                time.sleep(60)
        # Internet has returned. Start over.
        Logger.logMessage("Internet connection has returned. Will retrieve elevations.\n")
        return None

    
    @staticmethod
    def haversineDistance(lon1, lat1, lon2, lat2):
        """
        Calculate the great circle distance in kilometers between two points 
        on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians 
        lon1, lat1, lon2, lat2 = map(np.deg2rad, [lon1, lat1, lon2, lat2])
        
        # haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a)) 
        r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
        return c * r        
  


