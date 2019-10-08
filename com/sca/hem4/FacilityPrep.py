# -*- coding: utf-8 -*-
"""
Created on Mon Oct  2 10:35:51 2017

@author: dlindsey
"""
import com.sca.hem4.FindCenter as fc
from com.sca.hem4.CensusBlocks import *
from com.sca.hem4.log.Logger import Logger
from com.sca.hem4.runstream.Runstream import Runstream
from com.sca.hem4.upload.EmissionsLocations import *
from com.sca.hem4.upload.HAPEmissions import *
from com.sca.hem4.upload.FacilityList import *
from com.sca.hem4.support.NormalRounding import *
import sys
import math

distance = 'distance';
angle = 'angle';
sector = 'sector';
ring = 'ring';

##REFORMATTED TO MOVE THE DATA FRAME CREATION TO THE GUI
class FacilityPrep():

    def __init__(self, model):

        self.model = model
        

    def createRunstream(self, facid, runPhase):

        #%%---------- Facility Options --------------------------------------

        self.model.facops = self.model.faclist.dataframe.loc[self.model.faclist.dataframe[fac_id] == facid]

        # Set defaults of the facility options
        if self.model.facops[max_dist].isnull().sum() > 0 or self.model.facops.iloc[0][max_dist] > 50000:
            self.model.facops[max_dist] = 50000

        if self.model.facops[model_dist].isnull().sum() > 0:
            self.model.facops[model_dist] = 3000

        # Replace NaN with blank, No or 0
        # Note: use of elevations is defaulted to Y, acute hours is defaulted to 1
        #       and acute multiplier is defaulted to 1
        self.model.facops = self.model.facops.fillna({radial:0, circles:0, overlap_dist:0, hours:1, multiplier:1,
                                ring1:0, urban_pop:0, hivalu:1})
        self.model.facops.replace(to_replace={met_station:{"nan":"N"}, rural_urban:{"nan":""}, elev:{"nan":"Y"}, 
                                   dep:{"nan":"N"}, depl:{"nan":"N"}, phase:{"nan":""}, pdep:{"nan":"NO"}, 
                                   pdepl:{"nan":"NO"}, vdep:{"nan":"NO"}, vdepl:{"nan":"NO"}, 
                                   all_rcpts:{"nan":"N"}, user_rcpt:{"nan":"N"}, bldg_dw:{"nan":"N"}, 
                                   fastall:{"nan":"N"}, acute:{"nan":"N"}}, inplace=True)

        self.model.facops = self.model.facops.reset_index(drop = True)

        
        
        #----- Default missing or out of range facility options --------

        #  Maximum Distance
        if self.model.facops[max_dist][0] >= 50000:
            self.model.facops.loc[:, max_dist] = 50000
        elif self.model.facops[max_dist][0] == 0:
            self.model.facops.loc[:, max_dist] = 50000

        # Modeled Distance of Receptors
        if self.model.facops[model_dist][0] == 0:
            self.model.facops.loc[:, model_dist] = 3000

        # Radials
        if self.model.facops[radial][0] == 0:
            self.model.facops.loc[:, radial] = 16

        # Circles
        if self.model.facops[circles][0] == 0:
            self.model.facops.loc[:, circles] = 13

        # Overlap Distance
        if self.model.facops[overlap_dist][0] == 0:
            self.model.facops.loc[:, overlap_dist] = 30
        elif self.model.facops[overlap_dist][0] < 1:
            self.model.facops.loc[:, overlap_dist] = 30
        elif self.model.facops[overlap_dist][0] > 500:
            self.model.facops.loc[:, overlap_dist] = 30
        

        op_maxdist = self.model.facops[max_dist][0]
        op_modeldist = self.model.facops[model_dist][0]
        op_circles = self.model.facops[circles][0]
        op_radial = self.model.facops[radial][0]
        op_overlap = self.model.facops[overlap_dist][0]

        #%%---------- Emission Locations --------------------------------------

        # Get emission location info for this facility
        emislocs = self.model.emisloc.dataframe.loc[self.model.emisloc.dataframe[fac_id] == facid]

        # Replace NaN with blank or 0
        emislocs = emislocs.fillna({utmzone:0, source_type:'', lengthx:0, lengthy:0, angle:0,
                                    horzdim:0, vertdim:0, areavolrelhgt:0, stkht:0, stkdia: 0,
                                    stkvel:0, stktemp:0, elev:0, x2:0, y2:0})
        emislocs = emislocs.reset_index(drop = True)

        # Determine the utm zone to use for this facility
        facutmzone = self.zone2use(emislocs)

        # Convert all lat/lon coordinates to UTM and UTM coordinates to lat/lon
        slat = emislocs[lat].reset_index(drop=True)
        slon = emislocs[lon].reset_index(drop=True)
        sutmzone = emislocs[utmzone].reset_index(drop=True)
        
        # First compute lat/lon coors using whatever zone was provided
        alat, alon = UTM.utm2ll(slat, slon, sutmzone)
        emislocs[lat] = alat.tolist()
        emislocs[lon] = alon.tolist()

        # Next compute UTM coors using the common zone
        sutmzone = facutmzone*np.ones(len(emislocs[lat]))
        autmn, autme, autmz = UTM.ll2utm(slat, slon, sutmzone)
        emislocs[utme] = autme.tolist()
        emislocs[utmn] = autmn.tolist()
        emislocs[utmzone] = autmz.tolist()

        # Compute UTM of any x2 and y2 coordinates and add to emislocs
        slat = emislocs[y2].reset_index(drop=True)
        slon = emislocs[x2].reset_index(drop=True)
        sutmzone = emislocs[utmzone].reset_index(drop=True)

        alat, alon = UTM.utm2ll(slat, slon, sutmzone)
        emislocs["lat_y2"] = alat.tolist()
        emislocs["lon_x2"] = alon.tolist()

        sutmzone = facutmzone*np.ones(len(emislocs[lat]))
        autmn, autme, autmz = UTM.ll2utm(slat, slon, sutmzone)
        emislocs["utme_x2"] = autme.tolist()
        emislocs["utmn_y2"] = autmn.tolist()

        #%%---------- HAP Emissions --------------------------------------

        # Get emissions data for this facility
        hapemis = self.model.hapemis.dataframe.loc[self.model.hapemis.dataframe[fac_id] == facid]

        # Replace NaN with blank or 0
        hapemis = hapemis.fillna({emis_tpy:0, part_frac:0})
        hapemis = hapemis.reset_index(drop = True)


        #%%---------- Optional Buoyant Line Parameters ----------------------------------------- needs to be connected

        if hasattr(self.model.multibuoy, "dataframe"):

            buoyant_df = self.model.multibuoy.dataframe.loc[ self.model.multibuoy.dataframe[fac_id] == facid].copy()
            buoyant_df.reset_index(drop=True, inplace=True)

        else:
            # No buoyant line sources. Empty dataframe.
            buoyant_df = None

        #%%---------- Optional Polygon Vertex File ----------------------------------------- neeeds to be connected


        if hasattr(self.model.multipoly, "dataframe"):

            polyver_df = self.model.multipoly.dataframe.loc[self.model.multipoly.dataframe[fac_id] == facid].copy()
            slat = polyver_df[lat].reset_index(drop=True)
            slon = polyver_df[lon].reset_index(drop=True)
            szone = polyver_df[utmzone].reset_index(drop=True)

            # First compute lat/lon coors using whatever zone was provided
            alat, alon = UTM.utm2ll(slat, slon, szone)
            polyver_df[lat] = alat.tolist()
            polyver_df[lon] = alon.tolist()

            # Next compute UTM coors using the common zone
            sutmzone = facutmzone*np.ones(len(polyver_df[lat]))
            autmn, autme, autmz = UTM.ll2utm(slat, slon, sutmzone)
            polyver_df[utme] = autme.tolist()
            polyver_df[utmn] = autmn.tolist()
            polyver_df[utmzone] = autmz.tolist()

            # Assign source_type
            polyver_df[source_type] = "I"

        else:
            # No polygon sources. Empty dataframe.
            polyver_df = None

        #%%---------- Optional Building Downwash -------------------------------------

        if hasattr(self.model.bldgdw, "dataframe"):

            bldgdw_df = self.model.bldgdw.dataframe.loc[self.model.bldgdw.dataframe[fac_id] == facid].copy()

        else:
            bldgdw_df = None




        #%% ------ Optional Particle Data -------------------------------------

        if hasattr(self.model.partdep, "dataframe"):

            partdia_df = self.model.partdep.dataframe.loc[self.model.partdep.dataframe[fac_id] == facid].copy()

        else:
            partdia_df = None


        #%% -- Optional Land Use ----------------------------------------------

        if hasattr(self.model.landuse, "dataframe"):
            landuse_df = self.model.landuse.dataframe.loc[self.model.landuse.dataframe[fac_id] == facid].copy()

        else:
            landuse_df = None



        #%% --- Optional Seasons ---------------------------------------------

        if hasattr(self.model.seasons, "dataframe"):
            seasons_df = self.model.seasons.dataframe.loc[self.model.seasons.dataframe[fac_id] == facid].copy()

        else:
            seasons_df = None



        #%% --- Optional Emissions Variations --------------------------------

        if hasattr(self.model.emisvar, "dataframe"):

            #TODO - what is this for? Can emission variation file be in text format?           
            if self.model.emisvar.path[-3:] == 'txt':
                
                #if linked file set stored file path 
                emisvar_df = self.model.emisvar.path
                
            else:
                emisvar_df = self.model.emisvar.dataframe.loc[self.model.emisvar.dataframe[fac_id] == facid].copy()

        else:
            emisvar_df = None


        #%%-- Gas Params for gas runs -- needs to be incorporated better

        #if hasattr(self.model.gasparams, "dataframe"):
            #gasparams_df = self.model.gasparams.dataframe

        #else:
            #gasparams_df = None

        #%%---------- Get Census Block Receptors --------------------------------------

        # Keep necessary source location columns
        sourcelocs = emislocs[[fac_id,source_id,source_type,utme,utmn,utmzone
            ,lengthx,lengthy,angle,"utme_x2","utmn_y2"]].copy()

        # Is there a polygon source at this facility?
        # If there is, read the vertex file and append to sourcelocs
        if any(sourcelocs[source_type] == "I") == True:
            # remove the I source_type rows from sourcelocs before appending polyver_df to avoid duplicate rows
            sourcelocs = sourcelocs[sourcelocs.source_type != "I"]
            sourcelocs = sourcelocs.append(polyver_df)
            sourcelocs = sourcelocs.fillna({source_type:'', lengthx:0, lengthy:0, angle:0, "utme_x2":0, "utmn_y2":0})
            sourcelocs = sourcelocs.reset_index(drop=True)

        # Compute the coordinates of the facililty center
        cenx, ceny, cenlon, cenlat, max_srcdist, vertx_a, verty_a = fc.center(sourcelocs, facutmzone)

        self.model.computedValues['cenlat'] = cenlat
        self.model.computedValues['cenlon'] = cenlon

        #retrieve blocks
        maxdist = self.model.facops[max_dist][0]
        modeldist = self.model.facops[model_dist][0]

        if self.model.altRec_optns.get('altrec', None):
            self.innerblks, self.outerblks = self.getBlocksFromUrep(facid, cenx, ceny, cenlon, cenlat, facutmzone,
                maxdist, modeldist, sourcelocs, op_overlap)

        else:
            self.innerblks, self.outerblks = getblocks(cenx, ceny, cenlon, cenlat, facutmzone, maxdist, modeldist,
                sourcelocs, op_overlap, self.model)


        #%%---------- Optional User Receptors -----------------------------------------

        # If the user input any user receptors for this facility, then they will be
        # added into the Inner block receptor dataframe

        if hasattr(self.model.ureceptr, "dataframe"):

            user_recs = self.model.ureceptr.dataframe.loc[self.model.ureceptr.dataframe[fac_id] == facid].copy()
            user_recs.reset_index(inplace=True)

            if not user_recs.empty:
                # First compute lat/lon coors using whatever zone was provided
                slat = user_recs[lat].reset_index(drop=True)
                slon = user_recs[lon].reset_index(drop=True)
                szone = user_recs[utmzone].reset_index(drop=True)
                alat, alon = UTM.utm2ll(slat, slon, szone)
                user_recs[lat] = alat.tolist()
                user_recs[lon] = alon.tolist()

                # Next compute UTM coors using the common zone
                sutmzone = facutmzone*np.ones(len(user_recs[lat]))
                autmn, autme, autmz = UTM.ll2utm(slat, slon, sutmzone)
                user_recs[utme] = autme.tolist()
                user_recs[utmn] = autmn.tolist()
                user_recs[utmzone] = autmz.tolist()

                # Compute distance and bearing (angle) from the center of the facility
                user_recs['distance'] = np.sqrt((cenx - user_recs.utme)**2 + (ceny - user_recs.utmn)**2)
                user_recs['angle'] = user_recs.apply(lambda row: self.bearing(row[utme],row[utmn],cenx,ceny), axis=1)

                # If all user receptor elevations are NaN, then replace with closest block elevation.
                # If at least one elevation is not NaN, then leave non-NaN alone and replace NaN with 0.
                # If all hill heights are NaN, then replace with max of closest block hill, closest block elev,
                # or max user provided elev.
                maxelev = user_recs[elev].max(axis=0, skipna=True) \
                    if math.isnan(user_recs[elev].max(axis=0, skipna=True)) == False \
                    else 0
                maxhill = user_recs[hill].max(axis=0, skipna=True) \
                    if math.isnan(user_recs[hill].max(axis=0, skipna=True)) == False \
                    else 0
                elev_allnan = user_recs[elev].all(axis=0)
                hill_allnan = user_recs[hill].all(axis=0)

                if elev_allnan == True or hill_allnan == True:
                    for index, row in user_recs.iterrows():
                        elev_close, hill_close = self.urec_elevs(row[utme], row[utmn],
                                                                 self.innerblks, self.outerblks)
                        if elev_allnan == True:
                            user_recs.loc[index, elev] = elev_close
                        if hill_allnan == True:
                            user_recs.loc[index, hill] = max([maxelev, elev_close, hill_close])

                if elev_allnan == False:
                    # Not all elevs are NaN. Leave non-NaN alone and replace NaN with 0.
                    user_recs[elev].fillna(0, inplace=True)

                if hill_allnan == False:
                    # Not all hills are NaN. Leave non-NaN alone and replace NaN with 0.
                    user_recs[hill].fillna(0, inplace=True)

                # determine if the user receptors overlap any emission sources
                user_recs[overlap] = user_recs.apply(lambda row: self.check_overlap(row[utme],
                                                                                    row[utmn], sourcelocs, op_overlap), axis=1)


                # Add or remove columns to make user_recs compatible with innerblks
                #            user_recs.drop('fac_id', inplace=True, axis=1)
                user_recs['urban_pop'] = 0
                user_recs['population'] = 0
                if self.model.altRec_optns.get('altrec', None):
                    user_recs['rec_id'] = 'U_' + user_recs['rec_id']
                else:
                    user_recs['fips'] = 'U0000'
                    user_recs['idmarplot'] = 'U0000U' + user_recs['rec_id']

                # Append user_recs to innerblks
                self.innerblks = self.innerblks.append(user_recs, ignore_index=True)


        #%%----- Polar receptors ----------

        #..... Compute the first polar ring distance ......
                
        # First find the farthest distance to any source.
        maxsrcd = 0
        for i in range(0, len(vertx_a)):
            dist_cen = math.sqrt((vertx_a[i] - cenx)**2 + (verty_a[i] - ceny)**2)
            maxsrcd = max(maxsrcd, dist_cen)

        # If user first ring is > 100m, then use it, else first ring is maxsrcd + overlap.
        if self.model.facops[ring1][0] <= 100:
            ring1a = max(maxsrcd+op_overlap, 100)
            ring1b = min(ring1a, op_maxdist)
            firstring = normal_round(max(ring1b, 100))
        else:
            firstring = self.model.facops[ring1][0]
        polar_dist = []
        polar_dist.append(firstring)

        
        #.... Compute the rest of the polar ring distances (logarithmically spaced) .......

        if op_modeldist < op_maxdist:
            # first handle ring distances inside the modeling distance
            k = 1
            if op_modeldist <= polar_dist[0]:
                N_in = 0
                N_out = op_circles
                D_st2 = polar_dist[0]
            else:            
                N_in = normal_round(math.log(op_modeldist/polar_dist[0])/math.log(op_maxdist/polar_dist[0]) * (op_circles - 2))
                while k < N_in:
                    next_dist = round(polar_dist[k-1] * ((op_modeldist/polar_dist[0])**(1/N_in)), -1)
                    polar_dist.append(next_dist)
                    k = k + 1
                # set a ring at the modeling distance
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
            # set the last ring distance to the domain distance
            polar_dist.append(op_maxdist)
        else:
            # model distance = domain distance
            k = 1
            N_in = normal_round(math.log(op_modeldist/polar_dist[0])/math.log(op_maxdist/polar_dist[0]) * (op_circles - 1))
            while k < N_in:
                next_dist = round(polar_dist[k-1] * ((op_modeldist/polar_dist[0])**(1/N_in)), -1)
                polar_dist.append(next_dist)
                k = k + 1
            # set the last ring distance to the domain distance
            polar_dist.append(op_maxdist)            

        # setup list of polar angles
        start = 0.
        stop = 360. - (360./op_radial)
        polar_angl = np.linspace(start,stop,op_radial).tolist()

        # create lists of other polar receptor parameters
        polar_id = ["polgrid1"] * (len(polar_dist) * len(polar_angl))
        polar_utme = [normal_round(cenx + polardist * math.sin(math.radians(pa))) for polardist in polar_dist for pa in polar_angl]
        polar_utmn = [normal_round(ceny + polardist * math.cos(math.radians(pa))) for polardist in polar_dist for pa in polar_angl]
        polar_utmz = [facutmzone] * (len(polar_dist) * len(polar_angl))
        polar_lat, polar_lon = UTM.utm2ll(polar_utmn, polar_utme, polar_utmz)

        # create dist and angl lists of length op_circle*op_radial
        polar_dist2 = [i for i in polar_dist for j in polar_angl]
        polar_angl2 = [j for i in polar_dist for j in polar_angl]
        
        # sector and ring lists
        polar_sect = [int(((a*op_radial/360) % op_radial)+1) for a in polar_angl2]
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
        dfitems = [("id",polar_id), ("distance",polar_dist2), (angle,polar_angl2), (utme,polar_utme),
                   (utmn,polar_utmn), ("utmz",polar_utmz), (lon,polar_lon), (lat,polar_lat),
                   ("sector",polar_sect), ("ring",polar_ring)]
        polar_df = pd.DataFrame.from_dict(dict(dfitems))

        # define the index of polar_df as concatenation of sector and ring
        polar_idx = polar_df.apply(lambda row: self.define_polar_idx(row[sector], row[ring]), axis=1)
        polar_df.set_index(polar_idx, inplace=True)

        # determine if polar receptors overlap any emission sources
        polar_df[overlap] = polar_df.apply(lambda row: self.check_overlap(row[utme], row[utmn], sourcelocs, op_overlap), axis=1)

        # set rec_type of polar receptors
        polar_df[rec_type] = 'PG'
        
        #%%----- Add sector and ring to inner and outer receptors ----------

        # assign sector and ring number (integers) to each inner receptor and compute fractional sector (s) and ring_loc (log weighted) numbers
        if self.innerblks.empty == False:
            self.innerblks[sector], self.innerblks["s"], self.innerblks[ring], self.innerblks["ring_loc"] = \
                 zip(*self.innerblks.apply(lambda row: self.calc_ring_sector(polar_dist,row[distance],row[angle],op_radial), axis=1))
        else:
            self.innerblks[sector], self.innerblks["s"], self.innerblks[ring], self.innerblks["ring_loc"] = None, None, None, None
            
        # assign sector and ring number (integers) to each outer receptor and compute fractional sector (s) and ring_loc (log weighted) numbers
        self.outerblks[sector], self.outerblks["s"], self.outerblks[ring], self.outerblks["ring_loc"] = \
             zip(*self.outerblks.apply(lambda row: self.calc_ring_sector(polar_dist,row[distance],row[angle],op_radial), axis=1))

        
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
        if self.model.facops[elev][0].upper() == "Y":
            polar_df[elev], polar_df[hill], polar_df['avgelev'] = zip(*polar_df.apply(lambda row: 
                        self.assign_polar_elev_step1(row,self.innerblks,self.outerblks,maxdist), axis=1))
            # If user did not supply any source elevations, compute them. Otherwise, empty
            # source elevations will be taken as 0.
            if emislocs[elev].max() == 0 and emislocs[elev].min() == 0:
                emislocs[elev] = self.compute_emisloc_elev(polar_df,op_circles)
            # if polar receptor still has missing elevation, fill it in
            polar_df[elev], polar_df[hill], polar_df['avgelev'] = zip(*polar_df.apply(lambda row: 
                        self.assign_polar_elev_step2(row,self.innerblks,self.outerblks,emislocs), axis=1))
        else:
            polar_df[elev] = 0
            polar_df[hill] = 0
            emislocs[elev] = 0
            emislocs[hill] = 0

        
        # Assign the polar grid data frame to the model (exclude avgelev column)
        self.model.polargrid = polar_df.drop('avgelev', axis=1)


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

        runstream = Runstream(self.model.facops, emislocs, hapemis, buoyant_df,
                              polyver_df, bldgdw_df, partdia_df, landuse_df,
                              seasons_df, emisvar_df, self.model)
        runstream.build_co(runPhase, self.innerblks, self.outerblks)
        runstream.build_so(runPhase)
        runstream.build_re(self.innerblks, cenx, ceny, polar_df)
        metfile, distanceToMet = runstream.build_me(cenlat, cenlon)
        self.model.computedValues['metfile'] = metfile
        self.model.computedValues['distance'] = distanceToMet

        runstream.build_ou()

        return runstream
        #no return statement since it will just need to build the file
        #return rs.Runstream(self.model.facops, emislocs, hapemis, cenlat, cenlon, cenx, ceny, self.innerblks, user_recs, buoyant_df, polyver_df, polar_df, bldgdw_df, partdia_df, landuse_df, seasons_df, gasparams_df)

    
    
    #%% Calculate ring and sector of block receptors
    def calc_ring_sector(self, ring_distances, block_distance, block_angle, num_sectors):
            
        # Compute fractional sector number that will be used for interpolation
        # Note: sectors for interpolation go from 1 to num_sectors beginning at due north (zero degrees)
