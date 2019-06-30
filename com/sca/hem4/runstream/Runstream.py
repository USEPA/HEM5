# -*- coding: utf-8 -*-
"""
Created on Thu Oct 18 10:23:14 2018

@author: dlindsey

"""
import math
import os

from com.sca.hem4 import FindMet as fm
from com.sca.hem4.model.Model import *
from com.sca.hem4.support.UTM import *

class Runstream():
    """
    
    
    """
    
    def __init__(self, facops_df, emislocs_df, hapemis_df, urecs_df = None, 
                 buoyant_df = None, polyver_df = None, bldgdw_df = None, 
                 partdia_df = None, landuse_df = None, seasons_df = None,
                 emisvar_df = None, model = None):
        
        self.facoptn_df = facops_df
        self.emisloc_df = emislocs_df
        self.hapemis = hapemis_df
        self.user_recs = urecs_df
        self.buoyant_df = buoyant_df
        self.polyver_df = polyver_df
        self.bldgdw_df = bldgdw_df
        self.partdia_df = partdia_df
        self.landuse_df = landuse_df
        self.seasons_df = seasons_df
        self.emisvar_df = emisvar_df
        self.model = model
        self.urban = False

        
        #open file to write
        self.inp_f = open(os.path.join("aermod", "aermod.inp"), "w")
        
    def build_co(self, phase, innerblks, outerblks):
        """
        Creates CO section of Aermod.inp file
        """
           
    # Facility ID -------------------------------------------------------------
          
        facid = self.facoptn_df['fac_id'][0]                 
   
    # Hours -------------------------------------------------------------------
                
        self.hours = self.facoptn_df['hours'][0]                      
    
        av_t = [1,2,3,4,6,8,12,24]          # Possible Averaging Time Periods
    
        if self.facoptn_df['acute'][0] == 'N':
            self.hours = " ANNUAL "
        elif (self.hours in av_t) == 1:
            self.hours = str(self.hours) + " ANNUAL "
        else:
            self. hours = str(1) + " ANNUAL "
            
    # Elevations --------------------------------------------------------------
           
        self.eleva = self.facoptn_df['elev'][0]                        

        if self.model.urepOnly_optns.get('ureponly_flat', None):
            optel = " FLAT "
        elif self.eleva == "Y":
            optel = " ELEV "
        else:
            optel = " FLAT "
    
    # deposition & depletion --------------------------------------------------
        
        #logic for phase setting in model options
        
        if phase['phase'] == 'P':
            optdp = phase['settings'][0]
            titletwo = "CO TITLETWO  Particle-phase emissions \n"
            
        
        elif phase['phase'] == 'V':
            optdp = phase['settings'][0]
            titletwo = "CO TITLETWO  Vapor-phase emissions \n"
            
        else:
            optdp = ''
            titletwo = "CO TITLETWO  Combined particle and vapor-phase emissions \n"
    
    # Building downwash option ------------------------------------------------
        self.blddw = self.facoptn_df['bldg_dw'][0]
        
    # FASTALL Model Option for AERMOD -----------------------------------------
        fasta = self.facoptn_df['fastall'][0]                     
    
        if fasta == "Y":
            optfa = " FASTALL "
        else:
            optfa = ""

    # CO Section ----------------------------------------------------------
        
        co1 = "CO STARTING  \n"
        co2 = "CO TITLEONE  " + str(facid) + "\n"
        co3 = titletwo   
        co4 = "CO MODELOPT  CONC  BETA " + optdp + optel + optfa + "\n"  
    

        self.inp_f.write(co1)
        self.inp_f.write(co2)
        self.inp_f.write(co3)
        self.inp_f.write(co4)
        
        #check for user specified urban option
        if self.facoptn_df['rural_urban'].values[0] == 'U':
            self.urban = True
            urbanopt = "CO URBANOPT " + str(self.facoptn_df['urban_pop'].values[0]) + "\n"
            self.inp_f.write(urbanopt)
             
        #if rural is forced do nothing
        elif self.facoptn_df['rural_urban'].values[0] == 'R':
            
            self.urban = False
        
        #check if there is nothing default is to determin an urban option and set
        else:
            #get shortest distance in innerblks and check for urban population
            if not innerblks.empty:
                closest = innerblks.nsmallest(1, 'distance')
                if closest['urban_pop'].values[0] > 0:
                    self.urban = True
                    urbanopt = "CO URBANOPT  " + str(closest['urban_pop'].values[0]) + "\n"
                    self.inp_f.write(urbanopt)
                    
            else: #get shortest distance from outerblocks 
                closest = outerblks.nsmallest(1, 'distance')
                if closest['urban_pop'].values[0] > 0:
                    self.urban = True
                    urbanopt = "CO URBANOPT " + str(closest['urban_pop'].values[0]) + "\n"
                    self.inp_f.write(urbanopt)
                
            
            # Landuse Options for Deposition
        if phase['phase'] == 'V' and 'DDEP' in optdp:
            
            landval = self.landuse_df[self.landuse_df.columns[1:]].values[0]
            coland = ("CO GDLANUSE " + " ".join(map(str, landval)) + '\n')
            self.inp_f.write(coland)
    
            # Season Options for Deposition
            seasval = self.seasons_df[self.seasons_df.columns[1:]].values[0]
            coseas = ("CO GDSEASON " + " ".join(map(str,seasval)) + '\n')
            self.inp_f.write(coseas)

        co5 = "CO AVERTIME  " + self.hours + "\n"
        co6 = "CO POLLUTID  UNITHAP \n"
        co7 = "CO RUNORNOT  RUN \n"
        co8 = "CO FINISHED  \n" + "\n"
    
        self.inp_f.write(co5)
        self.inp_f.write(co6)
        self.inp_f.write(co7)
        self.inp_f.write(co8)    
    
    def build_so(self, phase):
        """
        Function writes SO section of Aermod.inp, names source types and 
        their parameters
        
        """
      
        
        srid = self.emisloc_df['source_id'][:]                           # Source ID
        cord = self.emisloc_df['location_type'][:]                       # Coordinate System
        xco1 = round(self.emisloc_df['utme'][:]).astype(int)             # X-Coordinate
        yco1 = round(self.emisloc_df['utmn'][:]).astype(int)             # Y-Coordinate
        utmz = self.emisloc_df['utmzone'][:]                             # UTM Zone
        srct = self.emisloc_df['source_type'][:]                         # Source Type
        lenx = self.emisloc_df['lengthx'][:]                             # Length in X-Direction
        leny = self.emisloc_df['lengthy'][:]                             # Length in Y-Direction
        angl = self.emisloc_df['angle'][:]                               # Angle of Emission Location
        latr = self.emisloc_df['horzdim'][:]                             # Initial Lateral/Horizontal Emission
        vert = round(self.emisloc_df['vertdim'][:],2)                    # Initial Vertical Emission
        relh = round(self.emisloc_df['areavolrelhgt'][:],2)              # Release Height
        stkh = round(self.emisloc_df['stkht'][:],3)                      # Stack Height
        diam = round(self.emisloc_df['stkdia'][:],3)                     # Stack Diameter
        emiv = round(self.emisloc_df['stkvel'][:],7)                     # Stack Exit Velocity
        temp = round(self.emisloc_df['stktemp'][:],2)                    # Stack Exit Temperature
        elev = self.emisloc_df['elev'][:]                                # Elevation of Source Location
        xco2 = round(self.emisloc_df['utme_x2'][:]).astype(int)          # Second X-Coordinate
        yco2 = round(self.emisloc_df['utmn_y2'][:]).astype(int)          # Second Y-Coordinate
    
    # initialize variable used to determine the first buoyant line source (if there is one)
        first_buoyant = 0

    # Need to confirm lenx is not 0
        area = self.emisloc_df['lengthx'][:] * self.emisloc_df['lengthy'][:]
    
    
    # Checks that may be done outside of this program
    
    #checks for emission variation and extracts source ids from linked txt file
        if self.emisvar_df is not None and type(self.emisvar_df) == str:
            so_col = []
            with open(self.emisvar_df) as fobj:
                for line in fobj:
                    row = line.split()
                    so_col.append(row[6])
            
            var_sources = set(so_col).tolist()

    
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
         
        so1 = "SO STARTING \n"
        so2 = "SO ELEVUNIT METERS \n"
    
        self.inp_f.write(so1)
        self.inp_f.write(so2)
    
        #loop through sources
        for index, row in self.emisloc_df.iterrows():
                    
            # Point Source ----------------------------------------------------
    
            if srct[index] == 'P':
                soloc = ("SO LOCATION " + str(srid[index]) + " POINT " + 
                         str(xco1[index]) + " " + str(yco1[index]) + " " +
                         str(elev[index]) + "\n")
                
                soparam = ("SO SRCPARAM " + str(srid[index]) + " 1000 " + 
                           str(stkh[index]) + " " + str(temp[index]) + " " +
                           str(emiv[index]) + " " + str(diam[index]) + "\n")
                
                self.inp_f.write(soloc)
                self.inp_f.write(soparam)
                
                if self.urban == True:
                    urbanopt = "SO URBANSRC " + str(srid[index]) + "\n"
                    self.inp_f.write(urbanopt)

                if self.blddw == "Y":
                    self.get_blddw(srid[index])
                    
                if phase['phase'] == 'P':
                    self.get_particle(srid[index])
                    
                elif phase['phase'] == 'V':
                    self.get_vapor(srid[index])
                      
                if (self.emisvar_df is not None and type(self.emisvar_df) != str
                    and srid[index] in self.emisvar_df['source_id'].values ):
                    self.get_variation(srid[index])
                
                #if linked file
                elif (self.emisvar_df is not None and 
                      type(self.emisvar_df) == str and srid[index] in var_sources ):
                    
                    solink = ("SO HOUREMIS " + self.emisvar_df + " " + 
                              srid[index] + " \n")
                    self.inp_f.write(solink)
    
                
            # Horizontal Point Source ----------------------------------------
    
            elif srct[index] == 'H':
                soloc = ("SO LOCATION " + str(srid[index]) + " POINTHOR " + 
                         str(xco1[index]) + " " + str(yco1[index]) + " " + 
                         str(elev[index]) + "\n")
                
                soparam = ("SO SRCPARAM " + str(srid[index]) + " 1000 " + 
                           str(stkh[index]) + " " + str(temp[index]) + " " + 
                           str(emiv[index]) + " " + str(diam[index]) + "\n")
                
                self.inp_f.write(soloc)
                self.inp_f.write(soparam)
                
                if self.urban == True:
                    urbanopt = "SO URBANSRC " + str(srid[index]) + "\n"
                    self.inp_f.write(urbanopt)
                
                if self.blddw == "Y":
                    self.get_blddw(srid[index])
                    
                if phase['phase'] == 'P':
                    self.get_particle(srid[index])
                    
                elif phase['phase'] == 'V':
                    self.get_vapor(srid[index])
                    
                if (self.emisvar_df is not None and type(self.emisvar_df) != str
                    and srid[index] in self.emisvar_df['source_id'].values ):
                    self.get_variation(srid[index])
                
                 #if linked file
                elif (self.emisvar_df is not None and 
                      type(self.emisvar_df) == str and srid[index] in var_sources ):
                    
                    solink = ("SO HOUREMIS " + self.emisvar_df + " " + 
                              srid[index] + " \n")
                    self.inp_f.write(solink)    
                
            # Capped Point Source ---------------------------------------------------
            
            elif srct[index] == 'C':
                soloc = ("SO LOCATION " + str(srid[index]) + " POINTCAP " + 
                         str(xco1[index]) + " " + str(yco1[index]) + " " + 
                         str(elev[index]) + "\n")
                
                soparam = ("SO SRCPARAM " + str(srid[index]) + " 1000 " + 
                           str(stkh[index]) + " " + str(temp[index]) + " " + 
                           str(emiv[index]) + " " + str(diam[index]) + "\n")
                
                self.inp_f.write(soloc)
                self.inp_f.write(soparam)
                
                if self.urban == True:
                    urbanopt = "SO URBANSRC " + str(srid[index]) + "\n"
                    self.inp_f.write(urbanopt)
                
                if self.blddw == "Y":
                    self.get_blddw(srid[index])
                    
                if phase['phase'] == 'P':
                    self.get_particle(srid[index])
                    
                elif phase['phase'] == 'V':
                    self.get_vapor(srid[index])
                    
                if (self.emisvar_df is not None and type(self.emisvar_df) != str
                    and srid[index] in self.emisvar_df['source_id'].values ):
                    self.get_variation(srid[index])
                
                 #if linked file
                elif (self.emisvar_df is not None and 
                      type(self.emisvar_df) == str and srid[index] in var_sources ):
                    
                    solink = ("SO HOUREMIS " + self.emisvar_df + " " + 
                              srid[index] + " \n")
                    self.inp_f.write(solink)
                
             # Area Source ---------------------------------------------------
    
            elif srct[index] == 'A':
                soloc = ("SO LOCATION " + str(srid[index]) + " AREA " + 
                         str(xco1[index]) + " " + str(yco1[index]) + " " + 
                         str(elev[index]) + "\n")
                
                soparam = ("SO SRCPARAM " + str(srid[index]) + " " + 
                           str(1000/area[index]) + " " + str(relh[index]) + " " 
                           + str(lenx[index]) + " " + str(leny[index]) + " " + 
                           str(angl[index]) + " " + str(vert[index]) + "\n") 
                
                self.inp_f.write(soloc)
                self.inp_f.write(soparam)
                
                if self.urban == True:
                    urbanopt = "SO URBANSRC " + str(srid[index]) + "\n"
                    self.inp_f.write(urbanopt)
                
                if self.blddw == "Y":
                    self.get_blddw(srid[index])
                    
                if phase['phase'] == 'P':
                    self.get_particle(srid[index])
                    
                elif phase['phase'] == 'V':
                    self.get_vapor(srid[index])
                    
                if (self.emisvar_df is not None and type(self.emisvar_df) != str
                    and srid[index] in self.emisvar_df['source_id'].values ):
                    self.get_variation(srid[index])
                
                 #if linked file
                elif (self.emisvar_df is not None and 
                      type(self.emisvar_df) == str and srid[index] in var_sources ):
                    
                    solink = ("SO HOUREMIS " + self.emisvar_df + " " + 
                              srid[index] + " \n")
                    self.inp_f.write(solink)
                    
            # Volume Source --------------------------------------------------
    
            elif srct[index] == 'V':
                soloc = ("SO LOCATION " + str(srid[index]) + " VOLUME " + 
                         str(xco1[index]) + " " + str(yco1[index]) + " " + 
                         str(elev[index]) + "\n")
                
                soparam = ("SO SRCPARAM " + str(srid[index]) + " 1000 " + 
                           str(relh[index]) + " " + str(latr[index]) + " " + 
                           str(vert[index]) + "\n")
                
                self.inp_f.write(soloc)
                self.inp_f.write(soparam)
                
                if self.urban == True:
                    urbanopt = "SO URBANSRC " + str(srid[index]) + "\n"
                    self.inp_f.write(urbanopt)
                
                if self.blddw == "Y":
                    self.get_blddw(srid[index])
                    
                if phase['phase'] == 'P':
                    self.get_particle(srid[index])
                    
                elif phase['phase'] == 'V':
                    self.get_vapor(srid[index])
                
                if (self.emisvar_df is not None and type(self.emisvar_df) != str
                    and srid[index] in self.emisvar_df['source_id'].values ):
                    self.get_variation(srid[index])
                
                #if linked file
                elif (self.emisvar_df is not None and 
                      type(self.emisvar_df) == str and srid[index] in var_sources ):
                    
                    solink = ("SO HOUREMIS " + self.emisvar_df + " " + 
                              srid[index] + " \n")
                    self.inp_f.write(solink)
                          
            # Area Polygon (Irregular) Source --------------------------------
    
            elif srct[index] == 'I':
                # subset polyver_df to one source_id
                poly_srid = list(self.polyver_df[self.polyver_df['source_id']==
                                                 srid[index]]['source_id'][:])
                
                poly_utme = list(self.polyver_df[self.polyver_df['source_id']==
                                                 srid[index]]['utme'][:])
    
                poly_utmn = list(self.polyver_df[self.polyver_df['source_id']==
                                                 srid[index]]['utmn'][:])
                
                poly_utmz = list(self.polyver_df[self.polyver_df['source_id']==
                                                 srid[index]]['utmzone'][:])
                
                poly_numv = list(self.polyver_df[self.polyver_df['source_id']==
                                                 srid[index]]['numvert'][:])
                
                poly_area = list(self.polyver_df[self.polyver_df['source_id']==
                                                 srid[index]]['area'][:])
                        
                soloc = ("SO LOCATION " + str(srid[index]) + " AREAPOLY " + 
                         str(xco1[index]) + " " + str(yco1[index]) + " " + \
                         " " + str(elev[index]) + "\n")
                
