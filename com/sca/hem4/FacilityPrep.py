# -*- coding: utf-8 -*-
"""
Created on Mon Oct  2 10:35:51 2017

@author: dlindsey
"""
from com.sca.hem4.CensusBlocks import *
from com.sca.hem4.log.Logger import Logger
from com.sca.hem4.runstream.Runstream import Runstream
from com.sca.hem4.upload.EmissionsLocations import *
from com.sca.hem4.upload.HAPEmissions import *
from com.sca.hem4.upload.FacilityList import *
from com.sca.hem4.support.NormalRounding import *
from com.sca.hem4.support.ElevHill import ElevHill
import math
import traceback

distance = 'distance';
angle = 'angle';
sector = 'sector';
ring = 'ring';
rec_type = 'rec_type';

class FacilityPrep():

    def __init__(self, model):

        self.model = model
        

    def createRunstream(self, facid, runPhase):

        #%%---------- Facility Options --------------------------------------
        self.model.facops = self.model.faclist.dataframe.loc[self.model.faclist.dataframe[fac_id] == facid].copy()

        op_maxdist = self.model.facops[max_dist].iloc[0]
        op_maxdistkm = op_maxdist/1000
        op_modeldist = self.model.facops[model_dist].iloc[0]
        op_circles = self.model.facops[circles].iloc[0]
        op_radial = int(self.model.facops[radial].iloc[0])
        op_overlap = self.model.facops[overlap_dist].iloc[0]

        self.fac_center = self.model.facops[fac_center].iloc[0]
        self.ring_distances = self.model.facops['ring_distances'].iloc[0]

        #%%---------- Emissions Locations --------------------------------------
        emislocs = self.model.emisloc.dataframe.loc[self.model.emisloc.dataframe[fac_id] == facid].copy()

        
        # If there is a bouyant line source with other sources, then it has to come last because of an Aermod v19191 bug.
        blRows = emislocs[emislocs[source_type]=='B']
        srcTypes = set(emislocs[source_type])
        if not blRows.empty and len(srcTypes) > 1:
            emislocs.drop(emislocs[emislocs[source_type]=='B'].index, inplace = True)
            emislocs = pd.concat([emislocs, blRows], ignore_index=True)

        # Determine the utm zone to use for this facility. Also get the hemisphere (N or S).
        facutmzonenum, hemi = UTM.zone2use(emislocs)
        facutmzonestr = str(facutmzonenum) + hemi

                
        # Compute lat/lon of any user supplied UTM coordinates
        emislocs[[lat, lon]] = emislocs.apply(lambda row: UTM.utm2ll(row[lat],row[lon],row[utmzone]) 
                               if row['location_type']=='U' else [row[lat],row[lon]], result_type="expand", axis=1)

        # Next compute UTM coordinates using the common zone
        emislocs[[utmn, utme]] = emislocs.apply(lambda row: UTM.ll2utm_alt(row[lat],row[lon],facutmzonenum,hemi)
                               , result_type="expand", axis=1)

        # Compute lat/lon of any x2 and y2 coordinates that were supplied as UTM
        emislocs[['lat_y2', 'lon_x2']] = emislocs.apply(lambda row: UTM.utm2ll(row["y2"],row["x2"],row["utmzone"]) 
                          if row['location_type']=='U' else [row["y2"],row["x2"]], result_type="expand", axis=1)

        # Compute UTM coordinates of lat_x2 and lon_y2 using the common zone
        emislocs[['utmn_y2', 'utme_x2']] = emislocs.apply(lambda row: UTM.ll2utm_alt(row["lat_y2"],row["lon_x2"],facutmzonenum,hemi)
                          , result_type="expand", axis=1)

        
        #%%---------- HAP Emissions --------------------------------------
        hapemis = self.model.hapemis.dataframe.loc[self.model.hapemis.dataframe[fac_id] == facid]


        #%%---------- Optional Buoyant Line Parameters -----------------------------------------

        if hasattr(self.model.multibuoy, "dataframe"):

            buoyant_df = self.model.multibuoy.dataframe.loc[ self.model.multibuoy.dataframe[fac_id] == facid].copy()
            buoyant_df.reset_index(drop=True, inplace=True)

        else:
            # No buoyant line sources. Empty dataframe.
            buoyant_df = None

        #%%---------- Optional Polygon Vertex File ----------------------------------------- 


        if hasattr(self.model.multipoly, "dataframe"):

            polyver_df = self.model.multipoly.dataframe.loc[self.model.multipoly.dataframe[fac_id] == facid].copy()

            if polyver_df.empty == False:
                            
                # Create utmn and utme columns. Fill with any provided utm coordinates otherwise fill with 0.
                polyver_df[[utmn, utme]] = polyver_df.apply(lambda row: self.copyUTMColumns(row[lat],row[lon])
                                         if row['location_type']=='U' else [0, 0],
                                         result_type="expand", axis=1)

                # Compute lat/lon of any user supplied UTM coordinates
                polyver_df[[lat, lon]] = polyver_df.apply(lambda row: UTM.utm2ll(row[lat],row[lon],row[utmzone]) 
                                   if row['location_type']=='U' else [row[lat],row[lon]], result_type="expand", axis=1)
    
                # Next compute UTM coordinates using the common zone
                polyver_df[[utmn, utme]] = polyver_df.apply(lambda row: UTM.ll2utm_alt(row[lat],row[lon],facutmzonenum,hemi)
                                   if row['location_type']=='L' else [row[utmn],row[utme]], result_type="expand", axis=1)
    
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
        sourcelocs = emislocs[[fac_id,source_id,source_type,lat,lon,utme,utmn,utmzone
            ,lengthx,lengthy,angle,"utme_x2","utmn_y2"]].copy()

        # Is there a polygon source at this facility?
        # If there is, read the vertex DF and append to sourcelocs
        if any(sourcelocs[source_type] == "I") == True:
            # remove the I source_type rows from sourcelocs before appending polyver_df to avoid duplicate rows
            sourcelocs = sourcelocs[sourcelocs.source_type != "I"]
            sourcelocs = pd.concat([sourcelocs, polyver_df])
            sourcelocs = sourcelocs.fillna({source_type:'', lengthx:0, lengthy:0, angle:0, "utme_x2":0, "utmn_y2":0})
            sourcelocs = sourcelocs.reset_index(drop=True)

        # Compute the coordinates of the facililty center if not specified in options
        if (self.fac_center == "" or self.ring_distances == ""):
            cenx, ceny, cenlon, cenlat, max_srcdist, vertx_a, verty_a = UTM.center(sourcelocs, facutmzonenum, hemi)

        if self.fac_center != "":
            # Grab the specified center and translate to/from UTM
            components = self.fac_center.split(',')
            if components[0] == "L":
                cenlat = float(components[1])
                cenlon = float(components[2])
                ceny, cenx, zone, hemi, epsg = UTM.ll2utm(cenlat, cenlon)
            else:
                ceny = int(float(components[1]))
                cenx = int(float(components[2]))

                zone = components[3].strip()
                cenlat, cenlon = UTM.utm2ll(ceny, cenx, zone)

        Logger.logMessage("Using facility center [x, y, lat, lon] = [" + str(cenx) + ", " + str(ceny) + ", " +
                              str(cenlat) + ", " + str(cenlon) + "]")
        self.model.computedValues['cenlat'] = cenlat
        self.model.computedValues['cenlon'] = cenlon

        # retrieve blocks
        maxdist = self.model.facops[max_dist].iloc[0]
        modeldist = self.model.facops[model_dist].iloc[0]
        
        try:
            
            if self.model.altRec_optns.get('altrec', None):
    
                self.innerblks, self.outerblks = getBlocksFromAltRecs(facid, cenx, ceny, cenlon, cenlat, facutmzonenum,
                    hemi, maxdist, modeldist, sourcelocs, op_overlap, self.model)
    
            else:
                
                self.innerblks, self.outerblks = getblocks(cenx, ceny, cenlon, cenlat, 
                                                           facutmzonenum, hemi, maxdist, 
                                                           modeldist, sourcelocs, op_overlap, 
                                                           self.model)

        except BaseException as ex:
            
            fullStackInfo = traceback.format_exc()
            message = ("An error occurred while trying to get census block:\n" 
                       + fullStackInfo)
            Logger.logMessage(message)
            
            
        if self.innerblks.empty:
            Logger.logMessage("No discrete receptors within the max distance. Aborting processing for this facility.")
            raise ValueError("No discrete receptors")

        # Assign to the model
        self.model.innerblks_df = self.innerblks
        self.model.outerblks_df = self.outerblks
        

        #%%---------- Optional User Receptors -----------------------------------------

        # If the user input any user receptors for this facility, then they will be
        # added into the Inner block receptor dataframe
        if hasattr(self.model.ureceptr, "dataframe"):

            user_recs = self.model.ureceptr.dataframe.loc[self.model.ureceptr.dataframe[fac_id] == facid].copy()
            
            if user_recs.empty == False:
                
                user_recs.utmzone = user_recs.utmzone.replace('nan', '0N', regex=True)
    
                # Create utmn and utme columns. Fill with any provided utm coordinates otherwise fill with 0.
                user_recs[[utmn, utme]] = user_recs.apply(lambda row: self.copyUTMColumns(row[lat],row[lon])
                                         if row['location_type']=='U' else [0, 0],
                                         result_type="expand", axis=1)

                # Compute lat/lon of any user supplied UTM coordinates
                user_recs[[lat, lon]] = user_recs.apply(lambda row: UTM.utm2ll(row[lat],row[lon],row[utmzone])
                             if row['location_type']=='U' else [row[lat],row[lon]], result_type="expand", axis=1)
        
                # Next compute UTM coordinates using the common zone
                user_recs[[utmn, utme]] = user_recs.apply(lambda row: UTM.ll2utm_alt(row[lat],row[lon],facutmzonenum,hemi)
                             if row['location_type']=='L' else [row[utmn],row[utme]], result_type="expand", axis=1)
        
                
                user_recs.reset_index(inplace=True)
    
    
                # Compute distance and bearing (angle) from the center of the facility
                user_recs['distance'] = np.sqrt((cenx - user_recs.utme)**2 + (ceny - user_recs.utmn)**2)
                user_recs['angle'] = user_recs.apply(lambda row: self.bearing(row[utme],row[utmn],cenx,ceny), axis=1)
                    
                # If facility is being run with elevated terrrain, get elevations
                # and hill heights if the user did not provide them.
                if self.model.facops[elev].iloc[0].upper() == "Y":
                    if user_recs[elev].max() == 0 and user_recs[elev].min() == 0:
                        message = ("Getting elevations for user receptors... \n")
                        Logger.logMessage(message)
                        coords = [(lon, lat) for lon, lat in zip(user_recs[lon], user_recs[lat])]
                        user_recs[elev] = ElevHill.getElev(coords)
                    if user_recs[hill].max() == 0 and user_recs[hill].min() == 0:
                        message = ("Computing hill heights for user receptors... \n")
                        Logger.logMessage(message)
                        usercoords_4hill = user_recs.loc[:, [lat, lon, elev]].to_numpy()
                        user_recs[hill] = ElevHill.getHill(usercoords_4hill, op_maxdistkm, cenlon, 
                                                          cenlat, self.model)
    
                # determine if the user receptors overlap any emission sources
                user_recs[overlap] = user_recs.apply(lambda row: self.check_overlap(row[utme],
                                                                                    row[utmn], sourcelocs, op_overlap), axis=1)
        
                # Add columns to make user receptors compatible with innerblks
                user_recs['urban_pop'] = 0
                user_recs['population'] = 0
                if not self.model.altRec_optns.get('altrec', None):
                    # using census data
                    user_recs.loc[:, 'fips'] = '00000'
                    user_recs.loc[:,'blockid'] = user_recs['rec_id'].str.zfill(15)
                                
                # Check for any user receptors that are already in the census data based on coordinates
                dups = pd.merge(self.innerblks[[utme, utmn]], user_recs[['rec_id', utme, utmn]], how='inner', on=[utme, utmn])
                if dups.empty == False:
                    # Some user receptors are already in the census. Remove these from the user receptor list.
                    user_recs = user_recs[~user_recs.set_index([utme, utmn]).index.isin(dups.set_index([utme, utmn]).index)].copy()
                
                    msg = 'The following user receptors have coordinates that are already in the Alternate Receptor data:\n' \
                        + str(dups['rec_id'].tolist()) + '\n' \
                        + 'They will be removed from the user receptor list.'
                    Logger.logMessage(msg)

                # Check for any user receptors that are already in the census data based on blockid
                # Only do this when using Census data
                if not self.model.altRec_optns.get('altrec', None):
                    dups = pd.merge(self.innerblks, user_recs, how='inner', on=['blockid'])
                    if dups.empty == False:
                        # Some user receptors are already in the census. Remove these from the user receptor list.
                        user_recs = user_recs[~user_recs.set_index(['blockid']).index.isin(dups.set_index(['blockid']).index)].copy()
                    
                        msg = 'The following user receptors have coordinates that are already in the Census data:\n' \
                            + str(dups['rec_id'].tolist()) + '\n' \
                            + 'They will be removed from the user receptor list.'
                        Logger.logMessage(msg)
                
                # Put into model
                self.model.userrecs_df = user_recs
                    
                # Append user_recs to innerblks
                self.innerblks = pd.concat([self.innerblks, user_recs], ignore_index=True)


        #%%----- Polar receptors ----------

        # Compute the first polar ring distance ......
        if self.ring_distances != "":
            distances = self.ring_distances.split(',')
            self.model.computedValues['firstring'] = float(distances[0])
            polar_dist = [float(x) for x in distances]
            Logger.logMessage("Using defined rings: " + str(polar_dist)[1:-1] )
        else:
            # First find the farthest distance to any source.
            maxsrcd = 0
            for i in range(0, len(vertx_a)):
                dist_cen = math.sqrt((vertx_a[i] - cenx)**2 + (verty_a[i] - ceny)**2)
                maxsrcd = max(maxsrcd, dist_cen)

            # If user first ring is > 100m, then use it, else first ring is maxsrcd + overlap.
            if self.model.facops[ring1].iloc[0] <= 100:
                ring1a = max(maxsrcd+op_overlap, 100)
                ring1b = min(ring1a, op_maxdist)
                firstring = normal_round(max(ring1b, 100))
            else:
                firstring = self.model.facops[ring1].iloc[0]

            # Store first ring in computedValues
            self.model.computedValues['firstring'] = firstring

            polar_dist = []
            polar_dist.append(firstring)


            # Make sure modeling distance is not less than first ring distance
            if self.model.facops[model_dist].iloc[0] < firstring:
                emessage = "Error! Modeling distance is less than first ring."
                Logger.logMessage(emessage)
                raise Exception("Modeling distance is less than first ring")

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

            # set computed polar distances to integers
            polar_dist = [int(item) for item in polar_dist]


        # setup list of polar angles
        start = 0.
        stop = 360. - (360./op_radial)
        polar_angl = np.linspace(start,stop,op_radial).tolist()

        # create distance and angle lists of length (number rings * number angles)
        polar_dist2 = [i for i in polar_dist for j in polar_angl]
        polar_angl2 = [j for i in polar_dist for j in polar_angl]

        # create lists of polar utm coordinates and IDs of same length
        polar_id = ["polgrid1"] * (len(polar_dist) * len(polar_angl))
        polar_utme = [normal_round(cenx + polardist * math.sin(math.radians(pa))) for polardist in polar_dist for pa in polar_angl]
        polar_utmn = [normal_round(ceny + polardist * math.cos(math.radians(pa))) for polardist in polar_dist for pa in polar_angl]
        polar_utmz = [facutmzonenum] * (len(polar_dist) * len(polar_angl))


        # sector and ring lists
        polar_sect = []
        for a in range(0, len(polar_angl2)):
            sectnum = int((a % op_radial) + 1)
            polar_sect.append(sectnum)         
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
        
        # construct the polar dataframe from the lists
        dfitems = [("id",polar_id), ("distance",polar_dist2), (angle,polar_angl2), (utme,polar_utme),
                   (utmn,polar_utmn), ("utmz",polar_utmz), 
                   ("sector",polar_sect), ("ring",polar_ring)]
        polar_df = pd.DataFrame.from_dict(dict(dfitems))

                
        # compute polar lat/lon
        polar_df[[lat, lon]] = polar_df.apply(lambda row: UTM.utm2ll(row[utmn],row[utme],facutmzonestr), 
                                              result_type="expand", axis=1)

        
        # define the index of polar_df as concatenation of sector and ring
        polar_idx = polar_df.apply(lambda row: self.define_polar_idx(row[sector], row[ring]), axis=1)
        polar_df.set_index(polar_idx, inplace=True)

        # determine if polar receptors overlap any emission sources
        polar_df[overlap] = polar_df.apply(lambda row: self.check_overlap(row[utme], row[utmn], sourcelocs, op_overlap), axis=1)

        # set rec_type of polar receptors
        polar_df[rec_type] = 'PG'
        
        #%%----- Add sector and ring to inner and outer receptors ----------

        # assign sector and ring number (integers) to each inner receptor and compute fractional sector (s)
        # and ring_loc (log weighted) numbers
        if self.innerblks.empty == False:
            self.innerblks[sector], self.innerblks["s"], self.innerblks[ring], self.innerblks["ring_loc"] = \
                 zip(*self.innerblks.apply(lambda row: self.calc_ring_sector(polar_dist,row[distance],row[angle],op_radial), axis=1))
        else:
            self.innerblks[sector], self.innerblks["s"], self.innerblks[ring], self.innerblks["ring_loc"] = None, None, None, None
            
        # assign sector and ring number (integers) to each outer receptor and compute fractional sector (s)
        # and ring_loc (log weighted) numbers
        if not self.outerblks.empty:
            self.outerblks[sector], self.outerblks["s"], self.outerblks[ring], self.outerblks["ring_loc"] = \
                 zip(*self.outerblks.apply(lambda row: self.calc_ring_sector(polar_dist,row[distance],row[angle],op_radial), axis=1))

        
        #%%------ Elevations and hill height ---------

        # If elevated terrain is being modeled, then assign elevations to emission sources 
        # that need them, and assign elevations and hill heights to polar receptors.
        
        if self.model.facops[elev].iloc[0].upper() == "Y":
            
            # Assign elevations to emission sources if not provided by the user
            if emislocs[elev].max() == 0 and emislocs[elev].min() == 0:
                message = ("Getting elevations for emission sources... \n")
                Logger.logMessage(message)
                coords = [(lon, lat) for lon, lat in zip(emislocs[lon], emislocs[lat])]
                emislocs[elev] = ElevHill.getElev(coords)
                              
            # Assign elevations to the polar receptors
            message = ("Getting elevations for polar receptors... \n")
            Logger.logMessage(message)
            coords = [(lon, lat) for lon, lat in zip(polar_df[lon], polar_df[lat])]
            polar_df[elev] = ElevHill.getElev(coords)
            
            # Assign hill heights to the polar receptors
            message = ("Computing hill heights for polar receptors... \n")
            Logger.logMessage(message)
            polarcoords_4hill = polar_df.loc[:, [lat, lon, elev]].to_numpy()
            polar_df[hill] = ElevHill.getHill(polarcoords_4hill, op_maxdistkm, cenlon, 
                                              cenlat, self.model)
            
            # Make sure hill heights are equal or greater than corresponding elevations
            qa_df = polar_df[polar_df[elev] > polar_df[hill]]
            if len(qa_df) > 0:
                Logger.logMessage("Some polar elevations are higher than the hill height. Aborting processing for this facility.")
                raise ValueError("Polar elev higher than hill height")

        else:
            
            polar_df[elev] = 0
            polar_df[hill] = 0
            emislocs[elev] = 0
            emislocs[hill] = 0

        # Put the polar grid data frame into the model
        self.model.polargrid = polar_df

         
        #%% this is where runstream file will be compiled

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
        # loop through ring distances in pairs of previous and current. Special case
        # if block is located on the last ring.
        numrings = len(ring_distances)
        if block_distance != ring_distances[numrings-1]:
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
        else:
            ring_loc = numrings - 1


        # Compute integer ring number that will be used for assigning elevations to polar receptors
        ring_int = int(ring_loc + 0.5)

        return sector_int, s, ring_int, ring_loc


    #%% Define polar receptor dataframe index
    def define_polar_idx(self, s, r):
        return "S" + str(s) + "R" + str(r)

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


    #%% rount utm coordinates
    def copyUTMColumns(self, utmn, utme):
        round_utmn = round(utmn)
        round_utme = round(utme)
        return [round_utmn, round_utme]

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