#        s = round(((block_angle * num_sectors)/360.0 % num_sectors), 2) + 1
        s = ((block_angle * num_sectors)/360.0 % num_sectors) + 1

        # Compute integer sector number that will be used for assigning elevations to polar receptors
        # .... these go from halfway between two radials to halfway between the next set of two radials, clockwise
        sector_int = int(((((block_angle * num_sectors)/360.0) + 0.5) % num_sectors) + 1)
        if sector_int == 0:
            sector_int = num_sectors

        # Compute fractional, log weighted ring value that will be used for interpolation. 
        # loop through ring distances in pairs of previous and current.
        ring_loc = 1
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

        # Compute integer ring number that will be used for assigning elevations to polar receptors
        ring_int = int(ring_loc + 0.5)

        return sector_int, s, ring_int, ring_loc

    #%% Assign elevation and hill height to polar receptors
    def assign_polar_elev_step1(self, polar_row, innblks, outblks, maxdist):

        sector1 = polar_row[sector]
        ring1 = polar_row[ring]

        #subset the inner and outer block dataframes to sector, ring
        innblks_sub = innblks.loc[(innblks[sector] == sector1) & (innblks[ring] == ring1)]
        outblks_sub = outblks.loc[(outblks[sector] == sector1) & (outblks[ring] == ring1)]

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

        #look at inner block subset
        for index, row in innblks_sub.iterrows():
            if row[elev] > r_maxelev:
                r_maxelev = row[elev]
                r_hill = row[hill]
            r_avgelev = r_avgelev + row[elev]
            r_popelev = r_popelev + row[elev] * row[population]
            r_nblk = r_nblk + 1
            r_pop = r_pop + row[population]
            d_test = math.sqrt(row[distance]**2 + polar_row[distance]**2 - 2*row[distance]*polar_row[distance]*math.cos(math.radians(row[angle]-polar_row[angle])))
            if d_test <= d_nearelev:
                d_nearelev = d_test
                r_nearelev = row[elev]


        #look at outer block subset
        for index, row in outblks_sub.iterrows():
            if row[elev] > r_maxelev:
                r_maxelev = row[elev]
                r_hill = row[hill]
            r_avgelev = r_avgelev + row[elev]
            r_popelev = r_popelev + row[elev] * row[population]
            r_nblk = r_nblk + 1
            r_pop = r_pop + row[population]
            d_test = math.sqrt(row[distance]**2 + polar_row[distance]**2 - 2*row[distance]*polar_row[distance]*math.cos(math.radians(row[angle]-polar_row[angle])))
            if d_test <= d_nearelev:
                d_nearelev = d_test
                r_nearelev = row[elev]


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
        return normal_round(r_maxelev), normal_round(r_hill), normal_round(r_avgelev)


    #%% Assign elevation and hill height to polar receptors that still have missing elevations
    def assign_polar_elev_step2(self, polar_row, innblks, outblks, emislocs):

        d_nearelev = 99999
        d_nearhill = 99999
        r_maxelev = -88888
        r_hill = -88888

        if polar_row[elev] == -999:

            #check emission locations
            emislocs_dist = np.sqrt((emislocs[utme] - polar_row[utme])**2 + (emislocs[utmn] - polar_row[utmn])**2)
            mindist_index = emislocs_dist.values.argmin()
            d_test = emislocs_dist.iloc[mindist_index]
            if d_test <= d_nearelev:
                d_nearelev = d_test
                r_nearelev = emislocs[elev].iloc[mindist_index]
                r_maxelev = r_nearelev
                r_avgelev = r_nearelev
                r_popelev = r_nearelev

            #check inner blocks
            if innblks.empty == False:
                inner_dist = np.sqrt((innblks[utme] - polar_row[utme])**2 + (innblks[utmn] - polar_row[utmn])**2)
                mindist_index = inner_dist.values.argmin()
                d_test = inner_dist.iloc[mindist_index]
                if d_test <= d_nearelev:
                    d_nearelev = d_test
                    r_nearelev = innblks[elev].iloc[mindist_index]
                    r_maxelev = r_nearelev
                    r_avgelev = r_nearelev
                    r_popelev = r_nearelev
                    r_nearhill = innblks[hill].iloc[mindist_index]
                    r_hill = r_nearhill
            
            #check outer blocks
            outer_dist = (outblks[utme] - polar_row[utme])**2 + (outblks[utmn] - polar_row[utmn])**2
            mindist_index = outer_dist.values.argmin()
            d_test = outer_dist.iloc[mindist_index]
            if d_test <= d_nearelev:
                d_nearelev = d_test
                r_nearelev = outblks[elev].iloc[mindist_index]
                r_maxelev = r_nearelev
                r_avgelev = r_nearelev
                r_popelev = r_nearelev
                r_nearhill = outblks[hill].iloc[mindist_index]
                r_hill = r_nearhill

            r_hill = max(r_hill, r_maxelev)
            
        else:

            r_maxelev = polar_row[elev]
            r_hill = polar_row[hill]
            r_avgelev = -999

        #Note: the max elevation is returned as the elevation for this polar receptor
        return normal_round(r_maxelev), normal_round(r_hill), normal_round(r_avgelev)

    #%% Compute the elevation to be used for all emission sources
    def compute_emisloc_elev(self, polars, num_rings):

        # The average of the average elevation for a ring will be used as the source elevation.

        D_selev = 0
        N_selev = 0
        ringnum = 1
        while D_selev == 0 and ringnum <= num_rings:
            polar_sub = polars.loc[polars[ring] == ringnum]
            for index, row in polar_sub.iterrows():
                if row['avgelev'] != -999:
                    D_selev = D_selev + row['avgelev']
                    N_selev = N_selev + 1
            ringnum = ringnum + 1

        if N_selev != 0:
            avgelev = D_selev / N_selev
        else:
            Logger.logMessage("Error! No elevation was computed for the emission sources.")
            #TODO Where should things be directed now?
            sys.exit()
                
        return normal_round(avgelev)

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
        utmzones_df = el_df[utmzone].loc[el_df[location_type] == "U"]
        if utmzones_df.shape[0] > 0:
            # there are some; find the smallest one
            min_utmzu = int(np.nan_to_num(utmzones_df).min(axis=0))
        else:
            min_utmzu = 0

        # Next, compute utm zones from any user provided longitudes and find smallest
        lon_df = el_df[[lon]].loc[el_df[location_type] == "L"]
        if lon_df.shape[0] > 0:
            lon_df["z"] = ((lon_df[lon]+180)/6 + 1).astype(int)
            min_utmzl = int(np.nan_to_num(lon_df["z"]).min(axis=0))
        else:
            min_utmzl = 0

        if min_utmzu == 0:
            utmZone = min_utmzl
        else:
            if min_utmzl == 0:
                utmZone = min_utmzu
            else:
                utmZone = min(min_utmzu, min_utmzl)

        if utmZone == 0:
            print("Error! UTM zone is 0")
            sys.exit()
