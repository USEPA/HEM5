# -*- coding: utf-8 -*-
"""
Created on Mon Oct  2 10:35:51 2017

@author: dlindsey
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 30 17:16:53 2017

@author: d
"""

#combining both prepare inputs and required inputs to set up, maybe too 
import os
import pandas as pd
import numpy as np
import json_census_blocks as cbr
import ll2utm
import utm2ll
import find_center as fc
import sys 
from tkinter import messagebox
import tkinter as tk
import HEM4_Runstream as rs
import subprocess
import Hem4_Output_Processing as po 
import math
import shutil
import queue



##REFORMATTED TO MOVE THE DATA FRAME CREATION TO THE GUI 
class Prepare_Inputs():
    
    def __init__(self, faclist_df, emisloc_df, hapemis_df, multipoly_df, multibuoy_df, ureceptr_df):
        
        self.faclist_df = faclist_df
        self.emisloc_df = emisloc_df
        self.hapemis_df = hapemis_df
    
        self.multipoly_df = multipoly_df
        self.multibuoy_df = multibuoy_df
        self.ureceptr_df = ureceptr_df
        self.message = "Hem 4 starting"
        
        #self.loc = loc
#%% HAP DOSAGE LIBRARY

        self.haplib_df = pd.read_excel(r"resources/Dose_response_library.xlsx"
            , names=("pollutant","group","cas_no","ure","rfc","aegl_1_1h","aegl_1_8h","aegl_2_1h"
                     ,"aegl_2_8h","erpg_1","erpg_2","mrl","rel","idlh_10","teel_0","teel_1","comments"
                     ,"drvalues","group_ure","tef","acute_con")
            , converters={"pollutant":str,"group":str,"cas_no":str,"ure":float,"rfc":float,"aegl_1_1h":float,"aegl_1_8h":float
            ,"aegl_2_1h":float,"aegl_2_8h":float,"erpg_1":float,"erpg_2":float,"mrl":float,"rel":float,"idlh_10":float
            ,"teel_0":float,"teel_1":float,"comments":str,"drvalues":float,"group_ure":float,"tef":float,"acute_con":float})

       
#%% Zone to use function

    def zone2use(self, el_df):
    
    # Set a common zone
#    utmzone = np.nan_to_num(el_df["utmzone"].min(axis=0))
            min_utmzu = np.nan_to_num(el_df["utmzone"].loc[el_df["location_type"] == "U"].min(axis=0))
            utmzl_df = el_df[["lon"]].loc[el_df["location_type"] == "L"]
            utmzl_df["z"] = ((utmzl_df["lon"]+180)/6 + 1).astype(int)
            min_utmzl = np.nan_to_num(utmzl_df["z"].min(axis=0))
            if min_utmzu == 0:
                utmzone = min_utmzl
            else:
                utmzone = min(min_utmzu, min_utmzl)

            return utmzone