#            poly_pos = poly_srid.index(srid[index])
                soparam = ("SO SRCPARAM " + str(srid[index]) + " " + 
                           str(1000/(poly_area[0])) + " " + str(relh[index]) + 
                           " " + str(poly_numv[0]) + "\n")
                
                self.inp_f.write(soloc)
                self.inp_f.write(soparam)
            
                for i in np.arange(len(poly_utmz)):
                    if np.isnan(poly_utmz[i]) == 1:
                        poly_utmz[i] = 0
                        
                vert_start = "SO AREAVERT " + str(poly_srid[0]) + " "
                vert_coor = ""
                for i in np.arange(len(poly_srid)):
                    if (i+1) % 6 == 0 or i == len(poly_srid):
                        vert_coor = (vert_coor + str(poly_utme[i]) + " " + 
                                     str(poly_utmn[i]) + " ")
                        
                        vert_line = vert_start + vert_coor + "\n"
                        self.inp_f.write(vert_line)
                        
                        vert_coor = str(poly_utme[i]) + " " + str(poly_utmn[i]) + " "
                    else:
                        vert_coor = (vert_coor + str(poly_utme[i]) + " " + 
                                     str(poly_utmn[i]) + " ")
                        ##write something?
                    
                if self.urban == True:
                    urbanopt = "SO URBANSRC " + str(srid[index]) + "\n"
                    self.inp_f.write(urbanopt)
                
                if self.blddw == "Y":
                    self.get_blddw(srid[index])
                    
                if phase['phase'] == 'P':
                    self.get_particle(srid[index])
                    
                elif phase['phase'] == 'V':
                    self.get_vapor(srid[index])
                
                if (self.emisvar_df is not None and type(self.emisvar_df) != str
                    and srid[index] in self.emisvar_df['source_id'].values ):
                    self.get_variation(srid[index])

                 #if linked file
                elif (self.emisvar_df is not None and 
                      type(self.emisvar_df) == str and srid[index] in var_sources ):
                    
                    solink = ("SO HOUREMIS " + self.emisvar_df + " " + 
                              srid[index] + " \n")
                    self.inp_f.write(solink)
                    
             # Line Source ----------------------------------------------------
    
            elif srct[index] == 'N':
                soloc = ("SO LOCATION " + str(srid[index]) + " LINE " + 
                         str(xco1[index]) + " " + str(yco1[index]) + " " + 
                         str(xco2[index]) + " " + str(yco2[index]) + 
                         " " + str(elev[index]) + "\n")
                
                line_len = (math.sqrt((xco1[index] - xco2[index])**2 + 
                                      (yco1[index] - yco2[index])**2))
                
                soparam = ("SO SRCPARAM " + str(srid[index]) + " " + 
                           str( round(1000 / ( lenx[index] * line_len ), 10 ) ) + " " + 
                           str(relh[index]) + " " + str(lenx[index]) + " " + 
                           str(vert[index]) + "\n")
                
                self.inp_f.write(soloc)
                self.inp_f.write(soparam)
                
                if self.urban == True:
                    urbanopt = "SO URBANSRC " + str(srid[index]) + "\n"
                    self.inp_f.write(urbanopt)
                
                if self.blddw == "Y":
                    self.get_blddw(srid[index])
                    
                if phase['phase'] == 'P':
                    self.get_particle(srid[index])
                    
                elif phase['phase'] == 'V':
                    self.get_vapor(srid[index])
                
                if (self.emisvar_df is not None and type(self.emisvar_df) != str
                    and srid[index] in self.emisvar_df['source_id'].values ):
                    self.get_variation(srid[index])
                    
                #if linked file
                elif (self.emisvar_df is not None and 
                      type(self.emisvar_df) == str and srid[index] in var_sources ):
                    
                    solink = ("SO HOUREMIS " + self.emisvar_df + " " + 
                              srid[index] + " \n")
                    self.inp_f.write(solink)
                    
                
            # Buoyant Line Source ---------------------------------------------
            
            elif srct[index] == 'B':
                soloc = ("SO LOCATION " + str(srid[index]) + " BUOYLINE " + 
                         str(xco1[index]) + " " + str(yco1[index]) + " " + 
                         str(xco2[index]) + " " + str(yco2[index]) + " " + 
                         str(elev[index]) + "\n")
                
                blemis = 1000 
                soparam = ("SO SRCPARAM " + str(srid[index]) + " " + 
                           str(blemis) + " " + str(relh[index]) + "\n")

                if first_buoyant == 0:
                    sobuopa = ("SO BLPINPUT " + str(self.buoyant_df['avgbld_len'][0]) + 
                               " " + str(self.buoyant_df['avgbld_hgt'][0]) + 
                               " " + str(self.buoyant_df['avgbld_wid'][0]) + 
                               " " + str(self.buoyant_df['avglin_wid'][0]) + 
                               " " + str(self.buoyant_df['avgbld_sep'][0]) + 
                               " " + str(self.buoyant_df['avgbuoy'][0]) + "\n")
                    
                    first_buoyant = 1
                    self.inp_f.write(sobuopa)
                
                self.inp_f.write(soloc)
                self.inp_f.write(soparam)
                
                if self.urban == True:
                    urbanopt = "SO URBANSRC " + str(srid[index]) + "\n"
                    self.inp_f.write(urbanopt)
                
                if self.blddw == "Y":
                    self.get_blddw(srid[index])
                    
                if phase['phase'] == 'P':
                    self.get_particle(srid[index])
                    
                elif phase['phase'] == 'V':
                    self.get_vapor(srid[index])
                    
                if (self.emisvar_df is not None and type(self.emisvar_df) != str
                    and srid[index] in self.emisvar_df['source_id'].values):
                    self.get_variation(srid[index])
               
                #if linked file
                elif (self.emisvar_df is not None and 
                      type(self.emisvar_df) == str and srid[index] in var_sources ):
                    
                    solink = ("SO HOUREMIS " + self.emisvar_df + " " + 
                              srid[index] + " \n")
                    self.inp_f.write(solink)

                
             
             # SO Source groups ---------------------------------------------
            
        self.uniqsrcs = srid.unique()
        for i in np.arange(len(self.uniqsrcs)):  
            sogroup = ("SO SRCGROUP " + self.uniqsrcs[i] + " " + 
                       self.uniqsrcs[i] + "-" + self.uniqsrcs[i] + "\n")
            self.inp_f.write(sogroup)
        so3 = "SO FINISHED \n" + "\n"
        self.inp_f.write(so3)
                
        
    def build_re(self, discrecs_df, cenx, ceny, polar_df):
        """
        Writes RE section to aer.inp
        
        """
        self.polar_df = polar_df
        newline = "\n"
        
        res = "RE STARTING  " + "\n"
        self.inp_f.write(res)
 

    ## Discrete Receptors

        recx = list(discrecs_df[utme][:])
        recy = list(discrecs_df[utmn][:])
        rece = list(discrecs_df[elev][:]) # Elevations
        rech = list(discrecs_df[hill][:]) # Hill height

        for i in np.arange(len(recx)):
            if self.eleva == "Y":
                redec = ("RE DISCCART  " + str(recx[i]) + " " + str(recy[i]) + 
                         " " + str(int(round(rece[i]))) + " " + 
                         str(int(round(rech[i]))) + "\n")
            else:
                redec = "RE DISCCART  " + str(recx[i]) + " " + str(recy[i]) + "\n"
            self.inp_f.write(redec)

            
    ## Polar Recptors
    
        rep = "RE GRIDPOLR polgrid1 STA" + "\n"
        repo = ("RE GRIDPOLR polgrid1 ORIG " + str(cenx) + " " + 
                str(ceny) + "\n")
        repd = "RE GRIDPOLR polgrid1 DIST "

        self.inp_f.write(rep)
        self.inp_f.write(repo)
        self.inp_f.write(repd)

        recep_dis = self.polar_df["distance"].unique()
        num_rings = len(recep_dis)
        
        for i in np.arange(num_rings):
            repdis = str(recep_dis[i]) + " "
            self.inp_f.write(repdis)

        self.inp_f.write(newline)

        repi = "RE GRIDPOLR polgrid1 DDIR "
        self.inp_f.write(repi)

        recep_dir = self.polar_df["angle"].unique()
        num_sectors = len(recep_dir)
        for i in np.arange(num_sectors):
            repdir = str(recep_dir[i]) + " "
            self.inp_f.write(repdir)

        self.inp_f.write(newline)
    
        #add elevations and hill height if user selected it
        if self.eleva == "Y":
            for i in range(1, num_sectors+1):
                indexStr = "S" + str(i) + "R1"
                repelev0 = ("RE GRIDPOLR polgrid1 ELEV " + 
                            str(self.polar_df["angle"].loc[indexStr]) + " ")
                
                self.inp_f.write(repelev0)
                
                for j in range(1, num_rings+1):
                    indexStr = "S" + str(i) + "R" + str(j)
                    repelev1 = str(self.polar_df["elev"].loc[indexStr]) + " "
                    self.inp_f.write(repelev1)

                self.inp_f.write(newline)

                rephill0 = ("RE GRIDPOLR polgrid1 HILL " + 
                            str(self.polar_df["angle"].loc[indexStr]) + " ")
                
                self.inp_f.write(rephill0)
                
                for j in range(1, num_rings+1):
                    indexStr = "S" + str(i) + "R" + str(j)
                    rephill1 = str(self.polar_df["hill"].loc[indexStr]) + " "
                    self.inp_f.write(rephill1)
                self.inp_f.write(newline)
        
        repe = "RE GRIDPOLR polgrid1 END" + "\n"
        self.inp_f.write(repe)
        
        ref = "RE FINISHED  " + "\n"
        self.inp_f.write(ref)
        
        
    def build_me(self, cenlat, cenlon):
        """
        Writes the ME section to aer.inp
        """
        
        surf_file, upper_file, surfdata_str, uairdata_str, prof_base, distance = fm.find_met(cenlat, cenlon)
    
        year = 2016 #How do we update this when we update the meteorology files?
    
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
    
        self.inp_f.write(mes)
        self.inp_f.write(me_sfc)
        self.inp_f.write(me_pfl)
        self.inp_f.write(me_sud)
        self.inp_f.write(me_uad)
        self.inp_f.write(me_prb)
        # inp_f.write(me_day)
        self.inp_f.write(mef)

        return surf_file, distance
        
    def build_ou(self):
        """
        Writes OU section of aer.inp
        """
        
        acute = self.facoptn_df['acute'][0] #move to ou
        acute_hrs = self.facoptn_df['hours'][0]
        if acute == "":
            acute = "N"
        
        ou = "OU STARTING \n"
        self.inp_f.write(ou)
    
        ou = "OU FILEFORM EXP \n"
        self.inp_f.write(ou)
 
        for j in np.arange(len(self.uniqsrcs)):  
            ou = ("OU PLOTFILE ANNUAL " + self.uniqsrcs[j] + 
                  " plotfile.plt 35 \n")
            self.inp_f.write(ou)
        
        if acute == "Y":
            recacu = "OU RECTABLE "  + str(acute_hrs) + " FIRST" + "\n"
            self.inp_f.write(recacu)
            for k in np.arange(len(self.uniqsrcs)):  
                acuou = ("OU PLOTFILE " + str(acute_hrs) + " " + self.uniqsrcs[k] + 
                      " FIRST maxhour.plt 40 \n")
                self.inp_f.write(acuou)

            #set in model options
            self.model.model_optns['acute'] = True
            
        
        ou = "OU FINISHED \n"
        self.inp_f.write(ou)
    
        self.inp_f.close()
        
    def get_blddw(self, srid):
        """
        Compiles and writes building downwash parameters for a given source
        to aer.inp
        
        """
        
        newline = "\n"
        
        bldgdim_df = self.bldgdw_df
        bldg_srid = bldgdim_df['source_id'][:]
        bldg_keyw = bldgdim_df['keyword'][:]
        
        for i in range(len(bldg_srid)):
            if srid == bldg_srid[i]:
                row = bldgdim_df.loc[i,]
                values = row.tolist()
                if values[2] == 'XBADJ':     
                    #keywords too short so adding 4 spaces to preserve columns                                
                    bldgdim = ('SO ' + values[2] + "    " +  
                               " ".join(str(x) for x in values[3:]))
                    self.inp_f.write(bldgdim)
                    self.inp_f.write(newline)
                    
                elif values[2] == 'YBADJ':
                    #keywords too short so adding 4 spaces to preserve columns                               
                    bldgdim = ('SO ' + values[2] + "    " +  
                               " ".join(str(x) for x in values[3:]))
                    self.inp_f.write(bldgdim)
                    self.inp_f.write(newline)
                
                else:
                    bldgdim = (" ".join(str(x) for x in values[1:]))
                    self.inp_f.write(bldgdim)
                    self.inp_f.write(newline)
                    
    def get_particle(self, srid):
        """
        Compiles and writes paremeters for particle deposition/depletion 
        by source
        """
            
       #get values for this source id
        
        partdia_source = self.partdia_df[self.partdia_df['source_id'] == srid]
        part_diam = partdia_source['part_diam'].tolist()
        part_dens = partdia_source['part_dens'].tolist()
        mass_frac = partdia_source['mass_frac'].tolist()
        

        sopdiam = ("SO PARTDIAM " + str(srid) + " " +
                   " ".join(map(str, part_diam)) +"\n")
        sopdens = ("SO PARTDENS " + str(srid) + " " +
                   " ".join(map(str, part_dens))+"\n")
        somassf = ("SO MASSFRAX " + str(srid) + " " +
                   " ".join(map(str, mass_frac))+"\n")
        
        #print(sopdiam)
        #print(sopdens)
        #print(somassf)
        self.inp_f.write(sopdiam)
        self.inp_f.write(somassf)
        self.inp_f.write(sopdens)
        
        #method 2 tbd