########### Route error to log ##################

        return utmZone


    #%% Check for receptors overlapping emission sources
    def check_overlap(self, rec_utme, rec_utmn, sourcelocs_df, overlap_dist):

        """

        Determine if the given receptor coordinate (rec_utme, rec_utmn) overlap any emission source

        """
        overlap = "N"

        for index, row in sourcelocs_df.iterrows():
           if row[lengthx] > 0 or row[lengthy] > 0:
               # area source
               inside_box = self.inbox(rec_utme, rec_utmn, row[utme], row[utmn],
                                  row[lengthx], row[lengthy], row[angle], overlap_dist)
               if inside_box == True:
                   overlap = "Y"
           else:
               # point source
               if math.sqrt((row[utme]-rec_utme)**2 + (row[utmn]-rec_utmn)**2) <= overlap_dist:
                   overlap = "Y"

        return overlap


    #%% See if point is within a box
    def inbox(self, xt, yt, box_x, box_y, len_x, len_y, angle, df):

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
                                   and df < math.sqrt((box_x+len_x*math.cos(A_rad) - xt)**2
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

    def copyUTMColumns(self, utmn, utme, utmz):
        return [utmn, utme, utmz]

    #%% compute a bearing from the center of the facility to a receptor (utm coordinates)
    def bearing(self, utme, utmn, cenx, ceny):
        if utmn > ceny:
            if utme > cenx:
                angle = math.degrees(math.atan((utme-cenx)/(utmn-ceny)))
            else:
                angle = 360 + math.degrees(math.atan((utme-cenx)/(utmn-ceny)))
        elif utmn < ceny:
            angle = 180 + math.degrees(math.atan((utme-cenx)/(utmn-ceny)))
        else:
            if utme >= cenx:
                angle = 90
            else:
                angle = 270
             
        return angle        


    # Determine inner and outer blocks from the set of user receptors only.
    def getBlocksFromUrep(self, facid, cenx, ceny, cenlon, cenlat, utmZone, maxdist, modeldist, sourcelocs, overlap_dist):

        # convert max outer ring distance from meters to degrees latitude
        maxdist_deg = maxdist*39.36/36/2000/60

        # Get all user receptors that correspond to the given fac id
        urecs = self.model.altreceptr.dataframe.loc[self.model.altreceptr.dataframe[fac_id] == facid]

        # If any population values are missing, we cannot create an Incidence report
        self.model.altRec_optns['altrec_nopop'] = urecs.isnull().any()[population]
        urecs[population] = pd.to_numeric(urecs[population], errors='coerce').fillna(0)

        # If any elevation or hill height values are missing, we must run in FLAT mode.
        self.model.altRec_optns['altrec_flat'] = urecs.isnull().any()[elev] or urecs.isnull().any()[hill]
        urecs[elev] = pd.to_numeric(urecs[elev], errors='coerce').fillna(0)
        urecs[hill] = pd.to_numeric(urecs[hill], errors='coerce').fillna(0)

        # Which location type is being used? If lat/lon, convert to UTM. Otherwise, just copy over
        # the relevant values.
        ltype = urecs.iloc[0][location_type]
        if ltype == 'L':
            urecs[utms] = urecs.apply(lambda row: UTM.ll2utm_alt(row[lat], row[lon], utmZone), axis=1)
        else:
            urecs[utms] = urecs.apply(lambda row: self.copyUTMColumns(row[lat], row[lon], utmZone), axis=1)

        #split utms column into utmn, utme, utmz
        urecs[[utmn, utme, utmz]] = pd.DataFrame(urecs.utms.values.tolist(), index= urecs.index)

        del urecs[utms]

        #coerce hill and elevation into floats
        urecs[hill] = pd.to_numeric(urecs[hill], errors='coerce').fillna(0)
        urecs[elev] = pd.to_numeric(urecs[elev], errors='coerce').fillna(0)

        #compute distance and bearing (angle) from the center of the facility
        urecs['distance'] = np.sqrt((cenx - urecs.utme)**2 + (ceny - urecs.utmn)**2)
        urecs['angle'] = urecs.apply(lambda row: bearing(row[utme],row[utmn],cenx,ceny), axis=1)
        urecs['urban_pop'] = 0

        #subset the urecs dataframe to blocks that are within the modeling distance of the facility
        modelblks = urecs.query('distance <= @maxdist')

        # Split modelblks into inner and outer block receptors
        innerblks, outerblks = in_box(modelblks, sourcelocs, modeldist, maxdist, overlap_dist, self.model)


#        Logger.log("OUTERBLOCKS", outerblks, False)

        # convert utme, utmn, utmz, and population to integers
        innerblks[utme] = innerblks[utme].astype(int)
        innerblks[utmn] = innerblks[utmn].astype(int)
        innerblks[utmz] = innerblks[utmz].astype(int)
        innerblks[population] = pd.to_numeric(innerblks[population], errors='coerce').astype(int)
        outerblks[utme] = outerblks[utme].astype(int)
        outerblks[utmn] = outerblks[utmn].astype(int)
        outerblks[utmz] = outerblks[utmz].astype(int)
        outerblks[population] = pd.to_numeric(outerblks[population], errors='coerce').astype(int)

        return innerblks, outerblks


    #%% Calculate elevation and hill height for user-specified receptors
    def urec_elevs(self, ur_utme, ur_utmn, innblks, outblks):
        """
        ur_utme - User receptor UTM Easting coordinate
        ur_utmn - User receptor UTM Northing coordinate
        innblks - Dataframe of inner block receptors
        outblks - Dataframe of outer block receptors
        """
        mindist = 999999
        
        # Loop over inner blocks looking for closest one
        for index, row in innblks.iterrows():
            temp_dist = np.sqrt((ur_utme - row.utme)**2 + (ur_utmn - row.utmn)**2)
            if temp_dist < mindist:
                mindist = temp_dist
                elev_est = row.elev
                hill_est = row.hill
        
        # Loop over outer blocks to see if any are closer
        for index, row in outblks.iterrows():
            temp_dist = np.sqrt((ur_utme - row.utme)**2 + (ur_utmn - row.utmn)**2)
            if temp_dist < mindist:
                mindist = temp_dist
                elev_est = row.elev
                hill_est = row.hill
        
        return elev_est, hill_est
        
    