#%% moved start_here to inside the prepare inputs object -- will be called seperately from another object but by moving it inside the other object which will take what was HEM 3 and pass facid  
#the object that calls this will need to be passed the fac_list df ids only so it can call them and run this loop.
    def prep_facility(self, facid):
        
    #%%---------- Facility Options --------------------------------------
    
        facops = self.faclist_df.loc[self.faclist_df.fac_id == facid]
        #print(facops)
    # Set defaults of the facility options
        if facops["max_dist"].isnull().sum() > 0 or facops["max_dist"] > 50000:
            facops["max_dist"] = 50000
    
        if facops["model_dist"].isnull().sum() > 0:
            facops["model_dist"] = 3000

    # Replace NaN with blank, No or 0
        facops = facops.fillna({"met_station":"", "rural_urban":"", "radial":0, "circles":0,
                            "overlap_dist":0, "acute":"N", "hours":0, "elev":"N", "multiplier":0,
                            "ring1":0, "dep":"", "depl":"N", "phase":"", "pdep":"N", "pdepl":"N",
                            "vdep":"N", "vdepl":"N", "all_rcpts":"N", "user_rcpt":"N", "bldg_dw":"N",
                            "urban_pop":0, "fastall":"N"})
        
        facops = facops.reset_index(drop = True)
        
        #print(facops)
     #----- Default missing or out of range facility options --------
 
    #  Maximum Distance
        if facops['max_dist'][0] >= 50000:
            facops.loc[:, 'max_dist'] = 50000
        elif facops['max_dist'][0] == 0:
            facops.loc[:, 'max_dist'] = 50000


    # Modeled Distance of Receptors
        if facops['model_dist'][0] == 0:
            facops.loc[:, 'model_dist'] = 3000

    
    # Radials
        if facops['radial'][0] == 0:
            facops.loc[:, 'radial'] = 16


    # Circles
        if facops['circles'][0] == 0:
            facops.loc[:, 'circles'] = 13

    
    # Overlap Distance 
        if facops['overlap_dist'][0] == 0:
            facops.loc[:, 'overlap_dist'] = 30
        elif facops['overlap_dist'][0] < 1:
            facops.loc[:, 'overlap_dist'] = 30
        elif facops['overlap_dist'][0] > 500:
            facops.loc[:, 'overlap_dist'] = 30

        op_maxdist = facops.get_value(0,"max_dist")
        op_modeldist = facops.get_value(0,"model_dist") 
        op_circles = facops.get_value(0,"circles") 
        op_radial = facops.get_value(0,"radial") 
    
    
    


    #%%---------- Emission Locations --------------------------------------

    # Get emission location info for this facility
        emislocs = self.emisloc_df.loc[self.emisloc_df.fac_id == facid]

    # Replace NaN with blank or 0
        emislocs = emislocs.fillna({"utmzone":0, "source_type":"", "lengthx":0, "lengthy":0, "angle":0,
                                "horzdim":0, "vertdim":0, "areavolrelhgt":0, "stkht":0, "stkdia": 0,
                                "stkvel":0, "stktemp":0, "elev":0, "x2":0, "y2":0})
        emislocs = emislocs.reset_index(drop = True)
        #print(emislocs)

    # Determine the utm zone to use for this facility
        facutmzone = self.zone2use(emislocs)
        #print(facutmzone)

    # Convert all lat/lon coordinates to UTM and UTM coordinates to lat/lon

        slat = emislocs["lat"]
        slon = emislocs["lon"]
        sutmzone = emislocs["utmzone"]
     
    # First compute lat/lon coors using whatever zone was provided
        alat, alon = utm2ll.utm2ll(slat, slon, sutmzone)
        emislocs["lat"] = alat.tolist()
        emislocs["lon"] = alon.tolist()

    # Next compute UTM coors using the common zone
        sutmzone = facutmzone*np.ones(len(emislocs["lat"]))
        autmn, autme, autmz = ll2utm.ll2utm(slat, slon, sutmzone)
        emislocs["utme"] = autme.tolist()
        emislocs["utmn"] = autmn.tolist()
        emislocs["utmzone"] = autmz.tolist()


    # Compute UTM of any x2 and y2 coordinates and add to emislocs
        slat = emislocs["y2"]
        slon = emislocs["x2"]
        sutmzone = emislocs["utmzone"]

        alat, alon = utm2ll.utm2ll(slat, slon, sutmzone)
        emislocs["lat_y2"] = alat.tolist()
        emislocs["lon_x2"] = alon.tolist()
        
        sutmzone = facutmzone*np.ones(len(emislocs["lat"]))
        autmn, autme, autmz = ll2utm.ll2utm(slat, slon, sutmzone)
        emislocs["utme_x2"] = autme.tolist()
        emislocs["utmn_y2"] = autmn.tolist()
        
    
    #%%---------- HAP Emissions --------------------------------------
    
    # Get emissions data for this facility
        hapemis = self.hapemis_df.loc[self.hapemis_df.fac_id == facid]

    # Replace NaN with blank or 0
        hapemis = hapemis.fillna({"emis_tpy":0, "part_frac":0})
        hapemis = hapemis.reset_index(drop = True)
  
    
    #%%---------- Optional User Receptors ----------------------------------------- ## needs to be connected
    
        if facops['user_rcpt'][0] == "Y":
        #swap above out for if hasattr(self, "ureceptor_df")
            user_recs = self.ureceptr_df.loc[self.ureceptr_df.fac_id == facid].copy()
            user_recs.reset_index(inplace=True)
            #print(user_recs)
            slat = user_recs["lat"]
            slon = user_recs["lon"]
            szone = user_recs["utmzone"]

        # First compute lat/lon coors using whatever zone was provided
            alat, alon = utm2ll.utm2ll(slat, slon, szone)
            user_recs["lat"] = alat.tolist()
            user_recs["lon"] = alon.tolist()
         
        # Next compute UTM coors using the common zone
            sutmzone = facutmzone*np.ones(len(user_recs["lat"]))
            autmn, autme, autmz = ll2utm.ll2utm(slat, slon, sutmzone)
            user_recs["utme"] = autme.tolist()
            user_recs["utmn"] = autmn.tolist()
            user_recs["utmzone"] = autmz.tolist()
        
        else:
        
        # No user receptors. Empty dataframe.
            user_recs = pd.DataFrame()
        


    #%%---------- Optional Buoyant Line Parameters ----------------------------------------- needs to be connected
    
        if "B" in map(str.upper, emislocs["source_type"].values):

            buoyant_df = self.multibuoy_df.loc[self.multibuoy_df.fac_id == facid].copy()
                
        else:
        
        # No buoyant line sources. Empty dataframe.
            buoyant_df = pd.DataFrame()
  
    

    #%%---------- Optional Polygon Vertex File ----------------------------------------- neeeds to be connected
    
        if "I" in map(str.upper, emislocs["source_type"].values):

            polyver_df = self.multipoly_df.loc[self.multipoly_df.fac_id == facid].copy()
            slat = polyver_df["lat"]
            slon = polyver_df["lon"]
            szone = polyver_df["utmzone"]

        # First compute lat/lon coors using whatever zone was provided
            alat, alon = utm2ll.utm2ll(slat, slon, szone)
            polyver_df["lat"] = alat.tolist()
            polyver_df["lon"] = alon.tolist()
         
        # Next compute UTM coors using the common zone
            sutmzone = facutmzone*np.ones(len(polyver_df["lat"]))
            autmn, autme, autmz = ll2utm.ll2utm(slat, slon, sutmzone)
            polyver_df["utme"] = autme.tolist()
            polyver_df["utmn"] = autmn.tolist()
            polyver_df["utmzone"] = autmz.tolist()
        
        # Assign source_type
            polyver_df["source_type"] = "I"
                
        else:
        
        # No polygon sources. Empty dataframe.
            polyver_df = pd.DataFrame()


      

    #%%---------- Get Census Block Receptors -------------------------------------- needs to be connected
    
    # Keep necessary source location columns
        sourcelocs = emislocs[["fac_id","source_id","source_type","utme","utmn","utmzone"
                          ,"lengthx","lengthy","angle","utme_x2","utmn_y2"]].copy()
 
    # Is there a polygon source at this facility? 
    # If there is, read the vertex file and append to sourcelocs