#         if part_met2 == "Y":
#        partme2_df = pd.read_excel(r"Currently not a created file") 
#        sourc = list(partme2_df['Source ID'][:])
#        sr_pos = sourc.index(srid[index])
#        someth2 = "SO METHOD_2 " + str(srid[index]) + " " + str(partme2_df['Fine Mass'][sr_pos]) + \
#            " " + str(partme2_df['Dmm'][sr_pos]) + "\n"
#        inp_f.write(someth2)

    def get_vapor(self, srid):
        """
        Compiles and writes parameters for vapor deposition/depletion by source
        """
        pollutants = (self.hapemis[(self.hapemis['source_id'] == srid)
                                    & (self.hapemis['part_frac'] < 1)]['pollutant'].str.lower())
            
        params = self.model.gasparams.dataframe.loc[self.model.gasparams.dataframe['pollutant'].isin(pollutants)]
                
        #write values if they exist in the 
        #so there should only be one pollutant per source id for vapor/gas deposition to work
        #currently default values if the size of pollutant list is greater than 1
        
        if len(params) != 1: ## check if len params works for empties
            #log message about defaulting 
            
            da    =    0.07
            dw    =    0.70
            rcl   = 2000.00
            henry =    5.00
            
            sodepos = ("SO GASDEPOS " + str(srid) + " " + str(da) + 
                       " " + str(dw) + " " + str(rcl) + " " + str(henry) + "\n")
            self.inp_f.write(sodepos)
            
        else:
        
        #check gas params dataframe for real values and pull them out for that one source
                #print('found vapor params', params)
            
                sodepos = ("SO GASDEPOS " + str(srid) + " " + str(params['da'][0]) + 
                       " " + str(params['dw'][0]) + " " + str(params['rcl'][0]) + 
                       " " + str(params['henry'][0]) + "\n")
                self.inp_f.write(sodepos)
   
    def get_variation(self, srid):
        """
        Compiles and writes parameters for emissions variation
        """
        
        #get row
        sourcevar =  self.emisvar_df[self.emisvar_df["source_id"] == srid]
        
        #get qflag
        qflag = sourcevar[sourcevar.columns[2]].str.upper().values[0]
        
        #get variation -- variable number of columns so slice all starting at 4
        variation = sourcevar[sourcevar.columns[3:]].values
        
        #seasons, windspeed or month will have only one list
        if len(variation) == 1:
        
            length = len(variation[0])
            
            #if seasons, windspeed or month
            if length == 4 or length == 6 or length == 12:
                var = variation[0].tolist()
                print(var)
                sotempvar = str("SO EMISFACT " + str(srid) + " " + qflag +  " " +
                             " ".join(map(str, var)) +"\n")
                
                self.inp_f.write(sotempvar)
            
        #everything elese will have lists in multiples of 12   
        else:
        
            for row in variation:
                var = variation.tolist()
                print(var)
                sotempvar = str("SO EMISFACT " + str(srid) + " " + qflag +  " " +
                         " ".join(map(str, var)) +"\n")
            
                self.inp_f.write(sotempvar)
        
                 
                
    
            

        
            
            
        
        
        
             