# -*- coding: utf-8 -*-
"""
Created on Mon Oct  2 10:35:51 2017

@author: dlindsey
"""

import math
import sys
import numpy as np
import pandas as pd
import find_center as fc
import json_census_blocks as cbr
from support.UTM import UTM
from runstream.Runstream import Runstream


##REFORMATTED TO MOVE THE DATA FRAME CREATION TO THE GUI
class FacilityPrep():
    
    def __init__(self, model):

        self.model = model
        

    def createRunstream(self, facid, phase):

        #%%---------- Facility Options --------------------------------------

        facops = self.model.faclist.dataframe.loc[self.model.faclist.dataframe.fac_id == facid]

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
        op_overlap = facops.get_value(0,"overlap_dist")

        #%%---------- Emission Locations --------------------------------------

        # Get emission location info for this facility
        emislocs = self.model.emisloc.dataframe.loc[self.model.emisloc.dataframe.fac_id == facid]

        # Replace NaN with blank or 0
        emislocs = emislocs.fillna({"utmzone":0, "source_type":"", "lengthx":0, "lengthy":0, "angle":0,
                                    "horzdim":0, "vertdim":0, "areavolrelhgt":0, "stkht":0, "stkdia": 0,
                                    "stkvel":0, "stktemp":0, "elev":0, "x2":0, "y2":0})
        emislocs = emislocs.reset_index(drop = True)

        # Determine the utm zone to use for this facility
        facutmzone = self.zone2use(emislocs)

        # Convert all lat/lon coordinates to UTM and UTM coordinates to lat/lon
        slat = emislocs["lat"]
        slon = emislocs["lon"]
        sutmzone = emislocs["utmzone"]

        # First compute lat/lon coors using whatever zone was provided
        alat, alon = UTM.utm2ll(slat, slon, sutmzone)
        emislocs["lat"] = alat.tolist()
        emislocs["lon"] = alon.tolist()

        # Next compute UTM coors using the common zone
        sutmzone = facutmzone*np.ones(len(emislocs["lat"]))
        autmn, autme, autmz = UTM.ll2utm(slat, slon, sutmzone)
        emislocs["utme"] = autme.tolist()
        emislocs["utmn"] = autmn.tolist()
        emislocs["utmzone"] = autmz.tolist()

        # Compute UTM of any x2 and y2 coordinates and add to emislocs
        slat = emislocs["y2"]
        slon = emislocs["x2"]
        sutmzone = emislocs["utmzone"]

        alat, alon = UTM.utm2ll(slat, slon, sutmzone)
        emislocs["lat_y2"] = alat.tolist()
        emislocs["lon_x2"] = alon.tolist()

        sutmzone = facutmzone*np.ones(len(emislocs["lat"]))
        autmn, autme, autmz = UTM.ll2utm(slat, slon, sutmzone)
        emislocs["utme_x2"] = autme.tolist()
        emislocs["utmn_y2"] = autmn.tolist()

        #%%---------- HAP Emissions --------------------------------------

        # Get emissions data for this facility
        hapemis = self.model.hapemis.dataframe.loc[self.model.hapemis.dataframe.fac_id == facid]

        # Replace NaN with blank or 0
        hapemis = hapemis.fillna({"emis_tpy":0, "part_frac":0})
        hapemis = hapemis.reset_index(drop = True)

        #%%---------- Optional User Receptors ----------------------------------------- ## needs to be connected


        if hasattr(self.model.ureceptr, "dataframe"):

            user_recs = self.model.ureceptr.dataframe.loc[self.model.ureceptr.dataframe.fac_id == facid].copy()
            user_recs.reset_index(inplace=True)

            slat = user_recs["lat"]
            slon = user_recs["lon"]
            szone = user_recs["utmzone"]

            # First compute lat/lon coors using whatever zone was provided
            alat, alon = UTM.utm2ll(slat, slon, szone)
            user_recs["lat"] = alat.tolist()
            user_recs["lon"] = alon.tolist()

            # Next compute UTM coors using the common zone
            sutmzone = facutmzone*np.ones(len(user_recs["lat"]))
            autmn, autme, autmz = UTM.ll2utm(slat, slon, sutmzone)
            user_recs["utme"] = autme.tolist()
            user_recs["utmn"] = autmn.tolist()
            user_recs["utmzone"] = autmz.tolist()

        else:
            # No user receptors. Empty dataframe.
            user_recs = None

        #%%---------- Optional Buoyant Line Parameters ----------------------------------------- needs to be connected

        if hasattr(self.model.multibuoy, "dataframe"):

            buoyant_df = self.model.multibuoy.dataframe.loc[ self.model.multibuoy.dataframe.fac_id == facid].copy()

        else:
            # No buoyant line sources. Empty dataframe.
            buoyant_df = None

        #%%---------- Optional Polygon Vertex File ----------------------------------------- neeeds to be connected


        if hasattr(self.model.multipoly, "dataframe"):

            polyver_df = self.model.multipoly.dataframe.loc[self.model.multipoly.dataframe.fac_id == facid].copy()
            slat = polyver_df["lat"]
            slon = polyver_df["lon"]
            szone = polyver_df["utmzone"]

            # First compute lat/lon coors using whatever zone was provided
            alat, alon = UTM.utm2ll(slat, slon, szone)
            polyver_df["lat"] = alat.tolist()
            polyver_df["lon"] = alon.tolist()

            # Next compute UTM coors using the common zone
            sutmzone = facutmzone*np.ones(len(polyver_df["lat"]))
            autmn, autme, autmz = UTM.ll2utm(slat, slon, sutmzone)
            polyver_df["utme"] = autme.tolist()
            polyver_df["utmn"] = autmn.tolist()
            polyver_df["utmzone"] = autmz.tolist()

            # Assign source_type
            polyver_df["source_type"] = "I"

        else:
            # No polygon sources. Empty dataframe.
            polyver_df = None

        #%%---------- Optional Building Downwash -------------------------------------
        
        if hasattr(self.model.bldgdw, "dataframe"):
            
            bldgdw_df = self.model.bldgdw.dataframe.loc[self.model.bldgdw.dataframe.fac_id==facid].copy()
            
        else:
            bldgdw_df = None
        



        #%% ------ Optional Particle Data -------------------------------------
        
        if hasattr(self.model.partdep, "dataframe"):
            
            partdia_df = self.model.partdep.dataframe.loc[self.model.partdep.dataframe.fac_id == facid].copy()
        
        else:
            partdia_df = None
            
            
        #%% -- Optional Land Use ----------------------------------------------
        
        if hasattr(self.model.landuse, "dataframe"):
            landuse_df = self.model.landuse.dataframe.loc[self.model.landuse.dataframe.fac_id == facid].copy()
            
        else:
            landuse_df = None
        
        
        
        #%% --- Optional Seasons ---------------------------------------------
        
        if hasattr(self.model.seasons, "dataframe"):
            seasons_df = self.model.seasons.dataframe.loc[self.model.seasons.dataframe.fac_id == facid].copy()
            
        else:
            seasons_df = None
            
            
            
        #%% --- Optional Emissions Variations --------------------------------
            
        if hasattr(self.model.emisvar, "dataframe"):
            emisvar_df = self.model.emisvar.dataframe.loc[self.model.emisvar.dataframe.fac_id == facid].copy()
        
        else:
            emisvar_df = None
        
        
        #%%-- Gas Params for gas runs -- needs to be incorporated better
        
        #if hasattr(self.model.gasparams, "dataframe"):
            #gasparams_df = self.model.gasparams.dataframe
            
        #else:
            #gasparams_df = None
        
        #%%---------- Get Census Block Receptors -------------------------------------- needs to be connected

        # Keep necessary source location columns
        sourcelocs = emislocs[["fac_id","source_id","source_type","utme","utmn","utmzone"
            ,"lengthx","lengthy","angle","utme_x2","utmn_y2"]].copy()

        # Is there a polygon source at this facility?
        # If there is, read the vertex file and append to sourcelocs
        if any(sourcelocs.source_type == "I") == True:
            # remove the I source_type rows from sourcelocs before appending polyver_df to avoid duplicate rows
            sourcelocs = sourcelocs[sourcelocs.source_type != "I"]
            sourcelocs = sourcelocs.append(polyver_df)
            sourcelocs = sourcelocs.fillna({"source_type":"", "lengthx":0, "lengthy":0, "angle":0, "utme_x2":0, "utmn_y2":0})
            sourcelocs = sourcelocs.reset_index()

        # Compute the coordinates of the facililty center
        cenx, ceny, cenlon, cenlat, max_srcdist, vertx_a, verty_a = fc.center(sourcelocs, facutmzone)
        
        #retrieve blocks
        maxdist = facops.get_value(0,"max_dist")
        modeldist = facops.get_value(0,"model_dist")
        self.innerblks, self.outerblks = cbr.getblocks(cenx, ceny, cenlon, cenlat, facutmzone, maxdist, modeldist, sourcelocs, op_overlap)
 
       
        #%%----- Polar receptors ----------

        # compute inner polar radius
        # If there is a polygon, find smallest circle fitting inside it and then move out almost to modeling distance
        if any(sourcelocs.source_type == "I") == True:
            inrad = max_srcdist/2
            for i in range(0, len(vertx_a)-1):
                for j in range(0, len(verty_a)-1):
                    dist_cen = math.sqrt((vertx_a[i] - cenx)**2 + (verty_a[j] - ceny)**2)
                    inrad = min(inrad, dist_cen)
            inrad = max(inrad+modeldist-10, 100)
        else:
            inrad = 0
            for i in range(0, len(vertx_a)-1):
                for j in range(0, len(verty_a)-1):
                    dist_cen = math.sqrt((vertx_a[i] - cenx)**2 + (verty_a[j] - ceny)**2)
                    inrad = max(inrad, dist_cen)

        # set the first polar ring distance (list item 0), do not override if user selected first ring > 100m
        if facops["ring1"][0] <= 100:
            ring1a = max(inrad+op_overlap, 100)
            ring1b = min(ring1a, op_maxdist)
            firstring = round(max(ring1b, 100))
        else:
            firstring = facops["ring1"][0]
        polar_dist = []
        polar_dist.append(firstring)

        # compute the rest of the polar ring distances (logarithmically spaced)

        # first handle ring distances inside the modeling distance
        k = 1
        if op_modeldist <= polar_dist[0]:
            N_in = 0
            N_out = op_circles
            D_st2 = polar_dist[0]
        else:
            N_in = round(math.log(op_modeldist/polar_dist[0])/math.log(op_maxdist/polar_dist[0]) * (op_circles - 1))
            while k < N_in:
                next_dist = round(polar_dist[k-1] * ((op_modeldist/polar_dist[0])**(1/N_in)), -1)
                # Add code to check if next_dist is the same as the previous distance?  Code is in input_ringdist
                polar_dist.append(next_dist)
                k = k + 1
            next_dist = op_modeldist
            polar_dist.append(next_dist)
            k = k + 1
            N_out = op_circles - 1 - N_in
            D_st2 = op_modeldist

        # next, handle ring distances outside the modeling distance
        while k < op_circles - 1:
            next_dist = round(polar_dist[k-1] * ((op_maxdist/D_st2)**(1/N_out)), -2)
            polar_dist.append(next_dist)
            k = k + 1

        # set the last distance to the modeling distance
        polar_dist.append(op_maxdist)

        # equally spaced - polar_dist = np.linspace(op_maxdist/op_circles,op_maxdist,op_circles).tolist()

        # setup list of polar angles
        start = 0.
        stop = 360. - (360./op_radial)
        polar_angl = np.linspace(start,stop,op_radial).tolist()

        # create lists of other polar receptor parameters
        polar_id = ["polgrid1"] * (len(polar_dist) * len(polar_angl))
        polar_utme = [round(cenx + polardist * math.sin(math.radians(pa))) for polardist in polar_dist for pa in polar_angl]
        polar_utmn = [round(ceny + polardist * math.cos(math.radians(pa))) for polardist in polar_dist for pa in polar_angl]
        polar_utmz = [facutmzone] * (len(polar_dist) * len(polar_angl))
        polar_lat, polar_lon = UTM.utm2ll(polar_utmn, polar_utme, polar_utmz)

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

        # construct the polar dataframe
        dfitems = [("id",polar_id), ("distance",polar_dist2), ("angle",polar_angl2), ("utme",polar_utme),
                   ("utmn",polar_utmn), ("utmz",polar_utmz), ("lon",polar_lon), ("lat",polar_lat),
                   ("sector",polar_sect), ("ring",polar_ring)]
        polar_df = pd.DataFrame.from_items(dfitems)

        # define the index of polar_df as concatenation of sector and ring
        polar_idx = polar_df.apply(lambda row: self.define_polar_idx(row['sector'], row['ring']), axis=1)
        polar_df.set_index(polar_idx, inplace=True)

        # determine if polar receptors overlap any emission sources
        polar_df["overlap"] = polar_df.apply(lambda row: self.polar_overlap(row["utme"], row["utmn"], sourcelocs, op_overlap), axis=1)

         # Assign the polar grid data frame to the model
        self.model.polargrid = polar_df
        
        
        #%%----- Add sector and ring to inner and outer receptors ----------

        # assign sector and ring number (integers) to each inner receptor and compute fractional sector (s) and ring_loc (log weighted) numbers
        self.innerblks["sector"], self.innerblks["s"], self.innerblks["ring"], self.innerblks["ring_loc"] = zip(*self.innerblks.apply(lambda row: self.calc_ring_sector(polar_dist,row["DISTANCE"],row["ANGLE"],op_radial), axis=1))

        # assign sector and ring number (integers) to each outer receptor and compute fractional sector (s) and ring_loc (log weighted) numbers
        self.outerblks["sector"], self.outerblks["s"], self.outerblks["ring"], self.outerblks["ring_loc"] = zip(*self.outerblks.apply(lambda row: self.calc_ring_sector(polar_dist,row["DISTANCE"],row["ANGLE"],op_radial), axis=1))


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


        #%%------ Elevations and hill height ---------

        # if the facility will use elevations, assign them to emission sources and polar receptors
        if facops.get_value(0,"elev").upper() == "Y":
            polar_df["elev"], polar_df["hill"] = zip(*polar_df.apply(lambda row: self.assign_polar_elev_step1(row,self.innerblks,self.outerblks,maxdist), axis=1))
            if emislocs["elev"].max() == 0 and emislocs["elev"].min() == 0:
                emislocs["elev"] = self.compute_emisloc_elev(polar_df,op_circles)
            # if polar receptor still has missing elevation, fill it in
            polar_df["elev"], polar_df["hill"] = zip(*polar_df.apply(lambda row: self.assign_polar_elev_step2(row,self.innerblks,self.outerblks,emislocs), axis=1))
        else:
            polar_df["elev"] = 0
            polar_df["hill"] = 0
            emislocs["elev"] = 0
            emislocs["hill"] = 0


        # export polar_df to an Excel file in the Working directory
        polardf_path = "working/" + facid + "_polar_receptors.xlsx"
        polardf_con = pd.ExcelWriter(polardf_path)
        polar_df.to_excel(polardf_con,'Sheet1')
        polardf_con.save()

        # export emislocs to an Excel file in the Working directory
        emislocs_path = "working/" + facid + "_emislocs.xlsx"
        emislocs_con = pd.ExcelWriter(emislocs_path)
        emislocs.to_excel(emislocs_con,'Sheet1')
        emislocs_con.save()

        #%% this is where runstream file will be compiled
        #new logic to be
        
        runstream = Runstream(facops, emislocs, hapemis, user_recs, buoyant_df,
                              polyver_df, bldgdw_df, partdia_df, landuse_df, 
                              seasons_df, emisvar_df, 
                              self.model.gasparams.dataframe)
        runstream.build_co(phase)
        runstream.build_so()
        runstream.build_re(self.innerblks, cenx, ceny, polar_df)
        runstream.build_me(cenlat, cenlon)
        runstream.build_ou()
        
        return runstream
        #no return statement since it will just need to build the file
        #return rs.Runstream(facops, emislocs, hapemis, cenlat, cenlon, cenx, ceny, self.innerblks, user_recs, buoyant_df, polyver_df, polar_df, bldgdw_df, partdia_df, landuse_df, seasons_df, gasparams_df)

    #%% Calculate ring and sector of block receptors
    
    def calc_ring_sector(self, ring_distances, block_distance, block_angle, num_sectors):
        
        ring_loc = -999
        
        # compute fractional sector number
        s = (block_angle * num_sectors)/360.0 % num_sectors
        
        # compute integer sector number
        sector_int = int(s) + 1
            
        # Compute ring_loc. loop through ring distances in pairs of previous and current
        previous = ring_distances[0]
        i = 0
        for ring in ring_distances[1:]:
            i = i + 1
            current = ring
            #if block is between rings, then interpolate distance and exit loop
            if block_distance >= previous and block_distance < current:
                ring_loc = i + (np.log(block_distance) - np.log(previous)) / (np.log(current) - np.log(previous))        
                break 
            previous = ring
                    
        # Compute integer ring number
        ring_int = math.floor(ring_loc)
         
        return sector_int, s, ring_int, ring_loc