#    polys = sourcelocs.loc[sourcelocs["source_type"] == "I"]
        if any(sourcelocs.source_type == "I") == True:
        # remove the I source_type rows from sourcelocs before appending polyver_df to avoid duplicate rows
            sourcelocs = sourcelocs[sourcelocs.source_type != "I"]
            sourcelocs = sourcelocs.append(polyver_df)
            sourcelocs = sourcelocs.fillna({"source_type":"", "lengthx":0, "lengthy":0, "angle":0, "utme_x2":0, "utmn_y2":0})
            sourcelocs = sourcelocs.reset_index()
        
#        vertexlist = self.multipoly_df[["lat","lon","utmzone"]].loc[self.multipoly_df.fac_id == facid].copy()
#
#        # Compute lat/lon of any UTM coordinates and add to vertexlist
#        ################### Use utm zone provided in the file? #############
#        slat = vertexlist["lat"]
#        slon = vertexlist["lon"]
#        sutmzone = vertexlist["utmzone"]
#
#        alat, alon = utm2ll.utm2ll(slat, slon, sutmzone)
#        vertexlist["lat"] = alat.tolist()
#        vertexlist["lon"] = alon.tolist()
#        
#        # Compute UTM of any lat/lon coordinates and add to vertexlist
#        sutmzone = facutmzone*np.ones(len(vertexlist["lat"]))
#        autmn, autme, autmz = ll2utm.ll2utm(slat, slon, sutmzone)
#        vertexlist["utme"] = autme.tolist()
#        vertexlist["utmn"] = autmn.tolist()
#        vertexlist["utmzone"] = autmz.tolist()
        
   
         
    # Compute the coordinates of the facililty center
        cenx, ceny, cenlon, cenlat = fc.center(sourcelocs, facutmzone)
        #print("cenlon")
        #print(cenlon)
        #print(cenlat)
        #print(cenx)
        #print(ceny)
    
    #%%........ Get census block receptors ...........................................
        maxdist = facops.get_value(0,"max_dist")
        #print(maxdist)
        modeldist = facops.get_value(0,"model_dist")
        #print(modeldist)
        self.innerblks, self.outerblks = cbr.getblocks(cenx, ceny, cenlon, cenlat, facutmzone, maxdist, modeldist, sourcelocs)
    
        # export innerblks to an Excel file in the Working directory
        innerblks_path = "working/innerblk_receptors.xlsx"
        innerblks_con = pd.ExcelWriter(innerblks_path)
        self.innerblks.to_excel(innerblks_con,'Sheet1')
        innerblks_con.save()

        # export outerblks to an Excel file in the Working directory
        outerblks_path = "working/outerblk_receptors.xlsx"
        outerblks_con = pd.ExcelWriter(outerblks_path)
        self.outerblks.to_excel(outerblks_con,'Sheet1')
        outerblks_con.save()
    
    #%%----- Polar receptors ----------
        polar_dist = np.linspace(op_maxdist/op_circles,op_maxdist,op_circles).tolist()
        start = 0.
        stop = 360. - (360./op_radial)
        polar_angl = np.linspace(start,stop,op_radial).tolist()
        polar_id = ["polgrid1"] * (len(polar_dist) * len(polar_angl))
        polar_utme = [cenx + pd * math.sin(math.radians(pa)) for pd in polar_dist for pa in polar_angl]
        polar_utmn = [ceny + pd * math.cos(math.radians(pa)) for pd in polar_dist for pa in polar_angl]
        polar_utmz = [facutmzone] * (len(polar_dist) * len(polar_angl))    
        polar_lat, polar_lon = utm2ll.utm2ll(polar_utmn, polar_utme, polar_utmz)
    
        # create dist and angl lists of length op_circle*op_radial
        polar_dist2 = [i for i in polar_dist for j in polar_angl]
        polar_angl2 = [j for i in polar_dist for j in polar_angl]

        # sector and ring lists
        polar_sect = [(int((a*op_radial/360)+0.5 % op_radial)) + 1 for a in polar_angl2]
        
        polar_ring = []
        remring = polar_dist2[0]
        ringcount = 1
        for i in range(len(polar_dist2)):
            if polar_dist2[i] == remring:
                polar_ring.append(ringcount)
            else:
                remring = polar_dist2[i]
                ringcount = ringcount + 1
                polar_ring.append(ringcount)
    
    
        dfitems = [("id",polar_id), ("distance",polar_dist2), ("angle",polar_angl2), ("utme",polar_utme),
               ("utmn",polar_utmn), ("utmz",polar_utmz), ("lon",polar_lon), ("lat",polar_lat),
               ("sector",polar_sect), ("ring",polar_ring)]
        polar_df = pd.DataFrame.from_items(dfitems)

    
        # export polar_df to an Excel file in the Working directory
        polardf_path = "working/polar_receptors.xlsx"
        polardf_con = pd.ExcelWriter(polardf_path)
        polar_df.to_excel(polardf_con,'Sheet1')
        polardf_con.save()
        
        self.message = "building runstream for " + str(facid)   
    
    #%% result ##needs to create a new object to be passed...
        #return facops, emislocs, hapemis, innerblks, outerblks, sourcelocs, user_recs, buoyant_df, polyver_df
        return rs.Runstream(facops, emislocs, hapemis, cenlat, cenlon, cenx, ceny, self.innerblks, user_recs, buoyant_df, polyver_df, polar_df)




