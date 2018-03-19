# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 15:07:13 2017

@author: dlindsey
"""


import os 
import pandas as pd
import numpy as np
import math

## User-Defined Functions/Modules

import ll2utm
import find_met as fm


## Test files
 # %% Optional Input Files (uncomment for test)
    
#    receptr_df = pd.read_excel(r"C:\HEM3_V153\Inputs_multi\Template_Multi_user_receptors.xlsx")
#    landuse_df = pd.read_excel(r"C:\HEM3_V153\Inputs_multi\Template_Multi_landuse.xlsx")
#    partdia_df = pd.read_excel(r"C:\HEM3_V153\Inputs_multi\Template_Multi_particle_data.xlsx")
#    gseason_df = pd.read_excel(r"C:\HEM3_V153\Inputs_multi\Template_Multi_seasons.xlsx")

#%%

class Runstream():
    
    def __init__(self, facops_df, emislocs_df, hapemis_df, cenlat, cenlon, cenx, ceny, innerblks_df, userrecs_df, buoyant_df, polyver_df, polar_df):
        self.facoptn_df = facops_df
        self.emisloc_df = emislocs_df
        self.hapemis = hapemis_df
        self.cenlat = cenlat
        self.cenlon = cenlon
        self.cenx = cenx
        self.ceny = ceny
        self.discrecs_df = innerblks_df
        #self.outerblks = outerblks_df
        #self.sourcelocs = sourcelocs
        self.user_recs = userrecs_df
        self.buoyant_df = buoyant_df
        self.polyver_df = polyver_df
        self.polar_df = polar_df
        
        
        
    def build(self):
        
        #print(str(self.facoptn_df['fac_id'][0]) + " starting in runstream")
     # %% Set variable emission factor yes/no variable to no. This will come from the GUI.
    
        varemis = 0
        
    # %% Emission Location File
    
        srid = self.emisloc_df['source_id'][:]                   # Source ID
        cord = self.emisloc_df['location_type'][:]           # Coordinate System
        xco1 = self.emisloc_df['utme'][:]                # X-Coordinate
        yco1 = self.emisloc_df['utmn'][:]                # Y-Coordinate
        utmz = self.emisloc_df['utmzone'][:]                    # UTM Zone
        srct = self.emisloc_df['source_type'][:]                 # Source Type
        lenx = self.emisloc_df['lengthx'][:]                    # Length in X-Direction
        leny = self.emisloc_df['lengthy'][:]                    # Length in Y-Direction
        angl = self.emisloc_df['angle'][:]                       # Angle of Emission Location
        latr = self.emisloc_df['horzdim'][:]                     # Initial Lateral/Horizontal Emission
        vert = self.emisloc_df['vertdim'][:]                    # Initial Vertical Emission
        relh = self.emisloc_df['areavolrelhgt'][:]              # Release Height
        stkh = self.emisloc_df['stkht'][:]                # Stack Height
        diam = self.emisloc_df['stkdia'][:]                    # Stack Diameter
        emiv = self.emisloc_df['stkvel'][:]                    # Stack Exit Velocity
        temp = self.emisloc_df['stktemp'][:]                 # Stack Exit Temperature
        elev = self.emisloc_df['elev'][:]                   # Elevation of Source Location
        xco2 = self.emisloc_df['utme_x2'][:]               # Second X-Coordinate
        yco2 = self.emisloc_df['utmn_y2'][:]               # Second Y-Coordinate
    
    # initialize variable used to determine the first buoyant line source (if there is one)
        first_buoyant = 0


    # Need to confirm lenx is not 0
        area = self.emisloc_df['lengthx'][:] * self.emisloc_df['lengthy'][:]
    
    
    # Checks that may be done outside of this program
    
    # Lat/Lon check also needs to be inserted
        utmz[np.isnan(utmz)] = 0
        lenx[np.isnan(lenx)] = 0
        leny[np.isnan(leny)] = 0
        angl[np.isnan(angl)] = 0
        latr[np.isnan(latr)] = 0
        vert[np.isnan(vert)] = 0
        relh[np.isnan(relh)] = 0
        stkh[np.isnan(stkh)] = 0
        diam[np.isnan(diam)] = 0
        emiv[np.isnan(emiv)] = 0
        temp[np.isnan(temp)] = 0
        elev[np.isnan(elev)] = 0
        xco2[np.isnan(xco2)] = 0
        yco2[np.isnan(yco2)] = 0

 # %% Facility Options File
    
    #----------------------------------------------------------------------------------------
        facid = self.facoptn_df['fac_id'][0]                  # Facility ID
    #----------------------------------------------------------------------------------------
        metst = self.facoptn_df['met_station'][0]                 # Met Station ID
    #----------------------------------------------------------------------------------------
        ruour = self.facoptn_df['rural_urban'][0]                 # Rural or Urban
    #----------------------------------------------------------------------------------------
        maxds = self.facoptn_df['max_dist'][0]                # Maximum Distance
    
        if maxds >= 50000:
            maxds = 50000
        elif np.isnan(maxds) == 1:
            maxds = 50000
    #----------------------------------------------------------------------------------------
        modds = self.facoptn_df['model_dist'][0]                  # Modeled Distance of Receptors
    
        if modds == 0:
            modds = 3000
        elif np.isnan(modds) == 1:
            modds = 3000
    #----------------------------------------------------------------------------------------
        radia = self.facoptn_df['radial'][0]                     # Radials
    
        if radia == 0:
            radia = 16
        elif np.isnan(radia) == 1:
            radia = 16
    #----------------------------------------------------------------------------------------
        circl = self.facoptn_df['circles'][0]                     # Circles
    
        if circl < 3:
            circl = 3
        elif np.isnan(circl) == 1:
            circl = 13
    #----------------------------------------------------------------------------------------
        overl = self.facoptn_df['overlap_dist'][0]                # Overlap Distance
    
        if overl == 0:
            overl = 30
        elif np.isnan(overl) == 1:
            overl = 30
        elif overl < 1:
            overl = 30
        elif overl > 500:
            overl = 30
    #----------------------------------------------------------------------------------------
        acute = self.facoptn_df['acute'][0]
    
        if acute == "":
            acute = "N"
    #----------------------------------------------------------------------------------------
        hours = self.facoptn_df['hours'][0]                       # Hours
    
        if np.isnan(hours) == 1:
            hours = str(1) + " ANNUAL "
    
        av_t = [1,2,3,4,6,8,12,24]                           # Possible Averaging Time Periods
    
        if (hours in av_t) == 1:
            hours = str(hours) + " ANNUAL "
        else:
            hours = str(1) + " ANNUAL "
    #----------------------------------------------------------------------------------------
        eleva = self.facoptn_df['elev'][0]                        # Elevations
    
        if eleva == "Y":
            optel = " ELEV "
        else:
            optel = " FLAT "
    #----------------------------------------------------------------------------------------
        firnd = self.facoptn_df['ring1'][0]                       # First Ring Distance
    
        if firnd < 100:
            firnd = 100
        else:
            firnd = firnd
    #----------------------------------------------------------------------------------------
        depos = self.facoptn_df['dep'][0]                         # Deposition
        vdepo = self.facoptn_df['vdep'][0]                        # Vapor Deposition
        pdepo = self.facoptn_df['pdep'][0]                        # Particle Deposition
    
        if depos == "":
            depos = "N"
    
        if ("Y" in depos) == 1:
            if pdepo == "WD" or vdepo == "WD":
                optds_1 = " WDEP DDEP "
            else:
                optds_1 = ""
            if pdepo == "DO" or vdepo == "DO":
                optds_2 = " DDEP "
            else:
                optds_2 = ""
            if pdepo == "WO" or vdepo == "WO":
                optds_3 = " WDEP "
            else:
                optds_3 = ""
            if pdepo == "NO" and vdepo == "NO":
                optds_4 = ""
            else:
                optds_4 = ""
            optds = " DEPOS " + optds_1 + optds_2 + optds_3 + optds_4
        else:
            optds = ""
    #----------------------------------------------------------------------------------------
        deple = self.facoptn_df['depl'][0]                        # Depletion
        vdepl = self.facoptn_df['vdepl'][0]                       # Vapor Depletion
        pdepl = self.facoptn_df['pdepl'][0]                       # Particle Depletion
    
        if deple == "Y":
            if pdepl == "WD" or vdepl == "WD":
                optdp_1 = " DRYDPLT WETDPLT "
                optdp = optdp_1
            else:
                optdp_1 = ""
                if pdepl == "DO" and vdepl == "DO":
                    optdp_2 = " DRYDPLT NOWETDPLT "
                else:
                    optdp_2 = ""
                if pdepl == "DO" and vdepl != "DO":
                    optdp_3 = " DRYDPLT "
                else:
                    optdp_3 = ""
                if pdepl != "DO" and vdepl == "DO":
                    optdp_4 = " DRYDPLT "
                else:
                    optdp_4 = ""
                if pdepl == "WO" and vdepl == "WO":
                    optdp_5 = " WETDPLT NODRYDPLT "
                else:
                    optdp_5 = ""
                if pdepl == "WO" and vdepl != "WO":
                    optdp_6 = " WETDPLT "
                else:
                    optdp_6 = ""
                if pdepl != "WO" and vdepl == "WO":
                    optdp_7 = " WETDPLT "
                else:
                    optdp_7 = ""
                if pdepl == "NO" and vdepl == "NO":
                    optdp_8 = ""
                else:
                    optdp_8 = ""
                if pdepl == "" or vdepl == "":
                    optdp_9 = ""
                else:
                    optdp_9 = ""
                optdp = optdp_1 + optdp_2 + optdp_3 + optdp_4 + optdp_5 + optdp_6 + optdp_7 + optdp_8 + optdp_9
        else:
            optdp = ""
    #----------------------------------------------------------------------------------------
        phase = self.facoptn_df['phase'][0]                       # Phase
    
        if phase == "":
            phase = "B"
    #----------------------------------------------------------------------------------------
        blddw = self.facoptn_df['bldg_dw'][0]
    #---------------------------------------------------------------------------------------- 
        fasta = self.facoptn_df['fastall'][0]                     # FASTALL Model Option for AERMOD
    
        if fasta == "Y":
            optfa = " FASTALL "
        else:
            optfa = ""
    #----------------------------------------------------------------------------------------
    # %% Converting Coordinates from UTM to Lat-Lon
    
       # nad = 83*np.ones(len(ylat))
    
        #utmn, utme, utmz = ll2utm.ll2utm(ylat,xlon,utmz)
        #xcor = utme
       #ycor = utmn
        #utmz = utmz
    
        #utn2, ute2, utz2 = ll2utm.ll2utm(yco2,xco2,utmz)
    
    # %% Begin Building AERMOD Runstream 
         
       
        inp_f = open("aermod.inp", "w")
    
    # %% CO Section
    
        co1 = "CO STARTING  \n"
        co2 = "CO TITLEONE  " + str(facid) + "\n"
        co3 = "CO TITLETWO  Combined particle and vapor-phase emissions \n"
        co4 = "CO MODELOPT  CONC  BETA " + optdp + optel + optds + optfa + "\n"
    
        inp_f.write(co1)
        inp_f.write(co2)
        inp_f.write(co3)
        inp_f.write(co4)
    
    # Season Options for Deposition
    
        if ("Y" in depos) == 1:
            coseas = "CO GDSEASON " + str(gseason_df['M01'][0]) + " " + str(gseason_df['M02'][0]) + " " + \
                str(gseason_df['M03'][0]) + " " + str(gseason_df['M04'][0]) + " " + str(gseason_df['M05'][0]) + \
                str(gseason_df['M06'][0]) + " " + str(gseason_df['M07'][0]) + " " + str(gseason_df['M08'][0]) + \
                str(gseason_df['M09'][0]) + " " + str(gseason_df['M10'][0]) + " " + str(gseason_df['M11'][0]) + \
                str(gseason_df['M12'][0])
            inp_f.write(coseas)
    
    # Landuse Options for Deposition
    
        if ("Y" in depos) == 1:
            coland = "CO GDLANUSE " + str(landuse_df['D01'][0]) + " " + str(landuse_df['D02'][0]) + " " + \
                str(landuse_df['D03'][0]) + " " + str(landuse_df['D04'][0]) + " " + str(landuse_df['D05'][0]) + " " + \
                str(landuse_df['D06'][0]) + " " + str(landuse_df['D07'][0]) + " " + str(landuse_df['D08'][0]) + " " + \
                str(landuse_df['D09'][0]) + " " + str(landuse_df['D10'][0]) + " " + str(landuse_df['D11'][0]) + " " + \
                str(landuse_df['D12'][0]) + " " + str(landuse_df['D13'][0]) + " " + str(landuse_df['D14'][0]) + " " + \
                str(landuse_df['D15'][0]) + " " + str(landuse_df['D16'][0]) + " " + str(landuse_df['D17'][0]) + " " + \
                str(landuse_df['D18'][0]) + " " + str(landuse_df['D19'][0]) + " " + str(landuse_df['D20'][0]) + " " + \
                str(landuse_df['D21'][0]) + " " + str(landuse_df['D22'][0]) + " " + str(landuse_df['D23'][0]) + " " + \
                str(landuse_df['D24'][0]) + " " + str(landuse_df['D25'][0]) + " " + str(landuse_df['D26'][0]) + " " + \
                str(landuse_df['D27'][0]) + " " + str(landuse_df['D28'][0]) + " " + str(landuse_df['D29'][0]) + " " + \
                str(landuse_df['D30'][0])
    
        co5 = "CO AVERTIME  " + hours + "\n"
        co6 = "CO POLLUTID  UNITHAP \n"
        co7 = "CO RUNORNOT  RUN \n"
        co8 = "CO FINISHED  \n" + "\n"
    
        inp_f.write(co5)
        inp_f.write(co6)
        inp_f.write(co7)
        inp_f.write(co8)
    
    # %% SO Section
    
        so1 = "SO STARTING \n"
        so2 = "SO ELEVUNIT METERS \n"
    
        inp_f.write(so1)
        inp_f.write(so2)
    
    ## Gas Deposition parameters if option is selected in file selection
    
        da    =    0.07
        dw    =    0.70
        rcl   = 2000.00
        henry =    5.00
    
        newline = "\n"
    
        for index, row in self.emisloc_df.iterrows():
                    
                   # %% # Point Source
    
            if srct[index] == 'P':
                soloc = "SO LOCATION " + str(srid[index]) + " POINT " + str(xco1[index]) + " " + str(yco1[index]) + " " + \
                    str(elev[index]) + "\n"
                soparam = "SO SRCPARAM " + str(srid[index]) + " 1000 " + str(stkh[index]) + " " + str(temp[index]) + " " + str(emiv[index]) + " " + \
                    str(diam[index]) + "\n"
                inp_f.write(soloc)
                inp_f.write(soparam)

            # For variable emission factors/rates

                if varemis == 1: ###################################
                    self.varyemi_df = pd.read_excel(r"C:\HEM3_V153\Inputs_multi\Template_Multi_temporal_mhrdow.xlsx") ###########################
                    vary_srid = self.varyemi_df['Source ID'][:]
                    vary_vary = self.varyemi_df['Variation'][:]
    
                    for i in np.arange(len(vary_srid)):
                        if srid[index] == vary_srid[i]:
                            if vary_vary[i] == "SEASON":
                                so_emisf = "SO EMISFACT " + str(vary_srid[i]) + " " + str(vary_vary[i]) + " 1000*"
                                inp_f.write(so_emisf)
                                for j in np.arange(3,7):
                                    seas_ef = varyemi_df[varyemi_df.columns[j]][i]
                                    so_emis_f = str(seas_ef) + " "
                                    inp_f.write(so_emis_f)
                                inp_f.write(newline)
                            elif vary_vary[i] == "WSPEED":
                                so_emisf = "SO EMISFACT " + str(vary_srid[i]) + " " + str(vary_vary[i]) + " 1000*"
                                inp_f.write(so_emisf)
                                for j in np.arange(3,9):
                                    seas_ef = varyemi_df[varyemi_df.columns[j]][i]
                                    so_emis_f = str(seas_ef) + " "
                                    inp_f.write(so_emis_f)
                                inp_f.write(newline)
                            else:
                                so_emisf = "SO EMISFACT " + str(vary_srid[i]) + " " + str(vary_vary[i]) + " 1000*"
                                inp_f.write(so_emisf)
                                for j in np.arange(3,12):
                                    seas_ef = varyemi_df[varyemi_df.columns[j]][i]
                                    so_emis_f = str(seas_ef) + " "
                                    inp_f.write(so_emis_f)
                                inp_f.write(newline)

            # For Building Downwash

                if blddw == "Y":
                    bldgdim_df = pd.read_excel(r"C:\HEM3_V153\Inputs_multi\Template_Multi_bldg_dimensions.xlsx") ####################################
                    bldg_srid = bldgdim_df['Source ID'][:]
                    bldg_keyw = bldgdim_df['Keyword'][:]
                    for i in np.arange(len(bldg_srid)):
                        if srid[index] == bldg_srid[i]:
                            bldgdim = "SO " + str(bldg_keyw[i]) + " " + str(bldg_srid[i]) + " "
                            inp_f.write(bldgdim)
                            for j in np.arange(4,len(bldgdim_df.columns[:])):
                                str(bldgdim_df[bldgdim_df.columns[j]][i]) + " "
                                inp_f.write(bldgdim)
                            newline
                            inp_f.write(newline)
    
                if ("Y" in depos) == 1:
                    sodepos = "SO GASDEPOS " + str(srid[index]) + " " + str(da) + " " + str(dw) + " " + str(rcl) + " " + str(henry)
                    inp_f.write(sodepos)
                    if phase == "Y" or phase == "B":
                        if part_met2 == "Y":
                            partme2_df = pd.read_excel(r"Currently not a created file") ################################
                            sourc = list(partme2_df['Source ID'][:])
                            sr_pos = sourc.index(srid[index])
                            someth2 = "SO METHOD_2 " + str(srid[index]) + " " + str(partme2_df['Fine Mass'][sr_pos]) + \
                                " " + str(partme2_df['Dmm'][sr_pos]) + "\n"
                            inp_f.write(someth2)
                        else:
                            sourc = list(partdia_df['Source ID'][:])
                            sr_pos = sourc.index(srid[index])
                            sopdiam = "SO PARTDIAM " + str(srid[sr_pos]) + " " + str(partdia_df['Particle diameter'][sr_pos])
                            sopdens = "SO PARTDENS " + str(srid[sr_pos]) + " " + str(partdia_df['Particle density'][sr_pos])
                            somassf = "SO MASSFRAX " + str(srid[sr_pos]) + " " + str(partdia_df['Mass fraction'][sr_pos])
                            inp_f.write(sopdiam)
                            inp_f.write(sopdens)
                            inp_f.write(somassf)
    
    
       
       #%% Capped Point Source
            elif srct[index] == 'C':
                soloc = "SO LOCATION " + str(srid[index]) + " POINTCAP " + str(xco1[index]) + " " + str(yco1[index]) + " " + \
                    str(elev[index]) + "\n"
                soparam = "SO SRCPARAM " + str(srid[index]) + " 1000 " + str(stkh[index]) + " " + str(temp[index]) + " " + str(emiv[index]) + " " + \
                    str(diam[index]) + "\n"
                inp_f.write(soloc)
                inp_f.write(soparam)
            
            # For variable emission factors/rates
            
                if varemis == 1:
                    varyemi_df = pd.read_excel(r"C:\HEM3_V153\Inputs_multi\Template_Multi_temporal_mhrdow.xlsx")
                    vary_srid = varyemi_df['Source ID'][:]
                    vary_vary = varyemi_df['Variation'][:]
    
                    for i in np.arange(len(vary_srid)):
                        if srid[index] == vary_srid[i]:
                            if vary_vary[i] == "SEASON":
                                so_emisf = "SO EMISFACT " + str(vary_srid[i]) + " " + str(vary_vary[i]) + " 1000*"
                                inp_f.write(so_emisf)
                                for j in np.arange(3,7):
                                    seas_ef = varyemi_df[varyemi_df.columns[j]][i]
                                    so_emis_f = str(seas_ef) + " "
                                    inp_f.write(so_emis_f)
                                inp_f.write(newline)
                            elif vary_vary[i] == "WSPEED":
                                so_emisf = "SO EMISFACT " + str(vary_srid[i]) + " " + str(vary_vary[i]) + " 1000*"
                                inp_f.write(so_emisf)
                                for j in np.arange(3,9):
                                    seas_ef = varyemi_df[varyemi_df.columns[j]][i]
                                    so_emis_f = str(seas_ef) + " "
                                    inp_f.write(so_emis_f)
                                inp_f.write(newline)
                            else:
                                so_emisf = "SO EMISFACT " + str(vary_srid[i]) + " " + str(vary_vary[i]) + " 1000*"
                                inp_f.write(so_emisf)
                                for j in np.arange(3,12):
                                    seas_ef = varyemi_df[varyemi_df.columns[j]][i]
                                    so_emis_f = str(seas_ef) + " "
                                    inp_f.write(so_emis_f)
                                inp_f.write(newline)
    
            # For Building Downwash
    
                if blddw == "Y":
                    bldgdim_df = pd.read_excel(r"C:\HEM3_V153\Inputs_multi\Template_Multi_bldg_dimensions.xlsx") ########### HARD CODE ##########
                    bldg_srid = bldgdim_df['Source ID'][:]
                    bldg_keyw = bldgdim_df['Keyword'][:]
                    for i in np.arange(len(bldg_srid)):
                        if srid[index] == bldg_srid[i]:
                            bldgdim = "SO " + str(bldg_keyw[i]) + " " + str(bldg_srid[i]) + " "
                            inp_f.write(bldgdim)
                            for j in np.arange(4,len(bldgdim_df.columns[:])):
                                str(bldgdim_df[bldgdim_df.columns[j]][i]) + " "
                                inp_f.write(bldgdim)
                            newline
                            inp_f.write(newline)
    
                if ("Y" in depos) == 1:
                    sodepos = "SO GASDEPOS " + str(srid[index]) + " " + str(da) + " " + str(dw) + " " + str(rcl) + " " + str(henry)
                    inp_f.write(sodepos)
                    if phase == "Y" or phase == "B":
                        if part_met2 == "Y":   ######### Add for facility list options?
                            sourc = list(partme2_df['Source ID'][:])
                            sr_pos = sourc.index(srid[index])
                            someth2 = "SO METHOD_2 " + str(srid[index]) + " " + str(partme2_df['Fine Mass'][sr_pos]) + \
                                " " + str(partme2_df['Dmm'][sr_pos]) + "\n"
                            inp_f.write(someth2)
                        else:
                            sourc = list(partdia_df['Source ID'][:])
                            sr_pos = sourc.index(srid[index])
                        sopdiam = "SO PARTDIAM " + str(srid[sr_pos]) + " " + str(partdia_df['Particle diameter'][sr_pos])
                        sopdens = "SO PARTDENS " + str(srid[sr_pos]) + " " + str(partdia_df['Particle density'][sr_pos])
                        somassf = "SO MASSFRAX " + str(srid[sr_pos]) + " " + str(partdia_df['Mass fraction'][sr_pos])
                        inp_f.write(sopdiam)
                        inp_f.write(sopdens)
                        inp_f.write(somassf)                     



       # %% # Horizontal Point Source
    
            elif srct[index] == 'H':
                soloc = "SO LOCATION " + str(srid[index]) + " POINTHOR " + str(xco1[index]) + " " + str(yco1[index]) + " " + \
                    str(elev[index]) + "\n"
                soparam = "SO SRCPARAM " + str(srid[index]) + " 1000 " + str(stkh[index]) + " " + str(temp[index]) + " " + str(emiv[index]) + " " + \
                    str(diam[index]) + "\n"
                inp_f.write(soloc)
                inp_f.write(soparam)
            
            # For variable emission factors/rates
            
                if varemis == 1:                                        # Activate with GUI Input only
                    varyemi_df = pd.read_excel(r"C:\HEM3_V153\Inputs_multi\Template_Multi_temporal_mhrdow.xlsx") ###################################
                    vary_srid = varyemi_df['Source ID'][:]
                    vary_vary = varyemi_df['Variation'][:]
    
                    for i in np.arange(len(vary_srid)):
                        if srid[index] == vary_srid[i]:
                            if vary_vary[i] == "SEASON":
                                so_emisf = "SO EMISFACT " + str(vary_srid[i]) + " " + str(vary_vary[i]) + " 1000*"
                                inp_f.write(so_emisf)
                                for j in np.arange(3,7):
                                    seas_ef = varyemi_df[varyemi_df.columns[j]][i]
                                    so_emis_f = str(seas_ef) + " "
                                    inp_f.write(so_emis_f)
                                inp_f.write(newline)
                            elif vary_vary[i] == "WSPEED":
                                so_emisf = "SO EMISFACT " + str(vary_srid[i]) + " " + str(vary_vary[i]) + " 1000*"
                                inp_f.write(so_emisf)
                                for j in np.arange(3,9):
                                    seas_ef = varyemi_df[varyemi_df.columns[j]][i]
                                    so_emis_f = str(seas_ef) + " "
                                    inp_f.write(so_emis_f)
                                inp_f.write(newline)
                            else:
                                so_emisf = "SO EMISFACT " + str(vary_srid[i]) + " " + str(vary_vary[i]) + " 1000*"
                                inp_f.write(so_emisf)
                                for j in np.arange(3,12):
                                    seas_ef = varyemi_df[varyemi_df.columns[j]][i]
                                    so_emis_f = str(seas_ef) + " "
                                    inp_f.write(so_emis_f)
                                inp_f.write(newline)
    
            # For Building Downwash
    
                if blddw == "Y":
                    bldgdim_df = pd.read_excel(r"C:\HEM3_V153\Inputs_multi\Template_Multi_bldg_dimensions.xlsx") ####################################
                    bldg_srid = bldgdim_df['Source ID'][:]
                    bldg_keyw = bldgdim_df['Keyword'][:]
                    for i in np.arange(len(bldg_srid)):
                        if srid[index] == bldg_srid[i]:
                            bldgdim = "SO " + str(bldg_keyw[i]) + " " + str(bldg_srid[i]) + " "
                            inp_f.write(bldgdim)
                            for j in np.arange(4,len(bldgdim_df.columns[:])):
                                str(bldgdim_df[bldgdim_df.columns[j]][i]) + " "
                                inp_f.write(bldgdim)
                            newline
                            inp_f.write(newline)
            
                if ("Y" in depos) == 1:
                    sodepos = "SO GASDEPOS " + str(srid[index]) + " " + str(da) + " " + str(dw) + " " + str(rcl) + " " + str(henry)
                    inp_f.write(sodepos)
                    if phase == "Y" or phase == "B":
                        if part_met2 == "Y":   ######### Add for facility list options?
                            sourc = list(partme2_df['Source ID'][:])####################### Change for Method_2 Dataframe
                            sr_pos = sourc.index(srid[index])
                            someth2 = "SO METHOD_2 " + str(srid[index]) + " " + str(partme2_df['Fine Mass'][sr_pos]) + \
                                " " + str(partme2_df['Dmm'][sr_pos]) + "\n"
                            inp_f.write(someth2)
                        else:
                            sourc = list(partdia_df['Source ID'][:])
                            sr_pos = sourc.index(srid[index])
                        sopdiam = "SO PARTDIAM " + str(srid[sr_pos]) + " " + str(partdia_df['Particle diameter'][sr_pos])
                        sopdens = "SO PARTDENS " + str(srid[sr_pos]) + " " + str(partdia_df['Particle density'][sr_pos])
                        somassf = "SO MASSFRAX " + str(srid[sr_pos]) + " " + str(partdia_df['Mass fraction'][sr_pos])
                        inp_f.write(sopdiam)
                        inp_f.write(sopdens)
                        inp_f.write(somassf)
        
          # %% # Area Source
    
            elif srct[index] == 'A':
                soloc = "SO LOCATION " + str(srid[index]) + " AREA " + str(xco1[index]) + " " + str(yco1[index]) + " " + \
                    str(elev[index]) + "\n"
                soparam = "SO SRCPARAM " + str(srid[index]) + " " + str(1000/area[index]) + " " + str(relh[index]) + " " + str(lenx[index]) + " " + str(leny[index]) + " " + \
                    str(angl[index]) + " " + str(vert[index]) + "\n" 
                inp_f.write(soloc)
                inp_f.write(soparam)
            
            # For variable emission factors/rates
            
                if varemis == 1:                                        # Activate with GUI Input only
                    varyemi_df = pd.read_excel(r"C:\HEM3_V153\Inputs_multi\Template_Multi_temporal_mhrdow.xlsx")
                    vary_srid = varyemi_df['Source ID'][:]
                    vary_vary = varyemi_df['Variation'][:]
    
                    for i in np.arange(len(vary_srid)):
                        if srid[index] == vary_srid[i]:
                            if vary_vary[i] == "SEASON":
                                so_emisf = "SO EMISFACT " + str(vary_srid[i]) + " " + str(vary_vary[i]) + " " + str(1000/area[index]) + "*"
                                inp_f.write(so_emisf)
                                for j in np.arange(3,7):
                                    seas_ef = varyemi_df[varyemi_df.columns[j]][i]
                                    so_emis_f = str(seas_ef) + " "
                                    inp_f.write(so_emis_f)
                                inp_f.write(newline)
                            elif vary_vary[i] == "WSPEED":
                                so_emisf = "SO EMISFACT " + str(vary_srid[i]) + " " + str(vary_vary[i]) + " " + str(1000/area[index]) + "*"
                                inp_f.write(so_emisf)
                                for j in np.arange(3,9):
                                    seas_ef = varyemi_df[varyemi_df.columns[j]][i]
                                    so_emis_f = str(seas_ef) + " "
                                    inp_f.write(so_emis_f)
                                inp_f.write(newline)
                            else:
                                so_emisf = "SO EMISFACT " + str(vary_srid[i]) + " " + str(vary_vary[i]) + " " + str(1000/area[index]) + "*"
                                inp_f.write(so_emisf)
                                for j in np.arange(3,12):
                                    seas_ef = varyemi_df[varyemi_df.columns[j]][i]
                                    so_emis_f = str(seas_ef) + " "
                                    inp_f.write(so_emis_f)
                                inp_f.write(newline)
    
            # For Building Downwash
    
                if blddw == "Y":
                    bldgdim_df = pd.read_excel(r"C:\HEM3_V153\Inputs_multi\Template_Multi_bldg_dimensions.xlsx") ####################################
                    bldg_srid = bldgdim_df['Source ID'][:]
                    bldg_keyw = bldgdim_df['Keyword'][:]
                    for i in np.arange(len(bldg_srid)):
                        if srid[index] == bldg_srid[i]:
                            bldgdim = "SO " + str(bldg_keyw[i]) + " " + str(bldg_srid[i]) + " "
                            inp_f.write(bldgdim)
                            for j in np.arange(4,len(bldgdim_df.columns[:])):
                                str(bldgdim_df[bldgdim_df.columns[j]][i]) + " "
                                inp_f.write(bldgdim)
                            newline
                            inp_f.write(newline)
            
                if ("Y" in depos) == 1:
                    sodepos = "SO GASDEPOS " + str(srid[index]) + " " + str(da) + " " + str(dw) + " " + str(rcl) + " " + str(henry)
                    inp_f.write(sodepos)
                    if phase == "Y" or phase == "B":
                        if part_met2 == "Y":   ######### Add for facility list options?
                            sourc = list(partme2_df['Source ID'][:])####################### Change for Method_2 Dataframe
                            sr_pos = sourc.index(srid[index])
                            someth2 = "SO METHOD_2 " + str(srid[index]) + " " + str(partme2_df['Fine Mass'][sr_pos]) + \
                                " " + str(partme2_df['Dmm'][sr_pos]) + "\n"
                            inp_f.write(someth2)
                        else:
                            sourc = list(partdia_df['Source ID'][:])
                            sr_pos = sourc.index(srid[index])
                        sopdiam = "SO PARTDIAM " + str(srid[sr_pos]) + " " + str(partdia_df['Particle diameter'][sr_pos])
                        sopdens = "SO PARTDENS " + str(srid[sr_pos]) + " " + str(partdia_df['Particle density'][sr_pos])
                        somassf = "SO MASSFRAX " + str(srid[sr_pos]) + " " + str(partdia_df['Mass fraction'][sr_pos])
                        inp_f.write(sopdiam)
                        inp_f.write(sopdens)
                        inp_f.write(somassf)
    

       # %% # Volume Source
    
            elif srct[index] == 'V':
                soloc = "SO LOCATION " + str(srid[index]) + " VOLUME " + str(xco1[index]) + " " + str(yco1[index]) + " " + \
                    str(elev[index]) + "\n"
                soparam = "SO SRCPARAM " + str(srid[index]) + " 1000 " + str(relh[index]) + " " + str(latr[index]) + " " + str(vert[index]) + "\n"
                inp_f.write(soloc)
                inp_f.write(soparam)
            
            # For variable emission factors/rates
            
                if varemis == 1:                                        # Activate with GUI Input only
                    varyemi_df = pd.read_excel(r"C:\HEM3_V153\Inputs_multi\Template_Multi_temporal_mhrdow.xlsx")
                    vary_srid = varyemi_df['Source ID'][:]
                    vary_vary = varyemi_df['Variation'][:]
                    
                    for i in np.arange(len(vary_srid)):
                        if srid[index] == vary_srid[i]:
                            if vary_vary[i] == "SEASON":
                                so_emisf = "SO EMISFACT " + str(vary_srid[i]) + " " + str(vary_vary[i]) + " 1000*"
                                inp_f.write(so_emisf)
                                for j in np.arange(3,7):
                                    seas_ef = varyemi_df[varyemi_df.columns[j]][i]
                                    so_emis_f = str(seas_ef) + " "
                                    inp_f.write(so_emis_f)
                                inp_f.write(newline)
                            elif vary_vary[i] == "WSPEED":
                                so_emisf = "SO EMISFACT " + str(vary_srid[i]) + " " + str(vary_vary[i]) + " 1000*"
                                inp_f.write(so_emisf)
                                for j in np.arange(3,9):
                                    seas_ef = varyemi_df[varyemi_df.columns[j]][i]
                                    so_emis_f = str(seas_ef) + " "
                                    inp_f.write(so_emis_f)
                                inp_f.write(newline)
                            else:
                                so_emisf = "SO EMISFACT " + str(vary_srid[i]) + " " + str(vary_vary[i]) + " 1000*"
                                inp_f.write(so_emisf)
                                for j in np.arange(3,12):
                                    seas_ef = varyemi_df[varyemi_df.columns[j]][i]
                                    so_emis_f = str(seas_ef) + " "
                                    inp_f.write(so_emis_f)
                                inp_f.write(newline)
    
            # For Building Downwash
    
                if blddw == "Y":
                    bldgdim_df = pd.read_excel(r"C:\HEM3_V153\Inputs_multi\Template_Multi_bldg_dimensions.xlsx") ####################################
                    bldg_srid = bldgdim_df['Source ID'][:]
                    bldg_keyw = bldgdim_df['Keyword'][:]
                    for i in np.arange(len(bldg_srid)):
                        if srid[index] == bldg_srid[i]:
                            bldgdim = "SO " + str(bldg_keyw[i]) + " " + str(bldg_srid[i]) + " "
                            inp_f.write(bldgdim)
                            for j in np.arange(4,len(bldgdim_df.columns[:])):
                                str(bldgdim_df[bldgdim_df.columns[j]][i]) + " "
                                inp_f.write(bldgdim)
                            newline
                            inp_f.write(newline)
            
                if ("Y" in depos) == 1:
                    sodepos = "SO GASDEPOS " + str(srid[index]) + " " + str(da) + " " + str(dw) + " " + str(rcl) + " " + str(henry)
                    inp_f.write(sodepos)
                    if phase == "Y" or phase == "B":
                        if part_met2 == "Y":   ######### Add for facility list options?
                            sourc = list(partme2_df['Source ID'][:])####################### Change for Method_2 Dataframe
                            sr_pos = sourc.index(srid[index])
                            someth2 = "SO METHOD_2 " + str(srid[index]) + " " + str(partme2_df['Fine Mass'][sr_pos]) + \
                                " " + str(partme2_df['Dmm'][sr_pos]) + "\n"
                            inp_f.write(someth2)
                        else:
                            sourc = list(partdia_df['Source ID'][:])
                            sr_pos = sourc.index(srid[index])
                        sopdiam = "SO PARTDIAM " + str(srid[sr_pos]) + " " + str(partdia_df['Particle diameter'][sr_pos])
                        sopdens = "SO PARTDENS " + str(srid[sr_pos]) + " " + str(partdia_df['Particle density'][sr_pos])
                        somassf = "SO MASSFRAX " + str(srid[sr_pos]) + " " + str(partdia_df['Mass fraction'][sr_pos])
                        inp_f.write(sopdiam)
                        inp_f.write(sopdens)
                        inp_f.write(somassf)
        
        # %% # Area Polygon (Irregular) Source
    
            elif srct[index] == 'I':
                # subset polyver_df to one source_id
                poly_srid = list(self.polyver_df[self.polyver_df['source_id']==srid[index]]['source_id'][:])
                poly_utme = list(self.polyver_df[self.polyver_df['source_id']==srid[index]]['utme'][:])
                poly_utmn = list(self.polyver_df[self.polyver_df['source_id']==srid[index]]['utmn'][:])
                poly_utmz = list(self.polyver_df[self.polyver_df['source_id']==srid[index]]['utmzone'][:])
                poly_numv = list(self.polyver_df[self.polyver_df['source_id']==srid[index]]['numvert'][:])
                poly_area = list(self.polyver_df[self.polyver_df['source_id']==srid[index]]['area'][:])
                        
                soloc = "SO LOCATION " + str(srid[index]) + " AREAPOLY " + str(xco1[index]) + " " + str(yco1[index]) + " " + \
                    " " + str(elev[index]) + "\n"
#            poly_pos = poly_srid.index(srid[index])
                soparam = "SO SRCPARAM " + str(srid[index]) + " " + str(1000/(poly_area[0])) + " " + str(relh[index]) + " " + \
                        str(poly_numv[0]) + "\n"
                inp_f.write(soloc)
                inp_f.write(soparam)
            
                for i in np.arange(len(poly_utmz)):
                    if np.isnan(poly_utmz[i]) == 1:
                        poly_utmz[i] = 0
                        
                vert_start = "SO AREAVERT " + str(poly_srid[0]) + " "
                vert_coor = ""
                for i in np.arange(len(poly_srid)):
                    if (i+1) % 6 == 0 or i == len(poly_srid):
                        vert_coor = vert_coor + str(poly_utme[i]) + " " + str(poly_utmn[i]) + " "
                        vert_line = vert_start + vert_coor + "\n"
                        inp_f.write(vert_line)
                        vert_coor = str(poly_utme[i]) + " " + str(poly_utmn[i]) + " "
                    else:
                        vert_coor = vert_coor + str(poly_utme[i]) + " " + str(poly_utmn[i]) + " "
            
            # For variable emission factors/rates
            
                if varemis == 1:                                        # Activate with GUI Input only
                    varyemi_df = pd.read_excel(r"C:\HEM3_V153\Inputs_multi\Template_Multi_temporal_mhrdow.xlsx")
                    vary_srid = varyemi_df['Source ID'][:]
                    vary_vary = varyemi_df['Variation'][:]
    
                    for i in np.arange(len(vary_srid)):
                        if srid[index] == vary_srid[i]:
                            if vary_vary[i] == "SEASON":
                                so_emisf = "SO EMISFACT " + str(vary_srid[i]) + " " + str(vary_vary[i]) + " " + str(1000/(poly_area[poly_pos])) + "*"
                                inp_f.write(so_emisf)
                                for j in np.arange(3,7):
                                    seas_ef = varyemi_df[varyemi_df.columns[j]][i]
                                    so_emis_f = str(seas_ef) + " "
                                    inp_f.write(so_emis_f)
                                inp_f.write(newline)
                            elif vary_vary[i] == "WSPEED":
                                so_emisf = "SO EMISFACT " + str(vary_srid[i]) + " " + str(vary_vary[i]) + " " + str(1000/(poly_area[poly_pos])) + "*"
                                inp_f.write(so_emisf)
                                for j in np.arange(3,9):
                                    seas_ef = varyemi_df[varyemi_df.columns[j]][i]
                                    so_emis_f = str(seas_ef) + " "
                                    inp_f.write(so_emis_f)
                                inp_f.write(newline)
                            else:
                                so_emisf = "SO EMISFACT " + str(vary_srid[i]) + " " + str(vary_vary[i]) + " " + str(1000/(poly_area[poly_pos])) + "*"
                                inp_f.write(so_emisf)
                                for j in np.arange(3,12):
                                    seas_ef = varyemi_df[varyemi_df.columns[j]][i]
                                    so_emis_f = str(seas_ef) + " "
                                    inp_f.write(so_emis_f)
                                inp_f.write(newline)
    
            # For Building Downwash
    
                if blddw == "Y":
                    bldgdim_df = pd.read_excel(r"C:\HEM3_V153\Inputs_multi\Template_Multi_bldg_dimensions.xlsx") ####################################
                    bldg_srid = bldgdim_df['Source ID'][:]
                    bldg_keyw = bldgdim_df['Keyword'][:]
                    for i in np.arange(len(bldg_srid)):
                        if srid[index] == bldg_srid[i]:
                            bldgdim = "SO " + str(bldg_keyw[i]) + " " + str(bldg_srid[i]) + " "
                            inp_f.write(bldgdim)
                            for j in np.arange(4,len(bldgdim_df.columns[:])):
                                str(bldgdim_df[bldgdim_df.columns[j]][i]) + " "
                                inp_f.write(bldgdim)
                            newline
                            inp_f.write(newline)
            
                if ("Y" in depos) == 1:
                    sodepos = "SO GASDEPOS " + str(srid[index]) + " " + str(da) + " " + str(dw) + " " + str(rcl) + " " + str(henry)
                    inp_f.write(sodepos)
                    if phase == "Y" or phase == "B":
                        if part_met2 == "Y":   ######### Add for facility list options?
                            sourc = list(partme2_df['Source ID'][:])####################### Change for Method_2 Dataframe
                            sr_pos = sourc.index(srid[index])
                            someth2 = "SO METHOD_2 " + str(srid[index]) + " " + str(partme2_df['Fine Mass'][sr_pos]) + \
                                " " + str(partme2_df['Dmm'][sr_pos]) + "\n"
                            inp_f.write(someth2)
                        else:
                            sourc = list(partdia_df['Source ID'][:])
                            sr_pos = sourc.index(srid[index])
                        sopdiam = "SO PARTDIAM " + str(srid[sr_pos]) + " " + str(partdia_df['Particle diameter'][sr_pos])
                        sopdens = "SO PARTDENS " + str(srid[sr_pos]) + " " + str(partdia_df['Particle density'][sr_pos])
                        somassf = "SO MASSFRAX " + str(srid[sr_pos]) + " " + str(partdia_df['Mass fraction'][sr_pos])
                        inp_f.write(sopdiam)
                        inp_f.write(sopdens)
                        inp_f.write(somassf)

        # %% # Line Source
    
            elif srct[index] == 'N':
                soloc = "SO LOCATION " + str(srid[index]) + " LINE " + str(xco1[index]) + " " + str(yco1[index]) + " " + str(xco2[index]) + " " + str(yco2[index]) + \
                    " " + str(elev[index]) + "\n"
                line_len = math.sqrt((xco1[index] - xco2[index])**2 + (yco1[index] - yco2[index])**2)
                soparam = "SO SRCPARAM " + str(srid[index]) + " " + str( 1000 / ( lenx[index] * line_len ) ) + " " + str(relh[index]) + " " + str(lenx[index]) + " " + \
                    str(vert[index]) + "\n"
                inp_f.write(soloc)
                inp_f.write(soparam)
                
            
            # For variable emission factors/rates
            
                if varemis == 1:                                        # Activate with GUI Input only
                    varyemi_df = pd.read_excel(r"C:\HEM3_V153\Inputs_multi\Template_Multi_temporal_mhrdow.xlsx")
                    vary_srid = varyemi_df['Source ID'][:]
                    vary_vary = varyemi_df['Variation'][:]
    
                    for i in np.arange(len(vary_srid)):
                        if srid[index] == vary_srid[i]:
                            if vary_vary[i] == "SEASON":
                                so_emisf = "SO EMISFACT " + str(vary_srid[i]) + " " + str(vary_vary[i]) + " " + str( 1000/(lenx[index]*wide)) + "*"
                                inp_f.write(so_emisf)
                                for j in np.arange(3,7):
                                    seas_ef = varyemi_df[varyemi_df.columns[j]][i]
                                    so_emis_f = str(seas_ef) + " "
                                    inp_f.write(so_emis_f)
                                inp_f.write(newline)
                            elif vary_vary[i] == "WSPEED":
                                so_emisf = "SO EMISFACT " + str(vary_srid[i]) + " " + str(vary_vary[i]) + " " + str( 1000/(lenx[index]*wide)) + "*"
                                inp_f.write(so_emisf)
                                for j in np.arange(3,9):
                                    seas_ef = varyemi_df[varyemi_df.columns[j]][i]
                                    so_emis_f = str(seas_ef) + " "
                                    inp_f.write(so_emis_f)
                                inp_f.write(newline)
                            else:
                                so_emisf = "SO EMISFACT " + str(vary_srid[i]) + " " + str(vary_vary[i]) + " " + str( 1000/(lenx[index]*wide)) + "*"
                                inp_f.write(so_emisf)
                                for j in np.arange(3,12):
                                    seas_ef = varyemi_df[varyemi_df.columns[j]][i]
                                    so_emis_f = str(seas_ef) + " "
                                    inp_f.write(so_emis_f)
                                inp_f.write(newline)
    
            # For Building Downwash
    
                if blddw == "Y":
                    bldgdim_df = pd.read_excel(r"C:\HEM3_V153\Inputs_multi\Template_Multi_bldg_dimensions.xlsx") ####################################
                    bldg_srid = bldgdim_df['Source ID'][:]
                    bldg_keyw = bldgdim_df['Keyword'][:]
                    for i in np.arange(len(bldg_srid)):
                        if srid[index] == bldg_srid[i]:
                            bldgdim = "SO " + str(bldg_keyw[i]) + " " + str(bldg_srid[i]) + " "
                            inp_f.write(bldgdim)
                            for j in np.arange(4,len(bldgdim_df.columns[:])):
                                str(bldgdim_df[bldgdim_df.columns[j]][i]) + " "
                                inp_f.write(bldgdim)
                            newline
                            inp_f.write(newline)
            
                if ("Y" in depos) == 1:
                    sodepos = "SO GASDEPOS " + str(srid[index]) + " " + str(da) + " " + str(dw) + " " + str(rcl) + " " + str(henry)
                    inp_f.write(sodepos)
                    if phase == "Y" or phase == "B":
                        if part_met2 == "Y":   ######### Add for facility list options?
                            sourc = list(partme2_df['Source ID'][:])####################### Change for Method_2 Dataframe
                            sr_pos = sourc.index(srid[index])
                            someth2 = "SO METHOD_2 " + str(srid[index]) + " " + str(partme2_df['Fine Mass'][sr_pos]) + \
                                " " + str(partme2_df['Dmm'][sr_pos]) + "\n"
                            inp_f.write(someth2)
                        else:
                            sourc = list(partdia_df['Source ID'][:])
                            sr_pos = sourc.index(srid[index])
                        sopdiam = "SO PARTDIAM " + str(sourc[sr_pos]) + " " + str(partdia_df['Particle diameter'][sr_pos])
                        sopdens = "SO PARTDENS " + str(sourc[sr_pos]) + " " + str(partdia_df['Particle density'][sr_pos])
                        somassf = "SO MASSFRAX " + str(sourc[sr_pos]) + " " + str(partdia_df['Mass fraction'][sr_pos])
                        inp_f.write(sopdiam)
                        inp_f.write(sopdens)
                        inp_f.write(somassf)
 
        # %% # Buoyant Line Source
    
            elif srct[index] == 'B':
                soloc = "SO LOCATION " + str(srid[index]) + " BUOYLINE " + str(xco1[index]) + " " + str(yco1[index]) + " " + str(xco2[index]) + " " + \
                    str(yco2[index]) + " " + str(elev[index]) + "\n"
                blemis = 1000 / (self.buoyant_df['avglin_wid'][0] * math.sqrt((xco1[index] - xco2[index])**2 + (yco1[index] - yco2[index])**2))
                soparam = "SO SRCPARAM " + str(srid[index]) + " " + str(blemis) + " " + str(relh[index]) + "\n"

                if first_buoyant == 0:
                    sobuopa = "SO BLPINPUT " + str(self.buoyant_df['avgbld_len'][0]) + " " + \
                        str(self.buoyant_df['avgbld_hgt'][0]) + " " + str(self.buoyant_df['avgbld_wid'][0]) + " " + \
                        str(self.buoyant_df['avglin_wid'][0]) + " " + str(self.buoyant_df['avgbld_sep'][0]) + " " + \
                        str(self.buoyant_df['avgbuoy'][0]) + "\n"
                    first_buoyant = 1
                    inp_f.write(sobuopa)
                
                inp_f.write(soloc)
                inp_f.write(soparam)
            
            # For variable emission factors/rates
            
                if varemis == 1:                                        # Activate with GUI Input only
                    varyemi_df = pd.read_excel(r"C:\HEM3_V153\Inputs_multi\Template_Multi_temporal_mhrdow.xlsx")
                    vary_srid = varyemi_df['Source ID'][:]
                    vary_vary = varyemi_df['Variation'][:]
    
                    for i in np.arange(len(vary_srid)):
                        if srid[index] == vary_srid[i]:
                            if vary_vary[i] == "SEASON":
                                so_emisf = "SO EMISFACT " + str(vary_srid[i]) + " " + str(vary_vary[i]) + " " + str(1000/str(area[index])) + "*"
                                inp_f.write(so_emisf)
                                for j in np.arange(3,7):
                                    seas_ef = varyemi_df[varyemi_df.columns[j]][i]
                                    so_emis_f = str(seas_ef) + " "
                                    inp_f.write(so_emis_f)
                                inp_f.write(newline)
                            elif vary_vary[i] == "WSPEED":
                                so_emisf = "SO EMISFACT " + str(vary_srid[i]) + " " + str(vary_vary[i]) + " " + str(1000/str(area[index])) + "*"
                                inp_f.write(so_emisf)
                                for j in np.arange(3,9):
                                    seas_ef = varyemi_df[varyemi_df.columns[j]][i]
                                    so_emis_f = str(seas_ef) + " "
                                    inp_f.write(so_emis_f)
                                inp_f.write(newline)
                            else:
                                so_emisf = "SO EMISFACT " + str(vary_srid[i]) + " " + str(vary_vary[i]) + " " + str(1000/str(area[index])) + "*"
                                inp_f.write(so_emisf)
                                for j in np.arange(3,12):
                                    seas_ef = varyemi_df[varyemi_df.columns[j]][i]
                                    so_emis_f = str(seas_ef) + " "
                                    inp_f.write(so_emis_f)
                                inp_f.write(newline)
    
            # For Building Downwash
    
                if blddw == "Y":
                    bldgdim_df = pd.read_excel(r"C:\HEM3_V153\Inputs_multi\Template_Multi_bldg_dimensions.xlsx") ####################################
                    bldg_srid = bldgdim_df['Source ID'][:]
                    bldg_keyw = bldgdim_df['Keyword'][:]
                    for i in np.arange(len(bldg_srid)):
                        if srid[index] == bldg_srid[i]:
                            bldgdim = "SO " + str(bldg_keyw[i]) + " " + str(bldg_srid[i]) + " "
                            inp_f.write(bldgdim)
                            for j in np.arange(4,len(bldgdim_df.columns[:])):
                                str(bldgdim_df[bldgdim_df.columns[j]][i]) + " "
                                inp_f.write(bldgdim)
                            newline
                            inp_f.write(newline)
            
                if ("Y" in depos) == 1:
                    sodepos = "SO GASDEPOS " + str(srid[index]) + " " + str(da) + " " + str(dw) + " " + str(rcl) + " " + str(henry)
                    inp_f.write(sodepos)
                    if phase == "Y" or phase == "B":
                        if part_met2 == "Y":   ######### Add for facility list options?
                            sourc = list(partme2_df['Source ID'][:])####################### Change for Method_2 Dataframe
                            sr_pos = sourc.index(srid[index])
                            someth2 = "SO METHOD_2 " + str(srid[index]) + " " + str(partme2_df['Fine Mass'][sr_pos]) + \
                                " " + str(partme2_df['Dmm'][sr_pos]) + "\n"
                            inp_f.write(someth2)
                        else:
                            sourc = list(partdia_df['Source ID'][:])
                            sr_pos = sourc.index(sr_pos)
                        sopdiam = "SO PARTDIAM " + str(sourc[sr_pos]) + " " + str(partdia_df['Particle diameter'][sr_pos])
                        sopdens = "SO PARTDENS " + str(sourc[sr_pos]) + " " + str(partdia_df['Particle density'][sr_pos])
                        somassf = "SO MASSFRAX " + str(sourc[sr_pos]) + " " + str(partdia_df['Mass fraction'][sr_pos])
                        inp_f.write(sopdiam)
                        inp_f.write(sopdens)
                        inp_f.write(somassf)
    
        
        
    # %% SO Source groups
    
        uniqsrcs = srid.unique()
        for i in np.arange(len(uniqsrcs)):  
            sogroup = "SO SRCGROUP " + uniqsrcs[i] + " " + uniqsrcs[i] + "-" + uniqsrcs[i] + "\n"
            inp_f.write(sogroup)
        so3 = "SO FINISHED \n" + "\n"
        inp_f.write(so3)
           
        
        
        


                       
    # %% RE Section
    
        res = "RE STARTING  " + "\n"
        inp_f.write(res)
 

    ## Discrete Receptors

        recx = list(self.discrecs_df['utme'][:])
        recy = list(self.discrecs_df['utmn'][:])
        rece = list(self.discrecs_df['ELEV'][:]) ############################# Elevations
        rech = list(self.discrecs_df['HILL'][:]) ############################# Hill height

        for i in np.arange(len(recx)):
            if eleva == "Y":
                redec = "RE DISCCART  " + str(recx[i]) + " " + str(recy[i]) + " " + str(int(round(rece[i]))) + " " + str(int(round(rech[i]))) + "\n"
            else:
                redec = "RE DISCCART  " + str(recx[i]) + " " + str(recy[i])
            inp_f.write(redec)

            
    ## Polar Recptors
    
        rep = "RE GRIDPOLR polgrid1 STA" + "\n"
        repo = "RE GRIDPOLR polgrid1 ORIG " + str(self.cenx) + " " + str(self.ceny) + "\n"
        repd = "RE GRIDPOLR polgrid1 DIST "

        inp_f.write(rep)
        inp_f.write(repo)
        inp_f.write(repd)

        recep_dis = self.polar_df["distance"].unique()
        num_rings = len(recep_dis)
        for i in np.arange(num_rings):
            repdis = str(recep_dis[i]) + " "
            inp_f.write(repdis)

        inp_f.write(newline)

        repi = "RE GRIDPOLR polgrid1 DDIR "
        inp_f.write(repi)

        recep_dir = self.polar_df["angle"].unique()
        num_sectors = len(recep_dir)
        for i in np.arange(num_sectors):
            repdir = str(recep_dir[i]) + " "
            inp_f.write(repdir)

        inp_f.write(newline)
    
        #add elevations and hill height if user selected it
        if eleva == "Y":
            for i in range(1, num_sectors+1):
                indexStr = "S" + str(i) + "R1"
                repelev0 = "RE GRIDPOLR polgrid1 ELEV " + str(self.polar_df["angle"].loc[indexStr]) + " "
                inp_f.write(repelev0)
                for j in range(1, num_rings+1):
                    indexStr = "S" + str(i) + "R" + str(j)
                    repelev1 = str(self.polar_df["elev"].loc[indexStr]) + " "
                    inp_f.write(repelev1)

                inp_f.write(newline)

                rephill0 = "RE GRIDPOLR polgrid1 HILL " + str(self.polar_df["angle"].loc[indexStr]) + " "
                inp_f.write(rephill0)
                for j in range(1, num_rings+1):
                    indexStr = "S" + str(i) + "R" + str(j)
                    rephill1 = str(self.polar_df["hill"].loc[indexStr]) + " "
                    inp_f.write(rephill1)
                
                inp_f.write(newline)
        
        repe = "RE GRIDPOLR polgrid1 END" + "\n"
        inp_f.write(repe)
    
    #    Elevations need to be done for polar receptors; module to find receptors
    
    ################## Only load this when user selects Yes in the GUI
#    receptr_df = pd.read_excel(r"C:\HEM3_V153\Inputs_multi\Template_Multi_user_receptors.xlsx")
#    
#    recx = list(receptr_df['X-coordinate'][:])
#    recy = list(receptr_df['Y-coordinate'][:])
#    recu = list(receptr_df['UTM Zone'][:])
#    rece = list(receptr_df['Elevation'][:]) ############################# Need Elevations
#    
#    for i in np.arange(len(recu)):
#        if np.isnan(recu[i]) == 1:
#            recu[i] = 0
#    
#    rec_un, rec_ue, rec_uz = ll2utm.ll2utm(recy,recx,recu)
#    
#    for i in np.arange(len(rec_ue)):
#        redec = "RE DISCCART  " + str(rec_ue[i]) + " " + str(rec_un[i]) + " " + str(rece[i]) + " " + str(rece[i]) + "\n"
#        inp_f.write(redec)
#    
#    ref = "RE FINISHED  " + "\n" + "\n"
#    inp_f.write(ref)
        ref = "RE FINISHED  " + "\n"
        inp_f.write(ref)

     # %% ME Section
    
    ############################ Give the option to select meteorology data?  If not, run this code to find meteorology automatically
    
        surf_file, upper_file, surfdata_str, uairdata_str, prof_base = fm.find_met(self.cenlat, self.cenlon)
    
        year = 2016 ########################################## How do we update this when we update the meteorology files?
    
        jsta = 1
        
        if ( year % 4 ) == 0:
            jend = 366
        else:
            jend = 365
    
        mes    = "ME STARTING \n"
        me_sfc = "ME SURFFILE  metdata\\" + surf_file + "\n"
        me_pfl = "ME PROFFILE  metdata\\" + upper_file + "\n"
        me_sud = "ME SURFDATA  " + surfdata_str +  "\n"
        me_uad = "ME UAIRDATA  " + uairdata_str + "\n"
        me_prb = "ME PROFBASE  " + str(prof_base) + "\n"
        # me_day = "ME DAYRANGE  " + str(jsta) + "-" + str(jend) + "\n"
        mef    = "ME FINISHED \n" 
    
        inp_f.write(mes)
        inp_f.write(me_sfc)
        inp_f.write(me_pfl)
        inp_f.write(me_sud)
        inp_f.write(me_uad)
        inp_f.write(me_prb)
        # inp_f.write(me_day)
        inp_f.write(mef)
    
    # %% OU Section
    
        ou = "OU STARTING \n"
        inp_f.write(ou)
    
        ou = "OU FILEFORM EXP \n"
        inp_f.write(ou)
 
        for j in np.arange(len(uniqsrcs)):  
            ou = "OU PLOTFILE ANNUAL " + uniqsrcs[j] + " resources\plotfile.plt 35 \n"
            inp_f.write(ou)
        
        if acute == "Y":
            recacu = "OU RECTABLE" + " 1 " + str(hours) + " FIRST" + "\n"
        ou = "OU FINISHED \n"
        inp_f.write(ou)
    
        inp_f.close()