#%% Assign elevation and hill height to polar receptors
    def assign_polar_elev_step1(self, polar_row, innblks, outblks, maxdist):
        
        sector1 = polar_row["sector"]
        ring1 = polar_row["ring"]
               
        #subset the inner and outer block dataframes to sector, ring
        innblks_sub = innblks.loc[(innblks["sector"] == sector1) & (innblks["ring"] == ring1)]
        outblks_sub = outblks.loc[(outblks["sector"] == sector1) & (outblks["ring"] == ring1)]
        
        #initialize variables
        r_nearelev = -999
        r_maxelev = -999
        r_hill = -999
        r_pop = 0
        r_nblk = 0
        r_avgelev = 0
        r_popelev = 0
        d_test = 0
        d_nearelev = 99999
        
        #try inner block subset
        for index, row in innblks_sub.iterrows():
            if row["ELEV"] > r_maxelev:
                r_maxelev = row["ELEV"]
                r_hill = row["HILL"]
            r_avgelev = r_avgelev + row["ELEV"]
            r_popelev = r_popelev + row["ELEV"] * row["POPULATION"]
            r_nblk = r_nblk + 1
            r_pop = r_pop + row["POPULATION"]
            d_test = math.sqrt(row["DISTANCE"]**2 + polar_row["distance"]**2 - 2*row["DISTANCE"]*polar_row["distance"]*math.cos(math.radians(row["ANGLE"]-polar_row["angle"])))
            if d_test <= d_nearelev:
                d_nearelev = d_test
                r_nearelev = row["ELEV"]
                   
        
        #try outer block subset
        for index, row in outblks_sub.iterrows():
            if row["ELEV"] > r_maxelev:
                r_maxelev = row["ELEV"]
                r_hill = row["HILL"]
            r_avgelev = r_avgelev + row["ELEV"]
            r_popelev = r_popelev + row["ELEV"] * row["POPULATION"]
            r_nblk = r_nblk + 1
            r_pop = r_pop + row["POPULATION"]
            d_test = math.sqrt(row["DISTANCE"]**2 + polar_row["distance"]**2 - 2*row["DISTANCE"]*polar_row["distance"]*math.cos(math.radians(row["ANGLE"]-polar_row["angle"])))
            if d_test <= d_nearelev:
                d_nearelev = d_test
                r_nearelev = row["ELEV"]

            
        #compute average and population elevations
        if r_nblk > 0:
            r_avgelev = r_avgelev/r_nblk
        else:
            r_avgelev = -999
        
        if r_pop > 0:
            r_popelev = r_popelev/r_pop
        else:
            r_popelev = -999
        
       
        #Note: the max elevation is returned as the elevation for this polar receptor
        return r_maxelev, r_hill              