#%% RUN Start Here
    def run_facilities(self):
        fac_list = []
        for index, row in self.faclist_df.iterrows():
            
            facid = row[0]
            fac_list.append(facid)
       
        
        for fac in fac_list:
            facid = fac
            #self.loc["textvariable"] = "Preparing " + facid
            result = self.prep_facility(facid)
                
            #self.loc["textvariable"]="Building Runstream File for " + facid
            #messagebox.showinfo("", "Building Runstream File for " + facid)
            
             
            result.build()
              
            fac_folder = "output/"+ str(facid) + "/"
            self.message = "starting aermod"    
            #run aermod
            #self.loc["textvariable"] =  "Starting Aermod for " + facid
                
            args = "aermod.exe aermod.inp" 
            subprocess.call(args, shell=False)
                
            #self.loc["textvariable"] = "Aermod complete for " + facid
            
            ## Check for successful aermod run:
            check = open('aermod.out','r')
            message = check.read()
            if 'UNSUCCESSFUL' in message:
                success = False
            else:
                success = True
            
            check.close()    
                
            if success == True:
                
            #move aermod.out to the fac output folder 
            #replace if one is already in there othewrwise will throw error
            
                if os.path.isfile(fac_folder + 'aermod.out'):
                    os.remove(fac_folder + 'aermod.out')
                    shutil.move('aermod.out', fac_folder)
                
                else:    
                    shutil.move('aermod.out', fac_folder)
            
            #process outputs
                process = po.Process_outputs(facid, self.haplib_df, result.hapemis, fac_folder, self.innerblks, result.polar_df)
                process.process()
                
            #self.loc["textvariable"] = "Analysis Complete"
                
                messagebox.showinfo("", "HEM4 finished processing all facilities")
#%% Testing the prepare inpusts object

#fac_path = "C:\HEM3_V153\INPUTS_MULTI\TEMPLATE_MULTI_FACILITY_LIST_OPTIONS.XLSX"
#hap_path = "C:\HEM3_V153\INPUTS_MULTI\TEMPLATE_MULTI_HAP_EMISSIONS.XLSX" 
#emisloc_path =  "C:\HEM3_V153\INPUTS_MULTI\TEMPLATE_MULTI_EMISSIONS_LOCATION.XLSX"                          
#census = " " 
#poly_path = None 
#bouyant_path = "C:\HEM3_V153\INPUTS_MULTI\TEMPLATE_MULTI_BUOYANTLINEPARAMETERS.XLSX"                                                                                                                 
#urep_path = None
#bd_path = None


#test = Prepare_Inputs(fac_path, emisloc_path, hap_path, poly_path, bouyant_path, urep_path)


#test.run_facilities()