#%% Assign elevation and hill height to polar receptors that still have missing elevations
    def assign_polar_elev_step2(self, polar_row, innblks, outblks, emislocs):

        d_nearelev = 99999
        d_nearhill = 99999
        r_maxelev = 88888
        r_hill = 88888
        
        if polar_row["elev"] == -999:
            
            #check emission locations
            emislocs_dist = np.sqrt((emislocs["utme"] - polar_row["utme"])**2 + (emislocs["utmn"] - polar_row["utmn"])**2)
            mindist_index = emislocs_dist.values.argmin()
            d_test = emislocs_dist.iloc[mindist_index]
            if d_test <= d_nearelev:
                d_nearelev = d_test
                r_nearelev = emislocs["elev"].iloc[mindist_index]
                r_maxelev = r_nearelev
                r_avgelev = r_nearelev
                r_popelev = r_nearelev
            
            #check inner blocks
            inner_dist = np.sqrt((innblks["utme"] - polar_row["utme"])**2 + (innblks["utmn"] - polar_row["utmn"])**2)
            mindist_index = inner_dist.values.argmin()
            d_test = inner_dist.iloc[mindist_index]
            if d_test <= d_nearelev:
                d_nearelev = d_test
                r_nearelev = innblks["ELEV"].iloc[mindist_index]
                r_maxelev = r_nearelev
                r_avgelev = r_nearelev
                r_popelev = r_nearelev
            if d_test <= d_nearhill:
                d_nearhill = d_test
                r_hill = innblks.get_value(mindist_index, "HILL")
    
            #check outer blocks
            outer_dist = np.sqrt((outblks["utme"] - polar_row["utme"])**2 + (outblks["utmn"] - polar_row["utmn"])**2)
            mindist_index = outer_dist.values.argmin()
            d_test = outer_dist.iloc[mindist_index]
            if d_test <= d_nearelev:
                d_nearelev = d_test
                r_nearelev = outblks["ELEV"].iloc[mindist_index]
                r_maxelev = r_nearelev
                r_avgelev = r_nearelev
                r_popelev = r_nearelev
            if d_test <= d_nearhill:
                d_nearhill = d_test
                r_hill = outblks["HILL"].iloc[mindist_index]
                
        else:
            
            r_maxelev = polar_row["elev"]
            r_hill = polar_row["hill"]
        
        #Note: the max elevation is returned as the elevation for this polar receptor
        return r_maxelev, r_hill   

#%% Compute the elevation to be used for all emission sources
    def compute_emisloc_elev(self, polars, num_rings):
        
        # The average of the average elevation for a ring will be used as the source elevation.
        
        D_selev = 0
        N_selev = 0
        ringnum = 1
        while D_selev == 0 and ringnum <= num_rings:
            polar_sub = polars.loc[polars["ring"] == ringnum]
            for index, row in polar_sub.iterrows():
                if row["elev"] != -999:
                    D_selev = D_selev + row["elev"]
                    N_selev = N_selev + 1
            ringnum = ringnum + 1
        
        if N_selev != 0:
            avgelev = D_selev / N_selev
        else:
            print("Error! No elevation computed for the emission sources.")
            sys.exit()
                  
        return avgelev           

#%% Define polar receptor dataframe index
    
    def define_polar_idx(self, s, r):
        return "S" + str(s) + "R" + str(r)

      
#%% Zone to use function

    def zone2use(self, el_df):
    
        """
        Create a common UTM Zone for this facility
        
        All emission sources input to Aermod must have UTM coordinates
        from a single UTM zone. This function will determine the single
        UTM zone to use.
        
        """
        
        # First, check for any utm zones provided by the user in the emission location file
        utmzones_df = el_df["utmzone"].loc[el_df["location_type"] == "U"]
        if utmzones_df.shape[0] > 0:
            # there are some; find the smallest one
            min_utmzu = int(np.nan_to_num(utmzones_df).min(axis=0))
        else:
            min_utmzu = 0
        
        # Next, compute utm zones from any user provided longitudes and find smallest            
        lon_df = el_df[["lon"]].loc[el_df["location_type"] == "L"]
        if lon_df.shape[0] > 0:
            lon_df["z"] = ((lon_df["lon"]+180)/6 + 1).astype(int)
            min_utmzl = int(np.nan_to_num(lon_df["z"]).min(axis=0))
        else:
            min_utmzl = 0
        
        if min_utmzu == 0:
            utmzone = min_utmzl
        else:
            if min_utmzl == 0:
                utmzone = min_utmzu
            else:
                utmzone = min(min_utmzu, min_utmzl)
        
        if utmzone == 0:
            print("Error! UTM zone is 0")
            sys.exit()
########### Route error to log ##################
            
        return utmzone


#%% Check for polar receptors overlapping emission sources
        
    def polar_overlap(self, polar_utme, polar_utmn, sourcelocs_df, overlap_dist):
        
        """
        
        Determine if the given polar coordinate (polar_utme, polar_utmn) overlap any emission source
        
        """
        overlap = "N"
        
        for index, row in sourcelocs_df.iterrows():
           if row["lengthx"] > 0 or row["lengthy"] > 0:
               # area source       
               inside_box = inbox(polar_utme, polar_utmn, row["utme"], row["utmn"],
                                  row["lengthx"], row["lengthy"], row["angle"], overlap_dist)
               if inside_box == True:
                   overlap = "Y"
           else:
               # point source
               if math.sqrt((row["utme"]-polar_utme)**2 + (row["utmn"]-polar_utmn)**2) <= overlap_dist:
                   overlap = "Y"
               
        return overlap


#%% See if point is within a box
        
def inbox(xt, yt, box_x, box_y, len_x, len_y, angle, df):

    """
    Determines whether a point (xt,yt) is within a fringe of df around a box
    with origin (box_x,box_y), dimensions (Len_x,Len_y), and oriented at an given
    "angle", measured clockwise from North.
    """

    inbox = False
        
    A_rad = math.radians(angle)
    D_e = (yt-box_y)*math.cos(A_rad) + (xt-box_x)*math.sin(A_rad) - len_y
    D_w = (box_y-yt)*math.cos(A_rad) + (box_x-xt)*math.sin(A_rad)
    D_n = (xt-box_x)*math.cos(A_rad) + (yt-box_y)*math.sin(A_rad) - len_x
    D_s = (box_x-xt)*math.cos(A_rad) + (box_y-yt)*math.sin(A_rad)
    D_sw = math.sqrt((xt-box_x)**2 + (yt-box_y)**2)
    D_se = (math.sqrt((box_x+len_x*math.cos(A_rad) - xt)**2 
                    + (box_y-len_x*math.sin(A_rad) - yt)**2))
    D_ne = (math.sqrt((box_x+len_x*math.cos(A_rad)+len_y*math.sin(A_rad) - xt)**2
				                    + (box_y+len_y*math.cos(A_rad)-len_x*math.sin(A_rad) - yt)**2))
    D_nw = (math.sqrt((box_x+len_y*math.sin(A_rad) - xt)**2
				                    + (box_y+len_y*math.cos(A_rad) - yt)**2))
    if D_e <= 0 and D_w <= 0:
        D_test = max(D_e, D_w, D_n, D_s)
    elif D_n <= 0 and D_s <= 0:
        D_test = max(D_e, D_w, D_n, D_s)
    else:
        D_test = min(D_ne, D_nw, D_se, D_sw)
           
    # First see if the point is in the rectangle
    if  (xt < box_x + math.tan(A_rad)*(yt-box_y) + (len_x+df)/math.cos(A_rad)
	                        and xt > box_x + math.tan(A_rad)*(yt-box_y) - df/math.cos(A_rad)
	                        and yt < box_y - math.tan(A_rad)*(xt-box_x) + (len_y+df)/math.cos(A_rad)
	                        and yt > box_y - math.tan(A_rad)*(xt-box_x) - df/math.cos(A_rad)):
         
         # Now check the corners
         if ((xt < box_x + math.tan(A_rad)*(yt-box_y)
			                   and yt < box_y - math.tan(A_rad)*(xt-box_x)
			                   and df < math.sqrt((box_x - xt)**2 + (box_y - yt)**2))
		                   or (xt > box_x + math.tan(A_rad)*(yt-box_y) + len_x/math.cos(A_rad)
			                   and yt < box_y - math.tan(A_rad)*(xt-box_x)
			                   and df < math.sqrt((box_x+len_x*math.cos(A_rad) - xt)*2
				                + (box_y-len_x*math.sin(A_rad) - yt)**2))
		                   or (xt > box_x + math.tan(A_rad)*(yt-box_y) + len_x/math.cos(A_rad)
			                   and yt > box_y - math.tan(A_rad)*(xt-box_x) + len_y/math.cos(A_rad)
			                   and df < math.sqrt((box_x+len_x*math.cos(A_rad)+len_y*math.sin(A_rad) - xt)**2
				                + (box_y+len_y*math.cos(A_rad)-len_x*math.sin(A_rad) - yt)**2))
		                   or (xt < box_x + math.tan(A_rad)*(yt-box_y)
			                   and yt > box_y - math.tan(A_rad)*(xt-box_x) + len_y/math.cos(A_rad)
			                   and df < math.sqrt((box_x+len_y*math.sin(A_rad) - xt)**2
				                + (box_y+len_y*math.cos(A_rad) - yt)**2))):
                   inbox = False
         else:
               inbox = True

    return inbox


#%% moved start_here to inside the prepare inputs object -- will be called seperately from another object but by moving it inside the other object which will take what was HEM 3 and pass facid  
#the object that calls this will need to be passed the fac_list df ids only so it can call them and run this loop.



#%% RUN Start Here
    # def run_facilities(self):
    #     fac_list = []
    #     for index, row in self.faclist_df.iterrows():
    #
    #         facid = row[0]
    #         fac_list.append(facid)
    #
    #
    #     for fac in fac_list:
    #         facid = fac
    #         #self.loc["textvariable"] = "Preparing " + facid
    #         result = self.prep_facility(facid)
    #
    #         #self.loc["textvariable"]="Building Runstream File for " + facid
    #         #messagebox.showinfo("", "Building Runstream File for " + facid)
    #
    #
    #         result.build()
    #
    #         fac_folder = "output/"+ str(facid) + "/"
    #         self.message = "starting aermod"
    #         #run aermod
    #         #self.loc["textvariable"] =  "Starting Aermod for " + facid
    #
    #         args = "aermod.exe aermod.inp"
    #         subprocess.call(args, shell=False)
    #
    #         #self.loc["textvariable"] = "Aermod complete for " + facid
    #
    #         ## Check for successful aermod run:
    #         check = open('aermod.out','r')
    #         message = check.read()
    #         if 'UNSUCCESSFUL' in message:
    #             success = False
    #         else:
    #             success = True
    #
    #         check.close()
    #
    #         if success == True:
    #
    #         #move aermod.out to the fac output folder
    #         #replace if one is already in there othewrwise will throw error
    #
    #             if os.path.isfile(fac_folder + 'aermod.out'):
    #                 os.remove(fac_folder + 'aermod.out')
    #                 shutil.move('aermod.out', fac_folder)
    #
    #             else:
    #                 shutil.move('aermod.out', fac_folder)
    #
    #         #process outputs
    #
    #             process = po.Process_outputs(facid, self.haplib_df, result.hapemis, fac_folder, self.innerblks, self.polar_df)
    #             process.process()
    #
    #         #self.loc["textvariable"] = "Analysis Complete"
    #
    #             messagebox.showinfo("", "HEM4 finished processing all facilities")
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


